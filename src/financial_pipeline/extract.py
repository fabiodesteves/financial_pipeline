"""Module for extracting raw financial data from external APIs."""

import os
import pandas as pd
import requests
from dotenv import load_dotenv
from yahooquery import Ticker

load_dotenv()


def get_sp500_tickers() -> list[str]:
    """Fetches the list of S&P 500 tickers from API Ninjas.

    Returns:
        list[str]: A list of S&P 500 stock ticker symbols.

    Raises:
        ValueError: If the API key is not set or the request fails.
    """
    API_KEY = os.getenv("API_NINJAS_KEY")
    if not API_KEY:
        raise ValueError("API_NINJAS_KEY environment variable is not set.")

    response = requests.get(
        "https://api.api-ninjas.com/v1/sp500", headers={"X-Api-Key": API_KEY}
    )
    response.raise_for_status()

    df_sp500 = pd.DataFrame(response.json())
    return df_sp500["ticker"].tolist()


def get_sp500_dataframe() -> pd.DataFrame:
    # TODO: maybe delete this function?
    """Fetches the S&P 500 data as a DataFrame.

    Returns:
        pd.DataFrame: A DataFrame containing S&P 500 company data.

    Raises:
        ValueError: If the API key is not set or the request fails.
    """
    API_KEY = os.getenv("API_NINJAS_KEY")
    if not API_KEY:
        raise ValueError("API_NINJAS_KEY environment variable is not set.")

    response = requests.get(
        "https://api.api-ninjas.com/v1/sp500", headers={"X-Api-Key": API_KEY}
    )
    response.raise_for_status()

    return pd.DataFrame(response.json())


"""Module for calculating financial metrics from stock data."""


def _validate_tickers_and_n(tickers: list[str], n: int | None) -> int:
    """Validates tickers list and optional n parameter.

    Args:
        tickers: A list of financial stock tickers.
        n: Optional number of tickers to process.

    Returns:
        The validated n value (or len(tickers) if n is None).

    Raises:
        TypeError: If tickers is not a list or contains non-string values,
                   or if n is not an integer.
        ValueError: If n is not positive or exceeds ticker count.
    """
    if not isinstance(tickers, list):
        raise TypeError("tickers must be a list.")
    if not all(isinstance(ticker, str) for ticker in tickers):
        raise TypeError("All tickers must be strings.")

    if n is not None:
        if not isinstance(n, int) or isinstance(n, bool):
            raise TypeError("n must be an integer.")
        if n < 1:
            raise ValueError("n must be a positive integer.")
        if n > len(tickers):
            raise ValueError(
                f"n must be less than or equal to the number of tickers ({len(tickers)})."
            )
        return n

    return len(tickers)


def get_financial_data(tickers: list[str], n: int | None = None) -> pd.DataFrame:
    """Gets financial data for the n first tickers provided.

    Data gathered:
        - "Revenue"
        - "Total debt"
        - "Equity"
        - "Liabilities"
        - "Cash and equivalents"
        - "Free cash flow"
        - "Market cap"
        - "Net income"
        - "Operating income"
        - "Dividend (Raw)"
        - "Buyback"

    Args:
        tickers: A list of financial stock tickers.
        n: The number of tickers to process (default: all tickers).

    Returns:
        pd.DataFrame: A DataFrame containing the financial data for the specified tickers.

    Raises:
        TypeError: If tickers is not a list, contains non-strings, or n is not an integer.
        ValueError: If n is not positive or exceeds ticker count.
    """
    n = _validate_tickers_and_n(tickers, n)

    data = {}
    for ticker in tickers[:n]:
        stock = Ticker(ticker)
        # gather statements (useful for the metrics)
        income_statement = stock.income_statement(frequency="a")
        balance_sheet = stock.balance_sheet(frequency="q")
        cash_flow = stock.cash_flow(frequency="a")
        summary = stock.summary_detail
        price_data = stock.price.get(ticker)
        if not isinstance(price_data, dict):
            print(f"Error processing {ticker}: No price data available ({price_data})")
            continue
        try:
            market_cap = price_data.get("marketCap")
            revenue = income_statement["TotalRevenue"].dropna().iloc[-1]
            free_cash_flow = cash_flow["FreeCashFlow"].dropna().iloc[-1]
            net_income = income_statement["NetIncome"].dropna().iloc[-1]
            equity = balance_sheet["StockholdersEquity"].dropna().iloc[-1]
            liabilities = (
                balance_sheet["TotalLiabilitiesNetMinorityInterest"].dropna().iloc[-1]
            )
            try:
                total_debt = balance_sheet["TotalDebt"].dropna().iloc[-1]
            except (KeyError, IndexError):
                total_debt = (
                    balance_sheet["LongTermDebt"].dropna().iloc[-1]
                    if "LongTermDebt" in balance_sheet.columns
                    else None
                )
            try:
                cash_and_equivalents = (
                    balance_sheet["CashCashEquivalentsAndShortTermInvestments"]
                    .dropna()
                    .iloc[-1]
                )
                operating_income = income_statement["OperatingIncome"].dropna().iloc[-1]
            except Exception:
                cash_and_equivalents = (
                    balance_sheet["CashAndCashEquivalents"].dropna().iloc[-1]
                )
                operating_income = income_statement["PretaxIncome"].dropna().iloc[-1]
            try:
                dividend_raw = summary[ticker]["trailingAnnualDividendYield"]
            except Exception:
                dividend_raw = 0
            try:
                buyback = (
                    (
                        cash_flow["RepurchaseOfCapitalStock"].dropna().iloc[-1]
                        + cash_flow["RepurchaseOfCapitalStock"].dropna().iloc[-2]
                    )
                    * -1
                    / 2
                )
            except Exception:
                buyback = 0
            data[ticker] = {
                "Revenue": revenue,
                "Total debt": total_debt,
                "Equity": equity,
                "Liabilities": liabilities,
                "Cash and equivalents": cash_and_equivalents,
                "Free cash flow": free_cash_flow,
                "Market cap": market_cap,
                "Net income": net_income,
                "Operating income": operating_income,
                "Dividend (Raw)": dividend_raw,
                "Buyback": buyback,
            }
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
    return pd.DataFrame.from_dict(data, orient="index").reset_index(names="Ticker")
