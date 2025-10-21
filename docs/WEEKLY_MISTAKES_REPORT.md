# Weekly Mistakes Report

A comprehensive script to generate detailed weekly (or custom period) mistakes reports from Quizypedia archives.

## Overview

This script fetches quiz data from a date range (default: last 7 days), extracts all your mistakes, and generates a detailed markdown report with statistics, daily breakdown, and comprehensive mistake analysis.

## Features

✅ **Flexible Date Ranges**
   - Last 7 days (default)
   - Last 14 days or any custom period
   - Specific date range

✅ **Smart Caching**
   - Downloads each day only once
   - Saves to `data/cache/quiz_html/` for reuse
   - Dramatically faster subsequent runs
   - Reduces load on quizypedia.fr server

✅ **Comprehensive Statistics**
   - Total quizzes completed
   - Overall accuracy rate
   - Average score per quiz
   - Mistakes by category

✅ **Detailed Breakdown**
   - Daily performance table
   - All mistakes with full details
   - Mistakes grouped by category
   - Question hints and all choices

✅ **Auto-Authentication**
   - Uses credentials from `.env` file
   - Supports both email/password and session cookies

✅ **Optional History Update**
   - Can update `mistakes_history.json` with new data

## Prerequisites

Make sure you have a `.env` file in the project root with your Quizypedia credentials:

```env
QUIZY_USER=your.email@example.com
QUIZY_PASS=yourpassword
# OR use a session cookie (faster)
QUIZY_COOKIE=wordpress_logged_in_xxxxx=value; other_cookie=value
```

## Usage

### Basic Usage

```bash
# Generate report for last 7 days (default)
uv run scripts/weekly_mistakes_report.py

# Last 14 days
uv run scripts/weekly_mistakes_report.py --days 14

# Last 30 days
uv run scripts/weekly_mistakes_report.py --days 30
```

### Specific Date Ranges

```bash
# Specific date range
uv run scripts/weekly_mistakes_report.py --start 2025-10-14 --end 2025-10-20

# From a date to yesterday
uv run scripts/weekly_mistakes_report.py --start 2025-10-01

# From 7 days ago to a specific date
uv run scripts/weekly_mistakes_report.py --end 2025-10-20
```

### Advanced Options

```bash
# Custom output filename
uv run scripts/weekly_mistakes_report.py --output my_report.md

# Show progress while fetching
uv run scripts/weekly_mistakes_report.py --verbose

# Update mistakes_history.json with fetched data
uv run scripts/weekly_mistakes_report.py --update-history

# Force fresh fetch (ignore cache)
uv run scripts/weekly_mistakes_report.py --no-cache --verbose

# Combine options
uv run scripts/weekly_mistakes_report.py --days 14 --verbose --update-history --output LAST_TWO_WEEKS.md
```

### Help

```bash
uv run scripts/weekly_mistakes_report.py --help
```

## Output Format

The generated report includes:

### 1. Executive Summary
- Number of quizzes completed
- Total questions and correct answers
- Total mistakes
- Accuracy percentage
- Average score

### 2. Daily Breakdown Table
A table showing for each day:
- Date
- Score (with emoji indicator)
- Number of mistakes
- Time taken

### 3. Mistakes by Category
Top 10 categories where you made the most mistakes

### 4. All Mistakes (Detailed)
Grouped by date, showing for each mistake:
- Question number and category
- Question text
- Hints provided
- All answer choices (marked)
- Your wrong answer
- The correct answer

### 5. Mistakes by Category (Detailed)
All mistakes grouped by category for focused study

## Example Output

```markdown
# 📋 Weekly Mistakes Report
**Period:** 2025-10-14 to 2025-10-20
**Generated:** 2025-10-21 12:43

---

## 📊 Executive Summary

- **Quizzes Completed:** 7
- **Total Questions:** 140
- **Total Correct:** 78
- **Total Mistakes:** 62
- **Accuracy Rate:** 55.7%
- **Average Score:** 11.1/20 per quiz

---

## 📅 Daily Breakdown

| Date | Score | Mistakes | Time |
|------|-------|----------|------|
| 2025-10-14 | ❌ 11/20 | 9 | 245s |
| 2025-10-15 | ❌ 11/20 | 9 | 198s |
| 2025-10-16 | ⚠️ 14/20 | 6 | 223s |
| 2025-10-17 | ❌ 10/20 | 10 | 267s |
...
```

