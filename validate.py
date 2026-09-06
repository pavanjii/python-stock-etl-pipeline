import pandas as pd


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

INPUT_FILE = "transformed_stock_data.csv"

VALIDATED_FILE = "validated_stock_data.csv"
FLAGGED_FILE = "flagged_stock_data.csv"

EXPECTED_TICKERS = {
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "META",
    "NVDA",
    "TSLA",
    "JPM",
}

EXPECTED_COLUMNS = [
    "Date",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "Ticker",
    "Daily_Return_Pct",
    "MA_7",
]

REQUIRED_COLUMNS = [
    "Date",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "Ticker",
]


# --------------------------------------------------
# 2. Load transformed data
# --------------------------------------------------

df = pd.read_csv(
    INPUT_FILE,
    parse_dates=["Date"]
)

print("Loaded:", INPUT_FILE)
print("Rows:", len(df))


# --------------------------------------------------
# 3. Schema check
# --------------------------------------------------

print("\n========== SCHEMA CHECK ==========")

actual_columns = df.columns.tolist()

missing_columns = [
    column
    for column in EXPECTED_COLUMNS
    if column not in actual_columns
]

unexpected_columns = [
    column
    for column in actual_columns
    if column not in EXPECTED_COLUMNS
]

if missing_columns:
    print("FAILED - Missing columns:", missing_columns)
else:
    print("PASS - All expected columns are present.")

if unexpected_columns:
    print("WARNING - Unexpected columns:", unexpected_columns)


# Expected data types
expected_dtypes = {
    "Date": "datetime",
    "Open": "numeric",
    "High": "numeric",
    "Low": "numeric",
    "Close": "numeric",
    "Volume": "numeric",
    "Ticker": "string",
    "Daily_Return_Pct": "numeric",
    "MA_7": "numeric",
}


schema_failures = []

for column, expected_type in expected_dtypes.items():

    if column not in df.columns:
        continue

    if expected_type == "datetime":

        if not pd.api.types.is_datetime64_any_dtype(
            df[column]
        ):
            schema_failures.append(column)

    elif expected_type == "numeric":

        if not pd.api.types.is_numeric_dtype(
            df[column]
        ):
            schema_failures.append(column)

    elif expected_type == "string":

        if not (
            pd.api.types.is_string_dtype(df[column])
            or df[column].dtype == object
        ):
            schema_failures.append(column)


if schema_failures:
    print(
        "FAILED - Incorrect data types:",
        schema_failures
    )
else:
    print("PASS - Data types are correct.")


# --------------------------------------------------
# 4. Create validation flag columns
# --------------------------------------------------

df["Validation_Failed"] = False
df["Failure_Reason"] = ""


def add_failure(mask, reason):
    """
    Mark rows that violate a validation rule.
    """

    df.loc[mask, "Validation_Failed"] = True

    existing_reason = df.loc[
        mask,
        "Failure_Reason"
    ]

    df.loc[
        mask,
        "Failure_Reason"
    ] = existing_reason.apply(
        lambda x: f"{x}; {reason}".strip("; ")
        if x
        else reason
    )


# --------------------------------------------------
# 5. Completeness check - nulls
# --------------------------------------------------

print("\n========== COMPLETENESS CHECK ==========")

null_mask = df[REQUIRED_COLUMNS].isnull().any(axis=1)

add_failure(
    null_mask,
    "Null in required field"
)

null_count = null_mask.sum()

if null_count == 0:
    print("PASS - No nulls in required fields.")
else:
    print(
        f"FAILED - {null_count} rows contain "
        "null required fields."
    )


# --------------------------------------------------
# 6. Completeness check - expected tickers
# --------------------------------------------------

actual_tickers = set(
    df["Ticker"].dropna().unique()
)

missing_tickers = (
    EXPECTED_TICKERS - actual_tickers
)

unexpected_tickers = (
    actual_tickers - EXPECTED_TICKERS
)

if missing_tickers:
    print(
        "FAILED - Missing tickers:",
        missing_tickers
    )
else:
    print("PASS - All expected tickers are present.")

if unexpected_tickers:
    print(
        "WARNING - Unexpected tickers:",
        unexpected_tickers
    )


# --------------------------------------------------
# 7. Completeness check - missing trading days
# --------------------------------------------------

print("\nChecking trading-day continuity...")

# We check continuity within each ticker.
# Weekends are naturally excluded.
#
# A missing trading day is identified by checking
# whether the gap between consecutive observations
# exceeds 4 calendar days. This allows for normal
# Friday-to-Monday gaps and most standard weekends.

df = df.sort_values(
    ["Ticker", "Date"]
).reset_index(drop=True)

df["Previous_Date"] = (
    df.groupby("Ticker")["Date"]
    .shift(1)
)

