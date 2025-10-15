# examples/fetch_all_categories.py
from src.scraper import QuizypediaScraper
from src.parser import parse_quiz
from src.database import QuizDB


s = QuizypediaScraper()
db = QuizDB('db/quizypedia.db')


for cat in s.iter_category_urls():
	for quiz_url in s.iter_quiz_urls_from_category(cat):
		html = s.fetch_quiz(quiz_url)
		data = parse_quiz(html)
		qid = db.insert_quiz(quiz_url, data['title'], data['description'], data['tags'])
		for i, q in enumerate(data['questions']):
			db.insert_question(qid, i, q['question_text'], q['choices'], q['correct_index'])
		print('saved', data['title'])