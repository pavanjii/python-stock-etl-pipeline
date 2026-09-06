import os
import logging
import yfinance as yf


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

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

STAGING_DIR = "staging"


# --------------------------------------------------
# 2. Logging configuration
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# 3. Create staging directory
# --------------------------------------------------

os.makedirs(STAGING_DIR, exist_ok=True)


# --------------------------------------------------
# 4. Ingest data ticker by ticker
# --------------------------------------------------

for ticker in TICKERS:

    try:
        logger.info(f"Starting ingestion for {ticker}")

        # Extract raw data from Yahoo Finance
        data = yf.download(
            ticker,
            period="1y",
            interval="1d",
            auto_adjust=False,
            actions=False,
            progress=False
        )

        # Check whether data was returned
        if data.empty:
            raise ValueError(
                f"No data returned for {ticker}"
            )

        # Save raw output WITHOUT cleaning/transformation
        output_file = os.path.join(
            STAGING_DIR,
            f"{ticker}_raw.csv"
        )

        data.to_csv(output_file)

        logger.info(
            f"Successfully ingested {ticker} "
            f"({len(data)} rows) -> {output_file}"
        )

    except Exception as e:

        logger.error(
            f"Failed to ingest {ticker}: {e}"
        )


logger.info("Ingestion process completed.")