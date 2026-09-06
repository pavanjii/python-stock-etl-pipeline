import pandas as pd

from validate import (
    check_required_nulls,
    check_price_relationship,
    check_non_positive_prices,
    check_negative_volume,
    check_large_daily_move,
)


def create_test_dataframe(**overrides):
    """Create a valid stock row that tests can modify."""

    data = {
        "Date": pd.Timestamp("2026-01-02"),
        "Open": 100.0,
        "High": 105.0,
        "Low": 95.0,
        "Close": 102.0,
        "Volume": 1000000,
        "Ticker": "TEST",
        "Daily_Return_Pct": 2.0,
        "MA_7": 101.0,
    }

    data.update(overrides)

    return pd.DataFrame([data])


def test_negative_price_is_flagged():
    df = create_test_dataframe(Open=-10.0)

    result = check_non_positive_prices(df)

    assert result.iloc[0]


def test_high_lower_than_low_is_flagged():
    df = create_test_dataframe(
        High=90.0,
        Low=95.0
    )

    result = check_price_relationship(df)

    assert result.iloc[0]


def test_negative_volume_is_flagged():
    df = create_test_dataframe(Volume=-100)

    result = check_negative_volume(df)

    assert result.iloc[0]


def test_missing_required_field_is_flagged():
    df = create_test_dataframe(Close=None)

    result = check_required_nulls(df)

    assert result.iloc[0]


def test_large_daily_move_is_flagged():
    df = create_test_dataframe(
        Daily_Return_Pct=16.0
    )

    result = check_large_daily_move(df)

    assert result.iloc[0]