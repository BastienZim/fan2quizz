<div align="center">

# fan2quizz

Two essential scripts for tracking **quizypedia.fr** daily quiz results.

</div>

---

## Overview
Simplified toolset for Quizypedia daily challenges:
1. **Daily Report** - Fetch and display leaderboard from public archive
2. **Personal Results Parser** - Parse your quiz answers from saved HTML

## Project Structure

```
fan2quizz/
├── fan2quizz/          # Main Python package
│   ├── cli.py          # Command-line interface
│   ├── database.py     # Database interactions
│   ├── scraper.py      # Web scraping utilities
│   └── utils.py        # Common utilities
├── scripts/            # Standalone scripts
│   ├── daily_report.py           # Fetch daily leaderboard
│   ├── parse_results.py          # Parse personal results
│   ├── track_mistakes.py         # Track mistakes
│   ├── accumulate_mistakes.py    # Accumulate historical mistakes
│   ├── process_quiz.py           # Complete workflow
│   ├── weekly_mistakes_report.py # Generate weekly reports
│   └── ...                       # Other utilities
├── data/               # Data storage (gitignored)
│   ├── cache/          # Cached quiz data
│   ├── db/             # SQLite database
│   ├── figures/        # Generated charts
│   ├── html/           # Saved HTML files
│   └── results/        # JSON results & mistakes
├── output/             # Generated reports (gitignored)
│   ├── reports/        # Markdown reports
│   ├── results/        # CSV exports
│   └── tests/          # Test outputs
├── docs/               # Documentation
└── README.md           # This file
```

## Core Scripts

### 1. Daily Report (`scripts/daily_report.py`)
Fetches public archive data and shows leaderboard with selected players.

**Features:**
* Fetch daily archive from quizypedia.fr
* Cache results locally
* Distribution statistics (scores, durations)
* Selected players leaderboard
* Slack-compatible table export
* Gen-Z style commentary (optional)

### 2. Personal Results Parser (`scripts/parse_results.py`)
Parses your personal quiz results from a saved HTML file.

**Features:**
* Extract your answers vs correct answers
* Score summary with timing
* Question-by-question breakdown
* JSON export for further processing

### 3. Mistakes Tracker (`scripts/track_mistakes.py` & `scripts/accumulate_mistakes.py`)
Track and analyze all your incorrect answers to improve your Quizypedia skills.

**Features:**
* Extract mistakes from quiz results
* Generate comprehensive mistakes log
* Group mistakes by category to identify weak areas
* Track mistakes over time with historical database
* Beautiful Markdown reports for easy review

### 4. Show Mistakes by Date (`scripts/show_mistakes_by_date.py`)
View your mistakes from any specific quiz date by fetching data from the archive.

**Features:**
* Fetch quiz data from any archive date (e.g., `https://www.quizypedia.fr/defi-du-jour/archives/2025/10/20/`)
* Display only mistakes or all questions with `--all` flag
* Automatic authentication using `.env` credentials
* Support for multiple date formats (YYYY-MM-DD, DD/MM/YYYY, etc.)
* Detailed mistake information with hints and all answer choices

### 5. Weekly Mistakes Report (`scripts/weekly_mistakes_report.py`)
Generate comprehensive reports for a week or any custom date range.

**Features:**
* Fetch and analyze multiple days of quiz data automatically
* Generate detailed weekly or monthly reports
* Executive summary with statistics and trends
* Daily breakdown table with scores
* Mistakes grouped by category and date
* Optional update of `mistakes_history.json`
* Flexible date ranges (last 7 days, last 14 days, custom ranges)

## Installation

