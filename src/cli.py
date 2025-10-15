# src/cli.py
import argparse
from datetime import date
from .scraper import QuizypediaScraper
from .parser import parse_quiz
from .database import QuizDB
from .utils import RateLimiter


def fetch(args):
	db = QuizDB(args.db)
	s = QuizypediaScraper(rate_limiter=RateLimiter(0.9))
	count = 0
	for cat in s.iter_category_urls():
		if args.limit and count >= args.limit:
			break
		for quiz_url in s.iter_quiz_urls_from_category(cat):
			if args.limit and count >= args.limit:
				break
			try:
				html = s.fetch_quiz(quiz_url)
				data = parse_quiz(html)
				qid = db.insert_quiz(quiz_url, data['title'], data['description'], data['tags'])
				for i, q in enumerate(data['questions']):
					db.insert_question(qid, i, q['question_text'], q['choices'], q['correct_index'])
				count += 1
				print(f"Saved {data['title']} ({quiz_url})")
			except Exception as e:
				print("Error fetching", quiz_url, e)


def search(args):
	db = QuizDB(args.db)
	rows = db.search_quizzes(args.query, limit=20)
	for r in rows:
		print(r)


def set_daily(args):
	db = QuizDB(args.db)
	# If quiz id not given but url is, insert/fetch it first
	if args.url and not args.quiz_id:
		from .scraper import QuizypediaScraper
		s = QuizypediaScraper(rate_limiter=RateLimiter(0.8))
		html = s.fetch_quiz(args.url)
		data = parse_quiz(html)
		qid = db.insert_quiz(args.url, data['title'], data['description'], data['tags'])
		for i, q in enumerate(data['questions']):
			db.insert_question(qid, i, q['question_text'], q['choices'], q['correct_index'])
		args.quiz_id = qid
	if not args.quiz_id:
		raise SystemExit("Provide --quiz-id or --url")
	db.set_daily_quiz(args.date, args.quiz_id)
	print(f"Daily quiz for {args.date} set to quiz {args.quiz_id}")


def leaderboard(args):
	d = args.date or date.today().isoformat()
	db = QuizDB(args.db)
	rows = db.leaderboard_for_date(d)
	if not rows:
		print("No attempts yet")
		return
	print(f"Leaderboard for {d}:")
	for rank, (player, score, total) in enumerate(rows, start=1):
		pct = (score / total * 100) if total else 0
		print(f"{rank:2d}. {player:<15} {score}/{total} ({pct:.0f}%)")


def daily_table(args):
	d = args.date or date.today().isoformat()
	db = QuizDB(args.db)
	rows = db.daily_table(d)
	if not rows:
		print("No attempts yet")
		return
	# Determine medals by best_score ordering
	print(f"Daily detailed table for {d}:\n")
	header = f"{'#':>2}  {'Player':<15} {'Score':>7}  {'Dur(s)':>7}  {'Rank':>5}  {'Attempts':>8}"
	print(header)
	print('-' * len(header))
	medals = ['🥇','🥈','🥉']
	for idx, row in enumerate(rows, start=1):
		player, best_score, total, attempts, best_duration, external_rank = row
		score_str = f"{best_score}/{total}" if total else str(best_score)
		dur = '' if best_duration is None or best_duration == 999999 else str(best_duration)
		erank = '' if external_rank is None else str(external_rank)
		medal = medals[idx-1] if idx <= 3 else '  '
		print(f"{idx:>2} {medal} {player:<15} {score_str:>7}  {dur:>7}  {erank:>5}  {attempts:>8}")
	db.close()


def attempt(args):
	db = QuizDB(args.db)
	quiz_id = args.quiz_id
	if args.url and not quiz_id:
		# ensure quiz exists
		from .scraper import QuizypediaScraper
		s = QuizypediaScraper(rate_limiter=RateLimiter(0.8))
		html = s.fetch_quiz(args.url)
		data = parse_quiz(html)
		quiz_id = db.insert_quiz(args.url, data['title'], data['description'], data['tags'])
		for i, q in enumerate(data['questions']):
			db.insert_question(quiz_id, i, q['question_text'], q['choices'], q['correct_index'])
	if not quiz_id:
		raise SystemExit("Need --quiz-id or --url")
	answers = [int(a) for a in args.answers.split(',')] if args.answers else []
	score = db.record_attempt(quiz_id, args.player, answers)
	attempt_id = db.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
	db.update_attempt_meta(attempt_id, args.duration, args.rank)
	print(f"Recorded attempt for {args.player}: {score} points")


