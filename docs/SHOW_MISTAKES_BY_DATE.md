# Show Mistakes by Date

This script allows you to display your personal mistakes from a specific day's quiz on Quizypedia.

## Overview

The script fetches the archive page for a specific date from `https://www.quizypedia.fr/defi-du-jour/archives/YYYY/MM/DD/`, extracts the quiz data (including questions, your answers, and correct answers), and displays only the questions you got wrong.

## Features

- 🔍 Fetch quiz data from any archive date
- ❌ Display only mistakes (or all questions with `--all` flag)
- 🔐 Automatic authentication using `.env` file
- 💾 **Smart caching** - downloads each day only once, saves to cache
- 📊 Shows detailed information for each mistake:
  - Question theme/category
  - Question text with hints
  - All answer choices
  - Your answer (marked as wrong)
  - The correct answer
- 💾 Optional: Save the HTML response to a file

## Prerequisites

Make sure you have a `.env` file in the project root with your Quizypedia credentials:

```env
QUIZY_USER=your.email@example.com
QUIZY_PASS=yourpassword
# OR use a session cookie (faster and more reliable)
QUIZY_COOKIE=wordpress_logged_in_xxxxx=value; other_cookie=value
```

## Usage

### Basic Usage

```bash
# Show mistakes from October 20, 2025
uv run scripts/show_mistakes_by_date.py 2025-10-20

# Alternative date formats
uv run scripts/show_mistakes_by_date.py 2025/10/20
uv run scripts/show_mistakes_by_date.py 20/10/2025

# Show yesterday's mistakes (default if no date provided)
uv run scripts/show_mistakes_by_date.py
```

### Advanced Options

```bash
# Show all questions (not just mistakes)
uv run scripts/show_mistakes_by_date.py 2025-10-20 --all

# Skip authentication (will show limited info)
uv run scripts/show_mistakes_by_date.py 2025-10-20 --no-auth

# Save HTML for later analysis
uv run scripts/show_mistakes_by_date.py 2025-10-20 --save archive.html

# Force fresh fetch (ignore cache)
uv run scripts/show_mistakes_by_date.py 2025-10-20 --no-cache

# Combine options
uv run scripts/show_mistakes_by_date.py 2025-10-20 --all --save archive.html
```

### Help

```bash
uv run scripts/show_mistakes_by_date.py --help
```

## Output Example

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
⏱️  Time: 245 seconds

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

## How It Works

1. **Check Cache**: First checks if HTML is already cached in `data/cache/quiz_html/`
2. **Authentication**: Uses credentials from `.env` to authenticate with Quizypedia (if needed)
3. **Fetch Archive**: Fetches the archive page HTML from the specific date URL (only if not cached)
4. **Cache Save**: Saves HTML to cache for future use (avoiding repeated downloads)
5. **Parse Data**: Extracts the `DC_DATA` and `DC_USER` JavaScript variables embedded in the HTML
6. **Filter & Display**: Filters questions to show only mistakes (unless `--all` is used)

### Cache Benefits

- **Faster**: Instant loading from cache vs ~1-2 seconds from server
- **Server-friendly**: Doesn't overload quizypedia.fr with repeated requests
- **Offline capable**: Once cached, can view mistakes without internet
- **Cache location**: `data/cache/quiz_html/YYYY-MM-DD.html`

## URL Format

The archive pages follow this format:
```
https://www.quizypedia.fr/defi-du-jour/archives/YYYY/MM/DD/
```

Example:
```
https://www.quizypedia.fr/defi-du-jour/archives/2025/10/20/
```

## Notes

- You must have completed the quiz on the website for that date for your answers to be recorded
- The script automatically clicks "Afficher les questions et les réponses" by fetching the archive page with authentication
- Without authentication, the script may show limited or no results
- The script uses the same authentication mechanism as other scripts in the project

## Troubleshooting

### Error: "DC_DATA not found in HTML"

This usually means:
- You're not authenticated (check your `.env` file)
- The date is incorrect or the quiz doesn't exist for that date
- The page structure has changed

**Solution**: Try visiting the URL in your browser while logged in:
```
https://www.quizypedia.fr/defi-du-jour/archives/2025/10/20/
```

### Error: "Login failed"

**Solution**: 
- Check your credentials in `.env`
- Try using `QUIZY_COOKIE` instead of email/password for more reliable authentication

### No mistakes shown but you know you made mistakes

**Solution**: Make sure you completed the quiz before the data was archived, or check if the date is correct.

## Related Scripts

- `fetch_today_quiz.py` - Fetch today's live quiz HTML
- `parse_results.py` - Parse quiz results from saved HTML
- `daily_report.py` - Generate daily/weekly reports
- `track_mistakes.py` - Track mistakes over time
