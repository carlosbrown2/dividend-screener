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

start = datetime.datetime.now()

#import screen criteria
settings = pd.read_csv('dividend_settings.txt',)
mindiv = float(settings.iloc[0])
minchowder = float(settings.iloc[2])
maxpe = float(settings.iloc[4])
maxpayout = float(settings.iloc[6])
maxdebt = float(settings.iloc[8])


url = 'https://bitly.com/USDividendChampions'
sheets = ['Champions', 'Contenders', 'Challengers']

print('Downloading and processing Dividend Sheet...\n')
df_list = funcs.get_master_sheet(url, sheets)

df = funcs.clean_data(df_list)

print('Total # of Stocks considered:',df.shape[0],'\n')

# Screen by criteria prior to fetching stock prices
# Screen stocks by yield, chowder rule, EPS, and debt/equity
evalexp = (df['Div.Yield'] > mindiv) & (df['Chowder Rule'] > minchowder) & \
            (df['EPS %Payout'] < maxpayout) & (df['Debt/Equity'] < maxdebt)
df = df.loc[evalexp, :].sort_values(by='Div.Yield', ascending=False)

print('Total # of Screened Stocks considered:',df.shape[0],'\n')
print('Fetching latest stock prices...\n')

#get latest stock price
ticker_list = list(df.Ticker.unique())
ticker_list_clean = [ticker for ticker in ticker_list if isinstance(ticker, str)]
quote_date = start.strftime('%Y-%m-%d')
start_date = start - datetime.timedelta(days=1)
print(quote_date, start_date)
dat = yf.download(ticker_list_clean,start=start_date,end=quote_date,group_by='ticker')

# Melt returned df
df_dat = dat.melt()
#drop date with nan values
df_dat.dropna(inplace=True)
#use Open, Close, etc as columns, no multi-index
df_dat = df_dat.pivot(index='variable_0',columns='variable_1',values='value')
df = df.merge(right=df_dat,how='left',left_on='Ticker',right_on=df_dat.index)

df['5/10 A/D*'] = df.apply(lambda row: funcs.fiveten(row),axis=1)

# Adjust dividend yield and price based on current up-to-date price
df['Div.Yield'] = df.apply(lambda row: row['Div.Yield']*row['Close']/row['Price'],axis=1)
df['P/E'] = df.apply(lambda row: row['TTM P/E']*row['Close']/row['Price'],axis=1)

# Add feature for 1 year DGR over 3 yr DGR
df['1/3 A/D'] = df['DGR 1-yr'] / df['DGR 3-yr']

print('***Summary of Eligible Stocks***')
print('Number of Stocks:',df.shape[0])
print('# Industries:',len(df['Industry'].unique()))
print('')
print(df[['Company','Ticker','Div.Yield','No.Yrs','5/10 A/D*','EPS %Payout',
            'Debt/Equity','P/E','Close']].head(15).sort_values(by='Div.Yield',ascending=False))

#save screen list for further analysis if desired
df.to_excel('DividendScreenList.xlsx')
elapsed = datetime.datetime.now()-start
print('Program Run time (s):',elapsed.seconds)
print('Program Run time (m):',round(elapsed.seconds/60,2))