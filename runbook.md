# Stock Price ETL Pipeline Runbook

## 1. Purpose

This project implements an end-to-end ETL pipeline that extracts one year of daily OHLCV stock market data from Yahoo Finance using `yfinance`, transforms it into a standardized dataset, validates data quality, and publishes validated and flagged records into MySQL.

The pipeline uses a single data source and keeps each ETL stage independent for easier maintenance and troubleshooting.

---

## 2. Pipeline architecture

```text
Yahoo Finance
      │
      ▼
ingest.py
      │
      ▼
staging/*.csv
      │
      ▼
transform.py
      │
      ▼
transformed_stock_data.csv
      │
      ▼
validate.py
      │
 ┌────┴─────┐
 ▼          ▼
validated   flagged
CSV         CSV
 │           │
 └────┬──────┘
      ▼
load.py
      │
      ▼
MySQL
 ┌───────────────┬────────────────┐
 │ clean_prices  │ flagged_prices │
 └───────────────┴────────────────┘
```

---

## 3. Project files

* `ingest.py` — Extracts raw OHLCV data for configured stock tickers and stores raw CSV files in the staging directory.
* `transform.py` — Reads staged files, standardizes schema and data types, calculates Daily Return % and 7-day Moving Average.
* `validate.py` — Applies schema, completeness, accuracy, and anomaly validation rules. Valid and flagged records are written separately.
* `load.py` — Publishes validated records to `clean_prices` and flagged records to `flagged_prices` in MySQL.
* `runbook.md` — Operational documentation for running and troubleshooting the pipeline.

---

## 4. Prerequisites

* Python 3.12+
* Virtual environment activated
* MySQL Server running
* MySQL database created
* Required Python packages installed

Install dependencies:

```powershell
python -m pip install yfinance pandas mysql-connector-python
```

---

## 5. Database setup

Create the database once using MySQL Workbench.

```sql
CREATE DATABASE stock_etl;
```

The tables are automatically created by `load.py`.

---

## 6. How to run the pipeline

Activate the virtual environment first.

```powershell
.venv\Scripts\Activate.ps1
```

Run each stage in order.

### Step 1 — Ingestion

```powershell
python ingest.py
```

Expected output:

* Eight raw CSV files inside `staging/`

### Step 2 — Transformation

```powershell
python transform.py
```

Expected output:

* `transformed_stock_data.csv`

### Step 3 — Validation

```powershell
python validate.py
```

Expected output:

* `validated_stock_data.csv`
* `flagged_stock_data.csv`

Review the flagged file before publishing.

### Step 4 — Load to MySQL

Update MySQL credentials inside `load.py`, then run:

```powershell
python load.py
```

Expected output:

* Valid rows inserted into `clean_prices`
* Flagged rows inserted into `flagged_prices`

---

## 7. Validation rules

The validation stage checks:

### Schema

* Expected columns exist.
* Correct data types are present.

### Completeness

* Required fields contain no null values.
* Expected stock tickers are present.
* Suspicious gaps in trading dates are flagged.

### Accuracy

* High price must be greater than or equal to Low price.
* Open, High, Low, and Close prices must be greater than zero.
* Volume cannot be negative.

### Anomaly

* Any absolute daily percentage move greater than 15% is routed to the flagged dataset for review.

Flagged rows are preserved with a failure reason instead of being deleted.

---

## 8. Troubleshooting

### Ingestion fails

Check:

* Internet connection
* Yahoo Finance availability
* Correct ticker symbols
* Whether staging directory is writable

### Transformation fails

Check:

* Raw CSV files exist inside `staging/`
* CSV structure matches the expected staged format
* Column names were not manually modified

### Validation produces flagged rows

Do not delete them.

Inspect:

```text
flagged_stock_data.csv
```

Determine whether the issue is a genuine market movement or a data-quality issue.

### MySQL load fails

Check:

* MySQL service is running.
* Username and password in `load.py` are correct.
* Database `stock_etl` exists.
* `mysql-connector-python` is installed inside `.venv`.

---

## 9. Success criteria

A successful run should produce:

* Eight raw staging CSV files
* One transformed CSV
* One validated CSV
* One flagged CSV
* MySQL table `clean_prices`
* MySQL table `flagged_prices`

The row counts in MySQL should match the validated and flagged CSV outputs from the validation stage.
