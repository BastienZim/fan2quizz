# 📊 Quick Start: Category Difficulty Radar Chart

## Basic Usage

### Generate chart for yesterday's quiz
```bash
uv run scripts/daily_report.py --radar
```

### Generate chart for a specific date (2 days ago)
```bash
uv run scripts/daily_report.py 2025-10-23 --radar
```

### Generate and display interactively
```bash
uv run scripts/daily_report.py 2025-10-23 --show-radar
```

## Combined with Other Features

### Full report with fun emojis + radar chart
```bash
uv run scripts/daily_report.py --fun --radar
```

### Save table and generate radar chart
```bash
uv run scripts/daily_report.py 2025-10-23 --fun --radar --save-table results.csv
```

### Copy to Slack and generate radar
```bash
uv run scripts/daily_report.py --clipboard-slack --radar
```

## Output Location

Charts are saved to: **`data/figures/category_difficulty_YYYY-MM-DD.png`**

Example:
- `data/figures/category_difficulty_2025-10-22.png`
- `data/figures/category_difficulty_2025-10-23.png`

## What the Chart Shows

### 8 Categories (arranged in a circle):
1. 🎨 Culture classique
2. 🎬 Culture moderne
3. 📚 Culture générale
4. 🗺️ Géographie
5. 📜 Histoire
6. 🌿 Animaux et plantes
7. 🔬 Sciences et techniques
8. ⚽ Sport

### Difficulty Scale (0-5):
- **5 (edge)** = Very easy - high success rate
- **4** = Easy
- **3** = Medium
- **2** = Difficult
- **1** = Very difficult
- **0 (center)** = Extremely difficult - low success rate

### Color Zones:
- 🟢 **Green zone (4-5)**: Easy questions
- 🟡 **Yellow zone (2-4)**: Medium difficulty
- 🔴 **Red zone (0-2)**: Difficult questions

## Interpreting the Chart

### High values (near edge) = Easy category
Questions in this category had high success rates among all players.

### Low values (near center) = Difficult category
Questions in this category were challenging for most players.

### Example Interpretation:

If the chart shows:
- **Sport: 4.5** → Sport questions were easy
- **Sciences et techniques: 2.1** → Science questions were difficult
- **Culture générale: 3.2** → General culture was medium difficulty

## Tips

1. **Compare multiple dates**: Generate charts for consecutive days to see difficulty patterns
2. **Look for spikes**: Sharp points indicate categories with extreme difficulty (easy or hard)
3. **Check symmetry**: A balanced octagon means consistent difficulty across categories
4. **Combine with mistakes report**: Cross-reference with your personal mistakes to see where you struggled

## Example Commands

```bash
# This week's quizzes (generate all charts)
for date in 2025-10-21 2025-10-22 2025-10-23; do
  uv run scripts/daily_report.py $date --radar
done

# View all generated charts
ls -lh data/figures/category_difficulty_*.png

# Generate today's report with everything
uv run scripts/daily_report.py --fun --radar --save-table report.md
```

## See Also

- 📖 [Full Documentation](docs/CATEGORY_RADAR_CHART.md)
- 📊 [Implementation Details](CATEGORY_RADAR_IMPLEMENTATION.md)
- 📈 [Score Evolution Charts](scripts/plot_evolution.py)
- 📝 [Mistakes Reports](scripts/generate_failed_questions.py)

---

**Note**: Current version (v1.0) uses simulated difficulty data for demonstration. Future version (v2.0) will calculate real difficulty based on actual player performance per category.
