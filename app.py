# -*- coding: utf-8 -*-
"""
Dividend Champions/Contenders/Challengers Analysis

By: CAB

"""
### CREATE VIRTUAL ENVIRONMENT ###
import pandas as pd
from numpy import nan
import yfinance as yf
import requests
import datetime
import funcs
import json
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import plotly.express as px
from flask_restful import Resource, Api
from requests import get
from static import dropdown, company_name, divyield, pe, chowder, fiveten
from static import debtequity, payout, getstocks, scatter_graph, inside
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


start = datetime.datetime.now()

# Screen criteria, will be controlled by user eventually
### Save data to dcc.Store

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])
server = app.server
api = Api(server)

# Set GET endpoint for interval ping
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

# Add resource to the api
api.add_resource(HelloWorld, '/hello')

app.layout = html.Div(children=[
    dcc.Store(id='stocks', storage_type='session'),
    dcc.Interval(
            id='interval-component',
            interval=1740*1000, # About every hour, fire
    ),
    html.Div(id='no-show', style={'display':'none'}),
    html.H1(children='Dividend Dashboard'),
    dbc.Row([
        dbc.Col([
            getstocks,
            dropdown, # ticker selector
        ]),
        dbc.Col([
                html.Div('Minimum Yield % '),
                html.Div('Max Payout % ', className='titlespacer'),
                html.Div('Max Debt/Equity % ', className='titlespacer')
        ], className='inputtitles'),
        html.Div([
            dcc.Input(
                    id="minyield",
                    type='number',
                    # placeholder="Minimum Yield %",
                    value=2.0,
                    className='inputs'
                ),
            dcc.Input(
                    id="maxpayout",
                    type='number',
                    value=60,
                    className='inputs'
                ),
            dcc.Input(
                    id="maxdebt",
                    type='number',
                    value=75,
                    className='inputs'
                )
            
        ], className='filtertitles') # Recessions Survived column
    ], className='dropdownrow'),
    dbc.Row([
        dbc.Col(html.Div(children='Sector : {}'.format(''), id='sector-div')),
        dbc.Col(html.Div(children='Industry : {}'.format(''), id='industry-div')),
        dbc.Col(html.Div(children='No Yrs : {}'.format(''), id='noyrs-div')),
    ]),
    dbc.Row([
        dbc.Col(divyield, className='divyield'), # Div. Yield
        dbc.Col(pe, className='fourrowcard_center'), # P/E
        dbc.Col(chowder, className='fourrowcard_center'), # Chowder Rule
        dbc.Col(fiveten, className='fiveten'), # 5/10 AGR
    ]),
    dbc.Row([
        dbc.Col([
            debtequity,
            payout,
            inside
        ], className='graphcards'), # Stacked cards
        dbc.Col([
            scatter_graph
        ], width=9), # Price Charts
    ], justify='end'),
    html.H5('Data Sources'),
    html.Link('DRIP Dividend Champions Spreadsheet', href='https://www.dripinvesting.org/Tools/Tools.asp'),
    html.Br(),
    html.Link('Yahoo Finance', href='https://finance.yahoo.com/')
], className='content')

@app.callback(Output('stocks', 'data'),
                Input('getstocks', 'n_clicks'))
def get_stocks(n_clicks):
    '''Grabs spreadsheet and latest prices'''
    ctx = dash.callback_context
    if n_clicks is None or ctx.triggered[0].get('value') is None:
        raise PreventUpdate

    url = 'https://bitly.com/USDividendChampions'
    sheets = ['Champions', 'Contenders', 'Challengers']

    print('Downloading and processing Dividend Sheet...\n')
    df_list = funcs.get_master_sheet(url, sheets)

    df = funcs.clean_data(df_list)

    print('Total # of Stocks considered:',df.shape[0],'\n')

    print('Total # of Screened Stocks considered:',df.shape[0],'\n')
    print('Fetching latest stock prices...\n')

    df['5/10 A/D*'] = df.apply(lambda row: funcs.fiveten(row),axis=1)

    # Add feature for 1 year DGR over 3 yr DGR
    df['1/3 A/D'] = df['DGR 1-yr'] / df['DGR 3-yr']
    
    # Remove non-string Tickers
    exclude_list = ['Averages for All', 'Communication Services', 'Consumer Discretionary', 'Consumer Staples', 'Energy']
    df = df.loc[~df.Company.isin(exclude_list), :]
    # Reduce length of Industry name
    industry_map_dict = {'Mortgage Real Estate Investment Trusts (REITS)':'Mortgage REITS',
                        'Independent Power and Renewable Electricity Producers': 'Ind. Power and Renew. Electricity Producers',
                        'Electronic Equipment, Instruments, and Components': 'Elec. Equip., Instruments, Components'}
    key_list = list(industry_map_dict.keys())
    # df.Industry = df.Industry.map(industry_map_dict)
    df.Industry = df.Industry.apply(lambda x: industry_map_dict.get(x) if x in key_list else x)
    
    # Drop NA values
    df = df.dropna(subset=['Company', 'Ticker'])
    # Add new columns
    df = df.assign(updated = False)
    df['P/E'] = 0
    df.to_csv('inspection.csv')
    return df.to_json(orient='records')