def list_quizzes(args):
    db = QuizDB(args.db)
    rows = db.conn.execute(
        "SELECT id, title, url FROM quizzes ORDER BY id DESC LIMIT ?",
        (args.limit,),
    ).fetchall()
    for r in rows:
        print(f"{r[0]:>4} | {r[1]} | {r[2]}")
    db.close()


def show_quiz(args):
    db = QuizDB(args.db)
    q = db.get_quiz(args.quiz_id)
    if not q:
        print("Quiz not found")
        return
    print(f"[{q['id']}] {q['title']}\nURL: {q['url']}\nTags: {', '.join(q['tags'])}\n---")
    for qs in q['questions']:
        print(f"Q{qs['qindex']+1}: {qs['question_text']}")
        for i, choice in enumerate(qs['choices']):
            print(f"  {i}. {choice}")
        print()
    db.close()


def stats(args):
    db = QuizDB(args.db)
    quiz_count = db.conn.execute("SELECT COUNT(*) FROM quizzes").fetchone()[0]
    question_count = db.conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    attempt_count = db.conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]
    daily_count = db.conn.execute("SELECT COUNT(*) FROM daily_quizzes").fetchone()[0]
    print(f"Quizzes: {quiz_count}")
    print(f"Questions: {question_count}")
    print(f"Attempts: {attempt_count}")
    print(f"Daily quiz entries: {daily_count}")
    db.close()


def my_best(args):
	d = args.date or date.today().isoformat()
	db = QuizDB(args.db)
	row = db.best_attempt_for_date_player(d, args.player)
	if not row:
		print(f"No attempt for {args.player} on {d}")
		return
	(aid, score, total, duration, external_rank, answers, attempted_at, quiz_id) = row
	pct = (score / total * 100) if total else 0
	print(f"Best attempt for {args.player} on {d} (quiz {quiz_id}):")
	print(f"  Attempt ID: {aid}")
	print(f"  Score: {score}/{total} ({pct:.0f}%)")
	if duration is not None:
		print(f"  Duration: {duration}s")
	if external_rank is not None:
		print(f"  External rank: {external_rank}")
	print(f"  Answers: {answers}")
	print(f"  Time: {attempted_at}")
	db.close()


def my_attempts(args):
	d = args.date or date.today().isoformat()
	db = QuizDB(args.db)
	rows = db.attempts_for_date_player(d, args.player)
	if not rows:
		print(f"No attempts for {args.player} on {d}")
		return
	print(f"All attempts for {args.player} on {d}:")
	for (aid, score, total, duration, external_rank, answers, attempted_at, quiz_id) in rows:
		pct = (score / total * 100) if total else 0
		extra = []
		if duration is not None:
			extra.append(f"{duration}s")
		if external_rank is not None:
			extra.append(f"rank {external_rank}")
		extra_s = ("; ".join(extra)) if extra else ""
		print(f"  #{aid} quiz {quiz_id} {score}/{total} ({pct:.0f}%) {answers} @ {attempted_at} {extra_s}")
	db.close()


