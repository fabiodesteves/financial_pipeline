"""Module for extracting raw financial data from external APIs."""

import os
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()


def get_sp500_tickers() -> list[str]:
    """Fetches the list of S&P 500 tickers from API Ninjas.

    Returns:
        list[str]: A list of S&P 500 stock ticker symbols.

    Raises:
        ValueError: If the API key is not set or the request fails.
    """
    api_key = os.getenv("API_NINJAS_KEY")
    if not api_key:
        raise ValueError("API_NINJAS_KEY environment variable is not set.")

    response = requests.get(
        "https://api.api-ninjas.com/v1/sp500", headers={"X-Api-Key": api_key}
    )
    response.raise_for_status()

    df_sp500 = pd.DataFrame(response.json())
    return df_sp500["ticker"].tolist()


def get_sp500_dataframe() -> pd.DataFrame:
    """Fetches the S&P 500 data as a DataFrame.

    Returns:
        pd.DataFrame: A DataFrame containing S&P 500 company data.

    Raises:
        ValueError: If the API key is not set or the request fails.
    """
    api_key = os.getenv("API_NINJAS_KEY")
    if not api_key:
        raise ValueError("API_NINJAS_KEY environment variable is not set.")

    response = requests.get(
        "https://api.api-ninjas.com/v1/sp500", headers={"X-Api-Key": api_key}
    )
    response.raise_for_status()

    return pd.DataFrame(response.json())