@app.callback([Output('yield-div', 'children'), Output('pe-div', 'children'), Output('chowder-div', 'children'),
                Output('fiveten-div', 'children'), Output('debtequity-div', 'children'), Output('payout-div', 'children'),
                Output('sector-div', 'children'), Output('industry-div', 'children'), Output('noyrs-div', 'children'),
                Output('inside-div', 'children')],
                Input('dropdown', 'value'),
                State('stocks', 'data'))
def update_cards(ticker, data):
    '''Update cards based on dropdown selection'''
    ctx = dash.callback_context
    if data is None or ctx.triggered[0].get('value') is None:
        raise PreventUpdate
    # check that stock price has been retrieved already
    df = pd.DataFrame.from_dict(json.loads(data))
    
    # Get latest stock price
    ticker_list = [ticker]
    ticker_list_clean = [ticker for ticker in ticker_list if isinstance(ticker, str)]

    quote_date = start.strftime('%Y-%m-%d')
    start_date = start - datetime.timedelta(days=7)
    
    print('Quote date is {}'.format(quote_date))
    print('Start date is {}'.format(start_date))
    # Get price data
    dat = yf.download(ticker_list_clean, start=start_date, end=quote_date, group_by='ticker')
    # df_dat = dat.iloc[[-2]].melt()
    # Drop rows with nan values
    dat.dropna(inplace=True)
    # df_dat = pd.pivot_table(df_dat, index='variable_0', columns='variable_1', values='value', aggfunc='mean')
    # Adjust dividend yield and price based on current up-to-date price
    df.loc[df.Ticker == ticker, 'Div.Yield'] = df.loc[df.Ticker == ticker, 'Div.Yield']*dat.loc[dat.index[-1], 'Close']/df.loc[df.Ticker == ticker, 'Price']
    df.loc[df.Ticker == ticker, 'P/E'] = df.loc[df.Ticker == ticker, 'TTM P/E']*dat.loc[dat.index[-1], 'Close']/df.loc[df.Ticker == ticker, 'Price']
    # df['P/E'] = df.apply(lambda row: row['TTM P/E']*row['Close']/row['Price'],axis=1)
    # df.loc[df.Ticker == ticker, 'updated'] = True
        
    divyield_ret = df.loc[df.Ticker == ticker, 'Div.Yield'].round(2).values
    pe_ret = df.loc[df.Ticker == ticker, 'P/E'].round(2)
    chowder_ret = df.loc[df.Ticker == ticker, 'Chowder Rule'].round(2)
    fiveten_ret = df.loc[df.Ticker == ticker, '5/10 A/D*'].round(2)
    debtequity_ret = df.loc[df.Ticker == ticker, 'Debt/Equity'].round(2)
    payout_ret = df.loc[df.Ticker == ticker, 'EPS %Payout'].round(2)
    inside_ret = df.loc[df.Ticker == ticker, 'Inside Own.']
    sector_ret = 'Sector : {}'.format(df.loc[df.Ticker == ticker, 'Sector'].values[0])
    industry_ret = 'Industry : {}'.format(df.loc[df.Ticker == ticker, 'Industry'].values[0])
    noyrs_ret = 'No. Yrs : {}'.format(df.loc[df.Ticker == ticker, 'No.Yrs'].values[0])

    return divyield_ret, pe_ret, chowder_ret, fiveten_ret, \
        debtequity_ret, payout_ret, sector_ret, industry_ret, noyrs_ret, inside_ret


@app.callback(Output('scatter', 'figure'),
            Input('stocks', 'data'))
def update_scatter(data):
    '''Update Graph based on fetched stocks'''
    if data is None:
        raise PreventUpdate
    df = pd.DataFrame.from_dict(json.loads(data))
    fig_scatter = px.scatter(df, x='No.Yrs', y='Div.Yield', color='Industry', hover_data=['Company', 'Ticker'])
    return fig_scatter


@app.callback(Output('dropdown', 'options'),
                [Input('minyield', 'value'),
                Input('maxdebt', 'value'),
                Input('maxpayout', 'value'),
                Input('stocks', 'data')])
def update_dropdown(minyield, maxdebt, maxpayout, data):
    '''Update dropdown on stock retrieval or update to filters'''
    if data is None:
        raise PreventUpdate
    df = pd.read_json(data, orient='records')

    df = df.loc[(df['Div.Yield']>minyield) & (df['EPS %Payout']<maxpayout) & (df['Debt/Equity']<maxdebt/100),:]
    ticker_dict = [{'label':label , 'value':value} for label, value in zip(df.Company.values, df.Ticker.values)]
    return ticker_dict

@app.callback(Output('no-show', 'children'),
            [Input('interval-component', 'n_intervals')])
def interval_get(n_intervals):
    # GET response from REST api to keep app awake
    response = get('https://divscreener.herokuapp.com/hello')
    return 'Success!'


if __name__ == '__main__':
    app.run_server(debug=False, port=8000)