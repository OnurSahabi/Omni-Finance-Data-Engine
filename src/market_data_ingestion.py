import yfinance as yf
import pandas as pd
import numpy as np

def fetch_market_data(ticker,
                      start=None,
                      end=None,
                      interval="1d") -> pd.DataFrame:

    df = yf.download(
        ticker,
        start=start,
        end=end,
        interval=interval,
        progress=False,
        group_by="column"
    )

    if df.empty:
        raise ValueError(f"{ticker} için veri bulunamadı")

    df.reset_index(inplace=True)

    df.columns = [
        c[0].lower().replace(" ", "_") if isinstance(c, tuple)
        else c.lower().replace(" ", "_")
        for c in df.columns
    ]
    #print(df.columns)



    df["ticker"] = ticker

    df["simple_return"] = df["close"].pct_change()

    df["log_return"] = np.log(df["close"]).diff()

    return df


def fetch_multiple_tickers(tickers,
                           start=None,
                           end=None,
                           interval="1d") -> pd.DataFrame:

    data = []

    for ticker in tickers:
        print(f"{ticker} indiriliyor...")

        try:
            df = fetch_market_data(ticker, start, end, interval)
            data.append(df)

        except Exception as e:
            print(f"{ticker} hata: {e}")

    if not data:
        return pd.DataFrame()

    return pd.concat(data, ignore_index=True)