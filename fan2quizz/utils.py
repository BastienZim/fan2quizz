# src/utils.py
import time
import random


DEFAULT_USER_AGENT = "quizypedia-parser/0.1 (+https://example.com)"




def sleep_backoff(min_seconds=0.5, max_seconds=1.5):
	"""Simple jittered sleep to be polite between requests."""
	time.sleep(random.uniform(min_seconds, max_seconds))




class RateLimiter:
	def __init__(self, min_delay: float = 0.5):
		self.min_delay = min_delay
		self._last = 0.0

	def wait(self):
		now = time.time()
		delta = now - self._last
		if delta < self.min_delay:
			time.sleep(self.min_delay - delta)
		self._last = time.time()