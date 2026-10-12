# Stock Market ETL Pipeline

A Python-based ETL pipeline that extracts daily stock market data from Yahoo Finance, transforms and validates it, and loads validated and flagged records into MySQL.

The project processes market data for eight stock tickers, applies data-quality checks, investigates the effect of different anomaly thresholds, and preserves flagged records for further review rather than silently discarding them.

## Project Overview

The pipeline processes daily OHLCV (Open, High, Low, Close, Volume) stock market data for the following eight tickers:

- AAPL
- MSFT
- GOOGL
- AMZN
- META
- NVDA
- TSLA
- JPM

The pipeline demonstrates practical data engineering concepts, including:

- Data extraction from an external source
- CSV-based staging
- Data transformation and standardization
- Derived metrics and moving averages
- Data-quality validation
- Automated testing with pytest
- Anomaly threshold sensitivity analysis
- MySQL database loading
- Documentation and version control

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | ETL development and data processing |
| pandas | Data transformation and analysis |
| yfinance | Stock market data extraction |
| MySQL | Persistent storage of validated and flagged records |
| mysql-connector-python | Python-to-MySQL connectivity |
| pytest | Automated validation tests |
| Git and GitHub | Version control and project hosting |

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
           +-------+-------+
           |               |
           v               v
 validated_stock_data.csv  flagged_stock_data.csv
           |               |
           +-------+-------+
                   |
                   v
                 load.py
                   |
                   v
                 MySQL
             +-----+-----+
             |           |
             v           v
        clean_prices  flagged_prices
```

### Pipeline stages

1. **Extract:** `ingest.py` retrieves stock market data and saves raw data in the staging directory.
2. **Transform:** `transform.py` standardizes columns and data types, sorts observations by date, and calculates daily percentage returns and a seven-observation moving average.
3. **Validate:** `validate.py` checks required fields, ticker completeness, suspicious date gaps, price relationships, non-positive prices, negative volume, and unusually large daily returns.
4. **Separate:** The pipeline writes validated records to `validated_stock_data.csv` and flagged records to `flagged_stock_data.csv`.
5. **Load:** `load.py` creates the MySQL tables if needed and loads validated and flagged records into their respective tables.

## Project Structure

```text
python-stock-etl-pipeline/
├── staging/
├── ingest.py
├── transform.py
├── validate.py
├── load.py
├── threshold_analysis.py
├── test_validate.py
├── transformed_stock_data.csv
├── validated_stock_data.csv
├── flagged_stock_data.csv
├── DATA_QUALITY_REPORT.md
├── runbook.md
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

The CSV files are generated or updated by the pipeline. The `staging/` directory contains extracted source data.

## Prerequisites

Install the following before running the project:

- Python 3.12 or a compatible Python version
- MySQL Server
- Git

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/pavanjii/python-stock-etl-pipeline.git
cd python-stock-etl-pipeline
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure MySQL

Create the database in MySQL if it does not already exist:

```sql
CREATE DATABASE stock_etl;
```

The pipeline uses the following environment variables:

| Variable | Purpose |
|---|---|
| `MYSQL_HOST` | MySQL server hostname |
| `MYSQL_USER` | MySQL username |
| `MYSQL_PASSWORD` | MySQL password |
| `MYSQL_DATABASE` | Target database name |

For Windows PowerShell, set these variables in the terminal before running `load.py`:

```powershell
$env:MYSQL_HOST = "localhost"
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "your_local_password"
$env:MYSQL_DATABASE = "stock_etl"
```

Replace the example password with your own local MySQL password.

The repository includes `.env.example` as a configuration reference. Copy it if you want to maintain a local `.env` file:

```powershell
Copy-Item .env.example .env
```

**Important:** The current `load.py` reads configuration through `os.getenv()`. Creating a `.env` file alone does not automatically load its values. Either set the environment variables as shown above or configure explicit `.env` loading in the application.

Never commit real credentials or your local `.env` file to GitHub.

### 5. Run the ETL pipeline

Run the scripts in the following order from the project root:

```powershell
python ingest.py
python transform.py
python validate.py
python load.py
```

Each stage depends on outputs generated by the preceding stage. Review the console output and generated files before proceeding to the next stage.

Refer to `runbook.md` for operational instructions and troubleshooting guidance.

## Data Transformation

The transformation stage standardizes the extracted market data into a consistent structure.

### Key transformations

- Converts the date field to a datetime type.
- Converts price and volume fields to numeric types.
- Removes rows with unconvertible required OHLCV values.
- Sorts observations chronologically for each ticker.
- Adds a ticker identifier to each record.
- Calculates daily percentage returns.
- Calculates a seven-observation moving average of closing prices.

### Derived metrics

**Daily percentage return**

The daily return is calculated from consecutive closing prices:

