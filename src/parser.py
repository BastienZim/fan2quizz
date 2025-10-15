from bs4 import BeautifulSoup
from typing import Dict, Any


def parse_quiz(html: str) -> Dict[str, Any]:
	"""Parse quiz HTML and extract metadata & questions."""
	soup = BeautifulSoup(html, "lxml")
	title = (soup.select_one("h1") or soup.title).get_text(strip=True)
	desc_el = soup.select_one(".intro, .description, .quiz-intro")
	description = desc_el.get_text(strip=True) if desc_el else ""
	tags = [t.get_text(strip=True) for t in soup.select('.tags a')]

	questions = []
	q_nodes = soup.select('.question') or soup.select('.quiz-question')
	if not q_nodes:
		q_nodes = list(soup.select('ol li'))

	for qn in q_nodes:
		q_text = qn.select_one('.qtext') or qn.select_one('h2') or qn
		q_text_str = q_text.get_text(separator=' ', strip=True)
		choices = [c.get_text(strip=True) for c in qn.select('.answer, .choice, li')]
		correct_index = None
		for i, c in enumerate(qn.select('.answer, .choice, li')):
			classes = c.get('class') or []
			if 'correct' in classes or 'reponse' in classes:
				correct_index = i
		questions.append({
			'question_text': q_text_str,
			'choices': choices,
			'correct_index': correct_index,
			'explanation': None,
		})

	return {
		'title': title,
		'description': description,
		'tags': tags,
		'questions': questions,
	}