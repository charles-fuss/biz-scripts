import requests
import pandas as pd

API_KEY = "NPs658oUw4xeDIGIwYuTD3ZbIMlGn9VD"
symbol = "AAPL"
years_of_history = 10510250  # Adjust as needed

url = f"https://financialmodelingprep.com/api/v3/income-statement/{symbol}?limit={years_of_history}&apikey={API_KEY}"
response = requests.get(url).json()

# create DataFrame from historical income statement data
df_income = pd.DataFrame(response)
breakpoint()
print(df_income.head())
