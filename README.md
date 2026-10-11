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

## Data Quality and Validation

The pipeline validates transformed stock market data before loading it into MySQL. It checks for common data-quality issues, including:

- Non-positive stock prices
- Invalid High–Low price relationships
- Negative trading volume
- Missing required fields
- Unusually large daily returns

Automated validation tests are implemented using `pytest`.

Run the tests with:

```bash
python -m pytest -v test_validate.py
```

**Latest test result:** 5 tests passed.

## Threshold Sensitivity Analysis

The `threshold_analysis.py` script evaluates how different absolute daily-return thresholds affect the number of flagged records in the transformed dataset.

| Absolute daily-return threshold | Records flagged | Percentage of records |
|---|---:|---:|
| 15% | 2 | 0.10% |
| 10% | 5 | 0.25% |
| 5% | 58 | 2.88% |

The analysis covers 2,016 records. Lowering the threshold increases the number of flagged records. A flagged record is not automatically a data-quality defect; further investigation is required to determine whether the movement is legitimate or caused by an issue in the data.

Run the analysis with:

```bash
python threshold_analysis.py
```

## Data Quality Report

See the [Data Quality Report](DATA_QUALITY_REPORT.md) for the validation results, threshold sensitivity analysis, records flagged at the 15% threshold, limitations, and recommended follow-up checks.

## Limitations and Future Improvements

- Investigate unusually large daily-return movements against reliable market data.
- Add tests for valid inputs and threshold-boundary behavior.
- Document the rationale for the selected validation thresholds.
- Continue improving validation coverage and pipeline reliability.