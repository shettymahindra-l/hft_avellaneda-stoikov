from decouple import config
from binance.client import Client
import datetime
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pandas_ta")
import numpy as np
np.NaN = np.nan   # Patch for pandas-ta expecting NaN
import pandas_ta as ta
import pandas_ta as ta
import os
import json
import time

# Binance client (testnet=True for safety!)
client = Client(config("API_KEY"), config("API_SECRET"), testnet=True)
asset = "ETHUSDT"
entry = 25
exit = 60

def fetch_klines(asset):
    """Fetch last 50 1-minute candles directly from Binance"""
    klines = client.get_klines(symbol=asset, interval=Client.KLINE_INTERVAL_1MINUTE, limit=50)
    df = pd.DataFrame(klines, columns=[
        "open_time","open","high","low","close","volume",
        "close_time","quote_asset_volume","number_of_trades",
        "taker_buy_base","taker_buy_quote","ignore"
    ])
    df["date"] = pd.to_datetime(df["open_time"], unit="ms")
    df["price"] = df["close"].astype(float)
    return df[["date","price"]]

def log(msg):
    print(f"LOG: {msg}")
    if not os.path.isdir("logs"):
        os.mkdir("logs")

    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    time_now = now.strftime("%H:%M:%S")
    with open(f"logs/{today}.txt", "a+") as log_file:
        log_file.write(f"{time_now} : {msg}\n")

def trade_log(sym, side, price, amount):
    log(f"{side} {amount} {sym} for {price} per")
    if not os.path.isdir("trades"):
        os.mkdir("trades")

    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")

    if not os.path.isfile(f"trades/{today}.csv"):
        with open(f"trades/{today}.csv", "w") as trade_file:
            trade_file.write("sym,side,amount,price\n")

    with open(f"trades/{today}.csv", "a+") as trade_file:
        trade_file.write(f"{sym},{side},{amount},{price}\n")

def create_account():
    account = {
        "is_buying": True,
        "assets": {}
    }
    with open("bot_account.json", "w") as f:
        f.write(json.dumps(account))

def is_buying():
    if os.path.isfile("bot_account.json"):
        with open("bot_account.json") as f:
            account = json.load(f)
            return account.get("is_buying", True)
    else:
        create_account()
        return True

def get_rsi(asset):
    klines = fetch_klines(asset)
    klines["rsi"] = ta.rsi(close=klines["price"], length=14)
    return klines["rsi"].iloc[-1]

def do_trade(account, client, asset, side, quantity):
    if side == "buy":
        order = client.order_market_buy(symbol=asset, quantity=quantity)
        account["is_buying"] = False
    else:
        order = client.order_market_sell(symbol=asset, quantity=quantity)
        account["is_buying"] = True

    order_id = order["orderId"]

    # Wait until filled
    while order["status"] != "FILLED":
        order = client.get_order(symbol=asset, orderId=order_id)
        time.sleep(1)

    price_paid = sum(float(fill["price"]) * float(fill["qty"]) for fill in order["fills"])
    trade_log(asset, side, price_paid, quantity)

    with open("bot_account.json", "w") as f:
        f.write(json.dumps(account))


        

# ======================
# Main trading loop
# ======================
rsi = get_rsi(asset)
old_rsi = rsi

while True:
    try:
        if not os.path.exists("bot_account.json"):
            create_account()

        with open("bot_account.json") as f:
            account = json.load(f)

        old_rsi = rsi
        rsi = get_rsi(asset)

        if account["is_buying"]:
            if rsi < entry and old_rsi > entry:
                do_trade(account, client, asset, "buy", 0.01)
        else:
            if rsi > exit and old_rsi < exit:
                do_trade(account, client, asset, "sell", 0.01)

        print(f"RSI: {rsi}")
        time.sleep(10)

    except Exception as e:
        log("ERROR: " + str(e))
