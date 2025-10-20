# Quiz History Analysis Tools

This document describes the data analysis scripts available for inspecting your quiz history.

## 📊 Available Data

Your workspace contains the following historical data:

### 1. **Archive Data** (`data/cache/archive/`)
- Daily leaderboard data from quizypedia.fr
- Contains scores, times, and ranks for all players
- Available dates: 2025-10-13 to 2025-10-19 (7 days)

### 2. **Personal Mistakes** (`mistakes_history.json`)
- Your incorrect answers with full details
- Includes question, hints, your answer, and correct answer
- Organized by date and category

### 3. **Quiz Results** (`defi_du_jour_results.json`)
- Latest quiz detailed results
- Question-by-question breakdown

## 🛠️ Analysis Scripts

### 1. **inspect_history.py** - Personal Performance Overview

Get insights into your personal quiz history.

```bash
# Overview (default)
uv run scripts/inspect_history.py

# Detailed performance trends
uv run scripts/inspect_history.py --detailed

# Deep dive into mistakes
uv run scripts/inspect_history.py --mistakes

# Compare with friends
uv run scripts/inspect_history.py --compare

# Specific date analysis
uv run scripts/inspect_history.py --date 2025-10-17

# Everything at once
uv run scripts/inspect_history.py --all
```

**Shows:**
- Total quizzes completed
- Average score, time, and rank
- Best and worst performances
- Mistakes by category
- Improvement trends
- Friend comparison

### 2. **player_evolution.py** - Track Score Evolution

See how players' scores evolve day by day.

```bash
# View your evolution
uv run scripts/player_evolution.py --player BastienZim

# View all tracked friends
uv run scripts/player_evolution.py

# View specific players
uv run scripts/player_evolution.py --players BastienZim louish jutabouret

# Compact table view
uv run scripts/player_evolution.py --table

# Export to CSV for Excel/Sheets
uv run scripts/player_evolution.py --csv evolution.csv

# Just show comparison summary
uv run scripts/player_evolution.py --summary
```

**Shows:**
- Daily score progression with visual bars
- Score changes day-to-day (+/- indicators)
- Performance statistics (avg, best, worst)
- Trend analysis (improving/declining)
- Player rankings
- Comparison with friends

## 📈 Your Current Stats (as of 2025-10-19)

**Personal Performance:**
- Quizzes Completed: 7/7
- Average Score: 11.4/20 (57%)
- Average Time: 262 seconds (~4.4 minutes)
- Average Rank: 995
- Best Score: 14/20 (2025-10-16)
- Worst Score: 10/20 (2025-10-17, 2025-10-19)
- Trend: -2.0 points 📉 (from 12 to 10)

**Mistakes:**
- Total Mistakes: 16
- Unique Categories: 16
- Mistake Rate: 11.4%

**Friend Rankings (by avg score):**
1. 🥇 François: 14.0/20 (2 games)
2. 🥈 Louis: 13.3/20 (7 games)
3. 🥉 Julien: 13.0/20 (7 games)
4. **Bastien: 11.4/20 (7 games)** ← You are here
5. Clement: 11.4/20 (5 games)

## 💡 Insights & Recommendations

### Strengths
- Consistent participation (7/7 days)
- Reasonable completion time (~4.4 min avg)

### Areas for Improvement
1. **Recent Trend**: Scores declining in last 3 quizzes (avg 10.7 vs first 3: 11.3)
2. **Gap to Leaders**: 1.9 points behind Louis, 1.6 points behind Julien
3. **Consistency**: Score variance from 10-14, aim for more stable high scores

### Action Items
1. 📚 Review `mistakes_by_category.md` to identify weak topics
2. 🎯 Focus on categories where you made mistakes
3. ⏱️ Maintain current speed but verify answers more carefully
4. 📊 Track daily to spot patterns in difficult questions
5. 💪 Target: reach 13-14/20 consistently to compete with Louis & Julien

## 🔄 Daily Workflow

**After each quiz:**
1. Fetch & process: `uv run scripts/complete_workflow.py`
2. Check evolution: `uv run scripts/player_evolution.py --player BastienZim`
3. Review mistakes: `cat mistakes_by_category.md`
4. Compare: `uv run scripts/inspect_history.py --compare`

## 📁 Export Options

All data can be exported for further analysis:

```bash
# Export evolution to CSV
uv run scripts/player_evolution.py --csv scores.csv

# View in spreadsheet software (Excel, Google Sheets, LibreOffice)
# Create charts, pivot tables, etc.
```

## 🎯 Goals

Set realistic goals based on your data:

- **Short-term** (1 week): Average 12/20, beat Clement
- **Medium-term** (1 month): Average 13/20, compete with Julien
- **Long-term**: Consistent 14+/20, challenge Louis & François

Track progress weekly with:
```bash
uv run scripts/inspect_history.py --detailed
```

---

**Remember:** Consistency beats perfection. Keep playing daily and reviewing mistakes! 🚀
