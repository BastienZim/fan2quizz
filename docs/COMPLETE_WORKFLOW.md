# Complete Workflow Guide

This guide shows how to use all the mistake tracking scripts together for a comprehensive quiz improvement workflow.

## Overview of Scripts

1. **`show_mistakes_by_date.py`** - View mistakes from any single date
2. **`weekly_mistakes_report.py`** - Generate reports for multiple days
3. **`track_mistakes.py`** - Track mistakes from today's quiz
4. **`accumulate_mistakes.py`** - Build historical mistakes database
5. **`process_quiz.py`** - Automated daily workflow

## Daily Workflow (After Completing Today's Quiz)

### Option 1: Automated (Recommended)
```bash
# Complete workflow in one command
uv run scripts/process_quiz.py
```

This will:
1. Parse your results from `defi_du_jour_debug.html`
2. Extract and save mistakes
3. Update `mistakes_history.json`
4. Regenerate all reports

### Option 2: Manual Steps
```bash
# Step 1: Parse today's results
uv run scripts/parse_results.py

# Step 2: Accumulate mistakes in history
uv run scripts/accumulate_mistakes.py
```

## Weekly Review Workflow

### Generate Weekly Report
```bash
# Every Monday, generate last week's report
uv run scripts/weekly_mistakes_report.py --days 7 --verbose --output WEEK_$(date +%Y%m%d).md
```

### Review Specific Past Dates
```bash
# Check a specific day you're curious about
uv run scripts/show_mistakes_by_date.py 2025-10-15
```

## Monthly Review Workflow

### Generate Monthly Report
```bash
# At the end of each month
uv run scripts/weekly_mistakes_report.py --days 30 --output MONTH_$(date +%Y%m).md --update-history
```

### Compare Performance
```bash
# Generate separate reports for each week
uv run scripts/weekly_mistakes_report.py --start 2025-10-01 --end 2025-10-07 --output week1.md
uv run scripts/weekly_mistakes_report.py --start 2025-10-08 --end 2025-10-14 --output week2.md
uv run scripts/weekly_mistakes_report.py --start 2025-10-15 --end 2025-10-21 --output week3.md
uv run scripts/weekly_mistakes_report.py --start 2025-10-22 --end 2025-10-31 --output week4.md
```

## Study/Preparation Workflow

### Identify Weak Categories
```bash
# Generate report for study period
uv run scripts/weekly_mistakes_report.py --days 30 --output STUDY_GUIDE.md
```

The report will show:
- Categories where you make the most mistakes
- Specific questions to review
- Patterns in your errors

### Focus on Specific Dates
```bash
# Review each day individually
uv run scripts/show_mistakes_by_date.py 2025-10-14 --all > day1.txt
uv run scripts/show_mistakes_by_date.py 2025-10-15 --all > day2.txt
uv run scripts/show_mistakes_by_date.py 2025-10-16 --all > day3.txt
```

## Catch-Up Workflow (Filling Historical Data)

If you've been doing quizzes but not tracking mistakes:

### Fetch Multiple Days at Once
```bash
# Fetch and analyze last 14 days
uv run scripts/weekly_mistakes_report.py --days 14 --update-history --verbose

# Or specific date range
uv run scripts/weekly_mistakes_report.py --start 2025-10-01 --end 2025-10-20 --update-history --verbose
```

### Review Individual Days if Needed
```bash
# Check specific days that had issues
uv run scripts/show_mistakes_by_date.py 2025-10-15 --save oct15.html
```

## Analysis Workflow

### Weekly Analysis
```bash
# Every Sunday evening or Monday morning
cd ~/fan2quizz

# Generate weekly report
uv run scripts/weekly_mistakes_report.py --verbose

# Open and review
cat WEEKLY_MISTAKES_REPORT.md
```

### Trend Analysis
```bash
# Compare different weeks
uv run scripts/weekly_mistakes_report.py --start 2025-10-01 --end 2025-10-07 --output week1.md
uv run scripts/weekly_mistakes_report.py --start 2025-10-08 --end 2025-10-14 --output week2.md

# Manually compare statistics in each file
```

## Automation Examples

### Weekly Report Automation (Linux/Mac)

Create `~/bin/weekly_quiz_report.sh`:
```bash
#!/bin/bash
cd ~/fan2quizz
uv run scripts/weekly_mistakes_report.py \
  --days 7 \
  --output "reports/WEEK_$(date +%Y%m%d).md" \
  --verbose \
  --update-history
```

Make it executable and add to cron:
```bash
chmod +x ~/bin/weekly_quiz_report.sh

# Add to crontab (run every Monday at 8 AM)
crontab -e
# Add line:
0 8 * * 1 /home/yourusername/bin/weekly_quiz_report.sh
```

### Daily Accumulation (After Manual Quiz)

