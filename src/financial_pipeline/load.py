"""Module to get financial data from other modules into DuckDB."""

import duckdb
import pandas as pd
from pathlib import Path

DB_PATH = Path("data/financial.duckdb")


def get_connection() -> duckdb.DuckDBPyConnection:
    """Returns a connection to the DuckDB database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))


def load_raw_financials(df: pd.DataFrame) -> None:
    """Loads raw financial metrics into the bronze layer.

    Args:
        df: DataFrame containing financial metrics per ticker.
    """
    with get_connection() as con:
        con.sql("""
            CREATE TABLE IF NOT EXISTS raw_financials AS
            SELECT *, current_timestamp AS loaded_at
            FROM df
            WHERE 1=0 -- create table with schema only on the first run
        """)
        con.sql("DELETE FROM raw_financials WHERE loaded_at::DATE = current_date")
        con.sql("INSERT INTO raw_financials SELECT *, current_timestamp FROM df")
