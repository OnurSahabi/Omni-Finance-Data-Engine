import argparse
from datetime import timedelta
from src.market_data_ingestion import fetch_multiple_tickers
from src.db_connection import get_connection
from psycopg2.extras import execute_batch


def get_args():
    parser = argparse.ArgumentParser(
        description="Piyasa verilerini indirir ve veritabanına kaydeder."
    )

    parser.add_argument(
        "--start",
        type=str,
        default="2020-01-01",
        help="Başlangıç tarihi (fallback)"
    )

    parser.add_argument(
        "--end",
        type=str,
        default=None,
        help="Bitiş tarihi"
    )

    return parser.parse_args()


if __name__ == "__main__":

    args = get_args()

    conn = get_connection()
    cur = conn.cursor()

    # asset listesi
    cur.execute("SELECT asset_id, api_symbol FROM assets")
    rows = cur.fetchall()

    assets_map = {api_symbol: asset_id for asset_id, api_symbol in rows}
    tickers = [api_symbol for _, api_symbol in rows]

    print("Tickers:", tickers)

    # son veri tarihini bul
    cur.execute("""
        SELECT MAX(price_time)
        FROM prices
    """)

    last_date = cur.fetchone()[0]

    if last_date is None:
        start_date = args.start
    else:
        start_date = last_date.strftime("%Y-%m-%d")

    print(f"Start date: {start_date}")
    print(f"End date: {args.end if args.end else 'today'}")

    df = fetch_multiple_tickers(
        tickers,
        start=start_date,
        end=args.end
    )

    if df.empty:
        print("No new data.")
        exit()

    df["asset_id"] = df["ticker"].map(assets_map)

    df = df.dropna(subset=["asset_id"])
    df["asset_id"] = df["asset_id"].astype(int)

    df = df.sort_values(["date", "asset_id"])

    prices_df = df[
        ["asset_id", "date", "open", "high", "low", "close", "volume"]
    ]

    if last_date is not None:
        prices_df = prices_df[prices_df["date"] > last_date]

    returns_df = df[
        ["asset_id", "date", "simple_return", "log_return"]
    ].dropna()

    prices_data = list(prices_df.itertuples(index=False, name=None))

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

    returns_data = list(returns_df.itertuples(index=False, name=None))

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