import yfinance as yf
import pandas as pd
import argparse
import pprint
import json
import time
import os



# load config
with open(os.path.join(os.getcwd(), "config.json"), 'r') as f:
    config = json.loads(f.read())

class Query():
    def __init__(self, query_type, query, num_results):
        self.query_type = query_type
        self.query = query
        self.num_results = num_results+1 if num_results is not None else float('inf')

def top_companies(base_query:Query) -> pd.DataFrame():
    if base_query.query_type == "sector":
        mark = yf.Sector(base_query.query) # you can then go into industries from a sector
        return mark.top_companies[:base_query.num_results].map(lambda x: f"{x:,}")
    else:
        indus = yf.Industry(base_query.query)
        return indus.top_companies[:base_query.num_results].map(lambda x: f"{x:,}")

def financials(base_query:Query) -> pd.DataFrame():
    desired_info = ['trailingPE', 'forwardPE', 'overallRisk', 'averageVolume', 'marketCap', 'sharesShort', 'currentPrice', 'totalRevenue', 'totalCash', 'totalDebt', 'grossMargins', 'fiftyDayAverageChange', 'fiftyTwoWeekChangePercent', ]
    financial_info = "\n".join([f"{x}: {y:,}" for (x,y) in yf.Ticker(base_query.query).info.items() if x in desired_info])
    print(f"{financial_info}\nsleeping 3s so u can appreciate these stats OwO")
    time.sleep(3)
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
    parser.add_argument("-f", "--financials", action="store_true", help="get finances")
    parser.add_argument("-oc", "--output_to_csv", type=str, help="send output to CSV & define output path")
    parser.add_argument("--list_sectors_tops", action="store_true", help="get the mappings for all of the sectors/industries")
    parser.add_argument("--list_sectors_intraday", action="store_true", help="get the mappings for all of the sectors/industries")
    parser.add_argument("--top_companies", action="store_true", help="get the top companies for the designated sector/industry")
    parser.add_argument("--top_gainers", action="store_true", help="get the top gainers for the day (>8%%)")
    parser.add_argument("--top_losers", action="store_true", help="get the top losers for the day (<-8%%)")
    
    args = parser.parse_args()

    if args.list_sectors_tops:
        pprint.pprint(config['SECTOR_INDUSTRY_MAPPINGS'])
    elif args.list_sectors_intraday:
        pprint.pprint(config['SECTORS_INTRADAY'])
    elif args.financials:
        # search financials 
        query_config = {
            "query_type": "financials", 
            "query": args.ticker, 
            "num_results": args.results
        }
        base_query = Query(**query_config)
        results = financials(base_query)
        pprint.pprint(results)
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
        base_query = yf.EquityQuery('and', [
            yf.EquityQuery('is-in', ['exchange', 'NYQ']),
            yf.EquityQuery('gt', ["intradaypricechange", 8]),
            *queries # case sensitive
        ])
        results = yf.screen(query=base_query)
        print("\ngrowth over {0} pct for {1} (sector): {2}".format(8, 'Technology', [x['symbol'] for x in results['quotes']]))
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
        base_query = yf.EquityQuery('and', [
            yf.EquityQuery('is-in', ['exchange', 'NYQ']),
            yf.EquityQuery('lt', ["intradaypricechange", -8]),
            *queries # case sensitive
        ])
        results = yf.screen(query=base_query)
        print("\ngrowth under {0} pct for {1} (sector): {2}".format(8, 'Technology', [x['symbol'] for x in results['quotes']]))
    elif args.industry == args.sector == args.ticker == None :
        raise ValueError("please select either a sector, industry, or ticker to query")
    elif args.earnings_history:
        if args.ticker == None:
            raise ValueError("please declare a ticker to query")
        query_config = {
            "query_type": "earnings", 
            "query": args.ticker, 
            "num_results": args.results
        }
        base_query = Query(**query_config)
        results = get_earnings(base_query) 
        pprint.pprint(results)
    elif args.industry != None or args.sector != None:
        if args.industry != None and args.sector != None:
            raise ValueError("you must choose EITHER an industry or sector, not both")
        if args.sector != None:
            # search sector
            query_config = {
                "query_type": "sector", 
                "query": args.sector, 
                "num_results": args.results
            }
            base_query = Query(**query_config)
            results = top_companies(base_query)
            print("\n\ntop companies for {1} (sector):\n{0}\n\n\n".format(results, base_query.query))

        elif args.industry != None:
            # search industry 
            query_config = {
                "query_type": "industry", 
                "query": args.industry, 
                "num_results": args.results
            }
            base_query = Query(**query_config)
            results = top_companies(base_query)
            print("\n\ntop companies for {1} (industry):\n{0}\n\n\n".format(results, base_query.query))

    if args.output_to_csv and type(results) == pd.DataFrame:
        if '.csv' not in args.output_to_csv:
            args.output_to_csv = f"{args.output_to_csv}.csv"
        results.to_csv(f"reporting/{args.output_to_csv}")
        print(f"successfully saved the query to reporting/{args.output_to_csv}")



if __name__ == "__main__":
    main()