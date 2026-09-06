# Stock Market ETL Pipeline

A Python-based ETL pipeline that extracts daily stock market data from Yahoo Finance, transforms and validates the data, and publishes clean and flagged records to MySQL.

The project is designed as a practical data engineering portfolio project demonstrating ETL development, data quality validation, automated testing, database loading, documentation, and version control.

## Project Overview

The pipeline processes one year of daily OHLCV data for eight stock tickers:

- AAPL
- MSFT
- GOOGL
- AMZN
- META
- NVDA
- TSLA
- JPM

The pipeline uses a single external data source: Yahoo Finance through the `yfinance` Python library.

## Architecture

```text
Yahoo Finance
      |
      v
  ingest.py
      |
      v
staging/*.csv
      |
      v
 transform.py
      |
      v
transformed_stock_data.csv
      |
      v
  validate.py
      |
      +----------------------+
      |                      |
      v                      v
validated_stock_data.csv   flagged_stock_data.csv
      |                      |
      +----------+-----------+
                 |
                 v
              load.py
                 |
                 v
              MySQL
          +------+------+
          |             |
          v             v
    clean_prices   flagged_prices