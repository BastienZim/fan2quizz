# New Scripts Summary

Two powerful scripts for working with Quizypedia archives.

## 1. show_mistakes_by_date.py

**Purpose:** Display mistakes from any specific quiz date.

**Key features:**
- Fetch quiz data from archive URLs
- Show only mistakes by default (`--all` for everything)
- Multiple date formats supported
- Automatic authentication via `.env`
- Smart caching for instant subsequent runs
- Detailed info: hints, all choices, your answer, correct answer
- Optional HTML save

**Usage:**
```bash
# Show mistakes from specific date
uv run scripts/show_mistakes_by_date.py 2025-10-20

# Show yesterday's mistakes
uv run scripts/show_mistakes_by_date.py

# Show all questions (not just mistakes)
uv run scripts/show_mistakes_by_date.py 2025-10-20 --all

# Force fresh fetch
uv run scripts/show_mistakes_by_date.py 2025-10-20 --no-cache
```

## 2. weekly_mistakes_report.py

**Purpose:** Generate comprehensive reports for any date range.

**Key features:**
- Fetch multiple days automatically (7, 14, 30 days or custom)
- Executive summary with statistics and accuracy
- Daily breakdown table
- Mistakes grouped by category
- Detailed mistake listings
- Optional update of `mistakes_history.json`
- Progress display with `--verbose`
- Smart caching

**Usage:**
```bash
# Last 7 days (default)
uv run scripts/weekly_mistakes_report.py

# Last 14 days
uv run scripts/weekly_mistakes_report.py --days 14

# Specific range
uv run scripts/weekly_mistakes_report.py --start 2025-10-14 --end 2025-10-20

# With progress and history update
uv run scripts/weekly_mistakes_report.py --days 7 --verbose --update-history
```

## How They Work

**Archive integration:**
1. Connect to Quizypedia with your credentials
2. Fetch archive pages (like clicking "Afficher les questions et les réponses")
3. Extract `DC_DATA` and `DC_USER` JavaScript variables
4. Parse quiz data and identify mistakes
5. Generate formatted reports

**With existing scripts:**

Daily workflow (today's quiz):
```bash
uv run scripts/fetch_today_quiz.py      # Fetch today
uv run scripts/parse_results.py          # Parse
uv run scripts/accumulate_mistakes.py    # Add to history
```

Historical review (past quizzes):
```bash
uv run scripts/show_mistakes_by_date.py 2025-10-15    # Single day
uv run scripts/weekly_mistakes_report.py --days 7      # Multiple days
```

## Key Benefits

**Smart caching:**
- Downloads each day only once
- Saves to `data/cache/quiz_html/`
- 5-7x faster subsequent runs
- Server-friendly

**Flexible:**
- Any date or date range
- Filter and order options
- Multiple output formats
- Works with existing workflow

**Comprehensive:**
- Full mistake details
- Statistics and trends
- Category grouping
- Study-ready format

## See Also

- [Show Mistakes by Date](SHOW_MISTAKES_BY_DATE.md) - Detailed usage
- [Weekly Mistakes Report](WEEKLY_MISTAKES_REPORT.md) - Report details
- [Caching System](CACHING_SYSTEM.md) - How caching works
- [Complete Workflow](COMPLETE_WORKFLOW.md) - Usage patterns
