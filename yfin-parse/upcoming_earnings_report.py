from datetime import datetime
from pandas import Timestamp
import yfinance as yf
import pandas as pd
import numpy as np
import json
import os

# load config
with open(os.path.join(os.getcwd(), "config.json"), 'r') as f:
    config = json.loads(f.read())

def get_earnings(ticker:str) -> Timestamp:
    earnings_dates = yf.Ticker(ticker).get_earnings_dates()
    if "ASTC" == ticker:
        breakpoint()

    # get most recent NaN earnings date
    try:
        upcoming_date = earnings_dates[pd.isna(earnings_dates['EPS Estimate'])].reset_index().iloc[-1]['Earnings Date']
        print(f"got earnings date for {ticker}")
    except TypeError:
        upcoming_date = np.nan
        print(f'no upcoming earnings found for {ticker}')
    except IndexError:
        upcoming_date = np.nan
        print(f'no results for {ticker}')
    except Exception as e:
        upcoming_date = np.nan
        print(f"unknown result {str(e)}")
    return upcoming_date


if __name__ == '__main__':
    # get top sector earnings
    desired_keys = ["technology"]
    report_df = pd.DataFrame({
        "symbol": [],
        "name":[],
        "earnings":[]
    })
    for key in desired_keys:
        for industry in config['SECTOR_INDUSTRY_MAPPINGS'][key]:
            tops = yf.Industry(industry).top_companies.iloc[:, 0].reset_index()[["symbol", "name"]] # give user ability to change top companies to somth else 
            tops['earnings'] = tops['symbol'].apply(lambda x: get_earnings(x))  # Apply the function for each symbol
            print(f"processed tops for {industry}")
            report_df = report_df.merge(tops, how='outer')
    rn = datetime.now().strftime("%Y-%m-%d")
    report_df = report_df.sort_values(['earnings'], ascending=False)
    report_df.to_csv(f"reporting/upcoming_earnings_{rn}.csv")
            
