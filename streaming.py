from decouple import config
from binance import ThreadedWebsocketManager
import psycopg2
import datetime

api_key = config("API_KEY")
api_secret = config("API_SECRET")
db_pass = config("DB_PASS")

def main():

    connection = psycopg2.connect(
        user="postgres",
        password=db_pass,
        host="127.0.0.1",
        port="5432",
        database="postgres"
    )
    cursor = connection.cursor()

    # ✅ Create table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS raw_trade_data (
        time TIMESTAMPTZ NOT NULL,
        symbol TEXT NOT NULL,
        price NUMERIC NOT NULL,
        quantity NUMERIC NOT NULL
    );
    """)
    connection.commit()

    # If using TimescaleDB:
    # cursor.execute("SELECT create_hypertable('raw_trade_data', 'time', if_not_exists => TRUE);")
    # connection.commit()

    stream = ["ethusdtT@trade", "solusdt@trade"]

    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
    twm.start()

    def handle_message(msg, cursor=cursor):
        msg = msg["data"]
        print(msg)

        query = """
        INSERT INTO raw_trade_data (time, symbol, price, quantity)
        VALUES (%s, %s, %s, %s)
        """

        timestamp = datetime.datetime.fromtimestamp(msg["T"] / 1000)
        record_to_insert = (timestamp, msg["s"], msg["p"], msg["q"])
        cursor.execute(query, record_to_insert)
        connection.commit()

    twm.start_multiplex_socket(callback=handle_message, streams=stream)
    twm.join()

if __name__ == "__main__":
    main()
