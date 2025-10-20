# 📚 Failed Questions Generator - Quick Guide

Generate customized study guides from your quiz mistakes with flexible ordering and filtering.

## 🚀 Quick Start

```bash
# Default: all questions ordered by date (newest first), correct answers only
uv run scripts/generate_failed_questions.py

# Show help
uv run scripts/generate_failed_questions.py --help
```

**Note:** By default, only the correct answer is shown (not all multiple choices). This keeps the output clean and focused for studying. Use `--show-choices` to see all options.

## 📋 Ordering Options

### By Date (Default)
```bash
uv run scripts/generate_failed_questions.py --order date
```
Groups questions by date, newest first. Perfect for reviewing recent mistakes.

### By Category
```bash
uv run scripts/generate_failed_questions.py --order category
```
Groups questions by category (alphabetically). Great for identifying patterns in specific topics.

### Sequential
```bash
uv run scripts/generate_failed_questions.py --order question
```
Lists all questions in order by date and question number.

## 🔍 Filtering Options

### By Domain
Filter questions by broad knowledge domain:

```bash
# Arts (literature, painting, opera, theater)
uv run scripts/generate_failed_questions.py --domain Arts

# History (events, people, dates)
uv run scripts/generate_failed_questions.py --domain Histoire

# Geography (cities, regions, places)
uv run scripts/generate_failed_questions.py --domain Géographie

# Music (bands, singers, songs)
uv run scripts/generate_failed_questions.py --domain Musique

# Sports (athletes, records, teams)
uv run scripts/generate_failed_questions.py --domain Sports

# Sciences (medicine, biology, physics)
uv run scripts/generate_failed_questions.py --domain Sciences

# Culture (food, traditions, pop culture)
uv run scripts/generate_failed_questions.py --domain Culture

# Mythology (legends, gods, heroes)
uv run scripts/generate_failed_questions.py --domain Mythologie
```

### By Text Filter
Filter by any text in date or category:

```bash
# Filter by specific date
uv run scripts/generate_failed_questions.py --filter "2025-10-17"

# Filter by category keyword
uv run scripts/generate_failed_questions.py --filter "Écrivains"
uv run scripts/generate_failed_questions.py --filter "football"
uv run scripts/generate_failed_questions.py --filter "Shakespeare"
```

## 🎯 Display Options

### Clean Study Format (Default)
```bash
uv run scripts/generate_failed_questions.py
```
Shows only: question, hint, correct answer, and learning notes. Best for studying.

### Show Multiple Choices
```bash
uv run scripts/generate_failed_questions.py --show-choices
```
Includes all answer options with ✓ marking the correct answer. Useful for quiz-style review.

### Show Your Mistakes
```bash
uv run scripts/generate_failed_questions.py --show-mistakes
```
Includes your wrong answers for self-assessment. Works with or without --show-choices.

### Complete View
```bash
uv run scripts/generate_failed_questions.py --show-mistakes --show-choices
```
Shows everything: your wrong answer (✗), correct answer (✓), all choices, and learning notes.

### Include Statistics
```bash
uv run scripts/generate_failed_questions.py --stats
```
Adds a statistics section showing breakdown by date and category.

## 💾 Output Options

### Default Output
By default, generates `FAILED_QUESTIONS_EXHAUSTIVE.md`

### Custom Output File
```bash
uv run scripts/generate_failed_questions.py --output my_study_guide.md
```

## 🎨 Common Usage Patterns

### Daily Review (after quiz)
```bash
# Review today's mistakes
uv run scripts/generate_failed_questions.py --filter "$(date +%Y-%m-%d)"
```

### Weekly Study Session
```bash
# All mistakes, by category, with stats
uv run scripts/generate_failed_questions.py --order category --stats
```

### Domain-Focused Study
```bash
# Focus on weak areas
uv run scripts/generate_failed_questions.py --domain Arts --order category
uv run scripts/generate_failed_questions.py --domain Histoire --show-mistakes
```

### Create Flashcards
```bash
# Simple format without choices (clean for memorization)
uv run scripts/generate_failed_questions.py --order category --output flashcards.md
```

### Quiz-Style Practice
```bash
# Include all choices for self-testing
uv run scripts/generate_failed_questions.py --show-choices --output quiz_practice.md
```

### Self-Assessment
```bash
# Include your mistakes to track patterns
uv run scripts/generate_failed_questions.py --show-mistakes --show-choices --stats --output assessment.md
```

## 📊 Example Outputs

### Example 1: Arts Domain Only
```bash
uv run scripts/generate_failed_questions.py --domain Arts --output arts_study.md
```
**Result:** 5 questions from Arts domain (literature, painting, opera, theater)

### Example 2: History by Category
```bash
uv run scripts/generate_failed_questions.py --domain Histoire --order category --stats
```
**Result:** Historical questions grouped by category with statistics

### Example 3: Specific Date Review
```bash
uv run scripts/generate_failed_questions.py --filter "2025-10-20" --show-mistakes
```
**Result:** Only questions from October 20, showing your mistakes

## 🎓 Study Workflow

### Step 1: Generate Study Guide
```bash
uv run scripts/generate_failed_questions.py --order category --output study.md
```

### Step 2: Review by Domain
```bash
# Study one domain at a time
uv run scripts/generate_failed_questions.py --domain Arts --output arts.md
uv run scripts/generate_failed_questions.py --domain Histoire --output histoire.md
uv run scripts/generate_failed_questions.py --domain Sciences --output sciences.md
```

### Step 3: Self-Test
```bash
# After studying, review with mistakes shown
uv run scripts/generate_failed_questions.py --show-mistakes --output self_test.md
```

### Step 4: Track Progress
```bash
# Weekly stats
uv run scripts/generate_failed_questions.py --stats --output weekly_progress.md
```

## 📝 Output Format

Each question includes:
- **Date** (when you made the mistake)
- **Category** (quiz category)
- **Question** (full question text)
- **Hint** (clue provided during quiz)
- **Correct Answer** (always shown)
- **Your Answer** (optional, with `--show-mistakes`, marked with ✗)
- **All Choices** (optional, with `--show-choices`, correct marked with ✓)
- **Learning Note** (contextual explanation)

**Default format** shows: Date, Category, Question, Hint, Correct Answer, Learning Note  
**With --show-choices:** Adds all multiple choice options  
**With --show-mistakes:** Adds your incorrect answer  
**With both flags:** Complete view of everything

## 🔧 Advanced Combinations

### Combine Multiple Options
```bash
# Arts domain, by category, with stats, show mistakes
uv run scripts/generate_failed_questions.py \
  --domain Arts \
  --order category \
  --stats \
  --show-mistakes \
  --output arts_complete.md
```

### Create Multiple Study Guides
```bash
# Generate one guide per domain
for domain in Arts Histoire Géographie Musique Sports Sciences; do
  uv run scripts/generate_failed_questions.py \
    --domain $domain \
    --order category \
    --output "${domain}_study.md"
done
```

## 💡 Tips

1. **Start with category order** to identify patterns
2. **Use domain filters** to focus study sessions
3. **Hide mistakes** when first studying (test yourself)
4. **Show mistakes** when reviewing (understand errors)
5. **Use stats** to track improvement over time
6. **Filter by date** to review recent mistakes
7. **Create separate files** for different study topics

## 📂 Generated Files

All generated files are Markdown format, can be viewed in:
- VS Code (native Markdown preview)
- Any Markdown viewer
- Converted to PDF for printing
- Imported to Notion, Obsidian, etc.

---

*Last Updated: October 20, 2025*
