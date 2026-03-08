from pathlib import Path

import pandas as pd

from src.db_connection import get_connection


def load_assets():
    base_dir = Path(__file__).resolve().parent.parent
    csv_path = base_dir / "data" / "assets.csv"

    df = pd.read_csv(csv_path)

    conn = get_connection()
    cur = conn.cursor()

    for _, row in df.iterrows():
        cur.execute(
            """
            INSERT INTO assets (ticker, name, asset_type, currency)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (ticker) DO NOTHING
            """,
            (
                row["ticker"],
                row["name"],
                row["asset_type"],
                row["exchange"],
                row["currency"],
            ),
        )

    conn.commit()
    cur.close()
    conn.close()

    print("Assets loaded")


if __name__ == "__main__":
    load_assets()