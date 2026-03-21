"""Module for calculating financial metrics from stock data."""

import pandas as pd
from yahooquery import Ticker


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
            except KeyError as e:  # noqa: E722
                print(f"Error calculating EV for {ticker}: {e}")
                cash_and_equivalents = (
                    balance_sheet["CashAndCashEquivalents"].dropna().iloc[-1]
                )
                ev = market_cap + total_debt - cash_and_equivalents
                op_income = income_statement["PretaxIncome"].dropna().iloc[-1]
            try:
                dividend_raw = summary[ticker]["trailingAnnualDividendYield"]
                dividend_yield = dividend_raw * 100
            except Exception as e:  # noqa: E722
                print(f"Error calculating dividend yield for {ticker}: {e}, {type(e)}")
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
            except Exception as e:  # noqa: E722
                print(f"Error calculating buyback yield for {ticker}: {e}")
                buyback_yield = 0
            data[ticker] = {
                "P/E": round(market_cap / net_income, 2),
                "Debt/Equity": round(total_debt / equity, 2),
                "Enterprise Value (M)": round(ev / 1000000, 3),
                "Market cap (M)": round(market_cap / 1000000, 3),
                "Net income (M)": round(net_income / 1000000, 3),
                "Operating income (M)": round(op_income / 1000000, 3),
                "Dividend Yield (%)": round(dividend_yield, 2),
                "Shareholder Yield (%)": round(dividend_yield + buyback_yield, 2),
                "Buyback Yield (%)": round(buyback_yield, 2),
            }
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
    return pd.DataFrame.from_dict(data, orient="index")
