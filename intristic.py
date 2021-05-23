# -*- coding: utf-8 -*-
""""""


import argparse
import textwrap

import requests
import cachetools
import pandas as pd
import matplotlib.pyplot as plt
# import seaborn as sns


def main():
    """Entry point of the application."""
    args = _Parser().specify_args().parse_args()
    ohlc = _fetch_ohlc(args.symbol, args.interval, args.tail)
    _print_info(args.interval, args.tail)
    _display_figure(ohlc)


def _display_figure(ohlc):
    # fig, axs = plt.subplots(ncols=len(ohlc.columns))
    # for price, ax in zip((price for _, price in ohlc.items()), axs):
    #     _make_plot(price, ax=ax)
    # for _, price in ohlc.items():
    #     fig = plt.figure()
    #     _make_plot(price, ax=fig.gca())
    _, axs = plt.subplots(2, 2)
    for price, ax in zip((price for _, price in ohlc.items()), axs.flatten()):
        _make_plot(price, ax=ax)
    plt.show()


def _print_info(interval, number):
    total = pd.Timedelta(interval) * number
    since = pd.Timestamp.today(tz="UTC").ceil("1d") - total
    msg = textwrap.dedent("""
        Note that:
        * displaying %s, since (around) %s
        * 2021-05-23 is 2021-05-23 00:00:00
        * high, low and close are almost never final
    """ % (total, since.strftime("%b %d, %Y")))[1:-1]
    print(msg)


@cachetools.cached(cachetools.TTLCache(1024, ttl=60 * 60))
def _fetch_ohlc(symbol, interval, limit):
    response = requests.get("https://api.binance.com/api/v3/klines", params={
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    })
    if not response.ok:
        # Should I do something here?
        pass
    # From https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#klinecandlestick-data
    # [
    #   [
    #     1499040000000,      // Open time
    #     "0.01634790",       // Open
    #     "0.80000000",       // High
    #     "0.01575800",       // Low
    #     "0.01577100",       // Close
    #     "148976.11427815",  // Volume
    #     1499644799999,      // Close time
    #     "2434.19055334",    // Quote asset volume
    #     308,                // Number of trades
    #     "1756.87402397",    // Taker buy base asset volume
    #     "28.46694368",      // Taker buy quote asset volume
    #     "17928899.62484339" // Ignore.
    #   ]
    # ]
    return (
        pd.DataFrame(response.json())
            [[1, 2, 3, 4, 6]]
            .set_axis(["open", "high", "low", "close", "time"], axis=1)
            .assign(time=lambda frame: (
                frame["time"]
                    .apply(pd.Timestamp, unit="ms")
                    .apply(lambda entry: entry + pd.Timedelta(1, unit="ms"))
            ))
            .set_index("time")
            .astype(float)
    )


def _make_plot(price, ax=None):
    intristic = _make_intristic(price)
    intristic.plot(marker=".", ax=ax)
    # plt.xticks(
    #     intristic.index,
    #     labels=_make_labels(price.index),
    #     rotation=-30,
    # )
    ax.grid(axis="y")
    ax.set_xticks(intristic.index)
    ax.set_xticklabels(_make_labels(price.index), rotation=-30)
    ax.set_xlim(intristic.index[[0, -1]])
    ax.set_title(
        # "ETHUSDT, 1D, %s" % price.name
        price.name
    )


def _make_intristic(price):
    # I should have it implemented somewhere...
    return pd.Series(
        index=price.pct_change().abs().fillna(0).cumsum().values,
        data=price.values,
    )


def _make_labels(index):
    step = len(index) // 10
    return reversed([
        timestamp.strftime("%Y-%m-%d")
        if i % step == 0
        else ""
        for i, timestamp in enumerate(reversed(index))
    ])


class _Parser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("description", __doc__)
        super().__init__(*args, **kwargs)

    def specify_args(self):
        self.add_argument("symbol", help="like ETHUSDT")
        self.add_argument(
            "-i", "--interval",
            default="1d",
            help="1d, 3d, 1w, etc.",
        )
        self.add_argument(
            "-t", "--tail",
            type=int,
            default=50,
            help="intervals to ask for, max 1000",
        )
        return self


if __name__ == "__main__":
    main()
