import io
from typing import BinaryIO
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime


class Market:

    def __init__(self, key: str):
        self.ti = TechIndicators(key=key, output_format='pandas')
        self.ts = TimeSeries(key=key, output_format='pandas')

    def get_wma(self, stock: str, since: datetime) -> BinaryIO:
        plt.clf()
        fig = plt.figure()
        ax = plt.gca()
        ax.set_ylabel('Dollar')

        def sort_data_and_plot(data: pd.DataFrame, x: str, y: str, label: str):
            data = data.reset_index()
            data['date'] = data['date'].astype('datetime64[ns]')
            data = data.loc[since < data['date']]
            data.plot(x=x, y=y, ax=ax, label=label)

        df: pd.DataFrame = self.ts.get_daily(symbol=stock, outputsize='full')[0]
        sort_data_and_plot(data=df, x='date', y='1. open', label='Value')

        for period in [45, 90, 120]:
            df: pd.DataFrame = self.ti.get_wma(symbol=stock, interval='daily', time_period=period)[0]
            sort_data_and_plot(data=df, x='date', y='WMA', label=str(period))

        plt.plot()
        # plt.show()
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        return buffer
