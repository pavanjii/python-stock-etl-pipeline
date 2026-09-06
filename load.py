import os
import pandas as pd
import mysql.connector
from mysql.connector import Error


# --------------------------------------------------
# Configuration
# --------------------------------------------------

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE", "stock_etl")
}

VALIDATED_FILE = "validated_stock_data.csv"
FLAGGED_FILE = "flagged_stock_data.csv"


# --------------------------------------------------
# Create database tables
# --------------------------------------------------

CREATE_CLEAN_TABLE = """
CREATE TABLE IF NOT EXISTS clean_prices (

    id INT AUTO_INCREMENT PRIMARY KEY,

    trade_date DATE NOT NULL,
    ticker VARCHAR(10) NOT NULL,

    open_price DOUBLE,
    high_price DOUBLE,
    low_price DOUBLE,
    close_price DOUBLE,

    volume BIGINT,

    daily_return_pct DOUBLE,
    ma_7 DOUBLE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY unique_price (trade_date, ticker)
)
"""


CREATE_FLAGGED_TABLE = """
CREATE TABLE IF NOT EXISTS flagged_prices (

    id INT AUTO_INCREMENT PRIMARY KEY,

    trade_date DATE,
    ticker VARCHAR(10),

    open_price DOUBLE,
    high_price DOUBLE,
    low_price DOUBLE,
    close_price DOUBLE,

    volume BIGINT,

    daily_return_pct DOUBLE,
    ma_7 DOUBLE,

    validation_failed BOOLEAN,
    failure_reason VARCHAR(255),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


# --------------------------------------------------
# Read CSV files
# --------------------------------------------------

def read_files():

    validated_df = pd.read_csv(
        VALIDATED_FILE,
        parse_dates=["Date"]
    )

    flagged_df = pd.read_csv(
        FLAGGED_FILE,
        parse_dates=["Date"]
    )

    return validated_df, flagged_df


# --------------------------------------------------
# Prepare validated rows
# --------------------------------------------------

def prepare_clean_rows(df):

    rows = []

    for _, row in df.iterrows():

        rows.append(
            (
                row["Date"].date(),
                row["Ticker"],
                float(row["Open"]),
                float(row["High"]),
                float(row["Low"]),
                float(row["Close"]),
                int(row["Volume"]),
                None if pd.isna(row["Daily_Return_Pct"])
                else float(row["Daily_Return_Pct"]),
                None if pd.isna(row["MA_7"])
                else float(row["MA_7"])
            )
        )

    return rows


# --------------------------------------------------
# Prepare flagged rows
# --------------------------------------------------

def prepare_flagged_rows(df):

    rows = []

    for _, row in df.iterrows():

        rows.append(
            (
                row["Date"].date(),
                row["Ticker"],
                float(row["Open"]),
                float(row["High"]),
                float(row["Low"]),
                float(row["Close"]),
                int(row["Volume"]),
                None if pd.isna(row["Daily_Return_Pct"])
                else float(row["Daily_Return_Pct"]),
                None if pd.isna(row["MA_7"])
                else float(row["MA_7"]),
                bool(row["Validation_Failed"]),
                row["Failure_Reason"]
            )
        )

    return rows


# --------------------------------------------------
# Publish to MySQL
# --------------------------------------------------

def load_data():

    validated_df, flagged_df = read_files()

    clean_rows = prepare_clean_rows(validated_df)
    flagged_rows = prepare_flagged_rows(flagged_df)

    connection = None

    try:

        connection = mysql.connector.connect(**DB_CONFIG)

        cursor = connection.cursor()

        print("Connected to MySQL")

        # Create tables if they don't exist
        cursor.execute(CREATE_CLEAN_TABLE)
        cursor.execute(CREATE_FLAGGED_TABLE)

        # Clear previous load
        cursor.execute("DELETE FROM clean_prices")
        cursor.execute("DELETE FROM flagged_prices")

        # --------------------------------------------------
        # Insert validated rows
        # --------------------------------------------------

        clean_insert = """
        INSERT INTO clean_prices
        (
            trade_date,
            ticker,
            open_price,
            high_price,
            low_price,
            close_price,
            volume,
            daily_return_pct,
            ma_7
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        cursor.executemany(
            clean_insert,
            clean_rows
        )

        # --------------------------------------------------
        # Insert flagged rows
        # --------------------------------------------------

        flagged_insert = """
        INSERT INTO flagged_prices
        (
            trade_date,
            ticker,
            open_price,
            high_price,
            low_price,
            close_price,
            volume,
            daily_return_pct,
            ma_7,
            validation_failed,
            failure_reason
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        if flagged_rows:

            cursor.executemany(
                flagged_insert,
                flagged_rows
            )

        # Commit transaction
        connection.commit()

        print(
            f"Inserted {len(clean_rows)} rows into clean_prices"
        )

        print(
            f"Inserted {len(flagged_rows)} rows into flagged_prices"
        )

        print("Transaction committed successfully.")

    except Error as e:

        if connection:
            connection.rollback()

        print("MySQL Error:", e)

    finally:

        if connection and connection.is_connected():

            cursor.close()
            connection.close()

            print("MySQL connection closed.")


# --------------------------------------------------
# Run
# --------------------------------------------------

if __name__ == "__main__":

    load_data()