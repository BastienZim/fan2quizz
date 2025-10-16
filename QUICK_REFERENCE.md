# 🚀 Quick Reference - fan2quizz

## Installation
```bash
cd /home/bastienzim/Documents/perso/fan2quizz
source .venv/bin/activate
pip install -e .  # Already done!
```

## Commands

### Daily Report
```bash
# Yesterday's report (default)
daily-report

# Specific date
daily-report 2025-10-15

# With fun emojis and commentary
daily-report --fun

# Force refresh from network
daily-report --refresh
```

### Parse Personal Results
```bash
# Parse saved HTML file
parse-results

# Note: Expects defi_du_jour_debug.html in current directory
```

## Direct Script Execution (Alternative)
```bash
python scripts/daily_report.py 2025-10-15
python scripts/parse_results.py
```

## Project Structure
```
fan2quizz/
├── scripts/           # Executable scripts
│   ├── daily_report.py
│   └── parse_results.py
├── fan2quizz/         # Main package
│   ├── cli.py         # CLI entry points
│   ├── database.py    # SQLite utilities
│   ├── scraper.py     # HTTP scraper
│   └── utils.py       # Rate limiter
└── data/              # Runtime data
    ├── cache/         # Cached JSON archives
    └── db/            # SQLite database
```

## Package Imports
```python
from fan2quizz import QuizDB, QuizypediaScraper, RateLimiter

# Use in your own scripts
db = QuizDB("data/db/quizypedia.db")
scraper = QuizypediaScraper()
```

## Files
- `pyproject.toml` - Package configuration & dependencies
- `requirements.txt` - Minimal dependencies (requests, bs4, lxml)
- `README.md` - Full documentation
- `.gitignore` - Git ignore rules

## Status
✅ Package installed and working  
✅ Commands available: `parse-results`, `daily-report`  
✅ Scripts can run directly  
✅ Clean structure with organized directories  
✅ Minimal dependencies (3 packages)  

Last updated: October 16, 2025
