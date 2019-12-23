from datetime import datetime
from io import BytesIO
from typing import BinaryIO

import matplotlib.pyplot as plt
import pandas as pd
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.timeseries import TimeSeries


class Market:

    def __init__(self, key: str):
        self.ti = TechIndicators(key=key, output_format='pandas')
        self.ts = TimeSeries(key=key, output_format='pandas')

    @staticmethod
    def sort_data_and_plot(data: pd.DataFrame, label: str, since: datetime, x: str, y: str, ax):
        data = data.reset_index()
        data['date'] = data['date'].astype('datetime64[ns]')
        data = data.loc[since < data['date']]
        data = data.loc[data[y] > 0.0].dropna()  # Remove zero values
        data.plot(x=x, y=y, ax=ax, label=label)

    def get_wma(self, stock: str, since: datetime) -> BinaryIO:
        # Init the plot
        plt.clf()
        fig = plt.figure()
        ax = plt.gca()
        ax.set_ylabel('Dollar')

        # Real price
        df: pd.DataFrame = self.ts.get_daily(symbol=stock, outputsize='full')[0]
        Market.sort_data_and_plot(data=df, label='Value', since=since, x='date', y='1. open', ax=ax)

        # Add wma for 45, 90, 120 days
        for period in [45, 90, 120]:
            df: pd.DataFrame = self.ti.get_wma(symbol=stock, interval='daily', time_period=period)[0]
            Market.sort_data_and_plot(data=df, label=str(period), since=since, x='date', y='WMA', ax=ax)

        # Draw and return png as buffer
        plt.plot()
        buffer = BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        return buffer
