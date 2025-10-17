# How to Check and Register Today's Quiz Mistakes

This guide explains the complete workflow for tracking your daily quiz mistakes.

## 📋 Prerequisites

1. **Complete the quiz** on [quizypedia.fr/defi-du-jour](https://www.quizypedia.fr/defi-du-jour/)
2. **View your results** on the website (the page that shows your score and answers)

## 🚀 Quick Start (Automated)

### Option 1: Complete Automated Workflow (Recommended if you have login)

If you have a quizypedia account and want everything automated:

```bash
uv run scripts/complete_workflow.py --email your@email.com --password yourpass
```

This will:
1. ✅ Fetch today's quiz with your answers
2. ✅ Parse your results
3. ✅ Track mistakes in historical log
4. ✅ Generate reports

### Option 2: Manual HTML Save + Process

**Most reliable method if automated fetch doesn't work:**

1. **Complete the quiz** on quizypedia.fr
2. **After completing**, you'll see your results page
3. **Save the HTML**:
   - **Method A (Best)**: Right-click on the page → "Save as" → Save as `defi_du_jour_debug.html` in your `fan2quizz` folder
   - **Method B**: Open DevTools (F12) → Elements tab → Right-click `<html>` → Copy → Copy outerHTML → Paste into `defi_du_jour_debug.html`
4. **Run the processing**:
   ```bash
   uv run scripts/process_quiz.py
   ```

### Option 3: Step by Step Manual Process

If you prefer to see each step:

```bash
# Step 1: Save HTML manually (see Option 2 above)

# Step 2: Parse results
uv run scripts/parse_results.py

# Step 3: Track mistakes
uv run scripts/accumulate_mistakes.py
```

## 📁 Output Files

After running the scripts, you'll have:

- **`mistakes_log.md`** - Chronological list of all your mistakes
- **`mistakes_by_category.md`** - Mistakes grouped by category (shows weak areas)
- **`mistakes_history.json`** - Master database of all mistakes
- **`defi_du_jour_results.json`** - Latest quiz results in JSON format

## 💡 Tips

1. **Best workflow**: Save HTML manually (most reliable) → Run `process_quiz.py`
2. **Run this after EVERY quiz** to build up your historical data
3. **Review `mistakes_by_category.md`** to identify your weak topics
4. **Study your weak categories** to improve your scores over time

## 🔧 Troubleshooting

### "Quiz data (DC_DATA) not found in HTML"

This means the HTML doesn't contain your quiz results. Solutions:
- Make sure you **completed the quiz** first
- Make sure you're on the **results page** (after finishing the quiz)
- Try manually saving the HTML from the browser (most reliable)

### "defi_du_jour_debug.html not found"

You need to save the quiz results HTML first. See Option 2 above.

### Parse script shows wrong date

The HTML file contains old data. Re-save the HTML from today's quiz results page.

## 📅 Daily Workflow

**Every day after completing the quiz:**

```bash
# 1. Complete quiz on quizypedia.fr
# 2. On the results page, save HTML as defi_du_jour_debug.html
# 3. Run processing:
uv run scripts/process_quiz.py
```

That's it! Your mistakes will be tracked automatically. 🎯