Create `~/bin/daily_quiz_process.sh`:
```bash
#!/bin/bash
cd ~/fan2quizz

# Check if today's HTML exists
if [ -f "defi_du_jour_debug.html" ]; then
    echo "Processing today's quiz..."
    uv run scripts/process_quiz.py
    echo "Done! Check mistakes_log.md"
else
    echo "No quiz HTML found. Run fetch_today_quiz.py first."
fi
```

## File Organization

Suggested directory structure:
```
fan2quizz/
├── defi_du_jour_debug.html        # Today's quiz HTML
├── defi_du_jour_results.json      # Today's parsed results
├── mistakes_history.json          # All historical mistakes
├── mistakes_log.md                # All mistakes (readable)
├── mistakes_by_category.md        # Mistakes by category
├── WEEKLY_MISTAKES_REPORT.md      # Latest weekly report
└── reports/                       # Archive of reports
    ├── WEEK_20251021.md
    ├── WEEK_20251014.md
    ├── MONTH_202510.md
    └── ...
```

## Common Scenarios

### Scenario 1: Missed Several Days
```bash
# Catch up on last 7 days
uv run scripts/weekly_mistakes_report.py --days 7 --update-history --verbose
```

### Scenario 2: Want to Review Last Week's Performance
```bash
# Generate report for specific week
uv run scripts/weekly_mistakes_report.py --start 2025-10-14 --end 2025-10-20 --verbose
```

### Scenario 3: Studying for a Test on Specific Categories
```bash
# Generate comprehensive report
uv run scripts/weekly_mistakes_report.py --days 30 --output STUDY.md

# Look at "Mistakes by Category" section to focus your study
```

### Scenario 4: Check Today's Performance Compared to Specific Past Day
```bash
# Today's mistakes
uv run scripts/show_mistakes_by_date.py  # defaults to yesterday

# Compare with a past date
uv run scripts/show_mistakes_by_date.py 2025-10-15
```

### Scenario 5: Building Complete Historical Database
```bash
# Fetch all data from a start date to now
uv run scripts/weekly_mistakes_report.py \
  --start 2025-10-01 \
  --end $(date -d "yesterday" +%Y-%m-%d) \
  --update-history \
  --verbose \
  --output COMPLETE_HISTORY.md
```

## Tips for Maximum Benefit

1. **Daily Habit**: Run `process_quiz.py` right after completing each quiz
2. **Weekly Review**: Generate and review weekly reports every Monday
3. **Focus Study**: Use category breakdowns to identify and improve weak areas
4. **Track Progress**: Save weekly reports with dates to compare over time
5. **Update History**: Use `--update-history` when catching up on missed days

## Troubleshooting Workflows

### Can't Find Mistakes from a Specific Date
```bash
# Try fetching that date directly
uv run scripts/show_mistakes_by_date.py 2025-10-15

# If it fails, check if you were logged in that day
# Archives only show your personal answers if you completed the quiz
```

### Missing Historical Data
```bash
# Rebuild history from scratch
uv run scripts/weekly_mistakes_report.py \
  --start 2025-10-01 \
  --end 2025-10-20 \
  --update-history \
  --verbose
```

### Want Fresh Data (Ignore Cache)
```bash
# The scripts automatically fetch fresh data from archives
# No cache bypass needed - they always fetch from the server
```

## Integration with Other Tools

### Export to Study Apps
```bash
# Generate JSON data for custom processing
uv run scripts/weekly_mistakes_report.py --days 14 --update-history

# mistakes_history.json can be processed by other tools
python my_custom_analysis.py mistakes_history.json
```

### Share Reports
```bash
# Generate a clean report to share
uv run scripts/weekly_mistakes_report.py --days 7 --output SHARED_REPORT.md

# Convert to PDF (requires pandoc)
pandoc SHARED_REPORT.md -o SHARED_REPORT.pdf
```

## Quick Reference Commands

| Task | Command |
|------|---------|
| Today's mistakes | `uv run scripts/process_quiz.py` |
| Yesterday's mistakes | `uv run scripts/show_mistakes_by_date.py` |
| Last 7 days report | `uv run scripts/weekly_mistakes_report.py` |
| Last 14 days report | `uv run scripts/weekly_mistakes_report.py --days 14` |
| Specific date | `uv run scripts/show_mistakes_by_date.py 2025-10-20` |
| Specific range | `uv run scripts/weekly_mistakes_report.py --start 2025-10-14 --end 2025-10-20` |
| Update history | `uv run scripts/weekly_mistakes_report.py --days 14 --update-history` |
| All questions (not just mistakes) | `uv run scripts/show_mistakes_by_date.py 2025-10-20 --all` |
| Verbose output | Add `--verbose` to any command |

## Next Steps

1. Set up your `.env` file with credentials
2. Run your first weekly report
3. Set up weekly automation (optional)
4. Start daily habit of running `process_quiz.py`
5. Review reports regularly to track improvement

Happy learning! 🎓