def fetch_daily_score(args):
	d = args.date or date.today().isoformat()
	year, month, day = map(int, d.split('-'))
	s = QuizypediaScraper(rate_limiter=RateLimiter(0.5))
	html = None
	if getattr(args, 'dump_html', None):
		html = s.get_daily_archive_html(year, month, day)
		with open(args.dump_html, 'w', encoding='utf-8') as f:
			f.write(html)
		if args.debug:
			print(f"[debug] wrote HTML to {args.dump_html} ({len(html)} bytes)")
	res = s.fetch_daily_archive_player(year, month, day, args.player, debug=args.debug, html=html)
	if not res:
		print(f"Player {args.player} not found in archive {d}")
		return
	rank, score, total, duration = res
	print(f"Archive result {d} for {args.player}: rank={rank} score={score}/{total} duration={duration}s")
	if args.record:
		db = QuizDB(args.db)
		quiz_id = db.get_daily_quiz(d)
		if not quiz_id:
			print("No daily quiz set for this date; cannot record attempt.")
			return
		# Record attempt without answers (unknown) then update metadata
		aid_score = db.record_attempt(quiz_id, args.player, [])  # answers empty
		attempt_id = db.conn.execute("SELECT last_insert_rowid()\n").fetchone()[0]
		db.update_attempt_meta(attempt_id, duration, rank)
		print(f"Recorded placeholder attempt id {attempt_id} with score={aid_score} (actual {score}/{total} not applied)")
		db.close()


def main():
	p = argparse.ArgumentParser(prog="fan2quizz")
	p.add_argument('--db', default='db/quizypedia.db', help='Path to SQLite database file')
	sub = p.add_subparsers(dest="cmd")

	f = sub.add_parser('fetch', help='crawl categories & quizzes')
	f.add_argument('--limit', type=int, default=50)
	f.set_defaults(func=fetch)

	s = sub.add_parser('search', help='search quizzes via FTS')
	s.add_argument('--query', required=True)
	s.set_defaults(func=search)

	sd = sub.add_parser('set-daily', help='set the daily quiz (by id or url)')
	sd.add_argument('--date', default=date.today().isoformat())
	sd.add_argument('--quiz-id', type=int)
	sd.add_argument('--url')
	sd.set_defaults(func=set_daily)

	lb = sub.add_parser('leaderboard', help='show leaderboard for date')
	lb.add_argument('--date')
	lb.set_defaults(func=leaderboard)

	dt = sub.add_parser('daily-table', help='rich daily leaderboard with duration & rank')
	dt.add_argument('--date')
	dt.set_defaults(func=daily_table)

	at = sub.add_parser('attempt', help='record a manual attempt')
	at.add_argument('--quiz-id', type=int)
	at.add_argument('--url')
	at.add_argument('--player', required=True)
	at.add_argument('--answers', help='comma separated chosen indices e.g. 0,2,1,3')
	at.add_argument('--duration', type=int, help='Time taken in seconds')
	at.add_argument('--rank', type=int, help='External/global rank if known')
	at.set_defaults(func=attempt)

	p_list = sub.add_parser("list", help="List recent quizzes")
	p_list.add_argument("--limit", type=int, default=10)
	p_list.set_defaults(func=list_quizzes)

	p_quiz = sub.add_parser("quiz", help="Show a quiz with questions")
	p_quiz.add_argument("--quiz-id", type=int, required=True)
	p_quiz.set_defaults(func=show_quiz)

	p_stats = sub.add_parser("stats", help="Show aggregate counts")
	p_stats.set_defaults(func=stats)

	mb = sub.add_parser('my-best', help='Show your best attempt for the day')
	mb.add_argument('--player', required=True)
	mb.add_argument('--date')
	mb.set_defaults(func=my_best)

	ma = sub.add_parser('my-attempts', help='List all your attempts for the day')
	ma.add_argument('--player', required=True)
	ma.add_argument('--date')
	ma.set_defaults(func=my_attempts)

	fd = sub.add_parser('fetch-daily-score', help='Fetch daily archive score for a player (does not store answers)')
	fd.add_argument('--date', help='Date YYYY-MM-DD (default today)')
	fd.add_argument('--player', required=True)
	fd.add_argument('--record', action='store_true', help='Also record as an attempt if daily quiz is set')
	fd.add_argument('--debug', action='store_true', help='Debug parsing of archive page')
	fd.add_argument('--dump-html', help='Write raw archive HTML to this file')
	fd.set_defaults(func=fetch_daily_score)

	args = p.parse_args()
	if hasattr(args, 'func'):
		args.func(args)
	else:
		p.print_help()


if __name__ == '__main__':
	main()