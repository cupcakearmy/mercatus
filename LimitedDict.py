import time
import math


class LimitedDict:

    def __init__(self, init: dict, limit: int):
        self.dict = init
        self.limit = limit

    def set(self, key, value):
        # Delete oldest element if there are too many
        if len(self.dict) + 1 > self.limit:
            timestamp = math.inf
            who = None
            for cur, item in self.dict.items():
                if item['when'] < timestamp:
                    timestamp = item['when']
                    who = cur
            del self.dict[who]

        self.dict[key] = {
            'value': value,
            'when': int(time.time())
        }

    def get(self, key):
        value = self.dict.get(key, None)
        return value['value'] if value else None

    def delete(self, key):
        self.dict.pop(key, None)

    def clear(self):
        self.dict.clear()

    def all(self):
        return [x['value'] for x in self.dict.values()]
