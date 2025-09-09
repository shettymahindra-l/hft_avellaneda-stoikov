import pandas as pd
import glob

# Load today's trade file (latest one)
files = sorted(glob.glob("trades/*.csv"))
if not files:
    print("No trade files found.")
    exit()

df = pd.read_csv(files[-1])  # take latest
print("Trades:\n", df)

pnl = 0
buy_price = None
qty = 0

for _, row in df.iterrows():
    if row["side"] == "buy":
        buy_price = row["price"]
        qty = row["amount"]
    elif row["side"] == "sell" and buy_price:
        trade_pnl = (row["price"] - buy_price) * qty
        pnl += trade_pnl
        print(f"Closed Trade: Bought at {buy_price}, Sold at {row['price']}, PnL = {trade_pnl:.2f}")
        buy_price = None

print(f"\nTotal PnL: {pnl:.2f}")
