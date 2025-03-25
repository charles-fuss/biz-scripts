import asyncio
import aiohttp

headers = {
    "authority": "api.robinhood.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": ("campaign=google; campaign_version=google%2C8140492012%2C84157057397%2C658217162828__robinhood__e; "
               "click_id=Cj0KCQiA7se8BhCAARIsAKnF3rx6AOTomEEU6Dl5tECRf_rzKOrE2aYbAVdUFSsJAUXtgIkfkM0sl-waAsmhEALw_wcB; "
               "device_id=da6e69b5-a677-442c-9c77-f657b1d91c79; "
               "_gac_UA-46330882-15=1.1737664069.Cj0KCQiA7se8BhCAARIsAKnF3rx6AOTomEEU6Dl5tECRf_rzKOrE2aYbAVdUFSsJAUXtgIkfkM0sl-waAsmhEALw_wcB; "
               "_gcl_aw=GCL.1737664069.Cj0KCQiA7se8BhCAARIsAKnF3rx6AOTomEEU6Dl5tECRf_rzKOrE2aYbAVdUFSsJAUXtgIkfkM0sl-waAsmhEALw_wcB; "
               "_gcl_gs=2.1.k1$i1737664064$u182294820; logged_in=True; "
               "__stripe_mid=d644cf56-2776-49e9-81e0-94717a691e2efc5048; "
               "_ga_M0TD9NPKQX=GS1.1.1738622202.3.1.1738622245.17.0.0; "
               "_gid=GA1.2.25223528.1739726442; "
               "_ga=GA1.1.cd6819b3c3a1a0292a3ef1cded60e707ef3395cf1840c0d9b0233a2ca91c76a1; "
               "_ga_LZSP5G3693=GS1.1.1739726441.1.0.1739726451.50.0.0; "
               "_ga_N6DVMV7XZB=GS1.1.1739726441.2.0.1739726451.0.0.0"),
    "priority": "u=0, i",
    "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/133.0.0.0 Safari/537.36")
}

async def get_instrument(session, instrument_url):
    # Fetch instrument info
    async with session.get(instrument_url, headers=headers) as resp:
        instrument_info = await resp.json()
    symbol = instrument_info['symbol']
    
    # Fetch fundamentals info
    fundamentals_url = f"https://api.robinhood.com/fundamentals/{symbol}/"
    async with session.get(fundamentals_url, headers=headers) as resp:
        fundamentals_info = await resp.json()
    desc = fundamentals_info.get('description', 'No description')
    
    return (symbol, desc)

async def parse_instruments(earnings_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(earnings_url, headers=headers) as resp:
            earnings_data = await resp.json()
        upcoming_earnings_instruments = earnings_data['instruments']
        
        # Create tasks for concurrent fetching
        tasks = [
            get_instrument(session, instrument)
            for instrument in upcoming_earnings_instruments
        ]
        # Wait for all tasks to complete and gather the results in a list
        results = await asyncio.gather(*tasks)
        return results

if __name__ == "__main__":
    earnings_url = "https://api.robinhood.com/midlands/tags/tag/upcoming-earnings/"
    all_earnings = asyncio.run(parse_instruments(earnings_url))
    print(f"All tickers: {[x[0] for x in all_earnings]}")
    print(f"All descriptions: {[x[1] for x in all_earnings]}")