# Show Mistakes by Date

Display your personal mistakes from a specific day's quiz.

## Overview

Fetches archive page for a specific date, extracts quiz data with your answers, and displays only questions you got wrong.

## Features

- Fetch quiz data from any archive date
- Display only mistakes (or all questions with `--all`)
- Automatic authentication via `.env`
- Smart caching (downloads once, saves locally)
- Detailed information: question, hints, all choices, your answer, correct answer
- Optional HTML save

## Prerequisites

`.env` file with credentials:
```env
QUIZY_USER=your.email@example.com
QUIZY_PASS=yourpassword
# OR session cookie (faster)
QUIZY_COOKIE=wordpress_logged_in_xxxxx=value
```

## Usage

**Basic:**
```bash
# Specific date
uv run scripts/show_mistakes_by_date.py 2025-10-20

# Alternative formats
uv run scripts/show_mistakes_by_date.py 2025/10/20
uv run scripts/show_mistakes_by_date.py 20/10/2025

# Yesterday (default)
uv run scripts/show_mistakes_by_date.py
```

**Options:**
```bash
# Show all questions
uv run scripts/show_mistakes_by_date.py 2025-10-20 --all

# Skip authentication
uv run scripts/show_mistakes_by_date.py 2025-10-20 --no-auth

# Save HTML
uv run scripts/show_mistakes_by_date.py 2025-10-20 --save archive.html

# Force fresh fetch
uv run scripts/show_mistakes_by_date.py 2025-10-20 --no-cache

# Help
uv run scripts/show_mistakes_by_date.py --help
```

## Output Format

```
📅 Fetching quiz for 2025-10-20...
📂 Loaded from cache (444829 bytes)

================================================================================
DÉFI DU JOUR - Your Mistakes
================================================================================

📊 Score: 10/20
❌ Mistakes: 10
⏱️  Time: 245 seconds

================================================================================
MISTAKES ONLY (10 mistakes):
================================================================================

────────────────────────────────────────────────────────────────────────────────
❌ Question 1: Category Name
────────────────────────────────────────────────────────────────────────────────
❓ Question text here
   💡 Hint: hint text

   A) Choice 1
   B) Choice 2
   C) Choice 3 ❌ (Your answer)
   D) Choice 4 ✓ (Correct answer)

💡 Learning: Additional information
```

## Caching

- First run downloads from server (~1-2s)
- Subsequent runs load from cache (<0.1s)
- Cache saved to `data/cache/quiz_html/`
- Use `--no-cache` to force fresh fetch

## See Also

- [Weekly Mistakes Report](WEEKLY_MISTAKES_REPORT.md) - Multi-day reports
- [Caching System](CACHING_SYSTEM.md) - How caching works
