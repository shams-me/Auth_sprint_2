import math
from time import time


class TokenBucket:
    def __init__(self, rate: int, capacity: int):
        self.rate = rate
        self.capacity = capacity
        self._current_tokens = capacity
        self._last_refill_time = time()

    def acquire_token(self):
        time_since_last_refill = self._get_elapsed_time()
        tokens_to_restore = self._calculate_tokens_to_add(time_since_last_refill)
        self._refill_tokens(tokens_to_restore)

        if self._current_tokens < 1:
            return False

        self._current_tokens -= 1
        return True

    def _get_elapsed_time(self):
        current_time = time()
        time_since_last_refill = current_time - self._last_refill_time
        self._last_refill_time = current_time
        return time_since_last_refill

    def _refill_tokens(self, tokens_to_restore):
        self._current_tokens = min(self.capacity, self._current_tokens + tokens_to_restore)

    def _calculate_tokens_to_add(self, last_time):
        return math.floor(last_time * self.rate)
