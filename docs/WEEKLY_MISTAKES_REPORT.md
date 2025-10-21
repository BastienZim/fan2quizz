# Weekly Mistakes Report

Generate comprehensive reports for any date range with statistics and mistake analysis.

## Overview

Fetches quiz data from multiple dates, extracts mistakes, and generates detailed markdown report with statistics, daily breakdown, and comprehensive analysis.

## Features

- Flexible date ranges (last 7/14/30 days or custom)
- Smart caching (downloads once, reuses forever)
- Comprehensive statistics and accuracy rates
- Daily performance table
- Mistakes grouped by category
- Detailed mistake listings with hints and choices
- Auto-authentication via `.env`
- Optional history update

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
# Last 7 days (default)
uv run scripts/weekly_mistakes_report.py

# Last 14 days
uv run scripts/weekly_mistakes_report.py --days 14

# Last 30 days
uv run scripts/weekly_mistakes_report.py --days 30
```

**Date ranges:**
```bash
# Specific range
uv run scripts/weekly_mistakes_report.py --start 2025-10-14 --end 2025-10-20

# From date to yesterday
uv run scripts/weekly_mistakes_report.py --start 2025-10-01

# Up to specific date
uv run scripts/weekly_mistakes_report.py --end 2025-10-20
```

**Options:**
```bash
# Custom output file
uv run scripts/weekly_mistakes_report.py --output my_report.md

# Show progress
uv run scripts/weekly_mistakes_report.py --verbose

# Update mistakes_history.json
uv run scripts/weekly_mistakes_report.py --update-history

# Force fresh fetch
uv run scripts/weekly_mistakes_report.py --no-cache --verbose

# Combine options
uv run scripts/weekly_mistakes_report.py --days 14 --verbose --update-history --output LAST_TWO_WEEKS.md
```

## Report Contents

**Executive Summary:**
- Total quizzes completed
- Overall accuracy rate
- Average score per quiz
- Total mistakes made

**Daily Breakdown Table:**
- Date, Score, Mistakes, Time for each day

**Mistakes by Category:**
- Grouped by topic/theme
- Count per category

**Detailed Listings:**
- All questions you got wrong
- Question text, hints, all choices
- Your answer and correct answer
- Learning notes

## Performance

| Days | First Run | Cached Run | Speedup |
|------|-----------|------------|---------|
| 7    | 10-15s    | 2-3s       | 5x      |
| 14   | 20-30s    | 3-4s       | 7x      |
| 30   | 45-60s    | 5-7s       | 9x      |

## Caching

- Automatically caches HTML files in `data/cache/quiz_html/`
- First run downloads from server
- Subsequent runs load instantly from cache
- Use `--no-cache` to force fresh fetch
- Verbose mode shows `(cached)` indicator

## Output Location

Default: `output/reports/WEEKLY_MISTAKES_REPORT.md`

## Tips

- Run with `--verbose` to see progress
- Use `--update-history` to sync with your mistake log
- Generate weekly on Monday for last 7 days
- Generate monthly at month-end for full period
- Cached data makes regenerating with different options instant

## See Also

- [Show Mistakes by Date](SHOW_MISTAKES_BY_DATE.md) - Single day view
- [Caching System](CACHING_SYSTEM.md) - How caching works
- [Complete Workflow](COMPLETE_WORKFLOW.md) - Usage patterns
