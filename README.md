<div align="center">

# fan2quizz

Scrape quizzes from [quizypedia.fr](https://www.quizypedia.fr/) and run a friendly **“quiz du jour” leaderboard** with your friends.

</div>

---

## ✨ Features

| Area | What you get |
|------|--------------|
| Crawling | Category traversal + quiz page fetching (rate‑limited) |
| Parsing | Extract title / description / tags / questions / (best‑effort) correct answers |
| Storage | SQLite with normalized tables + FTS5 for search |
| Search | Full‑text search over title, description, tags |
| Daily Quiz | Map a date (YYYY-MM-DD) to a quiz ID |
| Attempts | Record player answer indices; score auto‑computed |
| Leaderboard | Best score per player per day |
| CLI | Unified tool for fetch, search, set daily, attempt, stats, etc. |

---

## 🚀 Installation

### Option A: Using `uv` (recommended for speed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Option B: Standard virtualenv + pip
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The database file (default: `db/quizypedia.db`) is created automatically.

---

## 🏁 Quick Start
```bash
# Fetch up to 10 quizzes
python -m src.cli fetch --limit 10

# List recent quizzes
python -m src.cli list --limit 5

# Choose one and set it as today’s daily quiz
python -m src.cli set-daily --quiz-id 3

# Record an attempt (answers are comma-separated chosen option indices)
python -m src.cli attempt --quiz-id 3 --player alice --answers 0,2,1,3
python -m src.cli attempt --quiz-id 3 --player bob   --answers 0,1,1,3

# Show leaderboard for today
python -m src.cli leaderboard

# Stats overview
python -m src.cli stats
```

---

## 🧪 CLI Command Reference

Global option: `--db <path>` (placed before the subcommand) to override database file.

| Command | Description | Key Options |
|---------|-------------|-------------|
| `fetch` | Crawl categories and quizzes (stores them) | `--limit` max quizzes (approx) |
| `search` | FTS search across quizzes | `--query <text>` |
| `list` | List most recent quizzes | `--limit` |
| `quiz` | Show quiz (metadata + questions) | `--quiz-id` |
| `set-daily` | Assign a quiz to a date (by id or URL) | `--date`, `--quiz-id`, `--url` |
| `leaderboard` | Display leaderboard for date | `--date` (default today) |
| `attempt` | Record a player’s attempt | `--quiz-id` or `--url`, `--player`, `--answers` |
| `stats` | Aggregate counts (quizzes / questions / attempts / daily entries) | (none) |

Examples:
```bash
python -m src.cli search --query "histoire" --db db/quizypedia.db
python -m src.cli quiz --quiz-id 12
python -m src.cli set-daily --url https://www.quizypedia.fr/quiz/some-quiz-slug
python -m src.cli attempt --url https://www.quizypedia.fr/quiz/some-quiz-slug \
	--player charlie --answers 1,0,3,2
```

---

## 🗓 Daily Quiz Workflow
1. Fetch or identify a good quiz (`list`, `search`, or direct URL).
2. Set it: `set-daily --quiz-id 42` (or `--url` if not ingested yet).
3. Players run `attempt` with their answer indices in order of questions.
4. View rankings: `leaderboard` (best attempt per player kept automatically).

Scoring uses stored `correct_index` values if detected; otherwise all answers are treated as incorrect (score 0). The parser is heuristic—improving correctness detection is a good follow‑up task.

---

## 🧩 Data Model Overview

| Table | Purpose | Notable Columns |
|-------|---------|-----------------|
| `quizzes` | Quiz metadata | `url`, `title`, `tags` (comma‑sep) |
| `questions` | Questions for each quiz | `choices` (`||` delimited), `correct_index` |
| `attempts` | Player submissions | `player`, `score`, `total`, `answers` (comma list) |
| `daily_quizzes` | Date → quiz mapping | `date` (PK), `quiz_id` |
| `quizzes_fts` | FTS5 virtual table | title/description/tags |

Schema lives in `src/database.py` (`SCHEMA` constant). Foreign keys and indexes are set up for consistency & performance.

Scoring logic: For each answer index provided, compare against `correct_index` of the corresponding question (ordered by `qindex`). Null `correct_index` values (unknown) never award points.

---

## 🧠 Architecture Highlights
| Layer | File | Responsibility |
|-------|------|----------------|
| Fetching | `src/scraper.py` | HTTP GET + category + quiz URL iteration, basic UA + rate limit |
| Parsing | `src/parser.py` | Extract quiz structure using BeautifulSoup |
| Storage | `src/database.py` | SQLite schema + CRUD + leaderboard queries |
| CLI | `src/cli.py` | Command dispatcher for all operations |
| Utilities | `src/utils.py` | Rate limiting & polite delays |

---

## 🔍 Inspecting Data Manually
```bash
sqlite3 db/quizypedia.db "SELECT COUNT(*) FROM quizzes;"
sqlite3 db/quizypedia.db "SELECT id,title FROM quizzes ORDER BY id DESC LIMIT 5;"
sqlite3 db/quizypedia.db "SELECT * FROM attempts ORDER BY attempted_at DESC LIMIT 5;"
```

Use the `quiz` command for a pretty printed question/choice view instead of raw SQL.

---

## 🛠 Troubleshooting
| Symptom | Cause | Fix |
|---------|-------|-----|
| `sqlite3.OperationalError: unable to open database file` | Parent directory missing | Auto‑fixed (we now create it); delete DB and retry |
| 0 scores always | Parser couldn’t detect correct answers | Improve selector logic in `parser.py` |
| Duplicate quizzes not updating | `INSERT OR IGNORE` used | Add update path (TODO) |
| Slow fetching | Site throttling / network | Increase min delay or parallelize carefully (not yet implemented) |

---

## 🧪 Testing (Planned)
Future test areas:
- Parser robustness on saved HTML fixtures
- Scoring correctness edge cases
- Leaderboard tie handling
- CLI smoke tests (via `subprocess.run`)

---

## 🗺 Roadmap / Ideas
- Auto-detect official daily quiz via homepage heuristic (`guess_today_quiz_url`) integration
- Discord / Slack / Telegram bot for attempts
- Web UI (FastAPI + small frontend) for playing
- Export leaderboard as Markdown / JSON / CSV
- Add `update-answers` to retro-fill correct indices when discovered
- Packaging: add `pyproject.toml` entry points for `fan2quizz` command
- Retry logic & exponential backoff for transient HTTP errors
- Add caching layer (etag / last-modified) to reduce bandwidth

---

## 🤝 Contributing
1. Fork & create a feature branch.
2. Add or update tests (once test suite exists).
3. Run lint & format (TBD config) and ensure no regressions.
4. Open a PR describing rationale + screenshots / examples.

Code style: Keep changes minimal & avoid unrelated mass reformatting.

---

## 📄 License
Personal / educational use; verify legality of scraping in your jurisdiction. (Add an explicit license file if distributing.)

---

## ⚠️ Disclaimer
Website structure may change; selectors are heuristic. Use respectfully (low rate, no aggressive parallelism). Not affiliated with quizypedia.fr.

---

## 🙋 FAQ
**Q: Why are some scores zero?**  
Because the parser couldn’t mark correct answers (HTML lacked a clear indicator). Improve logic in `parser.py`.

**Q: Can I re-use an existing quiz for another day?**  
Yes, just call `set-daily --date YYYY-MM-DD --quiz-id <id>` again; it will overwrite.

**Q: How do I export data?**  
Use `sqlite3` directly or write a small export command (TODO: `export --format json`).

**Q: Are answer indices zero-based?**  
Yes. Provide them in the order the questions appear.

---

Happy quizzing! 🎉
