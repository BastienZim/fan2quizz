# Study Guide Generator

Generate customized study guides from your quiz mistakes with flexible ordering and filtering.

## Quick Start

```bash
# Default: by date, correct answers only
uv run scripts/generate_failed_questions.py

# Show help
uv run scripts/generate_failed_questions.py --help
```

**Note:** Default shows only correct answer (not all choices) for clean, focused studying. Use `--show-choices` to see all options.

## Ordering Options

**By date (default):**
```bash
uv run scripts/generate_failed_questions.py --order date
```
Groups by date, newest first. Review recent mistakes.

**By category:**
```bash
uv run scripts/generate_failed_questions.py --order category
```
Groups by category (alphabetically). Identify patterns in topics.

**Sequential:**
```bash
uv run scripts/generate_failed_questions.py --order question
```
Lists all questions in order by date and number.

## Filtering Options

**By domain:**
```bash
uv run scripts/generate_failed_questions.py --domain Arts
uv run scripts/generate_failed_questions.py --domain Histoire
uv run scripts/generate_failed_questions.py --domain Géographie
uv run scripts/generate_failed_questions.py --domain Musique
uv run scripts/generate_failed_questions.py --domain Sports
uv run scripts/generate_failed_questions.py --domain Sciences
uv run scripts/generate_failed_questions.py --domain Culture
uv run scripts/generate_failed_questions.py --domain Mythologie
```

**By text:**
```bash
# Filter by date
uv run scripts/generate_failed_questions.py --filter "2025-10-17"

# Filter by category keyword
uv run scripts/generate_failed_questions.py --filter "Écrivains"
uv run scripts/generate_failed_questions.py --filter "football"
uv run scripts/generate_failed_questions.py --filter "Shakespeare"
```

## Display Options

**Clean study format (default):**
```bash
uv run scripts/generate_failed_questions.py
```
Shows: question, hint, correct answer, learning notes.

**Show multiple choices:**
```bash
uv run scripts/generate_failed_questions.py --show-choices
```
Includes all options with ✓ marking correct answer. Quiz-style review.

**Show your mistakes:**
```bash
uv run scripts/generate_failed_questions.py --show-mistakes
```
Includes your wrong answers for self-assessment.

**Combined:**
```bash
uv run scripts/generate_failed_questions.py --show-choices --show-mistakes
```
Complete view with all info.

## Output Options

**Display to terminal (default):**
```bash
uv run scripts/generate_failed_questions.py --order category
```

**Save to file:**
```bash
uv run scripts/generate_failed_questions.py --order category --output study_guide.md
```

**With statistics:**
```bash
uv run scripts/generate_failed_questions.py --stats --order category
```

## Example Workflows

**Weekly study session:**
```bash
# Generate study guide by category
uv run scripts/generate_failed_questions.py --order category --show-choices --output weekly_study.md
```

**Focus on weak area:**
```bash
# Arts domain only
uv run scripts/generate_failed_questions.py --domain Arts --order category --show-choices
```

**Review specific week:**
```bash
# October 14-20
uv run scripts/generate_failed_questions.py --filter "2025-10-1" --order date
```

**Quiz practice:**
```bash
# Show all choices for self-testing
uv run scripts/generate_failed_questions.py --show-choices --order question
```

## Tips

- Order by category to identify weak areas
- Use `--show-choices` for quiz-style practice
- Filter by domain for focused review
- Save to file for offline study
- Use `--stats` to track improvement

## Output Format

**Default (clean):**
```
Question: [text]
Hint: [hint]
Correct Answer: [answer]
Learning: [notes]
```

**With choices:**
```
Question: [text]
Hint: [hint]
A) Choice 1
B) Choice 2
C) Choice 3 ✓
D) Choice 4
Learning: [notes]
```

**With mistakes:**
```
Question: [text]
Hint: [hint]
Your Answer: Choice 2 ❌
Correct Answer: Choice 3 ✓
Learning: [notes]
```
