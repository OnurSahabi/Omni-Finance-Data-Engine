from src.market_data_ingestion import fetch_multiple_tickers
from src.db_connection import get_connection
from psycopg2.extras import execute_batch

if __name__ == "__main__":

    conn = get_connection()
    cur = conn.cursor()


    cur.execute("SELECT asset_id, ticker FROM assets")

    rows = cur.fetchall()


    assets_map = {ticker: asset_id for asset_id, ticker in rows}


    tickers = [ticker for _, ticker in rows]

    print("Tickers:", tickers)

    print(f"Downloading data since 2024-01-01 for {len(tickers)} assets")

    df = fetch_multiple_tickers(
        tickers,
        start="2024-01-01"
    )


    df["asset_id"] = df["ticker"].map(assets_map)

    prices_df = df[
        ["asset_id", "date", "open", "high", "low", "close", "volume"]
    ]


    returns_df = df[
        ["asset_id", "date", "simple_return", "log_return"]
    ].dropna()

    print("\nPRICES")
    print(prices_df.head())

    print("\nRETURNS")
    print(returns_df.head())


    prices_data = prices_df.values.tolist()

    execute_batch(
        cur,
        """
        INSERT INTO prices
        (asset_id, price_time, open, high, low, close, volume)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (asset_id, price_time) DO NOTHING
        """,
        prices_data,
        page_size=1000
    )
    print(f"{len(prices_data)} price rows inserted")


    returns_data = returns_df.values.tolist()

    execute_batch(
        cur,
        """
        INSERT INTO returns
        (asset_id, return_time, simple_return, log_return)
        VALUES (%s,%s,%s,%s)
        ON CONFLICT (asset_id, return_time) DO NOTHING
        """,
        returns_data,
        page_size=1000
    )
    print(f"{len(returns_data)} return rows inserted")

    conn.commit()
    cur.close()
    conn.close()