df["Date_Gap_Days"] = (
    df["Date"] - df["Previous_Date"]
).dt.days


missing_day_mask = (
    df["Date_Gap_Days"] > 4
)

add_failure(
    missing_day_mask,
    "Possible missing trading day(s)"
)

missing_day_count = missing_day_mask.sum()

if missing_day_count == 0:
    print(
        "PASS - No suspicious gaps greater than "
        "4 calendar days."
    )
else:
    print(
        f"FAILED - {missing_day_count} rows have "
        "possible missing trading-day gaps."
    )


# --------------------------------------------------
# 8. Accuracy rule - High >= Low
# --------------------------------------------------

print("\n========== ACCURACY CHECK ==========")

high_low_mask = (
    df["High"].notna()
    & df["Low"].notna()
    & (df["High"] < df["Low"])
)

add_failure(
    high_low_mask,
    "High is less than Low"
)

print(
    "High >= Low failures:",
    high_low_mask.sum()
)


# --------------------------------------------------
# 9. Accuracy rule - Prices > 0
# --------------------------------------------------

price_columns = [
    "Open",
    "High",
    "Low",
    "Close",
]

for column in price_columns:

    invalid_price_mask = (
        df[column].notna()
        & (df[column] <= 0)
    )

    add_failure(
        invalid_price_mask,
        f"{column} <= 0"
    )

    print(
        f"{column} <= 0 failures:",
        invalid_price_mask.sum()
    )


# --------------------------------------------------
# 10. Accuracy rule - Volume >= 0
# --------------------------------------------------

invalid_volume_mask = (
    df["Volume"].notna()
    & (df["Volume"] < 0)
)

add_failure(
    invalid_volume_mask,
    "Volume is negative"
)

print(
    "Negative volume failures:",
    invalid_volume_mask.sum()
)


# --------------------------------------------------
# 11. Anomaly rule - Daily move > 15%
# --------------------------------------------------

print("\n========== ANOMALY CHECK ==========")

anomaly_mask = (
    df["Daily_Return_Pct"].notna()
    & (
        df["Daily_Return_Pct"].abs() > 15
    )
)

add_failure(
    anomaly_mask,
    "Daily price move exceeds 15%"
)

print(
    "Rows with daily move > 15%:",
    anomaly_mask.sum()
)


# --------------------------------------------------
# 12. Remove helper columns from final output
# --------------------------------------------------

df = df.drop(
    columns=[
        "Previous_Date",
        "Date_Gap_Days"
    ]
)


# --------------------------------------------------
# 13. Separate valid and flagged records
# --------------------------------------------------

flagged_df = df[
    df["Validation_Failed"]
].copy()

validated_df = df[
    ~df["Validation_Failed"]
].copy()


# --------------------------------------------------
# 14. Save outputs
# --------------------------------------------------

validated_df.to_csv(
    VALIDATED_FILE,
    index=False
)

flagged_df.to_csv(
    FLAGGED_FILE,
    index=False
)


# --------------------------------------------------
# 15. Validation summary
# --------------------------------------------------

print("\n========== VALIDATION SUMMARY ==========")

print(
    "Total rows:",
    len(df)
)

print(
    "Valid rows:",
    len(validated_df)
)

print(
    "Flagged rows:",
    len(flagged_df)
)

print(
    "Validation status:",
    "PASS"
    if len(flagged_df) == 0
    else "REVIEW REQUIRED"
)

print(
    f"\nValidated data saved to: {VALIDATED_FILE}"
)

print(
    f"Flagged data saved to: {FLAGGED_FILE}"
)


# --------------------------------------------------
# 16. Show flagged records
# --------------------------------------------------

if not flagged_df.empty:

    print("\n========== FLAGGED RECORDS ==========")

    print(
        flagged_df[
            [
                "Date",
                "Ticker",
                "Close",
                "Daily_Return_Pct",
                "Failure_Reason"
            ]
        ].to_string(index=False)
    )

def check_required_nulls(df):
    """Return rows where required fields contain null values."""
    required_columns = [
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "Ticker"
    ]

    return df[required_columns].isnull().any(axis=1)


def check_price_relationship(df):
    """Return rows where High is lower than Low."""
    return df["High"] < df["Low"]


def check_non_positive_prices(df):
    """Return rows where any price is zero or negative."""
    return (
        (df["Open"] <= 0)
        | (df["High"] <= 0)
        | (df["Low"] <= 0)
        | (df["Close"] <= 0)
    )


def check_negative_volume(df):
    """Return rows where volume is negative."""
    return df["Volume"] < 0


def check_large_daily_move(df, threshold=15):
    """Return rows where absolute daily return exceeds threshold."""
    return df["Daily_Return_Pct"].abs() > threshold