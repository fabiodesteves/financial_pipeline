"""Module for calculating financial metrics from stock data."""

import pandas as pd
from yahooquery import Ticker


def get_financial_data(n: int, tickers: list[str]) -> pd.DataFrame:
    """Gets financial data for the n first tickers provided.

    Data gathered:
        - "P/E"
        - "Debt/Equity"
        - "Enterprise Value (M)"
        - "Market cap (M)"
        - "Net income (M)"
        - "Operating income (M)"
        - "Dividend Yield (%)"
        - "Shareholder Yield (%)"
        - "Buyback Yield (%)"

    Args:
        n (int): The number of tickers to process.
        tickers (list[str]): A list of financial stock tickers.

    Returns:
        pd.DataFrame: A DataFrame containing the financial data for the specified tickers.

    Raises:
        ValueError:
            - If n is not a positive integer,
            - if n is greater than the number of tickers,
            - if n is not an integer,
            - if tickers is not a list,
            - if any ticker in tickers is not a string.
    """
    # Checking for potential errors in the input parameters
    if n < 1:
        raise ValueError("n must be a positive integer.")
    elif not isinstance(n, int):
        raise TypeError("n must be an integer.")
    elif n > len(tickers):
        raise ValueError(
            f"n must be less than or equal to the number of tickers ({len(tickers)})."
        )
    elif not isinstance(tickers, list):
        raise ValueError("tickers must be a list.")
    elif not all(isinstance(ticker, str) for ticker in tickers):
        raise ValueError("All tickers must be strings.")

    data = {}
    for ticker in tickers[:n]:
        stock = Ticker(ticker)
        # gather statements (useful for the metrics)
        income_statement = stock.income_statement(frequency="a")
        balance_sheet = stock.balance_sheet(frequency="q")
        cash_flow = stock.cash_flow(frequency="a")
        summary = stock.summary_detail
        try:
            market_cap = stock.price[ticker]["marketCap"]
            net_income = income_statement["NetIncome"].dropna().iloc[-1]
            equity = balance_sheet["StockholdersEquity"].dropna().iloc[-1]
            total_debt = balance_sheet["TotalDebt"].dropna().iloc[-1]
            # Calculate some valuation metrics
            try:
                cash_and_equivalents = (
                    balance_sheet["CashCashEquivalentsAndShortTermInvestments"]
                    .dropna()
                    .iloc[-1]
                )
                ev = market_cap + total_debt - cash_and_equivalents
                op_income = income_statement["OperatingIncome"].dropna().iloc[-1]
            except:  # noqa: E722
                cash_and_equivalents = (
                    balance_sheet["CashAndCashEquivalents"].dropna().iloc[-1]
                )
                ev = market_cap + total_debt - cash_and_equivalents
                op_income = income_statement["PretaxIncome"].dropna().iloc[-1]
            try:
                dividend_raw = summary[ticker]["trailingAnnualDividendYield"]
                dividend_yield = dividend_raw * 100
            except:  # noqa: E722
                dividend_yield = 0
            try:
                buyback = (
                    (
                        cash_flow["RepurchaseOfCapitalStock"].dropna().iloc[-1]
                        + cash_flow["RepurchaseOfCapitalStock"].dropna().iloc[-2]
                    )
                    * -1
                    / 2
                )
                buyback_yield = buyback * 100 / market_cap
            except:  # noqa: E722
                buyback_yield = 0
            data[ticker] = {
                "P/E": market_cap / net_income,
                "Debt/Equity": total_debt / equity,
                "Enterprise Value (M)": ev / 1000000,
                "Market cap (M)": market_cap / 1000000,
                "Net income (M)": net_income / 1000000,
                "Operating income (M)": op_income / 1000000,
                "Dividend Yield (%)": dividend_yield,
                "Shareholder Yield (%)": dividend_yield + buyback_yield,
                "Buyback Yield (%)": buyback_yield,
            }
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
    return pd.DataFrame.from_dict(data, orient="index")
