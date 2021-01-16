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
    df = pd.read_excel(filename,sheet_name=sheets)
    df_list = [df.get(sheet) for sheet in sheets]
    return df_list

def clean_data(df_list):
    # Clean data
    for df in df_list:
        df.drop(df.index[0:5], inplace=True)
        df.columns = ['Company','Ticker','Sector','Industry','No.Yrs','CCCSeq','DRIP DR',
                        'Fees SP','Price', 'Div.Yield', 'Current Dividend','Payouts/Year',
                        'Annualized','Qtly Sch','Previous Payout','Last Increased on:Ex-Div',
                        'Last Increased on:Pay','MR%Inc.','DGR 1-yr','DGR 3-yr','DGR 5-yr',
                        'DGR 10-yr','5/10 A/D*','Past 5yr DEG','&=MultiIncThisYrNotes',
                        'EPS %Payout','TTM P/E','FYE Month','TTM EPS','PEG','TTM P/Sales',
                        'MRQ P/Book','TTM ROE','TTM Growth','NY Growth','Past 5yr Growth',
                        'Est-5yr Growth','MktCap($Mil)','Inside Own.','Debt/Equity','TweedFactor',
                        'Chowder Rule','+/-% vs.Graham','Estimated Div:2018','2019','2020','2021',
                        '2022','Est. Payback$','Est. Payback%','5-yr Beta','52-wk Low','52-wk High',
                        '50-day MMA','200-day MMA','OTC','StreakBegan','RecessionsSurvived','TTM ROA']
        df.drop(df[df['Company']==nan].index,inplace=True)
        df.drop(df.index[-15:], inplace=True)
        
    # Concatenate all df's into master df
    df = pd.concat(df_list)
    # Convert datatype for columns of interest
    scr_col = ['Div.Yield','EPS %Payout','Debt/Equity','TTM P/E','Chowder Rule','DGR 1-yr',
                'DGR 3-yr','DGR 5-yr','DGR 10-yr','5/10 A/D*']
    for col in scr_col:
        df.loc[:, col] = df.loc[:, col].astype(float)
    return df

#calculate 5/10 A/D* for missing values
def fiveten(r):
    try:
        ans = abs(r['DGR 5-yr'])/abs(r['DGR 10-yr'])
        return ans
    except:
        return nan