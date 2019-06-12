from typing import List


class LimitedList:

    def __init__(self, init: List[str], limit: int):
        self.data = init
        self.limit = limit

    def _is_index(self, i: int) -> bool:
        return False if i < 0 or i > len(self.data) - 1 else True

    def add(self, value: str):
        # Delete oldest element if there are too many
        if len(self.data) + 1 > self.limit:
            self.data = self.data[1:]

        self.data.append(value)

    def get(self, i: int):
        return self.data[i] if self._is_index(i) else None

    def delete(self, value: str):
        if value in self.data:
            self.data.remove(value)
            return True
        return False

    def clear(self):
        self.data = []

    def all(self):
        return self.data
