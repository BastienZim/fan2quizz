# Fan2Quizz Documentation

Complete guide for tracking, analyzing, and visualizing your daily quiz performance.

## 📚 Table of Contents

- [Quick Start](#quick-start)
- [Daily Workflow](#daily-workflow)
- [Data Analysis](#data-analysis)
- [Visualizations](#visualizations)
- [Configuration](#configuration)

---

## Quick Start

### Prerequisites

1. Python 3.13+ with uv package manager
2. Complete the daily quiz at [quizypedia.fr/defi-du-jour](https://www.quizypedia.fr/defi-du-jour/)
3. Create a `.env` file with your credentials:
   ```
   QUIZY_USER=your_username
   QUIZY_PASS=your_password
   QUIZY_COOKIE=sessionid=your_session_cookie
   ```

### Installation

```bash
# Install dependencies
uv sync
```

---

## Daily Workflow

### Automated (Recommended)

Run the complete workflow after completing your quiz:

```bash
uv run scripts/complete_workflow.py
```

This will:
1. ✅ Fetch today's quiz HTML with your answers
2. ✅ Parse your results (score, mistakes, time)
3. ✅ Update historical mistake log
4. ✅ Generate reports

### Manual Alternative

If automated fetch doesn't work:

1. Complete the quiz on quizypedia.fr
2. Save the results page as `defi_du_jour_debug.html` in the project root
3. Run: `uv run scripts/complete_workflow.py --skip-fetch`

### Individual Steps

```bash
# Fetch today's quiz
uv run scripts/fetch_today_quiz.py

# Parse results
uv run scripts/parse_results.py

# Track mistakes
uv run scripts/accumulate_mistakes.py
```

---

## Data Analysis

### Archive Management

Check and download historical quiz data:

```bash
# Check what data you have (last 30 days)
uv run scripts/manage_archive.py

# Check specific date range
uv run scripts/manage_archive.py --from 2025-10-01 --to 2025-10-20

# Check last 14 days
uv run scripts/manage_archive.py --days 14

# Download missing data (prompts for confirmation)
uv run scripts/manage_archive.py --days 14 --download

# Custom range download
uv run scripts/manage_archive.py --from 2025-10-01 --download
```

**Shows:**
- Available dates with data
- Missing dates in range
- Option to download missing data
- Progress during download

### Fetch Historical Mistakes

Retroactively check quiz data from past dates:

```bash
# Check what dates already have mistakes logged
uv run scripts/fetch_historical_mistakes.py --check

# Try to fetch mistakes for a specific date
uv run scripts/fetch_historical_mistakes.py --date 2025-10-15

# Fetch multiple dates
uv run scripts/fetch_historical_mistakes.py --date 2025-10-15 --date 2025-10-14

# Fetch date range
uv run scripts/fetch_historical_mistakes.py --start 2025-10-06 --end 2025-10-15

# Skip dates already logged
uv run scripts/fetch_historical_mistakes.py --start 2025-10-06 --end 2025-10-19 --skip-existing
```

**⚠️ Important Limitation:**
Archives only contain questions and correct answers, NOT your personal wrong answers. 
The script will show your score but cannot determine which specific questions you missed.

For complete tracking, use the daily workflow on the quiz day.

📖 [Full Historical Mistakes Guide](HISTORICAL_MISTAKES.md)

### Personal Performance

Get insights into your quiz history:

```bash
# Quick overview
uv run scripts/inspect_history.py

# Detailed stats with trends
uv run scripts/inspect_history.py --detailed

# Analyze mistakes by category
uv run scripts/inspect_history.py --mistakes

# Compare with friends
uv run scripts/inspect_history.py --compare

# Specific date analysis
uv run scripts/inspect_history.py --date 2025-10-17

# Everything at once
uv run scripts/inspect_history.py --all
```

**Provides:**
- Total quizzes completed
- Average score and trends
- Mistake analysis by category
- Friend rankings and comparisons
- Best/worst performance dates

### Player Evolution

Track score evolution over time:

```bash
# Table view with trends
uv run scripts/player_evolution.py

# Export to CSV
uv run scripts/player_evolution.py --export

# Filter by players
uv run scripts/player_evolution.py --players BastienZim louish jutabouret
```

**Shows:**
- Daily scores for all players
- Day-to-day changes with trend indicators (↗/↘/→)
- Visual bar chart in terminal
- Comparison summary

---

## Visualizations

### Generate Plots

All plots are saved to `data/figures/` with professional seaborn styling.

```bash
# Single plot with all players
uv run scripts/plot_evolution.py

# Individual subplots per player
uv run scripts/plot_evolution.py --comparison

# Both visualizations
uv run scripts/plot_evolution.py --both

# Filter specific players
uv run scripts/plot_evolution.py --players BastienZim louish jutabouret

# Display interactively
uv run scripts/plot_evolution.py --show
```

### Available Plots

1. **score_evolution.png** - All players on one graph
   - Date vs Score (0-20)
   - Distinct colors, line styles, and markers per player
   - Reference lines at 50% and 75%
   - Score range shading (red/yellow/green)

2. **score_comparison.png** - Individual subplots (3x4 grid)
   - One subplot per player
   - Filled area under curve
   - Average line and trend indicator
   - Score value labels

3. **Custom plots** - Filter specific players
   - Compare top performers
   - Track specific friend groups

### Visual Features

- **Color Palette**: HUSL for maximum distinction (10 unique colors)
- **Line Styles**: 4 patterns (solid, dashed, dash-dot, dotted)
- **Markers**: 10 shapes (○, □, △, ◇, ▽, ⬠, ★, ⬡, ✕, +)
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

### Quiz fetch fails
- Check `.env` credentials are correct
- Verify session cookie is valid (may expire)
- Use manual HTML save method as fallback

### No data in plots
- Ensure archive files exist in `data/cache/archive/`
- Run workflow at least once to generate data
- Check date range in archive folder

### Wrong date in results
- Make sure you saved the correct results page
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
