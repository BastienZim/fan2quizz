# Fetching Historical Mistakes

Guide for retrieving quiz data from past dates, including your personal answers.

## Two Methods

### Method 1: Automated (Limited)
Fetches archived quizzes but **cannot** retrieve your personal wrong answers.

### Method 2: Manual (Complete) ⭐ Recommended

**To get YOUR specific answers:**

1. Navigate to archive: `https://www.quizypedia.fr/defi-du-jour/archives/YYYY/MM/DD/`
   Example: `https://www.quizypedia.fr/defi-du-jour/archives/2025/10/15/`

2. Log in to your account

3. Click **"Afficher les questions et les réponses"**
   This loads YOUR personal answers dynamically

4. Save page as HTML:
   - Right-click → "Save Page As..."
   - Save as: `defi_du_jour_debug.html` in project root

5. Process the saved HTML:
   ```bash
   uv run scripts/parse_results.py
   uv run scripts/accumulate_mistakes.py
   ```

This properly logs mistakes with your actual wrong answers!

## Understanding the Limitation

**Archive pages contain:**
- ✅ Questions
- ✅ All answer choices  
- ✅ Correct answers
- ✅ Your final score (from leaderboard)
- ❌ NOT your specific wrong answers

Your personal choices are only available:
1. On quiz day (when logged in)
2. From saved HTML files

## What You Can Do

**Check existing dates:**
```bash
uv run scripts/fetch_historical_mistakes.py --check
```

**Attempt to fetch:**
```bash
# Specific date
uv run scripts/fetch_historical_mistakes.py --date 2025-10-15

# Multiple dates
uv run scripts/fetch_historical_mistakes.py --date 2025-10-15 --date 2025-10-14

# Date range
uv run scripts/fetch_historical_mistakes.py --start 2025-10-06 --end 2025-10-15

# Skip existing
uv run scripts/fetch_historical_mistakes.py --start 2025-10-06 --end 2025-10-19 --skip-existing
```

The script will:
- Fetch archived quiz page
- Extract your score from leaderboard
- Warn if personal answers aren't available
- NOT add incomplete data to logs

**With saved HTML files:**
```bash
uv run scripts/complete_workflow.py
```

## Best Practices

**Daily workflow (recommended for future):**
1. Complete quiz on quizypedia.fr
2. Save page as HTML
3. Run: `uv run scripts/complete_workflow.py`

This captures everything including wrong answers.

**For perfect scores (20/20):**
Script automatically detects and logs appropriately with no mistakes.
