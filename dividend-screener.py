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

start = datetime.datetime.now()

#import screen criteria
settings = pd.read_csv('dividend_settings.txt',)
mindiv = float(settings.iloc[0])
minchowder = float(settings.iloc[2])
maxpe = float(settings.iloc[4])
maxpayout = float(settings.iloc[6])
maxdebt = float(settings.iloc[8])

print('Downloading Dividend Champions Sheet...\n')

### READ DIRECTLY WITH PANDAS ###
#obtain latest copy of USDividendChampions
url = 'https://bitly.com/USDividendChampions'
file = requests.get(url)

with open('DividendChampions.xlsx','wb') as d:
    d.write(file.content)
    
print('Processing Dividend Champions Spreadsheet...\n')

#read in the dividend stock data
filename = 'DividendChampions.xlsx'
df1 = pd.read_excel(filename,sheet_name='Champions')
df2 = pd.read_excel(filename,sheet_name='Contenders')
df3 = pd.read_excel(filename,sheet_name='Challengers')
df_list = [df1,df2,df3]

#clean data
for df in df_list:
    df.drop(df.index[0:5], inplace=True)
    df.columns = ['Company','Ticker','Sector','Industry','No.Yrs','CCCSeq','DRIP DR', 'Fees SP','Price', 'Div.Yield', 'Current Dividend','Payouts/Year', 'Annualized','Qtly Sch','Previous Payout','Last Increased on:Ex-Div','Last Increased on:Pay','MR%Inc.','DGR 1-yr','DGR 3-yr','DGR 5-yr','DGR 10-yr','5/10 A/D*','Past 5yr DEG','&=MultiIncThisYrNotes','EPS %Payout','TTM P/E','FYE Month','TTM EPS','PEG','TTM P/Sales','MRQ P/Book','TTM ROE','TTM Growth','NY Growth','Past 5yr Growth','Est-5yr Growth','MktCap($Mil)','Inside Own.','Debt/Equity','TweedFactor','Chowder Rule','+/-% vs.Graham','Estimated Div:2018','2019','2020','2021','2022','Est. Payback$','Est. Payback%','5-yr Beta','52-wk Low','52-wk High','50-day MMA','200-day MMA','OTC','StreakBegan','RecessionsSurvived','TTM ROA']
    df.drop(df[df['Company']==nan].index,inplace=True)
    df.drop(df.index[-15:], inplace=True)
    
#concatenate all df's into master df
df = pd.concat(df_list)
print('Total # of Stocks considered:',df.shape[0],'\n')
      
#convert datatype for columns of interest
scr_col = ['Div.Yield','EPS %Payout','Debt/Equity','TTM P/E','Chowder Rule','DGR 1-yr','DGR 3-yr','DGR 5-yr','DGR 10-yr','5/10 A/D*']
for col in scr_col:
    df[col] = df[col].astype(float)

print('Fetching latest stock prices...\n')

#get latest stock price
ticker_list = list(df.Ticker.unique())
ticker_list_clean = [ticker for ticker in ticker_list if isinstance(ticker, str)]
quote_date = start.strftime('%Y-%m-%d')
start_date = start - datetime.timedelta(days=1)
print(quote_date, start_date)
dat = yf.download(ticker_list_clean,start=start_date,end=quote_date,group_by='ticker')
print(dat.info())
#melt returned df
df_dat = dat.melt()
#drop date with nan values
df_dat.dropna(inplace=True)
#use Open, Close, etc as columns, no multi-index
df_dat = df_dat.pivot(index='variable_0',columns='variable_1',values='value')
df = df.merge(right=df_dat,how='left',left_on='Ticker',right_on=df_dat.index)
print(df.columns)
#calculate 5/10 A/D* for missing values
def fiveten(r):
    try:
        ans = abs(r['DGR 5-yr'])/abs(r['DGR 10-yr'])
        return ans
    except:
        return nan
df['5/10 A/D*'] = df.apply(lambda row: fiveten(row),axis=1)

#screen stocks by yield, chowder rule, EPS, and debt/equity
evalexp = (df['Div.Yield'] > mindiv) & (df['Chowder Rule'] > minchowder) & (df['EPS %Payout'] < maxpayout) & (df['Debt/Equity'] < maxdebt)
df_screen = df[evalexp].sort_values(by='Div.Yield',ascending=False)

#Adjust dividend yield and price based on current up-to-date price
df_screen['Div.Yield'] = df_screen.apply(lambda row: row['Div.Yield']*row['Close']/row['Price'],axis=1)
df_screen['P/E'] = df_screen.apply(lambda row: row['TTM P/E']*row['Close']/row['Price'],axis=1)

#add feature for 1 year DGR over 3 yr DGR
df_screen['1/3 A/D'] = df_screen['DGR 1-yr'] / df_screen['DGR 3-yr']

print('***Summary of Eligible Stocks***')
print('Number of Stocks:',df_screen.shape[0])
print('# Industries:',len(df_screen['Industry'].unique()))
print('')
print(df_screen[['Company','Ticker','Div.Yield','No.Yrs','5/10 A/D*','EPS %Payout','Debt/Equity','P/E','Close']].head(15).sort_values(by='Div.Yield',ascending=False))

#save screen list for further analysis if desired
df_screen.to_excel('DividendScreenList.xlsx')
elapsed = datetime.datetime.now()-start
print('Program Run time (s):',elapsed.seconds)
print('Program Run time (m):',round(elapsed.seconds/60,2))