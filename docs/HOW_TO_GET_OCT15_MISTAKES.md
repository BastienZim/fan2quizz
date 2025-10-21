# How to Get Your Mistakes from October 15th

Quick guide to retrieve your actual wrong answers from a specific past date.

## Steps

1. **Go to archive page:**
   ```
   https://www.quizypedia.fr/defi-du-jour/archives/2025/10/15/
   ```

2. **Log in** to your Quizypedia account

3. **Click "Afficher les questions et les réponses"**
   This loads YOUR personal answers

4. **Save the page:**
   - Right-click → "Save Page As..."
   - Save as: `defi_du_jour_debug.html`
   - Save in project root directory

5. **Process the saved HTML:**
   ```bash
   cd /home/bastienzim/Documents/perso/fan2quizz
   uv run scripts/parse_results.py
   uv run scripts/accumulate_mistakes.py
   uv run scripts/generate_failed_questions.py --order category
   ```

6. **View your mistakes:**
   ```bash
   # Just Oct 15
   uv run scripts/generate_failed_questions.py --filter "2025-10-15"
   
   # Full history
   uv run scripts/fetch_historical_mistakes.py --check
   ```

## What You'll Get

- ✅ All 20 questions from October 15
- ✅ Correct answers
- ✅ YOUR specific wrong answers
- ✅ Categories for each question
- ✅ Hints provided
- ✅ Complete study materials

## Repeat for Other Dates

Replace date in URL:
- Oct 14: `.../archives/2025/10/14/`
- Oct 13: `.../archives/2025/10/13/`
- etc.

Each time:
1. Click "Afficher les questions et les réponses"
2. Save as `defi_du_jour_debug.html` (overwrite previous)
3. Run processing scripts again

Mistakes are added to your history each time!

## Alternative: Automated (Limited)

For questions and correct answers only (without your specific choices):
```bash
uv run scripts/fetch_historical_mistakes.py --date 2025-10-15
```

Shows questions and your score, but NOT which answers you chose.

## For Future

Avoid this manual process by running daily workflow:
```bash
uv run scripts/complete_workflow.py
```

Run on same day as quiz to automatically capture everything.
