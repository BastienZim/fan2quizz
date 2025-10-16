# src/scraper.py
import requests
from bs4 import BeautifulSoup
from typing import Iterator, Optional, List, Dict, Any
import os
import json
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

	def discover_login_link(self, debug: bool = False) -> Optional[str]:
		"""Attempt to discover a login/connexion link from homepage.

		Returns the href (absolute path) or None.
		Heuristics: anchor text contains one of ['connexion','login','identifiant','se connecter'].
		"""
		try:
			resp = self.fetch('/')
		except Exception:
			return None
		soup = BeautifulSoup(resp.text, 'lxml')
		candidates = []
		for a in soup.select('a'):
			text = (a.get_text(' ', strip=True) or '').lower()
			if any(k in text for k in ['connexion','login','identifiant','se connecter']):
				href = a.get('href') or ''
				if href:
					candidates.append(href)
		if debug:
			print(f"[debug] discovered login link candidates: {candidates}")
		# Prefer first candidate that is not an in-page anchor
		for c in candidates:
			if c.startswith('#'):
				continue
			return c
		return None

	# --- Session / login helpers ---
	def login(self, username: str, password: str, debug: bool = False) -> bool:
		"""Attempt to authenticate (WordPress heuristic) and store session cookies.

		Steps:
		1. GET /wp-login.php to capture cookies + discover form inputs.
		2. Build payload with discovered hidden fields + provided credentials (log/pwd).
		3. POST to /wp-login.php with Referer.
		4. Check for 'wordpress_logged_in' cookie or redirect.

		Returns True on apparent success; False otherwise.
		"""
		login_path = f"{self.BASE}/wp-login.php"
		# If wp-login.php 404s, attempt discovery
		try:
			self.rate_limiter.wait()
			probe = self.session.get(login_path, timeout=10)
			if probe.status_code == 404:
				alt = self.discover_login_link(debug=debug)
				if alt:
					login_path = alt if alt.startswith('http') else f"{self.BASE}{alt}"
					if debug:
						print(f"[debug] using discovered login path: {login_path}")
		except Exception as e:
			if debug:
				print(f"[debug] initial wp-login probe failed: {e}")
			# continue with default path regardless
		self.rate_limiter.wait()
		try:
			resp_get = self.session.get(login_path, timeout=15)
			resp_get.raise_for_status()
		except Exception as e:
			if debug:
				print(f"[debug] initial GET failed: {e}")
			return False
		soup = BeautifulSoup(resp_get.text, 'lxml')
		form = soup.select_one('form#loginform') or soup.select_one('form')
		payload = {}
		if form:
			for inp in form.select('input'):
				name = inp.get('name')
				if not name:
					continue
				val = inp.get('value', '')
				payload[name] = val
		# Override credential fields (common WP names: log, pwd)
		payload['log'] = username
		payload['pwd'] = password
		# Ensure required fields
		payload.setdefault('rememberme', 'forever')
		payload.setdefault('redirect_to', f"{self.BASE}/defi-du-jour/")
		payload.setdefault('testcookie', '1')
		# Some themes require submit name
		payload.setdefault('wp-submit', 'Log In')
		if debug:
			print(f"[debug] login payload keys: {sorted(payload.keys())}")
		self.rate_limiter.wait()
		try:
			resp_post = self.session.post(login_path, data=payload, headers={'Referer': login_path}, timeout=15, allow_redirects=True)
			ck_names = [c.name for c in self.session.cookies]
			if debug:
				print(f"[debug] cookies after login: {ck_names}")
			if any(n.startswith('wordpress_logged_in') for n in ck_names):
				return True
			# Follow redirect to daily page for heuristic success
			if resp_post.url.endswith('/defi-du-jour/'):
				return True
			# As last resort, GET daily page and see if personalized markers exist
			self.rate_limiter.wait()
			daily_resp = self.session.get(f"{self.BASE}/defi-du-jour/", timeout=15)
			if 'déconnexion' in daily_resp.text.lower() or 'logout' in daily_resp.text.lower():
				return True
			return False
		except Exception as e:
			if debug:
				print(f"[debug] POST failed: {e}")
			return False

	def save_cookies(self, path: str):
		"""Persist cookies to JSON for later reuse."""
		data = {c.name: c.value for c in self.session.cookies}
		with open(path, 'w', encoding='utf-8') as f:
			json.dump(data, f)

	def load_cookies(self, path: str):
		"""Load cookies from JSON file if exists."""
		if not os.path.exists(path):
			return
		with open(path, 'r', encoding='utf-8') as f:
			data = json.load(f)
		for k, v in data.items():
			self.session.cookies.set(k, v)

	def set_cookies_from_header(self, cookie_header: str):
		"""Parse a raw 'Cookie:' header string and set cookies.

		Example:
		  'sessionid=abc123; another=xyz; wordpress_logged_in=...' -> sets each name/value.
		"""
		parts = [p.strip() for p in cookie_header.split(';') if p.strip()]
		for part in parts:
			if '=' in part:
				name, value = part.split('=', 1)
				self.session.cookies.set(name.strip(), value.strip())

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

	def fetch_daily_live_html(self) -> str:
		"""Fetch the live daily challenge page (requires login for personal answers)."""
		return self.fetch("/defi-du-jour/").text

	def parse_daily_live(self, html: str) -> Dict[str, Any]:
		"""Parse the daily live challenge page and extract questions with your chosen & correct answers.

		Heuristics: question blocks with class 'question', '.quiz-question', or list items within an ordered list.
		Choices marked with class hints like 'correct', 'bonne', 'selected', 'chosen', 'user', 'votre'.
		Returns dict: {title, description, questions:[{question_text, choices, correct_index, chosen_index}]}.
		"""
		soup = BeautifulSoup(html, 'lxml')
		title_el = soup.select_one('h1') or soup.title
		title = title_el.get_text(strip=True) if title_el else 'Défi du jour'
		desc_el = soup.select_one('.intro, .description, .quiz-intro')
		description = desc_el.get_text(strip=True) if desc_el else ''
		plain = soup.get_text(' ', strip=True).lower()
		login_required_phrases = [
			'merci de vous identifier',
			'pour jouer le défi du jour',
			'créer un compte',
			'connexion',  # generic
		]
		is_auth = not any(p in plain for p in login_required_phrases)
		q_nodes = soup.select('.question') or soup.select('.quiz-question')
		if not q_nodes:
			q_nodes = list(soup.select('ol li'))
		questions: List[Dict[str, Any]] = []
		for qn in q_nodes:
			q_text_el = qn.select_one('.qtext') or qn.select_one('h2') or qn
			q_text = q_text_el.get_text(separator=' ', strip=True)
			choice_nodes = qn.select('.answer, .choice, li') or qn.select('li')
			choices = [c.get_text(' ', strip=True) for c in choice_nodes]
			correct_index = None
			chosen_index = None
			for i, c in enumerate(choice_nodes):
				classes = ' '.join(c.get('class') or []).lower()
				# Correct answer hints
				if any(h in classes for h in ['correct','bonne','right','reponse-correcte']):
					correct_index = i
				# Chosen answer hints
				if any(h in classes for h in ['selected','chosen','votre','user','moi','answer-user']):
					chosen_index = i
				# Inline icon/text hints
				text_low = c.get_text(' ', strip=True).lower()
				if chosen_index is None and ('(votre' in text_low or 'votre réponse' in text_low):
					chosen_index = i
				if correct_index is None and ('bonne réponse' in text_low or text_low.endswith('(correct)')):
					correct_index = i
			questions.append({
				'question_text': q_text,
				'choices': choices,
				'correct_index': correct_index,
				'chosen_index': chosen_index,
			})
		return {
			'title': title,
			'description': description,
			'questions': questions,
			'auth': is_auth,
			'reason': None if is_auth else 'login_required'
		}

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