# Fan2Quizz Documentation

Track, analyze, and visualize your daily Quizypedia quiz performance.

## 📚 Quick Navigation

**Daily Use:** [Workflow](#daily-workflow) | [Historical Data](#archive-management)  
**Analysis:** [Mistakes](#mistake-tracking) | [Reports](#reports) | [Visualizations](#visualizations)  
**Reference:** [Scripts](#script-reference) | [Configuration](#configuration)

---

## Quick Start

**Prerequisites:**
- Python 3.13+ with uv
- `.env` file with credentials:
  ```env
  QUIZY_USER=your_username
  QUIZY_PASS=your_password
  QUIZY_COOKIE=sessionid=your_session_cookie
  ```

**Install:**
```bash
uv sync
```

---

## Daily Workflow

**Automated (Recommended):**
```bash
uv run scripts/complete_workflow.py
```

Fetches quiz, parses results, updates history, generates reports.

**Manual (if needed):**
1. Save quiz results page as `defi_du_jour_debug.html`
2. Run: `uv run scripts/complete_workflow.py --skip-fetch`

**Individual Commands:**
```bash
uv run scripts/fetch_today_quiz.py        # Fetch only
uv run scripts/parse_results.py           # Parse only
uv run scripts/accumulate_mistakes.py     # Update history
```

---

## Archive Management

**Check available data:**
```bash
uv run scripts/manage_archive.py                        # Last 30 days
uv run scripts/manage_archive.py --days 14              # Last 14 days
uv run scripts/manage_archive.py --from 2025-10-01     # Custom range
```

**Download missing data:**
```bash
uv run scripts/manage_archive.py --days 14 --download
```

Shows available dates with scores
- Missing dates in range
- Option to download missing data
- Progress during download

### Fetch Historical Mistakes

Retroactively check quiz data from past dates:

```bash
# Check what dates already have mistakes logged
uv run scripts/fetch_historical_mistakes.py --check



---

## Mistake Tracking

**View past mistakes:**
```bash
uv run scripts/show_mistakes_by_date.py 2025-10-20     # Specific date
uv run scripts/show_mistakes_by_date.py --all          # All questions
```

**Generate reports:**
```bash
uv run scripts/weekly_mistakes_report.py              # Last 7 days
uv run scripts/weekly_mistakes_report.py --days 14    # Last 14 days
uv run scripts/weekly_mistakes_report.py --start 2025-10-01 --end 2025-10-20
```

**Fetch historical data:**
```bash
uv run scripts/fetch_historical_mistakes.py --date 2025-10-15
uv run scripts/fetch_historical_mistakes.py --start 2025-10-06 --end 2025-10-15
```

⚠️ **Note:** Archives contain questions and correct answers only, not your personal wrong choices. For complete tracking, use daily workflow on quiz day.

📖 See: [Historical Mistakes Guide](HISTORICAL_MISTAKES.md) | [Caching System](CACHING_SYSTEM.md)

---

## Analysis & Reports

**Performance insights:**
```bash
uv run scripts/inspect_history.py                     # Overview
uv run scripts/inspect_history.py --detailed          # Stats + trends
uv run scripts/inspect_history.py --mistakes          # By category
uv run scripts/inspect_history.py --all               # Everything
```

**Player evolution:**
```bash
uv run scripts/player_evolution.py                    # Table view
uv run scripts/player_evolution.py --export           # Export CSV
```

**Study guides:**
```bash
uv run scripts/generate_failed_questions.py           # All mistakes
uv run scripts/generate_failed_questions.py --order category
uv run scripts/generate_failed_questions.py --domain Arts
uv run scripts/generate_failed_questions.py --filter "2025-10-17"
```

📖 See: [Study Guide Generator](STUDY_GUIDE_GENERATOR.md)

---

## Visualizations

**Generate plots:**
```bash
uv run scripts/plot_evolution.py                      # All players
uv run scripts/plot_evolution.py --comparison         # Individual subplots
uv run scripts/plot_evolution.py --both               # Both visualizations
uv run scripts/plot_evolution.py --show               # Interactive display
```

**Category difficulty radar chart:**
```bash
uv run scripts/daily_report.py 2025-10-22 --radar    # Generate chart
uv run scripts/daily_report.py --show-radar          # Interactive view
```

**Outputs** (saved to `data/figures/`):
- `score_evolution.png` - All players on one graph with trends
- `category_difficulty_YYYY-MM-DD.png` - Radar chart showing quiz difficulty by category
- `score_comparison.png` - Individual subplots (3x4 grid) with stats

**Features:**
- Professional seaborn styling with 10 distinct colors
- Multiple line styles and markers for clarity
- Reference lines (50%, 75%) and score range shading
- Average lines and trend indicators

---

## Reports

**Daily reports:**
```bash
uv run scripts/daily_report.py
```

**Weekly mistakes report:**
```bash
uv run scripts/weekly_mistakes_report.py --verbose --update-history
```

**Generated files** (in `output/reports/`):
- `WEEKLY_MISTAKES_REPORT.md` - Comprehensive weekly analysis
- `mistakes_by_category.md` - Grouped by topic
- `mistakes_log.md` - Chronological list
- `MISTAKES_SUMMARY.md` - Statistics summary

---

## Script Reference

**Daily:**
- `complete_workflow.py` - Full automated workflow
- `fetch_today_quiz.py` - Fetch today's quiz
- `parse_results.py` - Parse HTML results
- `accumulate_mistakes.py` - Update history

**Historical:**
- `show_mistakes_by_date.py` - View single date mistakes
- `weekly_mistakes_report.py` - Multi-day reports
- `fetch_historical_mistakes.py` - Fetch past quizzes
- `manage_archive.py` - Check/download historical data

**Analysis:**
- `inspect_history.py` - Performance insights
- `player_evolution.py` - Score tracking table
- `plot_evolution.py` - Matplotlib visualizations
- `generate_failed_questions.py` - Study guides

**Other:**
- `daily_report.py` - Generate daily report
- `track_mistakes.py` - Track mistakes manually

---

## Configuration

**Environment variables** (`.env` file):
```env
QUIZY_USER=your_username
QUIZY_PASS=your_password
QUIZY_COOKIE=sessionid=your_session_cookie
```

**Data locations:**
- `data/cache/archive/` - Historical quiz data (JSON)
- `data/cache/quiz_html/` - Cached HTML pages
- `data/results/` - Results and mistake logs
- `data/figures/` - Generated plots
- `output/reports/` - Generated reports

**Caching:**
- HTML files cached automatically to avoid re-downloading
- Use `--no-cache` flag to force fresh fetch
- Cache dramatically speeds up subsequent runs

📖 See: [Caching System](CACHING_SYSTEM.md) | [Complete Workflow](COMPLETE_WORKFLOW.md)

---

## Tips

💡 **Best practices:**
- Run `complete_workflow.py` daily for accurate tracking
- Use `--verbose` flags to see progress
- Check `manage_archive.py` regularly for data gaps
- Generate weekly reports every Monday

💡 **Performance:**
- Cached data = 5-7x faster runs
- Use specific date ranges to limit downloads
- `--show` flag for interactive plot exploration

💡 **Study efficiently:**
- Order by category to identify weak areas
- Filter by domain for focused review
- Use `--show-choices` for quiz-style practice

---

## Additional Documentation

- [Complete Workflow Guide](COMPLETE_WORKFLOW.md)
- [Caching System Details](CACHING_SYSTEM.md)
- [Historical Mistakes Guide](HISTORICAL_MISTAKES.md)
- [Study Guide Generator](STUDY_GUIDE_GENERATOR.md)
- [Weekly Mistakes Report](WEEKLY_MISTAKES_REPORT.md)
- [Show Mistakes by Date](SHOW_MISTAKES_BY_DATE.md)

- **Accessibility**: Three-level distinction (color + line + marker)
- **Professional styling**: Seaborn whitegrid theme

---

## Configuration

### Environment Variables (.env)

```bash
QUIZY_USER=your_username          # Your quizypedia username
QUIZY_PASS=your_password          # Your quizypedia password
QUIZY_COOKIE=sessionid=...        # Session cookie for authentication
```

### Player Name Mapping

Edit `scripts/player_evolution.py` to customize player display names:

```python
PLAYER_NAMES = {
    'jutabouret': 'Julien',
    'louish': 'Louis',
    'BastienZim': 'Bastien',
    # Add more mappings...
}
```

### Data Structure

```
data/
├── cache/
│   └── archive/          # Daily leaderboard JSON files
│       ├── 2025-10-13.json
│       ├── 2025-10-14.json
│       └── ...
├── figures/              # Generated plots (PNG)
│   ├── score_evolution.png
│   ├── score_comparison.png
│   └── ...
└── db/                   # Database files (if used)

mistakes_history.json     # Your personal mistake log
defi_du_jour_results.json # Latest quiz results
player_scores_evolution.csv # Exported score data
```

---

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `complete_workflow.py` | Full automation (fetch → parse → track) | Daily workflow |
| `fetch_today_quiz.py` | Fetch today's quiz HTML | Automatic quiz retrieval |
| `parse_results.py` | Parse quiz HTML for results | Extract scores and mistakes |
| `accumulate_mistakes.py` | Update historical mistake log | Track mistakes over time |
| `manage_archive.py` | Check & download historical data | Archive management |
| `inspect_history.py` | Analyze personal performance | View stats and trends |
| `player_evolution.py` | Track player scores over time | Compare with friends |
| `plot_evolution.py` | Generate visualizations | Create plots |
| `generate_failed_questions.py` | Generate study guides from mistakes | Flexible ordering/filtering |

---

## Tips & Tricks

### Daily Routine

```bash
# Complete quiz on website, then:
uv run scripts/complete_workflow.py && uv run scripts/plot_evolution.py --both
```

### Check Your Progress

```bash
# Quick stats
uv run scripts/inspect_history.py --detailed

# See today's performance
uv run scripts/inspect_history.py --date $(date +%Y-%m-%d)
```

### Compare with Friends

```bash
# Rankings
uv run scripts/inspect_history.py --compare

# Visual comparison
uv run scripts/plot_evolution.py --players BastienZim louish jutabouret
```

### Analyze Weak Areas

```bash
# Find mistake patterns
uv run scripts/inspect_history.py --mistakes
```

### Fill Historical Gaps

```bash
# Check what data you're missing
uv run scripts/manage_archive.py --days 30

# Download last 2 weeks
uv run scripts/manage_archive.py --days 14 --download
```

### Generate Study Materials

```bash
# Generate failed questions study guide (default: by date, correct answers only)
uv run scripts/generate_failed_questions.py

# Order by category (alphabetically)
uv run scripts/generate_failed_questions.py --order category

# Show all multiple choice options
uv run scripts/generate_failed_questions.py --show-choices

# Filter by domain (Arts, Histoire, Sciences, etc.)
uv run scripts/generate_failed_questions.py --domain Arts

# Filter by date or category keyword
uv run scripts/generate_failed_questions.py --filter "October 20"

# Include your wrong answers (for self-assessment)
uv run scripts/generate_failed_questions.py --show-mistakes

# Complete view with mistakes and all choices
uv run scripts/generate_failed_questions.py --show-mistakes --show-choices

# With statistics
uv run scripts/generate_failed_questions.py --stats --order category

# Combine options
uv run scripts/generate_failed_questions.py --domain Histoire --order category --show-choices
```

---

## Troubleshooting

**Quiz fetch fails:**
- Verify `.env` credentials
- Check session cookie validity (may expire)
- Try manual workflow with saved HTML

**Missing data:**
- Run `manage_archive.py` to check gaps
- Use `--download` flag to fetch missing days

**Plot errors:**
- Install matplotlib/seaborn: `uv pip install matplotlib seaborn`
- Ensure archive data exists

**Cache issues:**
- Use `--no-cache` to force fresh fetch
- Clear cache: `rm -rf data/cache/quiz_html/`

---

---

For detailed guides, see the [docs/](.) directory.
- Re-fetch with `uv run scripts/fetch_today_quiz.py`

---

## Contributing

Feel free to add new analysis scripts or visualizations! Follow the existing patterns:
- Use `.env` for credentials
- Save outputs to appropriate `data/` subdirectories
- Include progress indicators (✅, 📊, etc.)
- Document new features

---

## License

Personal project for quiz performance tracking.
