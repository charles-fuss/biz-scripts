import yfinance as yf
import pandas as pd
import argparse
import pprint
import json
import os



# load config
with open(os.path.join(os.getcwd(), "config.json"), 'r') as f:
    config = json.loads(f.read())

class Query():
    def __init__(self, query_type, query, num_results, historical=None):
        self.query_type = query_type
        self.query = query
        self.num_results = num_results+1 if num_results is not None else float('inf')
        self.historical = False if not historical else historical

def top_companies(base_query:Query) -> pd.DataFrame():
    if base_query.query_type == "sector":
        mark = yf.Sector(base_query.query) # you can then go into industries from a sector
        return mark.top_companies[:base_query.num_results].map(lambda x: f"{x:,}")
    else:
        indus = yf.Industry(base_query.query)
        return indus.top_companies[:base_query.num_results].map(lambda x: f"{x:,}")

def financials(base_query:Query) -> pd.DataFrame():
    # tbd
    ticker = yf.Ticker(base_query.query)
    if base_query.historical:
        breakpoint()
    desired_info = ['displayName', 'symbol' 'currentPrice', 'industry', 'sector', 'fullExchangeName',  'region', 'market',
                    'totalRevenue', 'totalCash', 'totalDebt', 'overallRisk', 'maxAge', 'volume', 
                    'averageDailyVolume3Month', 'sharesOutstanding', 
                    'trailingPE', 'forwardPE', 'overallRisk', 'lastFiscalYearEnd',
                    'averageVolume', 'marketCap', 'sharesShort', 'currentPrice', 
                    'grossMargins', 'fiftyDayAverageChange', 'fiftyTwoWeekChangePercent']
    financial_info = {x:[y] for x,y in ticker.info.items() if x in desired_info}
    breakpoint()
    return pd.DataFrame(financial_info)
    
def income_statement(base_query:Query) -> pd.DataFrame():
    return yf.Ticker(base_query.query).income_stmt.map(lambda x: f"{x:,}")


def get_earnings(base_query:Query) -> pd.DataFrame():
    return yf.Ticker(base_query.query).get_earnings_dates().map(lambda x: f"{x:,}")


def main():

    parser = argparse.ArgumentParser(prog="yfin-parse", description="yahoo finance parser")
    parser.add_argument("-i", "--industry", type=str, help="industry to parse")
    parser.add_argument("-s", "--sector", type=str, help="sector to parse")
    parser.add_argument("-t", "--ticker", type=str, help="ticker to parse")
    parser.add_argument("-r", "--results", type=int, default=10, help="number of returned results (default=max=10)")
    parser.add_argument("-eh", "--earnings-history", action="store_true", help="get earnings history")
    parser.add_argument("-f", "--financials", action="store_true", help="get finances (ticker ONLY)")
    parser.add_argument("-hd", "--historical_data", action="store_true", help="get historical data (EXCLUSIVELY 3MO INTERVAL)")
    parser.add_argument("-is", "--income_statement", action="store_true", help="income statement (ticker ONLY)")
    parser.add_argument("--list_sectors_tops", action="store_true", help="get the mappings for all of the sectors/industries")
    parser.add_argument("--list_sectors_intraday", action="store_true", help="get the mappings for all of the sectors/industries")
    parser.add_argument("--top_companies", action="store_true", help="get the top companies for the designated sector/industry")
    parser.add_argument("--top_gainers", action="store_true", help="get the top gainers for the day (>8%)")
    parser.add_argument("--top_losers", action="store_true", help="get the top losers for the day (<-8%)")
    parser.add_argument("--to_json", action="store_true", help="return as json instead of dataframe")
    args = parser.parse_args()

    if args.list_sectors_tops:
        pprint.pprint(config['SECTOR_INDUSTRY_MAPPINGS'])
    elif args.list_sectors_intraday:
        pprint.pprint(config['SECTORS_INTRADAY'])
    elif args.financials:
        if not args.ticker:
            raise ValueError("ticker required for financials")
        # search financials 
        query_config = {
            "query_type": "financials", 
            "query": args.ticker, 
            "num_results": args.results,
            "historical": args.historical_data
        }

        base_query = Query(**query_config)
        finances_df = financials(base_query)
        if not args.to_json:
            pprint.pprint(finances_df.reset_index())
        else:
            print(finances_df.to_json())
    elif args.income_statement:
        if not args.ticker:
            raise ValueError("ticker required for financials")
        # search financials 
        query_config = {
            "query_type": "income_statement", 
            "query": args.ticker, 
            "num_results": args.results,
            "historical": args.historical_data
        }

        base_query = Query(**query_config)
        pprint.pprint(income_statement(base_query))
    elif args.top_gainers:
        if not args.sector:
            raise ValueError("please include a sector to query")
        try:
            queries = [
                yf.EquityQuery('is-in', ["sector", args.sector]) if args.sector else None,
                # more tbd...
            ]
        except ValueError:
            raise ValueError("sector not found. please consult --list-sectors-intraday for all mappings")
        # Remove None values from queries list
        queries = [q for q in queries if q]
        query = yf.EquityQuery('and', [
            yf.EquityQuery('is-in', ['exchange', 'NYQ']),
            yf.EquityQuery('gt', ["intradaypricechange", 8]),
            *queries # case sensitive
        ])
        sc = yf.screen(query=query)
        print("\ngrowth over {0} pct for {1} (sector): {2}".format(8, 'Technology', [x['symbol'] for x in sc['quotes']]))
    elif args.top_losers:
        if not args.sector:
            raise ValueError("please include a sector to query")
        try:
            queries = [
                yf.EquityQuery('is-in', ["sector", args.sector]) if args.sector else None,
                # more tbd...
            ]
        except ValueError:
            raise ValueError("sector not found. please consult --list-sectors-intraday for all mappings")
        
        # Remove None values from queries list
        queries = [q for q in queries if q]
        query = yf.EquityQuery('and', [
            yf.EquityQuery('is-in', ['exchange', 'NYQ']),
            yf.EquityQuery('lt', ["intradaypricechange", -8]),
            *queries # case sensitive
        ])
        sc = yf.screen(query=query)
        print("\ngrowth under {0} pct for {1} (sector): {2}".format(8, 'Technology', [x['symbol'] for x in sc['quotes']]))
    elif args.industry == args.sector == args.ticker == None :
        raise ValueError("please select either a sector, industry, or ticker to query")
    elif args.earnings_history:
        if args.ticker == None:
            raise ValueError("please declare a ticker to query")
        query_config = {
            "query_type": "earnings", 
            "query": args.ticker, 
            "num_results": args.results,
            "historical": args.historical_data
        }
        base_query = Query(**query_config)
        pprint.pprint(get_earnings(base_query))
    elif args.industry != None or args.sector != None:
        if args.industry != None and args.sector != None:
            raise ValueError("you must choose EITHER an industry or sector, not both")
        if args.sector != None:
            # search sector
            query_config = {
                "query_type": "sector", 
                "query": args.sector, 
                "num_results": args.results,
                "historical": args.historical_data
            }
            base_query = Query(**query_config)
            top = top_companies(base_query)
        elif args.industry != None:
            # search industry 
            query_config = {
                "query_type": "industry", 
                "query": args.industry, 
                "num_results": args.results,
                "historical": args.historical_data
            }
            base_query = Query(**query_config)
            top = top_companies(base_query)
        print("\n\ntop companies for {1} (sector):\n{0}\n\n\n".format(top, base_query.query))
    


if __name__ == "__main__":
    main()