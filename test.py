from binance.client import Client
import datetime
import psycopg2
from decouple import config

client = Client(config("API_KEY"), config("API_SECRET"), testnet=True)

connection = psycopg2.connect(
    user="postgres",
    password=config("DB_PASS"),
    host="127.0.0.1",
    port="5432",
    database="postgres"
)
cursor = connection.cursor()

symbol = "ETHBTC"

# Fetch candles
candles = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=5)

print("🔥 Raw Binance response:")
print(candles)  # 👈 Add this

for c in candles:
    timestamp = datetime.datetime.fromtimestamp(c[0] / 1000.0)
    o, h, l, close, volume = c[1], c[2], c[3], c[4], c[5]
    print(timestamp, o, h, l, close, volume)  # 👈 Debugging

    cursor.execute("""
        INSERT INTO ohlc_data_minute (date, symbol, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
    """, (timestamp, symbol, o, h, l, close, volume))

connection.commit()
print("✅ Done inserting candles")
