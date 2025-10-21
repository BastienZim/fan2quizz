# Wikipedia-Enhanced Mistake Reports

This document describes how to use the `mistakes_with_wikipedia.py` script to generate enriched mistake reports with Wikipedia links.

## Overview

The script takes your quiz mistakes and automatically finds relevant Wikipedia articles for each incorrect answer, helping you learn more about the topics you got wrong.

## Features

- ✅ Automatic Wikipedia link generation for all correct answers
- ✅ Supports both chronological and category-grouped reports
- ✅ Filter by date range (last N days)
- ✅ Summary statistics showing top mistake categories
- ✅ Bilingual support (French by default, configurable)
- ✅ Smart caching to avoid duplicate API calls
- ✅ Respectful API usage with proper User-Agent headers

## Usage

### Basic Usage

Generate a full report with Wikipedia links for all mistakes:

```bash
uv run scripts/mistakes_with_wikipedia.py
```

This creates: `output/reports/mistakes_with_wikipedia.md`

### Filter by Date Range

Get mistakes from the last 7 days:

```bash
uv run scripts/mistakes_with_wikipedia.py --days 7
```

Get mistakes from the last 30 days:

```bash
uv run scripts/mistakes_with_wikipedia.py --days 30
```

### Group by Category

Organize mistakes by topic instead of chronologically:

```bash
uv run scripts/mistakes_with_wikipedia.py --group-by-category
```

### Custom Output File

Save to a specific location:

```bash
uv run scripts/mistakes_with_wikipedia.py --output my_mistakes.md
```

### Summary Statistics Only

View statistics without generating a full report:

```bash
uv run scripts/mistakes_with_wikipedia.py --summary-only
```

### Skip Wikipedia Links (Faster)

Generate report without Wikipedia links (useful for quick previews):

```bash
uv run scripts/mistakes_with_wikipedia.py --no-wikipedia
```

## Report Formats

### Chronological Report

Default format shows mistakes in order from oldest to newest:

```markdown
### ❌ Question 7 — 2025-10-21
**Category:** Cours d'eau arrosant les capitales d'Asie

**Question:** Quel(s) cours d'eau associe-t-on à cette (ces) capitale(s) ?

**Hints:**
- Capitale(s): Bangkok

- ❌ **Your Answer:** Fleuve Rouge
- ✅ **Correct Answer:** Chao Phraya

**Learn More:**
- [📖 Wikipedia: Chao Phraya](https://fr.wikipedia.org/wiki/Chao_Phraya)
```

### Category-Grouped Report

Groups all mistakes by their quiz category:

```markdown
## 📂 Cours d'eau arrosant les capitales d'Asie
**3 mistake(s)**

### ❌ Question 7 — 2025-10-21
...
```

## How Wikipedia Linking Works

1. **Correct Answer Lookup**: The script searches French Wikipedia for the correct answer
2. **Category Lookup**: It also attempts to find a Wikipedia page for the topic/category
3. **Caching**: Results are cached during generation to avoid duplicate API calls
4. **Fallback**: If no Wikipedia page is found, it displays "_No Wikipedia page found_"

## Requirements

The script uses only Python standard library modules:
- `urllib` for API requests
- `json` for data handling
- No external dependencies needed!

## Output Directory

All reports are saved to:
```
output/reports/
├── mistakes_with_wikipedia.md       # Default chronological report
└── mistakes_by_category_wiki.md     # Category-grouped report
```

## Examples

### Example 1: Quick Daily Review

Review today's mistakes with Wikipedia links:

```bash
uv run scripts/mistakes_with_wikipedia.py --days 1
```

### Example 2: Weekly Study Guide

Generate a weekly study guide organized by topic:

```bash
uv run scripts/mistakes_with_wikipedia.py --days 7 --group-by-category
```

### Example 3: Custom Analysis

Generate multiple formats for comprehensive review:

```bash
# Chronological view
uv run scripts/mistakes_with_wikipedia.py --days 7 --output reports/weekly_chrono.md

# Category view
uv run scripts/mistakes_with_wikipedia.py --days 7 --group-by-category --output reports/weekly_topics.md

# Quick stats
uv run scripts/mistakes_with_wikipedia.py --days 7 --summary-only
```

## Summary Statistics

The script always shows summary statistics:

```
============================================================
📊 SUMMARY STATISTICS
============================================================
Total Mistakes: 33
Unique Categories: 33
Date Range: 2025-10-16 to 2025-10-21

Top 5 Categories:
  • Plantes de la famille des Solanacées (1): 1 mistake(s)
  • Cours d'eau arrosant les capitales d'Asie: 1 mistake(s)
  • Sélectionneurs actuels d'équipes nationales de football: 1 mistake(s)
  • Présidents français des IIe et IIIe Républiques: 1 mistake(s)
  • Personnalités des guerres de Vendée et de la Chouannerie: 1 mistake(s)
============================================================
```

## Tips

- 💡 Use `--group-by-category` to identify your weakest topics
- 💡 Use `--days 7` for weekly review sessions
- 💡 Use `--summary-only` to quickly check your progress
- 💡 The Wikipedia links open in French by default (matches quiz language)
- 💡 Share the generated markdown files with study partners

## Troubleshooting

### No Wikipedia Links Found

If Wikipedia links aren't appearing:
- Check your internet connection
- Some obscure topics may not have Wikipedia pages
- Try the `--no-wikipedia` flag to verify the report generation works

### API Rate Limiting

The script includes:
- 100ms delay between API calls
- Proper User-Agent header
- Caching to minimize requests

These should prevent any rate limiting issues.

## Related Scripts

- `track_mistakes.py` - Basic mistake logging
- `weekly_mistakes_report.py` - Weekly summary reports
- `show_mistakes_by_date.py` - View mistakes for specific dates
- `generate_failed_questions.py` - Exhaustive failure analysis

## Integration with Workflow

Add this to your daily workflow:

```bash
# 1. Fetch today's quiz
uv run scripts/fetch_today_quiz.py

# 2. Generate Wikipedia-enhanced report
uv run scripts/mistakes_with_wikipedia.py --days 1

# 3. Review the report
cat output/reports/mistakes_with_wikipedia.md
```
