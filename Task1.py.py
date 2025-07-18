# crypto_price_dashboard.py
"""
Cryptocurrency Price Tracker Dashboard (display only)
---------------------------------------------------
Fetches recent market data for any coin via CoinGecko’s free API and shows a
Matplotlib dashboard **without saving an image to disk**.

Run:
    python crypto_price_dashboard.py --coin bitcoin --days 90

Dependencies:
    pip install requests pandas matplotlib python-dateutil
"""
from __future__ import annotations

import argparse
import datetime as dt
from typing import List

import requests
import pandas as pd
import matplotlib.pyplot as plt

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/{id}/market_chart"


def fetch_market_data(coin: str, days: int) -> pd.DataFrame:
    """Return daily price series for *coin* over *days* (USD)."""
    resp = requests.get(
        COINGECKO_URL.format(id=coin),
        params={"vs_currency": "usd", "days": days, "interval": "daily"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()["prices"]  # [[unix_ms, price], ...]
    df = pd.DataFrame(data, columns=["unix_ms", "price"])
    df["date"] = pd.to_datetime(df["unix_ms"], unit="ms", utc=True)
    df.set_index("date", inplace=True)
    df.drop(columns=["unix_ms"], inplace=True)
    df["pct_return"] = df["price"].pct_change() * 100
    return df.dropna()


def plot_dashboard(df: pd.DataFrame, coin: str) -> None:
    """Show two‑panel dashboard (price trend + return histogram)."""
    fig = plt.figure(figsize=(10, 8))
    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2)

    # Price trend
    ax1.plot(df.index, df["price"], linewidth=1.8)
    ax1.set_title(f"{coin.capitalize()} price (USD)")
    ax1.set_ylabel("Price (USD)")
    ax1.grid(True, linestyle=":", linewidth=0.5)
    fig.autofmt_xdate()

    # Return histogram
    ax2.hist(df["pct_return"], bins=30, edgecolor="black", alpha=0.75)
    ax2.set_title("Distribution of daily returns (%)")
    ax2.set_xlabel("Daily % change")
    ax2.set_ylabel("Frequency")
    ax2.grid(axis="y", linestyle=":", linewidth=0.5)

    fig.tight_layout()
    plt.show()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="CoinGecko Price Dashboard (display only)")
    p.add_argument("--coin", default="bitcoin", help="Coin ID on CoinGecko (default: bitcoin)")
    p.add_argument("--days", type=int, default=30, help="Look‑back period in days (max 90)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    df = fetch_market_data(args.coin, args.days)
    if df.empty:
        print("No data returned. Check coin ID or date range.")
        return
    plot_dashboard(df, args.coin)


if __name__ == "__main__":
    main()
