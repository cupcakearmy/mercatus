from typing import List, Optional


class LimitedList:
    """
    Basically a List that has a maximum amount of entries.
    When full and new elements get appended the oldest gets deleted.
    """

    def __init__(self, limit: int, init: Optional[List[str]]):
        self.data = init if init else []
        self.limit = limit

    def __len__(self):
        return len(self.data)

    def _is_index(self, i: int) -> bool:
        return False if i < 0 or i > len(self.data) - 1 else True

    def add(self, value: any):
        print(f'Before {self.data}')
        # Delete oldest element if there are too many
        if len(self.data) + 1 > self.limit:
            self.data = self.data[1:]

        self.data.append(value)
        print(f'After {self.data}')

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
