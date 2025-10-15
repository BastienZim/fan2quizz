# src/scraper.py
import requests
from bs4 import BeautifulSoup
from typing import Iterator, Optional
from .utils import RateLimiter, DEFAULT_USER_AGENT




class QuizypediaScraper:
	BASE = "https://www.quizypedia.fr"

	def __init__(self, session: Optional[requests.Session] = None, rate_limiter: Optional[RateLimiter] = None):
		self.session = session or requests.Session()
		self.session.headers.update({"User-Agent": DEFAULT_USER_AGENT})
		self.rate_limiter = rate_limiter or RateLimiter(0.7)

	def fetch(self, path: str) -> requests.Response:
		url = path if path.startswith("http") else f"{self.BASE}{path}"
		self.rate_limiter.wait()
		resp = self.session.get(url, timeout=15)
		resp.raise_for_status()
		return resp

	def iter_category_urls(self) -> Iterator[str]:
		"""Yield category page URLs from the homepage categories listing."""
		resp = self.fetch("/")
		soup = BeautifulSoup(resp.text, "lxml")
		seen = set()
		for a in soup.select("a"):
			href = a.get("href") or ""
			if not href.startswith('/'):
				continue
			if 'categorie' in href and href not in seen:
				seen.add(href)
				yield href

	def iter_quiz_urls_from_category(self, category_path: str) -> Iterator[str]:
		"""Follow pagination in a category and yield quiz URLs."""
		page = 1
		while True:
			path = f"{category_path.rstrip('/')}/page/{page}"
			resp = self.fetch(path)
			soup = BeautifulSoup(resp.text, "lxml")
			links = [a.get('href') for a in soup.select('a') if a.get('href') and '/quiz/' in a.get('href')]
			if not links:
				break
			for link in links:
				yield link
			page += 1

	def fetch_quiz(self, quiz_path: str) -> str:
		resp = self.fetch(quiz_path)
		return resp.text

	def guess_today_quiz_url(self) -> Optional[str]:
		"""Heuristic to find today's 'quiz du jour' from homepage (placeholder)."""
		resp = self.fetch('/')
		soup = BeautifulSoup(resp.text, 'lxml')
		# Look for prominent quiz link (hero section) containing 'quiz' keyword
		for sel in ['.featured a', '.hero a', 'article a', 'h2 a']:
			for a in soup.select(sel):
				href = a.get('href') or ''
				text = a.get_text(strip=True).lower()
				if '/quiz/' in href and ('jour' in text or 'quiz' in text):
					return href
		return None

	def get_daily_archive_html(self, year: int, month: int, day: int) -> str:
		path = f"/defi-du-jour/archives/{year:04d}/{month:02d}/{day:02d}/"
		return self.fetch(path).text

	def fetch_daily_archive_player(self, year: int, month: int, day: int, player: str, debug: bool = False, html: Optional[str] = None):
		"""Fetch a daily challenge archive page and extract a player's (rank, score, total, duration_seconds).

		Returns tuple (rank, score, total, duration_seconds) where some values may be None
		if not parsed, or None if the player row cannot be located.
		"""
		if html is None:
			path = f"/defi-du-jour/archives/{year:04d}/{month:02d}/{day:02d}/"
			html = self.fetch(path).text
		soup = BeautifulSoup(html, 'lxml')
		player_norm = player.strip().lower()
		import re
		def norm(s: str) -> str:
			return s.replace('\xa0', ' ').strip()

		# 1. Structured table parsing
		for table in soup.select('table'):
			rows = table.find_all('tr')
			for tr in rows:
				cells = [norm(c.get_text(' ', strip=True)) for c in tr.find_all(['td','th'])]
				if not cells or len(cells) < 2:
					continue
				joined = ' '.join(cells).lower()
				if player_norm not in joined:
					continue
				if debug:
					print(f"[debug] matched row cells: {cells}")
				# Extract fields
				rank = score = total = duration = None
				# Rank: first integer in first cell
				m_rank = re.search(r"\b(\d{1,5})\b", cells[0])
				if m_rank:
					rank = int(m_rank.group(1))
				# Score/total: any cell pattern x / y
				for c in cells:
					m_sc = re.search(r"(\d{1,3})\s*/\s*(\d{1,3})", c)
					if m_sc:
						score = int(m_sc.group(1))
						total = int(m_sc.group(2))
						break
				# Duration: ### s
				for c in cells:
					m_du = re.search(r"(\d{1,5})\s*s", c)
					if m_du:
						duration = int(m_du.group(1))
						break
				if rank is not None or score is not None or duration is not None:
					return (rank, score, total, duration)

		# 2. Fallback: previous heuristic gathering text blocks
		candidates = []
		for tr in soup.select('tr'):
			text = ' '.join(tr.stripped_strings)
			if player_norm in text.lower():
				candidates.append(text)
		for div in soup.select('.score, .result, .classement, li'):
			text = ' '.join(div.stripped_strings)
			if player_norm in text.lower():
				candidates.append(text)
		if debug:
			print(f"[debug] fallback candidates: {candidates}")
		for text in candidates:
			m = re.search(r"^(\d+)\s+.*?\b" + re.escape(player_norm) + r"\b.*?(\d+)\s*/\s*(\d+).*?-\s*(\d+)\s*s", text.lower())
			if m:
				return (int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))
			# Fallback partial extractions
			rank_match = re.search(r"^(\d+)", text)
			score_match = re.search(r"(\d+)\s*/\s*(\d+)", text)
			dur_match = re.search(r"(\d+)\s*s", text)
			if player_norm in text.lower() and (rank_match or score_match or dur_match):
				rank = int(rank_match.group(1)) if rank_match else None
				score = int(score_match.group(1)) if score_match else None
				total = int(score_match.group(2)) if score_match else None
				duration = int(dur_match.group(1)) if dur_match else None
				return (rank, score, total, duration)
		# 3. Liberal plain-text scan across full page
		plain = soup.get_text('\n')
		lines = [norm(line) for line in plain.splitlines() if player_norm in line.lower()]
		if debug and lines:
			print(f"[debug] liberal lines containing player: {lines[:10]}")
		if lines:
			import re as _re
			joined = ' '.join(lines)
			m_rank = _re.search(r"(\d{1,5})\D{0,10}" + player_norm, joined.lower())
			m_score = _re.search(r"(\d{1,3})\s*/\s*(\d{1,3})", joined)
			m_dur = _re.search(r"(\d{1,5})\s*s", joined)
			rank = int(m_rank.group(1)) if m_rank else None
			score = int(m_score.group(1)) if m_score else None
			total = int(m_score.group(2)) if m_score else None
			duration = int(m_dur.group(1)) if m_dur else None
			if any(v is not None for v in (rank, score, duration)):
				return (rank, score, total, duration)
		return None