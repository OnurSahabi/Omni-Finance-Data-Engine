import argparse 
from src.market_data_ingestion import fetch_multiple_tickers
from src.db_connection import get_connection
from psycopg2.extras import execute_batch


def get_args():
    parser = argparse.ArgumentParser(
        description="Piyasa verilerini yfinance üzerinden indirir ve veritabanına kaydeder.")

    parser.add_argument(
        "--start",
        type=str,
        default="2020-01-01",  # Eğer terminalden tarih girilmezse bu kullanılacak
        help="Başlangıç tarihi (Format: YYYY-AA-GG, Örn: 2023-05-01)"
    )

    parser.add_argument(
        "--end",
        type=str,
        default=None,  # Eğer girilmezse yfinance varsayılan olarak bugünü alır
        help="Bitiş tarihi (Format: YYYY-AA-GG, Örn: 2024-01-01)"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT asset_id, api_symbol FROM assets")

    rows = cur.fetchall()

    assets_map = {api_symbol: asset_id for asset_id, api_symbol in rows}

    tickers = [api_symbol for _, api_symbol in rows]

    print("Tickers:", tickers)

    print(f"Downloading data since {args.start} to {args.end if args.end else 'today'} for {len(tickers)} assets")

    df = fetch_multiple_tickers(
        tickers,
        start=args.start,
        end=args.end
    )

    df["asset_id"] = df["ticker"].map(assets_map)

    df = df.dropna(subset=["asset_id"])
    df["asset_id"] = df["asset_id"].astype(int)

    df = df.sort_values(["date", "asset_id"])

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