## Use Cases

### Weekly Review
Generate a report every Monday for the previous week:
```bash
uv run scripts/weekly_mistakes_report.py --days 7 --verbose
```

### Study Preparation
Generate a comprehensive report for exam preparation:
```bash
uv run scripts/weekly_mistakes_report.py --days 30 --output STUDY_GUIDE.md
```

### Track Progress
Generate reports for specific periods to track improvement:
```bash
# Week 1
uv run scripts/weekly_mistakes_report.py --start 2025-10-01 --end 2025-10-07 --output week1.md

# Week 2
uv run scripts/weekly_mistakes_report.py --start 2025-10-08 --end 2025-10-14 --output week2.md
```

### Update Historical Data
Fetch and update your mistakes history:
```bash
uv run scripts/weekly_mistakes_report.py --days 14 --update-history --verbose
```

## Performance

- **Smart caching**: Each day downloaded only once, subsequent runs use cache
- First run (no cache): ~1-2 seconds per day fetched
- Subsequent runs (with cache): Nearly instant for cached days
- 7-day report (first time): ~10-15 seconds
- 7-day report (cached): ~2-3 seconds
- 14-day report (first time): ~20-30 seconds
- Cache location: `data/cache/quiz_html/`

### Cache Management

The cache ensures you never download the same day twice:
- Run the script multiple times without worrying about server load
- Update your report with new styling without re-fetching
- Use `--no-cache` flag only when you need fresh data (e.g., if quiz was updated)

## Error Handling

The script handles various scenarios:
- Missing quiz data for specific dates (skips and continues)
- Authentication failures (warns but continues)
- Network errors (reports which dates failed)

If a date fails to fetch, it will be excluded from the report, and you'll see a message indicating which dates were successfully processed.

## Integration with Other Scripts

This script works well with:

- **`show_mistakes_by_date.py`** - For detailed single-day analysis
- **`accumulate_mistakes.py`** - Use `--update-history` to keep your historical data updated
- **`track_mistakes.py`** - For ongoing mistake tracking

## Tips

1. **Regular Weekly Reviews**: Run this every Monday to review the previous week
2. **Use `--verbose`**: See progress for long date ranges
3. **Save Multiple Reports**: Use custom output names to compare different periods
4. **Update History**: Use `--update-history` to maintain a comprehensive mistakes database
5. **Focus on Categories**: Use the category breakdown to identify weak areas

## Troubleshooting

### No data for certain dates

**Cause**: Quiz might not have been completed or data not available

**Solution**: Check individual dates with `show_mistakes_by_date.py`:
```bash
uv run scripts/show_mistakes_by_date.py 2025-10-15
```

### Authentication issues

**Cause**: Invalid or expired credentials

**Solution**: 
1. Check your `.env` file
2. Try using `QUIZY_COOKIE` instead of email/password
3. Log into the website and copy fresh cookies

### Incomplete mistake details

**Cause**: Archive page doesn't include personal answers for old dates

**Solution**: This is expected for historical data. The script shows questions and correct answers, but your personal wrong answers might not be available.

## Related Scripts

- **`show_mistakes_by_date.py`** - View mistakes from a specific day
- **`track_mistakes.py`** - Track mistakes from today's quiz
- **`accumulate_mistakes.py`** - Accumulate mistakes over time
- **`fetch_historical_mistakes.py`** - Fetch historical quiz data

## File Output

Default output file: `WEEKLY_MISTAKES_REPORT.md` (in project root)

You can specify a custom location:
```bash
uv run scripts/weekly_mistakes_report.py --output ~/Documents/my_report.md
```

## Automation

You can automate weekly reports with a cron job:

```bash
# Run every Monday at 8 AM
0 8 * * 1 cd /path/to/fan2quizz && uv run scripts/weekly_mistakes_report.py --verbose --update-history
```

Or create a shell script:

```bash
#!/bin/bash
cd /path/to/fan2quizz
uv run scripts/weekly_mistakes_report.py \
  --days 7 \
  --output "WEEKLY_$(date +%Y%m%d).md" \
  --verbose \
  --update-history
```
