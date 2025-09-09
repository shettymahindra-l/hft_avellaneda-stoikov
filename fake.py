from datetime import datetime
import os

def trade_log(sym, side, price, amount):
    if not os.path.isdir("trades"):
        os.mkdir("trades")

    today = datetime.now().strftime("%Y-%m-%d")

    if not os.path.isfile(f"trades/{today}.csv"):
        with open(f"trades/{today}.csv", "w") as trade_file:
            trade_file.write("sym,side,amount,price\n")

    with open(f"trades/{today}.csv", "a+") as trade_file:
        trade_file.write(f"{sym},{side},{amount},{price}\n")

# Simulate a buy and sell
trade_log("ETHUSDT", "buy", 1600.50, 0.01)
trade_log("ETHUSDT", "sell", 1625.80, 0.01)

print("Fake trades written.")
