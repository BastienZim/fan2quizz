# 📊 Category Difficulty Radar Chart

## Overview

The category difficulty radar chart visualizes the relative difficulty of quiz questions across different thematic categories. This provides a quick visual insight into which topic areas were easier or harder in a given daily quiz.

## Categories

The radar chart displays difficulty scores for 8 quiz categories:

1. **Culture classique** - Classical culture, literature, arts
2. **Culture moderne** - Modern culture, entertainment, pop culture  
3. **Culture générale** - General knowledge
4. **Géographie** - Geography
5. **Histoire** - History
6. **Animaux et plantes** - Animals and plants
7. **Sciences et techniques** - Science and technology
8. **Sport** - Sports

## Difficulty Scale

The chart uses a **0-5 scale** from center to edge:

- **0 (center)**: Very difficult - low player success rate
- **1-2**: Difficult (red zone)
- **2-4**: Medium difficulty (yellow zone)
- **4-5**: Easy (green zone)
- **5 (edge)**: Very easy - high player success rate

## Usage

### Generate radar chart with daily report

```bash
# Generate chart for yesterday (default)
uv run scripts/daily_report.py --radar

# Generate chart for specific date
uv run scripts/daily_report.py 2025-10-22 --radar

# Generate and display interactively
uv run scripts/daily_report.py 2025-10-22 --show-radar
```

### Command-line options

- `--radar`: Generate the category difficulty radar chart
- `--show-radar`: Generate and display the chart interactively (implies `--radar`)

## Output

The chart is saved to: `data/figures/category_difficulty_YYYY-MM-DD.png`

## Implementation Details

### Current Version (v1.0 - Demo)

The current implementation generates **simulated difficulty data** with random values between 2.0-4.5 for demonstration purposes.

### Future Enhancement (v2.0 - Real Data)

To calculate real category difficulty scores, the system needs to:

1. **Parse quiz HTML** from `data/cache/quiz_html/YYYY-MM-DD.html` to extract:
   - Question text
   - Category tags for each question
   - Correct answers

2. **Aggregate player performance** by category:
   - Count correct/incorrect answers per category
   - Calculate success rate: `correct_answers / total_answers`
   - Convert to 0-5 scale: `difficulty_score = success_rate * 5`

3. **Handle missing data**:
   - If a category has no questions, exclude from chart
   - If category data is unavailable, use neutral score (2.5)

### Data Sources

Real implementation should pull from:
- Quiz HTML cache: `data/cache/quiz_html/`
- Player results: `data/cache/archive/YYYY-MM-DD.json`
- Mistakes data: `data/results/mistakes_history.json`

## Example Output

The radar chart shows:
- **Title**: "Difficulté du Quiz par Catégorie" with date
- **8 axes**: One for each category
- **Color zones**: Red (difficult), yellow (medium), green (easy)
- **Legend**: Explains the difficulty scale
- **Note**: Clarifies that 5 = easy, 0 = difficult

## Dependencies

- `matplotlib`: For chart generation
- `matplotlib.patches`: For colored zones

Install with: `uv pip install matplotlib`

## Related Commands

```bash
# Full daily report with all features
uv run scripts/daily_report.py 2025-10-22 --fun --radar --save-table report.csv

# Interactive visualization
uv run scripts/daily_report.py --show-radar

# Check generated figures
ls -lh data/figures/category_difficulty_*.png
```

## Future Enhancements

1. **Real data integration**: Parse actual quiz categories and player performance
2. **Comparison mode**: Overlay multiple dates to see difficulty trends
3. **Category breakdown**: Show which specific questions belonged to each category
4. **Player-specific view**: Compare how different players performed across categories
5. **Historical analysis**: Track category difficulty over time (weekly/monthly averages)
