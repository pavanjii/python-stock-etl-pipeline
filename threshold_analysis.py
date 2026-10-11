
import pandas as pd

df = pd.read_csv("transformed_stock_data.csv")

thresholds = [15, 10, 5]

print(f"Total records: {len(df)}")
print("\nThreshold sensitivity analysis")

for threshold in thresholds:
    mask = df["Daily_Return_Pct"].abs() > threshold
    flagged = df.loc[mask]

    print(f"\nThreshold: {threshold}%")
    print(f"Flagged records: {len(flagged)}")
    percentage = len(flagged) / len(df) * 100 if not df.empty else 0
    print(f"Percentage flagged: {percentage:.2f}%")

    if not flagged.empty:
        print(
            flagged[
                ["Date", "Ticker", "Daily_Return_Pct"]
            ].sort_values("Daily_Return_Pct").to_string(index=False)
        )
