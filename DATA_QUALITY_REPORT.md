# Data Quality Report — Python Stock ETL Pipeline

## 1. Overview

This report summarizes the validation checks and threshold sensitivity analysis performed on the transformed stock dataset containing 2,016 records.

## 2. Validation Checks

The existing automated tests cover the following conditions:

- Non-positive stock prices
- Invalid High–Low price relationships
- Negative trading volume
- Missing required fields
- Unusually large daily returns

**Test result:** All five existing validation tests passed using `python -m pytest -v test_validate.py`.

## 3. Threshold Sensitivity Analysis

The `threshold_analysis.py` script evaluates daily returns using absolute thresholds. A record is flagged when the absolute daily return exceeds the selected threshold.

| Absolute daily-return threshold | Records flagged | Percentage of dataset |
|---|---:|---:|
| 15% | 2 | 0.10% |
| 10% | 5 | 0.25% |
| 5% | 58 | 2.88% |

These results demonstrate that lower thresholds flag more records. The counts measure sensitivity to the configured threshold; they do not establish whether a flagged record is erroneous.

## 4. Records Flagged at the 15% Threshold

| Date | Ticker | Daily return |
|---|---|---:|
| 2026-07-31 | AMZN | +15.3206% |
| 2026-07-30 | MSFT | +15.5067% |

These records require further investigation against reliable market data and relevant corporate or market events before they can be classified as data-quality defects.

## 5. Limitations and Next Steps

- Investigate the two records flagged at the 15% threshold.
- Compare suspicious values with an independent, reliable data source.
- Add tests for valid inputs and threshold-boundary behavior.
- Document the rationale for the selected threshold.
- Re-run the validation suite after changes to the pipeline.

## 6. Reproducibility

Run the existing tests:

```powershell
python -m pytest -v test_validate.py
```

Run the threshold sensitivity analysis:

```powershell
python threshold_analysis.py
```

The analysis requires `transformed_stock_data.csv` in the project directory and the project's Python dependencies to be installed.
