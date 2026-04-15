from financial_pipeline.extract import get_sp500_tickers, get_financial_data
from financial_pipeline.load import load_raw_financials

tickers = get_sp500_tickers()
df_financials = get_financial_data(tickers)
load_raw_financials(df_financials)

print("Pipeline complete.")
