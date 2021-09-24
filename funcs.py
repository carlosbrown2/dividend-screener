import requests
import pandas as pd
from numpy import nan

def get_master_sheet(url, sheets):
    '''Retrieve master spreadsheet and return list of dfs'''
    file = requests.get(url)
    filename = 'DividendChampions.xlsx'
    with open(filename,'wb') as d:
        d.write(file.content)
    #read in the dividend stock data
    df = pd.read_excel(filename,sheet_name=sheets, engine='openpyxl')
    df_list = [df.get(sheet) for sheet in sheets]
    return df_list

def clean_data(df_list):
    # Clean data
    for df in df_list:
        # print(df.head())
        
        # df.columns= ['Symbol','Company','FV','Sector','No Years','Price','Div Yield','5Y Avg Yield',
        #             'Current Div','Payouts/ Year','Annualized','Previous Div','Ex-Date','Pay-Date',
        #             'Low','High','DGR 1Y','DGR 3Y','DGR 5Y','DGR 10Y','TTR 1Y','TTR 3Y','Fair Value',
        #             'FV %', 'Filler', 'Streak Basis','Chowder Number','EPS 1Y','Revenue 1Y','NPM','CF/Share','ROE',
        #             'Current R','Debt/Capital', 'ROTC', 'P/E', 'P/BV','PEG', 'New Member', 'Industry']
        df.columns = df.iloc[1,:]
        df.drop(df.index[[0,1]], inplace=True)
        # print(df.columns)
        df.drop(df[df['Company']==nan].index,inplace=True)
        # df = df.assign(fiveten = df['DGR 5Y'] / df['DGR 10Y'])
        # df.drop(df.index[-15:], inplace=True)
      
    # Concatenate all df's into master df
    df = pd.concat(df_list)

    # Convert datatype for columns of interest
    scr_col = ['Price','Debt/Capital','P/E','Chowder Number','DGR 1Y',
                'DGR 3Y','DGR 5Y','DGR 10Y']
    for col in scr_col:
        df.loc[:, col] = df.loc[:, col].astype(float)

    df = df.assign(EPS = df.loc[:,'Price'] / df.loc[:,'P/E'])
    df = df.assign(Payout = df['Current Div'] * df['Payouts/ Year'] / df['EPS'] * 100)
    return df

#calculate 5/10 A/D* for missing values
def fiveten(r):
    try:
        ans = abs(r['DGR 5Y'])/abs(r['DGR 10Y'])
        return ans
    except:
        return nan