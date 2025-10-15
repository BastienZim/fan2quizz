<div align="center">

# fan2quizz

Scrape quizzes from **quizypedia.fr** and run a lightweight daily quiz + friend leaderboard.

</div>

---

## Overview
Fan2quizz lets you: fetch quizzes, store them locally (SQLite + FTS5), assign a quiz to a day, record attempts, and view a per‑day leaderboard.

## Core Features (short)
* Rate‑limited scraping (categories & quiz pages)
* Heuristic parsing (title, description, tags, questions, best‑guess correct answers)
* SQLite storage + full‑text search
* Daily quiz mapping (date → quiz id)
* Attempts + automatic scoring
* Leaderboard + basic stats
* Optional standalone daily report script with Slack export

## Install
Using uv (fast) or plain pip.
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh  # (optional)
uv venv .venv && source .venv/bin/activate
uv pip install -r requirements.txt
# or:
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Quick Start
```bash
python -m src.cli fetch --limit 10
python -m src.cli list --limit 5
python -m src.cli set-daily --quiz-id 3
python -m src.cli attempt --quiz-id 3 --player alice --answers 0,2,1,3
python -m src.cli leaderboard
python -m src.cli stats
```

## CLI (essential)
`--db <path>` can precede any subcommand.

| Cmd | Purpose | Common opts |
|-----|---------|-------------|
| fetch | Crawl quizzes | --limit |
| search | FTS search | --query |
| list | Recent quizzes | --limit |
| quiz | Show quiz detail | --quiz-id / --url |
| set-daily | Map quiz to a date | --date / --quiz-id / --url |
| attempt | Record attempt | --quiz-id / --url / --player / --answers |
| leaderboard | Daily leaderboard | --date |
| stats | Summary counts | (none) |

Scoring uses stored `correct_index`; if unknown, answer gives no point.

## Daily Flow
1. Fetch quizzes.
2. Pick one → `set-daily`.
3. Players run `attempt` (answers are zero‑based indices in order).
4. View `leaderboard`.

## Daily Report Script (optional)
`examples/daily_report.py` produces a focused report & Slack table for a date (default yesterday).
Basic usage:
```bash
python examples/daily_report.py --fun
python examples/daily_report.py 2025-10-14 --save-table out/sel.csv
python examples/daily_report.py --clipboard-slack
```
Notable flags: `--no-cache`, `--refresh`, `--emojis`, `--genz`, `--fun`, `--save-table <path>`, `--clipboard`, `--clipboard-slack`, `--slack-print`.
Optional extras: `pip install rich pyperclip wcwidth` for nicer output & clipboard.

## Data (very short)
Tables: quizzes, questions, attempts, daily_quizzes (+ FTS virtual table). Schema lives in `src/database.py`.

## Troubleshooting (quick)
| Issue | Hint |
|-------|------|
| Scores all zero | Parser didn’t find correct answers → enhance selectors |
| DB open error | Ensure `db/` exists (auto‑created). |
| Slow fetch | Increase delay or reduce `--limit`. |

## Roadmap (trimmed)
Bot integration · Web UI · Better answer detection · Export improvements · Packaging entry point · HTTP caching.

## Contributing
Small focused PRs; avoid unrelated reformatting. Add tests when they exist.

## License & Disclaimer
Personal / educational use. Site structure may change; scrape politely. Not affiliated with quizypedia.fr.

## FAQ (mini)
Q: Zero‑based answers? A: Yes.  
Q: Re‑use quiz on another day? A: `set-daily --date YYYY-MM-DD --quiz-id <id>` overwrites.  
Q: Export selected players table? A: Use the daily report script with `--save-table`.

Happy quizzing! 🎉
