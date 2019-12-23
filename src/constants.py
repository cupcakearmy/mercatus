from enum import Enum


class Section(Enum):
    Watchlist = 'watchlist'  # The list of Stocks/ETF to watch
    Code = 'code'  # Market code for a given stock, etf, etc.
    API_Key = 'api_key'  # Alpha Vantage API Key
    Running = 'running'  # Currently sending updates. Avoid overloading the API
    Enabled = 'enabled'  # Whether the bot should send automatic updates
    Interval = 'interval'  # Time axis of the graph
    Frequency = 'frequency'  # How ofter updates should be sent
    LastRun = 'last_run'  # Last time an update was sent to the user
    CurrentToEdit = 'current_to_edit'  # Current element to edit in the conversation handler
