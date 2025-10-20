# How to Get Your Mistakes from October 15th

## Complete Solution (Recommended)

Follow these steps to get your actual wrong answers from October 15, 2025:

### Step 1: Go to the Archive Page
Open your browser and visit:
```
https://www.quizypedia.fr/defi-du-jour/archives/2025/10/15/
```

### Step 2: Log In
Make sure you're logged in to your Quizypedia account.

### Step 3: Click the Button
Click on **"Afficher les questions et les réponses"** (Show questions and answers)

This will load the quiz with YOUR personal answers highlighted.

### Step 4: Save the Page
- Right-click anywhere on the page
- Select "Save Page As..." or "Save As..."  
- Save the file as: `defi_du_jour_debug.html`
- Save it in your `fan2quizz` project root directory

### Step 5: Process the Saved HTML
Run these commands in your terminal:

```bash
cd /home/bastienzim/Documents/perso/fan2quizz

# Parse the saved HTML
uv run scripts/parse_results.py

# Add mistakes to your history
uv run scripts/accumulate_mistakes.py

# Generate updated study guide
uv run scripts/generate_failed_questions.py --order category
```

### Step 6: View Your Mistakes
```bash
# See just Oct 15 mistakes
uv run scripts/generate_failed_questions.py --filter "2025-10-15"

# Or check the full history
uv run scripts/fetch_historical_mistakes.py --check
```

## What You'll Get

After following these steps, you'll have:
- ✅ All 20 questions from October 15
- ✅ The correct answers
- ✅ YOUR specific wrong answers (for the 9 you got wrong)
- ✅ Categories for each question
- ✅ Hints that were provided
- ✅ Complete study materials

## Repeat for Other Dates

You can repeat this process for any other dates:
- Oct 14: `https://www.quizypedia.fr/defi-du-jour/archives/2025/10/14/`
- Oct 13: `https://www.quizypedia.fr/defi-du-jour/archives/2025/10/13/`
- etc.

Just remember to:
1. Click "Afficher les questions et les réponses"
2. Save as `defi_du_jour_debug.html` (overwrite the previous one)
3. Run the processing scripts again

Each time you run it, the mistakes will be added to your history!

## Alternative: Automated (Limited)

If you just want to see the questions and correct answers without your specific wrong choices:

```bash
uv run scripts/fetch_historical_mistakes.py --date 2025-10-15
```

This will show:
- ✅ Questions and correct answers
- ✅ Your score (11/20)
- ❌ NOT which specific answers you chose

## Tips

**For the future:** To avoid this manual process, use the daily workflow:
```bash
uv run scripts/complete_workflow.py
```

Run this on the same day you complete the quiz, and it will automatically:
- Fetch the quiz with your answers
- Log all mistakes
- Generate reports

**Batch processing:** If you have multiple dates to process:
1. Save HTML for date 1 → process → save results
2. Save HTML for date 2 → process → save results  
3. etc.

The `accumulate_mistakes.py` script will keep adding to your history without duplicates.