> **📦 This project uses [UV](https://github.com/astral-sh/uv)** - a blazingly fast Python package installer and resolver.
> 
> **New to UV?** Check out the complete [UV Setup Guide](UV_SETUP.md) for installation and usage details.

**Quick Setup:**

```bash
# 1. Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and setup
git clone https://github.com/BastienZim/fan2quizz.git
cd fan2quizz

# 3. Install package in editable mode with uv
uv pip install -e .

# Or install from requirements.txt
uv pip install -r requirements.txt
```

## Quick Start

### Using Command-Line Tools (after `uv pip install -e .`)
```bash
# Daily report (yesterday by default)
daily-report
daily-report --fun
daily-report 2025-10-15

# Parse personal results
parse-results
```

### Using Scripts Directly
```bash
# Yesterday's report (default)
uv run scripts/daily_report.py

# Specific date
uv run scripts/daily_report.py 2025-10-15

# With fun emoji commentary
uv run scripts/daily_report.py --fun

# Save table to CSV
uv run scripts/daily_report.py --save-table out/leaderboard.csv

# Copy Slack-formatted table to clipboard
uv run scripts/daily_report.py --clipboard-slack
```

### Personal Results Parser
```bash
# Parse saved HTML file (from browser or scraper)
uv run scripts/parse_results.py

# Reads: data/html/defi_du_jour_debug.html
# Outputs: Console report + data/results/defi_du_jour_results.json
```

### Mistakes Tracker
```bash
# EASIEST: Complete workflow (parse + track mistakes)
uv run scripts/process_quiz.py

# OR manually:
# Track mistakes from current quiz session
uv run scripts/track_mistakes.py
# Generates: output/reports/mistakes_log.md, output/reports/mistakes_by_category.md, data/results/mistakes_log.json

# Accumulate mistakes over time (run after each quiz)
uv run scripts/accumulate_mistakes.py
# Updates: data/results/mistakes_history.json
# Regenerates: output/reports/mistakes_log.md (with ALL historical mistakes)
```

**Workflow:**
1. Complete daily quiz on quizypedia.fr
2. Save HTML or run scraper
3. Run `process_quiz.py` (or `parse_results.py` + `accumulate_mistakes.py` manually)
4. Review `output/reports/mistakes_log.md` to learn from errors

**Output Files:**
- `output/reports/mistakes_log.md` - Chronological list of all mistakes
- `output/reports/mistakes_by_category.md` - Mistakes grouped by category (shows weak areas)
- `data/results/mistakes_history.json` - Master database of all mistakes
- `data/results/mistakes_log.json` - Current session mistakes only

### Show Mistakes by Date
```bash
# Show mistakes from a specific date
uv run scripts/show_mistakes_by_date.py 2025-10-20
uv run scripts/show_mistakes_by_date.py 20/10/2025

# Show yesterday's mistakes (default)
uv run scripts/show_mistakes_by_date.py

# Show all questions, not just mistakes
uv run scripts/show_mistakes_by_date.py 2025-10-20 --all

# Save HTML for later analysis
uv run scripts/show_mistakes_by_date.py 2025-10-20 --save archive.html
```

**Use Cases:**
- Review mistakes from any past date
- Check your performance on specific quizzes
- Retrieve quiz data you didn't save at the time

### Weekly Mistakes Report
```bash
# Generate report for last 7 days (default)
uv run scripts/weekly_mistakes_report.py

# Last 14 days
uv run scripts/weekly_mistakes_report.py --days 14

# Specific date range
uv run scripts/weekly_mistakes_report.py --start 2025-10-14 --end 2025-10-20

# Custom output file with progress
uv run scripts/weekly_mistakes_report.py --days 7 --output MY_REPORT.md --verbose

# Update historical database
uv run scripts/weekly_mistakes_report.py --days 14 --update-history --verbose
```

**Output:** `WEEKLY_MISTAKES_REPORT.md` (or custom filename)
Contains:
- Executive summary with statistics
- Daily breakdown table
- Top mistake categories
- Detailed list of all mistakes
- Mistakes grouped by category

**Use Cases:**
- Weekly performance review
- Identify weak knowledge areas
- Track improvement over time
- Generate study guides for specific periods

## Daily Report Options

### Command-Line Flags
```bash
# Cache control
--no-cache           # Skip cache, always fetch fresh
--refresh            # Fetch fresh and update cache

# Output styling  
--emojis             # Add emoji to output
--genz               # Gen-Z style commentary
--fun                # Both emojis + genz (recommended)

# Export options
--save-table PATH    # Save table to CSV
--clipboard          # Copy table to clipboard
--clipboard-slack    # Copy Slack-formatted table
--slack-print        # Print Slack format to console
```

### Optional Dependencies
```bash
uv pip install rich pyperclip wcwidth
```
- **rich**: Better console tables
- **pyperclip**: Clipboard support
- **wcwidth**: Better Unicode width calculation

## Personal Results Parser

### How to Get HTML File

1. **Save from browser**: 
   - Visit quizypedia.fr/defi-du-jour after completing quiz
   - Right-click → "Save as" → `data/html/defi_du_jour_debug.html`

2. **Or use browser DevTools**:
   - Open DevTools (F12)
   - Copy entire HTML
   - Save to `data/html/defi_du_jour_debug.html`

### Output Format

**Console**: Human-readable with emojis
```
✅ Correct answer
❌ Wrong answer
💡 Hints/clues
```

**JSON file**: Structured data for programmatic use
```json
{
  "user_info": {"good_responses": 14, "elapsed_time": 227},
  "questions": [...]
}
```

## Project Structure

```
fan2quizz/
├── parse_defi_results.py       # Personal results parser
├── examples/
│   └── daily_report.py          # Public leaderboard report
├── src/
│   ├── database.py              # SQLite utilities (used by daily_report)
│   ├── scraper.py               # HTTP scraper (used by daily_report)
│   └── utils.py                 # Rate limiter (used by daily_report)
├── cache/                       # Cached archive data
└── db/                          # SQLite database (optional)
```

## License & Disclaimer
Personal / educational use. Site structure may change; scrape politely. Not affiliated with quizypedia.fr.

Happy quizzing! 🎉

### List Yesterday's Answers (quick)
*Note: This script was removed during cleanup. Use the scripts above instead.*
Output sample:
```
Player: BastienZIm
Date: 2025-10-15
Score: 17/20 (duration: 123 s, rank: 42)

Q1. Who painted ...?
	Answer: 2 -> Léonard de Vinci ✅

Q2. Capital of ...?
	Answer: 1 -> Lyon ❌
	Correct: 0 -> Paris
```
If no attempt exists the script tells you how to proceed (set daily quiz + record attempt).

### Live Daily Answers (authenticated)
To see your own chosen answers and the correct ones directly from the site (without first recording them manually):
1. Login (heuristic WordPress endpoints) to persist cookies:
```bash
uv run -m fan2quizz.cli login --email you@example.com --password 'yourpass' --session .quizypedia_session.json
```
2. Fetch live page & show answers:
```bash
uv run -m fan2quizz.cli daily-live --session .quizypedia_session.json
```
Add `--json` for structured output. The parser is heuristic; if classes or labels change, update `parse_daily_live` in `fan2quizz/scraper.py`.

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

## Selenium Daily Challenge Scraper (optional)
If you prefer a browser-rendered approach (e.g. dynamic content, future JS additions) you can use `scrape_quizypedia_defi_du_jour.py` which logs in and extracts your personal quiz results from the daily challenge page.

### Setup
1. Ensure dependencies installed (selenium, webdriver-manager, python-dotenv, beautifulsoup4, lxml).
2. Create a `.env` file (do not commit) with:
```
QUIZY_USER=your_username
QUIZY_PASS=your_password
QUIZY_COOKIE=sessionid=xxx; csrftoken=yyy  # (optional, for faster auth)
```
3. Run the scraper:
```bash
uv run scrape_quizypedia_defi_du_jour.py
```

### Features
The scraper now extracts:
- **Your personal answers** (which choices you selected)
- **Correct answers** (the right choices marked by the site)
- **Question text and hints** (descriptions, images, etc.)
- **Theme information** for each question
- **Success ratios** and statistics

Output example:
```json
{
  "title": "Quizypedia",
  "bullets_preview": [],
  "cta": "https://www.quizypedia.fr/defi-du-jour/",
  "archive_links_sample": [...],
  "questions": [
    {
      "question_text": "Quelle pathologie associe-t-on à la description suivante ?",
      "choices": ["Scarlatine", "Lèpre", "Mélanome", "Psoriasis"],
      "correct_index": 3,
      "chosen_index": 3
    }
  ],
  "auth": true
}
```

### Parsing Your Results
After running the scraper, the HTML is saved to `data/html/defi_du_jour_debug.html`. Use the parser to get a formatted report:

```bash
uv run parse_defi_results.py
```

This produces:
- **Detailed results** for each question (your answer vs correct answer)
- **Score summary** (e.g., 14/20 correct, 227 seconds)
- **JSON export** to `data/results/defi_du_jour_results.json` for further processing

Example output:
```
================================================================================
DÉFI DU JOUR - Results
================================================================================

Correct Answers: 14/20
Time Elapsed: 227 seconds

Question 1: Pathologies et lésions de la peau (2)
❓ Quelle pathologie associe-t-on à la description suivante ?
   💡 Description: Maladie inflammatoire de la peau...
   
   Choices:
   0. Scarlatine
   1. Lèpre
   2. Mélanome
   3. Psoriasis ✓ CORRECT (YOUR ANSWER)

   ✅ You got this one right!
```

### Configuration
- **Headless mode**: Set `headless=False` in the `Config` dataclass (line 52) to see the browser.
- **Cookies**: Stored in `quizypedia_cookies.json` for faster subsequent runs.
- **Cookie header**: Add `QUIZY_COOKIE` to `.env` to inject raw session cookies (faster than login).

### Quick Workflow
Use the provided shell script to scrape and parse in one go:
```bash
./examples/scrape_and_parse_daily.sh
```
This will scrape your results, parse them, display a formatted report, and archive the JSON data in `out/defi_results/`.

### Troubleshooting
- If login fails, check credentials in `.env`
- If questions aren't parsed, the site HTML structure may have changed (update `extract_defi_du_jour` in the script)
- For debugging, check `data/html/defi_du_jour_debug.html` to see what the scraper captured

