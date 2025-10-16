# Mistakes Tracking - Quick Reference

This guide explains how to use the mistakes tracking system to improve your Quizypedia performance.

## Quick Start

### Daily Workflow

After completing your daily quiz:

```bash
# 1. Parse your quiz results (if not already done)
uv run scripts/parse_results.py

# 2. Add mistakes to your historical log
uv run scripts/accumulate_mistakes.py

# 3. Review your mistakes
cat mistakes_log.md
cat mistakes_by_category.md
```

## Scripts Overview

### `track_mistakes.py`
Extracts mistakes from the **current** quiz session only.

**Input:** `defi_du_jour_results.json` (from `parse_results.py`)

**Output:**
- `mistakes_log.md` - Formatted report for current session
- `mistakes_by_category.md` - Category analysis for current session
- `mistakes_log.json` - Structured data for current session

**Usage:**
```bash
uv run scripts/track_mistakes.py
```

### `accumulate_mistakes.py`
Builds a **complete historical database** of all your mistakes over time.

**Input:** `defi_du_jour_results.json` (from `parse_results.py`)

**Output:**
- `mistakes_history.json` - Master database with ALL mistakes
- `mistakes_log.md` - Updated with complete history
- `mistakes_by_category.md` - Updated with complete history

**Usage:**
```bash
uv run scripts/accumulate_mistakes.py
```

**Features:**
- Checks for duplicate dates
- Prompts before overwriting existing data
- Maintains chronological order (newest first)
- Shows top categories with most mistakes

## Output Files

### `mistakes_log.md`
Chronological view of all mistakes, organized by date.

**Great for:**
- Reviewing recent quiz sessions
- Tracking improvement over time
- Seeing all mistakes for a specific date

**Structure:**
```markdown
# Quizz du Jour - Complete Mistakes Log

## 📅 2025-10-16
**Mistakes:** 6

### Question 3 - Quartiers de villes françaises
**Question:** Dans quelle ville trouve-t-on ces quartiers ?
...
```

### `mistakes_by_category.md`
Mistakes grouped by category/theme.

**Great for:**
- Identifying your weak areas
- Focused study on specific topics
- Seeing which categories need more practice

**Structure:**
```markdown
# Mistakes by Category - Complete History

## Summary
| Category | Mistakes |
|----------|----------|
| Geography | 15 |
| History | 12 |
...

## Geography
**Total mistakes:** 15

### 2025-10-16 - Question 3
...
```

### `mistakes_history.json`
Machine-readable format for further analysis.

**Structure:**
```json
[
  {
    "date": "2025-10-16",
    "question_number": 3,
    "category": "Geography",
    "question": "...",
    "hints": ["..."],
    "your_answer": "Wrong answer",
    "correct_answer": "Right answer",
    "all_choices": ["A", "B", "C", "D"]
  }
]
```

## Tips for Improvement

### 1. Review by Category
Focus on your weakest categories first:
```bash
# Open the category analysis
cat mistakes_by_category.md | head -50
```

### 2. Look for Patterns
- Do you make mistakes on specific question types?
- Are there certain topics you consistently miss?
- Do you confuse similar concepts?

### 3. Study Your Mistakes
- Read each mistake carefully
- Understand WHY the correct answer is right
- Note the hints you might have missed

### 4. Track Progress
- Compare mistake counts week over week
- Note which categories you've improved in
- Celebrate when you don't repeat mistakes!

## Handling Multiple Quiz Sessions

The `accumulate_mistakes.py` script prevents duplicates:

```bash
# First time for a date
uv run scripts/accumulate_mistakes.py
# → Adds mistakes to history

# Running again for same date
uv run scripts/accumulate_mistakes.py
# → Warns you and asks if you want to replace
```

## Advanced Usage

### Export to Other Formats

You can use the JSON files for custom analysis:

```python
import json

# Load all historical mistakes
with open('mistakes_history.json') as f:
    mistakes = json.load(f)

# Find all mistakes in a specific category
geo_mistakes = [m for m in mistakes if 'Géo' in m['category']]
print(f"Geography mistakes: {len(geo_mistakes)}")

# Count mistakes by date
from collections import Counter
dates = Counter(m['date'] for m in mistakes)
print("Mistakes per date:", dates)
```

### Combine with Daily Report

Track your ranking alongside your mistakes:

```bash
# Get your ranking
uv run scripts/daily_report.py

# Track your mistakes
uv run scripts/accumulate_mistakes.py
```

## Maintenance

### Backup Your Data

Your mistakes are personal learning data - back them up!

```bash
# Backup mistakes
cp mistakes_history.json backups/mistakes_$(date +%Y%m%d).json

# Or commit to a private branch
git checkout -b personal-data
git add mistakes_history.json
git commit -m "Backup mistakes data"
```

### Reset and Start Fresh

If you want to start over:

```bash
# Remove all tracking files
rm mistakes_log.md mistakes_by_category.md mistakes_log.json mistakes_history.json

# Run accumulate again to rebuild from current session
uv run scripts/accumulate_mistakes.py
```

## Troubleshooting

### "DC_DATA not found in HTML"
**Problem:** The parser can't find quiz data in your HTML file.

**Solution:** 
- Make sure you saved the complete page (not just part of it)
- Check that `defi_du_jour_debug.html` exists
- Try the scraper script again

### "defi_du_jour_results.json not found"
**Problem:** You haven't parsed your results yet.

**Solution:**
```bash
uv run scripts/parse_results.py
```

### No mistakes found
**Problem:** You got a perfect score!

**Solution:** Celebrate! 🎉 No mistakes to track.

## Questions?

- Check `README.md` for general project documentation
- Review `scripts/track_mistakes.py` source code for details
- Open an issue on GitHub if you find bugs

Happy learning! 📚
