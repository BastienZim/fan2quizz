# Fetching Historical Mistakes

This guide explains how to get quiz data from past dates, including your personal answers.

## Two Methods

### Method 1: Automated (Questions + Correct Answers Only)

The automated script can fetch archived quizzes but **cannot** retrieve your personal wrong answers.

### Method 2: Manual (Complete with Your Answers) ⭐ Recommended

To get YOUR specific answers from past quizzes:

1. **Navigate to the archive page:**
   ```
   https://www.quizypedia.fr/defi-du-jour/archives/YYYY/MM/DD/
   ```
   Example: `https://www.quizypedia.fr/defi-du-jour/archives/2025/10/15/`

2. **Log in to your account** (if not already logged in)

3. **Click "Afficher les questions et les réponses"** (Show questions and answers)
   - This loads YOUR personal answers dynamically
   - The page now shows which answers you chose

4. **Save the page as HTML:**
   - Right-click → "Save Page As..."
   - Save as: `defi_du_jour_debug.html` in your project root
   
5. **Process the saved HTML:**
   ```bash
   cd /path/to/fan2quizz
   uv run scripts/parse_results.py
   uv run scripts/accumulate_mistakes.py
   ```

This will properly log your mistakes with your actual wrong answers!

## Understanding the Limitation

**Important:** The archived quiz pages only contain:
- ✅ The questions
- ✅ All answer choices  
- ✅ The correct answers
- ✅ Your final score (from leaderboard)
- ❌ NOT your specific wrong answers

Your personal answer choices are only available:
1. On the quiz day itself (when logged in)
2. From saved HTML files (defi_du_jour_debug.html)

## What You Can Do

### Check What Dates You Have

```bash
# See which dates already have mistakes logged
uv run scripts/fetch_historical_mistakes.py --check
```

Output example:
```
📋 Dates with mistakes already logged:
============================================================
   ✓ 2025-10-16 (6 mistakes)
   ✓ 2025-10-17 (10 mistakes)
   ✓ 2025-10-20 (10 mistakes)

Total: 3 dates with 26 mistakes
```

### Attempt to Fetch Historical Data

```bash
# Try to fetch for a specific date
uv run scripts/fetch_historical_mistakes.py --date 2025-10-15
```

The script will:
1. Fetch the archived quiz page
2. Extract your score from the leaderboard
3. Warn you if personal answers aren't available
4. NOT add incomplete data to your mistakes log

Example output when answers aren't available:
```
📅 Fetching quiz for 2025-10-15...
   Score: 11/20
   Time: 0s
   ⚠️  Archive doesn't contain your personal answers
   ⚠️  Based on score: you got 9 wrong out of 20
   ⚠️  Cannot determine which specific questions you missed
```

### Fetch Multiple Dates

```bash
# Multiple specific dates
uv run scripts/fetch_historical_mistakes.py --date 2025-10-15 --date 2025-10-14

# Date range
uv run scripts/fetch_historical_mistakes.py --start 2025-10-06 --end 2025-10-15

# Skip dates you already have
uv run scripts/fetch_historical_mistakes.py --start 2025-10-06 --end 2025-10-19 --skip-existing
```

### If You Have Saved HTML Files

If you saved the quiz HTML on the day you completed it:

1. Make sure the file is named `defi_du_jour_debug.html`
2. Run the normal workflow:
```bash
uv run scripts/complete_workflow.py
```

This will extract your actual answers and log mistakes properly.

## Perfect Scores

If you had a perfect score (20/20) on a date, the script will detect this:

```bash
uv run scripts/fetch_historical_mistakes.py --date 2025-10-08
```

Output:
```
📅 Fetching quiz for 2025-10-08...
   Score: 20/20
   Time: 145s
   🎉 Perfect score - no mistakes!
```

## Best Practices

### Daily Workflow (Recommended)

To track your mistakes properly going forward:

1. Complete the quiz on quizypedia.fr
2. Save the page as HTML
3. Run the complete workflow:
```bash
uv run scripts/complete_workflow.py
```

This captures everything including your wrong answers.

### Retroactive Analysis

For past dates, you can still:
- See your scores in the archive data
- View all the questions and correct answers
- Identify weak categories by date
- Study the correct answers

But you won't be able to see which specific wrong answers you chose.

## Command Reference

```bash
# Check existing data
uv run scripts/fetch_historical_mistakes.py --check

# Fetch single date
uv run scripts/fetch_historical_mistakes.py --date YYYY-MM-DD

# Fetch date range  
uv run scripts/fetch_historical_mistakes.py --start YYYY-MM-DD --end YYYY-MM-DD

# Skip already logged dates
uv run scripts/fetch_historical_mistakes.py --start 2025-10-01 --end 2025-10-20 --skip-existing

# Specify username (default: BastienZim)
uv run scripts/fetch_historical_mistakes.py --date 2025-10-15 --username YourUsername

# Auto-regenerate study guide after
uv run scripts/fetch_historical_mistakes.py --date 2025-10-15 --regenerate
```

## Troubleshooting

### "DC_DATA not found in HTML"

The quiz data might not be available for that date in the archives.

Solution:
```bash
# Check if archive exists for that date
uv run scripts/manage_archive.py --days 30
```

### "Archive doesn't contain your personal answers"

This is expected for archived pages. It means you completed the quiz but the archive doesn't have your chosen answers.

Options:
1. Accept the limitation - you can still see questions and correct answers
2. If you have saved HTML from that day, use `complete_workflow.py` instead

### "Login failed"

Make sure your `.env` file has valid credentials:
```
QUIZY_COOKIE=your_session_id
```
or
```
QUIZY_USER=YourUsername
QUIZY_PASS=YourPassword
```

## See Also

- [README](README.md) - Main documentation
- [Archive Management](README.md#archive-management) - Downloading historical data
- [Study Guide Generator](STUDY_GUIDE_GENERATOR.md) - Creating study materials
