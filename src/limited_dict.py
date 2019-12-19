import time
from math import inf


class LimitedDict:

    def __init__(self, limit: int, init: dict):
        self.dict = init
        self.limit = limit

    def __len__(self):
        return len(self.dict)

    def __setitem__(self, key, value):
        # Delete the oldest if there are too many entries
        if len(self.dict) + 1 > self.limit:
            timestamp = inf
            oldest = None
            for cur, item in self.dict.items():
                if item['when'] < timestamp:
                    timestamp = item['when']
                    oldest = cur
            del self.dict[oldest]

        self.dict[key] = {
            'value': value,
            'when': int(time.time())
        }

    def __getitem__(self, key):
        value = self.dict.get(key, None)
        return value['value'] if value else None

    def __delitem__(self, key):
        self.dict.pop(key, None)

    def clear(self):
        self.dict.clear()

    def all(self):
        return {
            key: value['value']
            for key, value in self.dict.items()
        }
