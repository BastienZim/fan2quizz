# New Scripts Summary

## What Was Created

I've created two powerful new scripts for your fan2quizz project that work with the Quizypedia archives:

### 1. `show_mistakes_by_date.py` - Single Day Mistake Viewer
**Purpose:** Display your mistakes from any specific quiz date

**Key Features:**
- ✅ Fetch quiz data from archive URLs (e.g., `https://www.quizypedia.fr/defi-du-jour/archives/2025/10/20/`)
- ✅ Show only mistakes by default, or all questions with `--all`
- ✅ Support multiple date formats (YYYY-MM-DD, DD/MM/YYYY, etc.)
- ✅ Automatic authentication via `.env` file
- ✅ Detailed information: hints, all choices, your answer, correct answer
- ✅ Optional HTML save for later analysis

**Usage Examples:**
```bash
# Show mistakes from October 20, 2025
uv run scripts/show_mistakes_by_date.py 2025-10-20

# Show yesterday's mistakes
uv run scripts/show_mistakes_by_date.py

# Show all questions (not just mistakes)
uv run scripts/show_mistakes_by_date.py 2025-10-20 --all
```

### 2. `weekly_mistakes_report.py` - Multi-Day Report Generator
**Purpose:** Generate comprehensive reports for any date range

**Key Features:**
- ✅ Fetch multiple days automatically (last 7 days, 14 days, or custom range)
- ✅ Executive summary with statistics and accuracy rates
- ✅ Daily breakdown table
- ✅ Mistakes grouped by category
- ✅ Detailed mistake listings
- ✅ Optional update of `mistakes_history.json`
- ✅ Progress display with `--verbose`

**Usage Examples:**
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

## How They Work Together

### Archive Integration
Both scripts use the same archive fetching mechanism:
1. Connect to Quizypedia with your credentials
2. Fetch archive pages (equivalent to clicking "Afficher les questions et les réponses")
3. Extract `DC_DATA` and `DC_USER` JavaScript variables
4. Parse quiz data and identify mistakes
5. Generate formatted reports

### With Existing Scripts
These new scripts complement your existing workflow:

