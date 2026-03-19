# importing libraries
import pandas as pd
import requests
from yahooquery import Ticker
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_NINJAS_KEY")

url = "https://api.api-ninjas.com/v1/sp500"
headers = {"X-Api-Key": API_KEY}

response = requests.get(url, headers=headers)
data = response.json()

tickers = [company["ticker"] for company in data]
print(tickers[:10])


# Step 1: Collect the list of S&P 500 companies and their tickers
# def get_sp500_tickers():
#     """Retrieves a list of tickers from S&P 500 index

#     Returns:
#         _type_: _description_
#     """
#     url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
#     html = requests.get(url).text
#     sp500_data = pd.read_html(html)[
#         0
#     ]  # Maybe there'll be a need to adjust the index depending on the table structure
#     sp500_data["Ticker"] = sp500_data["Ticker"].str.replace(".", "-")
#     tickers = sp500_data["Ticker"].tolist()
# #     return tickers

# tickers = get_sp500_tickers()