\[
\text{Daily Return (\%)} =
\left(\frac{\text{Current Close}}{\text{Previous Close}}-1\right)\times100
\]

**Seven-observation moving average**

`MA_7` represents the rolling average of seven closing-price observations. It is a seven-observation average, not necessarily seven calendar days.

## Data Quality and Validation

The validation stage checks for common data-quality issues before records are separated and loaded into MySQL.

### Validation rules

- **Required-field completeness:** Checks for null values in required fields.
- **Ticker completeness:** Checks whether all expected tickers are represented and identifies unexpected tickers.
- **Date continuity:** Flags observations where consecutive dates have a gap greater than four calendar days.
- **Price relationship:** Flags rows where the high price is lower than the low price.
- **Positive prices:** Flags zero or negative Open, High, Low, or Close prices.
- **Volume validity:** Flags negative volume.
- **Large daily movements:** Flags absolute daily returns strictly greater than 15%.

The date-gap check is a heuristic. A gap greater than four calendar days indicates a possible missing trading day and does not by itself prove that data is missing.

### Output files

| File | Purpose |
|---|---|
| `transformed_stock_data.csv` | Combined transformed stock data |
| `validated_stock_data.csv` | Records that pass the configured validation rules |
| `flagged_stock_data.csv` | Records requiring further investigation |

A flagged record is not automatically a data-quality defect. Large market movements may be genuine and should be investigated before being classified as incorrect data.

## Threshold Sensitivity Analysis

The `threshold_analysis.py` script evaluates how changing the absolute daily-return threshold affects the number of flagged records.

The following results were verified against the current dataset of 2,016 records.

| Absolute daily-return threshold | Records flagged | Percentage of records |
|---|---:|---:|
| 15% | 2 | 0.10% |
| 10% | 5 | 0.25% |
| 5% | 58 | 2.88% |

The analysis uses a strict `>` comparison. For example, at the 15% threshold, a return must be greater than +15% or less than -15% to be flagged. A return of exactly +15% or -15% is not flagged.

Lower thresholds identify more observations for investigation. However, a larger flagged count does not necessarily mean the underlying data is less accurate.

Run the analysis using:

```powershell
python threshold_analysis.py
```

### Records flagged at the 15% threshold

The latest verified analysis identified these two records:

| Date | Ticker | Daily return |
|---|---|---:|
| 2026-07-31 | AMZN | +15.320589% |
| 2026-07-30 | MSFT | +15.506733% |

These records exceed the configured threshold. Their underlying causes should be investigated using a second price source, adjusted-price data, or other reliable market information before attributing the movements to a specific event.

## Database Load Results

The current verified MySQL load contains 2,016 records across the two target tables.

| MySQL table | Records loaded |
|---|---:|
| `clean_prices` | 2,014 |
| `flagged_prices` | 2 |
| **Total** | **2,016** |

The `clean_prices` table stores records that pass the configured validation rules. The `flagged_prices` table stores records that require further investigation, along with their validation failure reasons.

The current loader clears existing rows in both tables before inserting the latest CSV contents. Therefore, each successful run replaces the previous table contents with the current dataset rather than preserving a historical record of every load.

## Automated Testing

The project uses pytest to test the data-quality helper functions in `validate.py`.

The test suite currently contains eight tests covering:

- Non-positive stock prices
- Invalid High–Low price relationships
- Negative trading volume
- Missing required fields
- Large daily movements
- Valid stock records passing the tested checks
- Positive 15% threshold-boundary behavior
- Negative 15% threshold-boundary behavior

**Latest verified test result: 8 tests passed in 1.82 seconds.**

Run the tests with:

```powershell
python -m pytest -v test_validate.py
```

These tests cover the configured helper functions. They do not replace end-to-end testing of data extraction, transformation, validation, or MySQL loading.

## Data Quality Report

See [DATA_QUALITY_REPORT.md](DATA_QUALITY_REPORT.md) for additional validation results, threshold sensitivity findings, flagged records, limitations, and recommended follow-up checks.

## Limitations and Future Improvements

- Cross-check the two records flagged at the 15% threshold against a second price source or adjusted-close data.
- Document evidence before attributing flagged movements to earnings or other events.
- Document the rationale for the selected validation thresholds.
- Expand automated tests to cover additional validation rules and edge cases.
- Add integration tests for MySQL loading, error handling, and repeat-load behavior.
- Improve validation reporting and failure handling.
- Consider using a trading calendar instead of a simple calendar-day-gap heuristic.
- Add reproducible logging and execution summaries for each pipeline stage.
- Consider a historical-load strategy if retaining data across repeated runs becomes a requirement.

## Author

**Pavan Kumar**

GitHub: [pavanjii](https://github.com/pavanjii)