**Daily Workflow (Today's Quiz):**
```bash
uv run scripts/fetch_today_quiz.py      # Fetch today's quiz
uv run scripts/parse_results.py          # Parse results
uv run scripts/accumulate_mistakes.py    # Add to history
```

**Historical Review (Past Quizzes):**
```bash
uv run scripts/show_mistakes_by_date.py 2025-10-15  # Single day
uv run scripts/weekly_mistakes_report.py --days 7    # Multiple days
```

## Output Examples

### show_mistakes_by_date.py Output:
```
📅 Fetching quiz for 2025-10-20...
🔐 Using session cookie from .env...
✅ Session cookie loaded!
🌐 Fetching archive page...
✅ Fetched HTML (444829 bytes)
================================================================================
DÉFI DU JOUR - Your Mistakes
================================================================================

📊 Score: 10/20
❌ Mistakes: 10
⏱️  Time: N/A seconds

================================================================================
MISTAKES ONLY (10 mistakes):
================================================================================

────────────────────────────────────────────────────────────────────────────────
❌ Question 1: Pâtisseries et desserts français (1)
────────────────────────────────────────────────────────────────────────────────
❓ Quel département a pour spécialité la pâtisserie suivante ?
   💡 Spécialité: Nonnette

   Choices:
   1. Rhône ✗ YOUR ANSWER (WRONG)
   2. Finistère
   3. Meuse
   4. Côte-d'Or ✓ CORRECT

   💭 You answered: Rhône
   ✓ Correct answer: Côte-d'Or
...
```

### weekly_mistakes_report.py Output:
```
📅 Generating report for 2025-10-14 to 2025-10-20

🔐 Using session cookie from .env
🔍 Fetching data for 7 days...

  Fetching 2025-10-14... ✓ (11/20)
  Fetching 2025-10-15... ✓ (11/20)
  Fetching 2025-10-16... ✓ (14/20)
  Fetching 2025-10-17... ✓ (10/20)
  Fetching 2025-10-18... ✓ (12/20)
  Fetching 2025-10-19... ✓ (10/20)
  Fetching 2025-10-20... ✓ (10/20)

📝 Generating report...
✅ Report saved to: /home/.../WEEKLY_MISTAKES_REPORT.md

============================================================
📊 Summary:
   - Quizzes analyzed: 7
   - Total mistakes found: 62
   - Report saved to: WEEKLY_MISTAKES_REPORT.md
============================================================
```

The generated markdown report includes:
- Executive summary with statistics
- Daily performance table
- Top mistake categories
- Detailed mistakes by date
- Mistakes grouped by category

## Documentation Created

1. **`docs/SHOW_MISTAKES_BY_DATE.md`** - Complete guide for single-day script
2. **`docs/WEEKLY_MISTAKES_REPORT.md`** - Complete guide for weekly report script
3. **`docs/COMPLETE_WORKFLOW.md`** - Integration guide showing all workflows
4. **Updated `README.md`** - Added sections for both new scripts

## Testing Results

Both scripts have been tested and work perfectly:

✅ **Single date fetching:** Successfully fetches and displays mistakes from October 20, 2025
✅ **Multiple date ranges:** Successfully fetches 3-day and 7-day ranges
✅ **Authentication:** Works with session cookies from `.env`
✅ **Date format support:** Handles YYYY-MM-DD, DD/MM/YYYY, and more
✅ **Report generation:** Creates beautiful, comprehensive markdown reports
✅ **Error handling:** Gracefully handles missing dates and authentication issues

## Use Cases

### Weekly Review
```bash
# Every Monday
uv run scripts/weekly_mistakes_report.py --verbose
```

### Historical Analysis
```bash
# Review a specific past week
uv run scripts/weekly_mistakes_report.py --start 2025-10-01 --end 2025-10-07
```

### Single Day Deep Dive
```bash
# Review a particularly difficult quiz
uv run scripts/show_mistakes_by_date.py 2025-10-15 --all
```

### Study Preparation
```bash
# Generate 30-day study guide
uv run scripts/weekly_mistakes_report.py --days 30 --output STUDY_GUIDE.md
```

### Database Building
```bash
# Catch up on historical data
uv run scripts/weekly_mistakes_report.py --days 30 --update-history --verbose
```

## Key Advantages

1. **No Manual HTML Saving Required:** Fetches directly from archives
2. **Flexible Date Handling:** Multiple formats and ranges supported
3. **Automatic Authentication:** Uses existing `.env` credentials
4. **Comprehensive Reports:** Statistics, breakdowns, and detailed listings
5. **Integration Ready:** Works with existing mistake tracking system
6. **Beautiful Output:** Emoji-enhanced, well-formatted markdown

## Next Steps for You

1. **Test with your data:**
   ```bash
   uv run scripts/show_mistakes_by_date.py 2025-10-20
   ```

2. **Generate your first weekly report:**
   ```bash
   uv run scripts/weekly_mistakes_report.py --verbose
   ```

3. **Set up weekly automation:** (optional)
   - Add to crontab for automatic Monday morning reports
   - See `docs/COMPLETE_WORKFLOW.md` for examples

4. **Customize as needed:**
   - Adjust date ranges
   - Modify output formats
   - Add to your existing workflow

## Files Created

**Scripts:**
- `scripts/show_mistakes_by_date.py` (346 lines)
- `scripts/weekly_mistakes_report.py` (513 lines)

**Documentation:**
- `docs/SHOW_MISTAKES_BY_DATE.md`
- `docs/WEEKLY_MISTAKES_REPORT.md`
- `docs/COMPLETE_WORKFLOW.md`
- Updated `README.md`

All scripts follow your project's coding style and include:
- Comprehensive docstrings
- Type hints
- Error handling
- Help messages
- Example usage

Enjoy your new mistake tracking capabilities! 🎉
