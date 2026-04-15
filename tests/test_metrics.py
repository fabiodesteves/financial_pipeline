"""Tests for the metrics module."""

import pytest
from financial_pipeline.extract import get_financial_data


class TestGetFinancialData:
    """Tests for get_financial_data function."""

    def test_n_must_be_positive(self):
        """Test that n must be a positive integer."""
        with pytest.raises(ValueError, match="n must be a positive integer."):
            get_financial_data(["AAPL"], -1)

    def test_n_must_be_integer(self):
        """Test that n must be an integer."""
        with pytest.raises(TypeError, match="n must be an integer."):
            get_financial_data(["AAPL"], 1.5)

    def test_n_cannot_exceed_tickers_length(self):
        """Test that n cannot exceed the number of tickers."""
        with pytest.raises(ValueError):
            get_financial_data(["AAPL", "MSFT"], 5)

    def test_tickers_must_be_list(self):
        """Test that tickers must be a list."""
        with pytest.raises(TypeError, match="tickers must be a list."):
            get_financial_data("AAPL", 1)

    def test_all_tickers_must_be_strings(self):
        """Test that all tickers must be strings."""
        with pytest.raises(TypeError, match="All tickers must be strings."):
            get_financial_data([123], 1)
