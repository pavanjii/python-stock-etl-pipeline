import os
import pandas as pd


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

STAGING_DIR = "staging"

TICKERS = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "META",
    "NVDA",
    "TSLA",
    "JPM",
]


# --------------------------------------------------
# 2. Transform one staged file
# --------------------------------------------------

def transform_ticker(ticker):
    """
    Read one raw staging file and transform it
    into a standardized DataFrame.
    """

    input_file = os.path.join(
        STAGING_DIR,
        f"{ticker}_raw.csv"
    )

    # Read the raw CSV exactly as it was staged
    raw_df = pd.read_csv(input_file)

    # --------------------------------------------------
    # The yfinance CSV contains two metadata rows:
    #
    # Row 0 -> Ticker
    # Row 1 -> Date
    #
    # Actual market data starts from row 2.
    # --------------------------------------------------

    df = raw_df.iloc[2:].copy()

    # Rename "Price" column to "Date"
    df = df.rename(
        columns={"Price": "Date"}
    )

    # --------------------------------------------------
    # Select required OHLCV fields
    # --------------------------------------------------

    df = df[
        [
            "Date",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]
    ].copy()

    # --------------------------------------------------
    # Standardize data types
    # --------------------------------------------------

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    numeric_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Add ticker
    df["Ticker"] = ticker

    # --------------------------------------------------
    # Remove rows that could not be converted
    # --------------------------------------------------

    df = df.dropna(
        subset=[
            "Date",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]
    )

    # --------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------

    df = df.sort_values(
        "Date"
    ).reset_index(drop=True)

    # --------------------------------------------------
    # Derived field 1:
    # Daily percentage return
    # --------------------------------------------------

    df["Daily_Return_Pct"] = (
        df["Close"]
        .pct_change()
        * 100
    )

    # --------------------------------------------------
    # Derived field 2:
    # 7-day moving average
    # --------------------------------------------------

    df["MA_7"] = (
        df["Close"]
        .rolling(window=7)
        .mean()
    )

    return df


# --------------------------------------------------
# 3. Transform all staged files
# --------------------------------------------------

def transform_all():

    transformed_frames = []

    for ticker in TICKERS:

        print(f"Transforming {ticker}...")

        try:

            df = transform_ticker(ticker)

            transformed_frames.append(df)

            print(
                f"{ticker}: {len(df)} rows transformed"
            )

        except Exception as e:

            print(
                f"ERROR transforming {ticker}: {e}"
            )

    # Make sure at least one file was transformed
    if not transformed_frames:

        raise ValueError(
            "No ticker files were successfully transformed."
        )

    # Combine all ticker DataFrames
    clean_df = pd.concat(
        transformed_frames,
        ignore_index=True
    )

    # Final ordering
    clean_df = clean_df.sort_values(
        ["Ticker", "Date"]
    ).reset_index(drop=True)

    return clean_df


# --------------------------------------------------
# 4. Run transformation
# --------------------------------------------------

if __name__ == "__main__":

    clean_df = transform_all()

    print(
        "\n========== TRANSFORMATION COMPLETE =========="
    )

    print("\nShape:")
    print(clean_df.shape)

    print("\nColumns:")
    print(clean_df.columns.tolist())

    print("\nData types:")
    print(clean_df.dtypes)

    print("\nSample:")
    print(
        clean_df.head(10).to_string(index=False)
    )

    # Save transformed data
    output_file = "transformed_stock_data.csv"

    clean_df.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nTransformed data saved to: {output_file}"
    )