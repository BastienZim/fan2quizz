# Repository Structure Migration Notes

## Changes Made

The repository has been reorganized for better clarity and maintainability:

### New Directory Structure

```
fan2quizz/
├── data/                    # All data files (gitignored)
│   ├── cache/               # Cached quiz data
│   ├── db/                  # SQLite database
│   ├── figures/             # Generated charts
│   ├── html/                # Saved HTML files (NEW)
│   └── results/             # JSON results & mistakes (NEW)
├── output/                  # Generated reports (gitignored)
│   ├── reports/             # Markdown reports (NEW)
│   ├── results/             # CSV exports (NEW)
│   └── tests/               # Test outputs (NEW)
├── docs/                    # Documentation
├── scripts/                 # Python scripts
└── README.md                # Main documentation
```

### File Migrations

**From root → `data/html/`:**
- `defi_du_jour_debug.html`

**From root → `data/results/`:**
- `defi_du_jour_results.json`
- `mistakes_history.json`
- `mistakes_log.json`

**From root → `output/reports/`:**
- `mistakes_log.md`
- `mistakes_by_category.md`
- `MISTAKES_REPORT_14DAYS.md`
- `MISTAKES_SUMMARY.md`
- `WEEKLY_MISTAKES_LAST7DAYS.md`
- `WEEKLY_MISTAKES_REPORT.md`
- `FAILED_QUESTIONS_EXHAUSTIVE.md`

**From root → `output/results/`:**
- `player_scores_evolution.csv`

**From root → `output/tests/`:**
- `CACHED_TEST.md`
- `TEST_CACHE.md`
- `TEST_WEEKLY_REPORT.md`

## Scripts That Need Path Updates

The following scripts reference hardcoded file paths and may need updating:

### High Priority (Frequently Used)
1. **`scripts/parse_results.py`** - Reads `defi_du_jour_debug.html`, writes `defi_du_jour_results.json`
2. **`scripts/track_mistakes.py`** - Reads `defi_du_jour_results.json`, writes `mistakes_log.md`, `mistakes_log.json`
3. **`scripts/accumulate_mistakes.py`** - Reads/writes `mistakes_history.json`, updates `mistakes_log.md`
4. **`scripts/process_quiz.py`** - Uses parse_results and track_mistakes
5. **`scripts/weekly_mistakes_report.py`** - Writes `WEEKLY_MISTAKES_REPORT.md`, reads/writes `mistakes_history.json`

### Medium Priority
6. **`scripts/fetch_today_quiz.py`** - Writes `defi_du_jour_debug.html`
7. **`scripts/generate_failed_questions.py`** - Reads `mistakes_history.json`
8. **`scripts/inspect_history.py`** - Reads `mistakes_history.json`, `defi_du_jour_results.json`
9. **`scripts/fetch_historical_mistakes.py`** - Reads/writes `mistakes_history.json`
10. **`scripts/complete_workflow.py`** - References various output files

### Recommended Path Pattern

For consistency, scripts should use:

```python
from pathlib import Path

# Project root
ROOT = Path(__file__).parent.parent

# Input files
HTML_FILE = ROOT / "data" / "html" / "defi_du_jour_debug.html"
RESULTS_FILE = ROOT / "data" / "results" / "defi_du_jour_results.json"
HISTORY_FILE = ROOT / "data" / "results" / "mistakes_history.json"
MISTAKES_JSON = ROOT / "data" / "results" / "mistakes_log.json"

# Output files
MISTAKES_MD = ROOT / "output" / "reports" / "mistakes_log.md"
MISTAKES_BY_CAT = ROOT / "output" / "reports" / "mistakes_by_category.md"
WEEKLY_REPORT = ROOT / "output" / "reports" / "WEEKLY_MISTAKES_REPORT.md"
SCORE_EVOLUTION_CSV = ROOT / "output" / "results" / "player_scores_evolution.csv"
```

## Updated .gitignore

The `.gitignore` file has been updated to:
- Ignore entire `output/` directory
- Ignore `data/results/*` and `data/html/*` (with .gitkeep files)
- Remove individual file patterns (now covered by directory patterns)

## Documentation Updates

- ✅ `README.md` - Updated all file path references
- ✅ `QUICK_REFERENCE.md` - Updated output file table
- ✅ `output/README.md` - Created to explain output structure
- 📋 `docs/` - May need updates (check individual doc files)

## Next Steps

1. **Test the scripts** - Verify they still work with moved files
2. **Update script paths** - Modify the scripts listed above to use new paths
3. **Update docs/** - Check documentation files for outdated paths
4. **Create .gitkeep files** - Ensure empty directories are tracked:
   - ✅ `data/results/.gitkeep`
   - ✅ `data/html/.gitkeep`
   - Consider adding for `output/` subdirectories if needed

## Benefits of New Structure

1. **Cleaner root directory** - Only essential files (README, config, requirements)
2. **Clear separation** - Data vs. generated outputs vs. source code
3. **Better gitignore** - Easier to exclude all generated files
4. **More intuitive** - New users can understand structure at a glance
5. **Scalable** - Easy to add new categories of files
