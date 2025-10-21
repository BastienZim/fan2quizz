# Complete Workflow Guide

Comprehensive quiz improvement workflow using all tracking scripts together.

## Scripts Overview

| Script | Purpose |
|--------|---------|
| `show_mistakes_by_date.py` | View mistakes from single date |
| `weekly_mistakes_report.py` | Generate multi-day reports |
| `track_mistakes.py` | Track today's mistakes |
| `accumulate_mistakes.py` | Build historical database |
| `process_quiz.py` | Automated daily workflow |

## Daily Workflow

### Automated (Recommended)
```bash
uv run scripts/process_quiz.py
```

Automatically:
1. Parses results from `defi_du_jour_debug.html`
2. Extracts and saves mistakes
3. Updates `mistakes_history.json`
4. Regenerates all reports

### Manual Steps
```bash
uv run scripts/parse_results.py              # Parse results
uv run scripts/accumulate_mistakes.py        # Update history
```

## Weekly Review

**Generate weekly report:**
```bash
# Every Monday
uv run scripts/weekly_mistakes_report.py --days 7 --verbose --output WEEK_$(date +%Y%m%d).md
```

**Review specific dates:**
```bash
uv run scripts/show_mistakes_by_date.py 2025-10-15
```

## Monthly Review

**Generate monthly report:**
```bash
uv run scripts/weekly_mistakes_report.py --days 30 --output MONTH_$(date +%Y%m).md --update-history
```

**Compare weekly performance:**
```bash
# Generate separate reports for each week
uv run scripts/weekly_mistakes_report.py --start 2025-10-01 --end 2025-10-07 --output week1.md
uv run scripts/weekly_mistakes_report.py --start 2025-10-08 --end 2025-10-14 --output week2.md
uv run scripts/weekly_mistakes_report.py --start 2025-10-15 --end 2025-10-21 --output week3.md
uv run scripts/weekly_mistakes_report.py --start 2025-10-22 --end 2025-10-31 --output week4.md
```

## Study/Preparation

**Identify weak categories:**
```bash
uv run scripts/weekly_mistakes_report.py --days 30 --output STUDY_GUIDE.md
```

Shows:
- Categories with most mistakes
- Specific questions to review
- Error patterns

**Focus on specific dates:**
```bash
uv run scripts/show_mistakes_by_date.py 2025-10-14 --all > day1.txt
uv run scripts/show_mistakes_by_date.py 2025-10-15 --all > day2.txt
uv run scripts/show_mistakes_by_date.py 2025-10-16 --all > day3.txt
```

## Catch-Up Workflow

Fill historical data gaps:

**Fetch multiple days:**
```bash
# Last 14 days
uv run scripts/weekly_mistakes_report.py --days 14 --update-history --verbose

# Specific date range
uv run scripts/weekly_mistakes_report.py --start 2025-10-01 --end 2025-10-20 --update-history --verbose
```

**Check what you have:**
```bash
uv run scripts/manage_archive.py --days 30
```

**Download missing data:**
```bash
uv run scripts/manage_archive.py --days 14 --download
```

## Analysis Workflow

**Performance insights:**
```bash
uv run scripts/inspect_history.py --all           # Comprehensive view
uv run scripts/inspect_history.py --detailed      # Stats + trends
uv run scripts/inspect_history.py --mistakes      # By category
```

**Generate visualizations:**
```bash
uv run scripts/plot_evolution.py --both           # All plots
uv run scripts/player_evolution.py --export       # CSV data
```

## Study Guide Generation

**All mistakes:**
```bash
uv run scripts/generate_failed_questions.py
```

**By category:**
```bash
uv run scripts/generate_failed_questions.py --order category
```

**By domain:**
```bash
uv run scripts/generate_failed_questions.py --domain Arts
uv run scripts/generate_failed_questions.py --domain Histoire
```

**Filtered:**
```bash
uv run scripts/generate_failed_questions.py --filter "2025-10-17"
uv run scripts/generate_failed_questions.py --filter "Shakespeare"
```

## Complete Example Routine

**Daily (after quiz):**
```bash
uv run scripts/complete_workflow.py
uv run scripts/plot_evolution.py --both
```

**Weekly (Monday morning):**
```bash
uv run scripts/weekly_mistakes_report.py --days 7 --verbose
uv run scripts/generate_failed_questions.py --order category --output study.md
```

**Monthly (end of month):**
```bash
uv run scripts/weekly_mistakes_report.py --days 30 --update-history
uv run scripts/inspect_history.py --all
uv run scripts/player_evolution.py --export
```

## Tips

- Run daily workflow immediately after quiz for accurate tracking
- Use `--verbose` to see progress
- Generate study guides weekly to identify patterns
- Check `manage_archive.py` monthly for data gaps
- Export CSV data for external analysis
