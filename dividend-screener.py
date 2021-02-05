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
from static import dropdown, company_name, divyield, pe, chowder, fiveten
from static import debtequity, payout, getstocks, scatter_graph
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


start = datetime.datetime.now()

# Screen criteria, will be controlled by user eventually
### Save data to dcc.Store

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])
app.layout = html.Div(children=[
    dcc.Store(id='stocks', storage_type='session'),
    html.H1(children='Dividend Dashboard'),
    dbc.Row([
        dbc.Col([
            getstocks,
            dropdown, # ticker selector
        ]),
        dbc.Col([
            html.Div('pe filter'),
            html.Div('div yield filter'),
            html.Div('% payout filter'),
        ]) # Recessions Survived column
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
        ], className='graphcards'), # Stacked cards
        dbc.Col([
            scatter_graph
        ], width=9), # Price Charts
    ], justify='end')
], className='content')

@app.callback([Output('dropdown', 'options'), Output('stocks', 'data')],
                Input('getstocks', 'n_clicks'))
def get_stocks(n_clicks):
    '''Grabs spreadsheet and latest prices'''
    ctx = dash.callback_context
    if n_clicks is None or ctx.triggered[0].get('value') is None:
        raise PreventUpdate
    mindiv = 3.0
    minchowder = 8
    maxpe = 25
    maxpayout = 75
    maxdebt = 0.7


    url = 'https://bitly.com/USDividendChampions'
    sheets = ['Champions', 'Contenders', 'Challengers']

    print('Downloading and processing Dividend Sheet...\n')
    df_list = funcs.get_master_sheet(url, sheets)

    df = funcs.clean_data(df_list)

    print('Total # of Stocks considered:',df.shape[0],'\n')

    print('Total # of Screened Stocks considered:',df.shape[0],'\n')
    print('Fetching latest stock prices...\n')

    #get latest stock price
    ticker_list = list(df.Ticker.unique())
    ticker_list_clean = [ticker for ticker in ticker_list if isinstance(ticker, str)]
    quote_date = start.strftime('%Y-%m-%d')
    start_date = start - datetime.timedelta(days=7)
    print(quote_date, start_date)
    dat = yf.download(ticker_list_clean,start=start_date,end=quote_date,group_by='ticker')
    # Melt returned df
    df_dat = dat.iloc[[-2]].melt()
    # Drop rows with nan values
    df_dat.dropna(inplace=True)
    # Use Open, Close, etc as columns, no multi-index
    df_dat = pd.pivot_table(df_dat, index='variable_0', columns='variable_1', values='value', aggfunc='mean')
    
    df = df.merge(right=df_dat,how='left',left_on='Ticker',right_on=df_dat.index)
    df['5/10 A/D*'] = df.apply(lambda row: funcs.fiveten(row),axis=1)

    # Adjust dividend yield and price based on current up-to-date price
    df['Div.Yield'] = df.apply(lambda row: row['Div.Yield']*row['Close']/row['Price'],axis=1)
    df['P/E'] = df.apply(lambda row: row['TTM P/E']*row['Close']/row['Price'],axis=1)

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
    ticker_dict = [{'label':label , 'value':value} for label, value in zip(df.Company.values, df.Ticker.values)]
    df.to_csv('inspection.csv')
    return ticker_dict, df.to_json(orient='records')

@app.callback([Output('yield-div', 'children'), Output('pe-div', 'children'), Output('chowder-div', 'children'),
                Output('fiveten-div', 'children'), Output('debtequity-div', 'children'), Output('payout-div', 'children'),
                Output('sector-div', 'children'), Output('industry-div', 'children'), Output('noyrs-div', 'children')],
                Input('dropdown', 'value'),
                State('stocks', 'data'))
def update_cards(ticker, data):
    '''Update cards based on dropdown selection'''
    ctx = dash.callback_context
    if data is None or ctx.triggered[0].get('value') is None:
        raise PreventUpdate
    df = pd.DataFrame.from_dict(json.loads(data))
    divyield_ret = df.loc[df.Ticker == ticker, 'Div.Yield'].round(2).values
    pe_ret = df.loc[df.Ticker == ticker, 'P/E'].round(2)
    chowder_ret = df.loc[df.Ticker == ticker, 'Chowder Rule'].round(2)
    fiveten_ret = df.loc[df.Ticker == ticker, '5/10 A/D*'].round(2)
    debtequity_ret = df.loc[df.Ticker == ticker, 'Debt/Equity'].round(2)
    payout_ret = df.loc[df.Ticker == ticker, 'EPS %Payout'].round(2)
    sector_ret = 'Sector : {}'.format(df.loc[df.Ticker == ticker, 'Sector'].values[0])
    industry_ret = 'Industry : {}'.format(df.loc[df.Ticker == ticker, 'Industry'].values[0])
    noyrs_ret = 'No. Yrs : {}'.format(df.loc[df.Ticker == ticker, 'No.Yrs'].values[0])

    return divyield_ret, pe_ret, chowder_ret, fiveten_ret, \
        debtequity_ret, payout_ret, sector_ret, industry_ret, noyrs_ret

@app.callback(Output('scatter', 'figure'),
            Input('stocks', 'data'))
def update_scatter(data):
    '''Update Graph based on fetched stocks'''
    if data is None:
        raise PreventUpdate
    df = pd.DataFrame.from_dict(json.loads(data))
    fig_scatter = px.scatter(df, x='No.Yrs', y='Div.Yield', color='Industry', hover_data=['Company', 'Ticker'])
    return fig_scatter

# @app.callback(Output(),
#             [Input(), Input(), Input()])
# def update_filtered_stocks(input):
#     '''Update outputs based on filter changes'''

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)