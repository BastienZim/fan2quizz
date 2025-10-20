# Score Evolution Plots - Quick Reference

## 📊 Generated Visualizations (Enhanced with Seaborn!)

All plots now use **seaborn** for professional, publication-quality visualizations with improved readability and aesthetics.

Your workspace contains matplotlib/seaborn plots in `data/figures/`:

### 1. **score_evolution.png** - All Players Overview
- **X-axis**: Date (formatted as "Mon DD")
- **Y-axis**: Score (0-20)
- **Curves**: All 10 tracked players with distinct colors
- **Enhanced Features**: 
  - ✨ Seaborn color palette (husl) for better color distinction
  - 📍 Score values labeled with styled boxes
  - 📊 Reference lines at 50% (10/20) and 75% (15/20)
  - 🎨 Background shading for score ranges (red/yellow/green)
  - 📈 Thicker lines (3px) with white borders on markers
  - 🧹 Clean design with removed spines
  - 🎯 Professional grid styling

### 2. **score_comparison.png** - Individual Subplots
- **Layout**: 3x4 grid of individual player charts
- **Each subplot shows**:
  - 🎨 Filled area under curve for better visibility
  - Player's score trend with styled markers
  - Average score and trend indicator (↗/↘/→)
  - Dashed line at player's average
  - Score values in styled boxes
  - White background with clean grid

### 3. **top_competition.png** - You vs Top Competitors
- **Players**: Bastien, Louis, Julien
- **Focus**: Direct comparison with main rivals
- **Cleaner**: Fewer curves, easier to read trends

## 🎨 Seaborn Enhancements

### Visual Improvements
- **Color Palette**: HUSL color space for maximum distinction
- **Typography**: Larger, bolder fonts for better readability
- **Grid Style**: Professional whitegrid with subtle lines
- **Markers**: Larger markers (10px) with white edges
- **Line Width**: Thicker lines (3px) for clarity
- **Labels**: Styled boxes with semi-transparent backgrounds
- **Shading**: Score range indicators (red: 0-10, yellow: 10-15, green: 15-20)

## 🛠️ How to Regenerate Plots

**Note**: All plots are automatically saved to `data/figures/` directory.

### Basic Commands

```bash
# All players (default)
uv run scripts/plot_evolution.py

# Specific players
uv run scripts/plot_evolution.py --players BastienZim louish jutabouret

# Custom output file
uv run scripts/plot_evolution.py --output my_plot.png

# Both main plot and subplots
uv run scripts/plot_evolution.py --both
```

### Styling Options

```bash
# Dark theme
uv run scripts/plot_evolution.py --style dark

# ggplot style
uv run scripts/plot_evolution.py --style ggplot

# Seaborn style
uv run scripts/plot_evolution.py --style seaborn
```

### Interactive Display

```bash
# Show plot interactively (don't just save)
uv run scripts/plot_evolution.py --show

# Show specific players interactively
uv run scripts/plot_evolution.py --players BastienZim louish --show
```

### Comparison Subplots

```bash
# Individual player subplots only
uv run scripts/plot_evolution.py --comparison

# Save to specific file
uv run scripts/plot_evolution.py --comparison --output comparison.png
```

## 📈 What the Plots Show

### Key Insights from Current Data

**Louis (🥇):**
- Started strong (16/20 on Oct 13)
- Dipped mid-week (11/20)
- Strong recovery (15/20 on Oct 17-18)
- Currently declining (12/20 on Oct 19)

**Julien (🥈):**
- Steady improvement trend
- Started at 13, ended at 15
- Most consistent upward trajectory
- Best current form

**You (Bastien):**
- Mid-range performance (10-14/20)
- Peak on Oct 16 (14/20)
- Recent decline (10/20 on Oct 17 & 19)
- More volatile than top players

**Clement:**
- Started strong but declining
- Missing recent days (no data Oct 18-19)
- Lowest recent score (8/20 on Oct 17)

## 🎯 Analysis Tips

### Look for:
1. **Trends**: Who's improving vs declining?
2. **Consistency**: Who has steadiest scores?
3. **Volatility**: Large score swings indicate unreliable performance
4. **Recent form**: Last 2-3 days matter most
5. **Gaps**: Missing data points (player didn't play that day)

### Action Items Based on Plots:
- **If your line is below others**: Review mistakes in those categories
- **If your line is volatile**: Focus on consistency, not speed
- **If your line is declining**: Check recent mistakes for patterns
- **If gaps appear**: Maintain daily participation for better tracking

## 🔄 Update Workflow

**After each new quiz:**

1. Fetch and process data:
   ```bash
   uv run scripts/complete_workflow.py
   ```

2. Regenerate plots:
   ```bash
   uv run scripts/plot_evolution.py --both
   ```

3. Review updated visualizations to track progress

## 💡 Advanced Usage

### Export for Presentations

```bash
# High-resolution PNG (300 DPI)
uv run scripts/plot_evolution.py --output presentation.png

# Dark theme for slides
uv run scripts/plot_evolution.py --style dark --output slides.png
```

### Focus on Specific Matchup

```bash
# You vs Louis (direct competition)
uv run scripts/plot_evolution.py --players BastienZim louish --output vs_louis.png

# Top 3 players only
uv run scripts/plot_evolution.py --players louish jutabouret BastienZim
```

### Create Weekly Reports

```bash
# Generate all visualizations
uv run scripts/plot_evolution.py --both

# View evolution data
uv run scripts/player_evolution.py --table

# Check personal stats
uv run scripts/inspect_history.py --detailed
```

## 📊 Plot Features Explained

### Main Plot (score_evolution.png)
- **Markers**: Circles on each data point
- **Lines**: Connect consecutive days
- **Labels**: Score value above each point
- **Grid**: Helps read exact values
- **Legend**: Player names (right side)
- **Reference lines**: Gray dotted lines at 10 and 15

### Comparison Plot (score_comparison.png)
- **Title per subplot**: Shows avg and trend
- **Individual scales**: Each player's full journey
- **Trend indicators**: 📈 (improving), 📉 (declining), ➡️ (stable)
- **Compact date format**: MM-DD only

## 🎨 Color Scheme

Each player has a consistent color across all plots:
- Red tones: #E63946, #E74C3C
- Blue tones: #457B9D, #3498DB
- Green tones: #2A9D8F, #2ECC71
- Orange/Yellow: #F4A261, #F39C12
- Purple: #9B59B6
- Turquoise: #1ABC9C

This ensures easy recognition across different visualizations.

## 🔧 Troubleshooting

### "matplotlib is not installed"
```bash
uv pip install matplotlib
```

### "No data found"
- Ensure data exists in `data/cache/archive/`
- Run `daily_report.py` to fetch data first

### Emoji warnings (harmless)
The warnings about missing emoji glyphs are cosmetic only and don't affect the plots.

### Plot doesn't show
- Use `--show` flag to display interactively
- Or just open the PNG file in any image viewer

---

**Last Updated**: 2025-10-20  
**Data Range**: 2025-10-13 to 2025-10-19 (7 days)  
**Total Players Tracked**: 10
