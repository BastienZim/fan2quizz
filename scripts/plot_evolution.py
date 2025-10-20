#!/usr/bin/env python3
"""Generate matplotlib plots showing score evolution over time.

This script creates visualizations of player performance using matplotlib,
with dates on x-axis and scores on y-axis, one curve per player.

Usage:
    uv run scripts/plot_evolution.py                     # All players
    uv run scripts/plot_evolution.py --players BastienZim louish jutabouret
    uv run scripts/plot_evolution.py --output evolution.png
    uv run scripts/plot_evolution.py --style dark        # Dark theme
    uv run scripts/plot_evolution.py --show              # Display interactively
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "data" / "cache" / "archive"
FIGURES_DIR = ROOT / "data" / "figures"

# Ensure figures directory exists
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Default players to track
DEFAULT_PLAYERS = [
    "jutabouret", "louish", "KylianMbappe", "BastienZim", 
    "kamaiel", "phllbrn", "DestroyOps", "pascal-condamine",
    "ColonelProut", "fpCraft"
]

REAL_NAMES = {
    "jutabouret": "Julien",
    "louish": "Louis",
    "kylianmbappe": "Clement",
    "bastienzim": "Bastien",
    "kamaiel": "Raphael",
    "phllbrn": "Ophélie",
    "destroyops": "Alexis",
    "pascal-condamine": "Pascal",
    "colonelprout": "Lucas",
    "fpcraft": "François",
}

# Color palette for players
COLORS = [
    '#E63946',  # Red
    '#457B9D',  # Blue
    '#2A9D8F',  # Teal
    '#F4A261',  # Orange
    '#9B59B6',  # Purple
    '#E74C3C',  # Bright red
    '#3498DB',  # Bright blue
    '#2ECC71',  # Green
    '#F39C12',  # Yellow-orange
    '#1ABC9C',  # Turquoise
]

# Different line styles for better distinction
LINE_STYLES = ['-', '--', '-.', ':', '-', '--', '-.', ':', '-', '--']

# Different marker shapes for better distinction
MARKERS = ['o', 's', '^', 'D', 'v', 'p', '*', 'h', 'X', 'P']


def load_all_archives() -> List[Dict[str, Any]]:
    """Load all archive files."""
    archives = []
    for archive_file in sorted(CACHE_DIR.glob("*.json")):
        if archive_file.name != ".gitkeep":
            try:
                data = json.loads(archive_file.read_text())
                archives.append(data)
            except Exception:
                pass
    return archives


def extract_player_evolution(archives: List[Dict], players: List[str]) -> Dict[str, Dict[str, int]]:
    """Extract score evolution for specified players.
    
    Returns:
        Dict mapping player -> {date -> score}
    """
    evolution = defaultdict(dict)
    
    for archive in archives:
        date = archive.get("date")
        results = archive.get("results", [])
        
        # Extract data for each tracked player
        for entry in results:
            user = entry.get("user", "")
            if user.lower() in [p.lower() for p in players]:
                score = entry.get("good_responses", 0)
                evolution[user.lower()][date] = score
    
    return dict(evolution)


def create_evolution_plot(evolution: Dict[str, Dict], players: List[str], 
                         output_file: str = None, style: str = 'default',
                         show: bool = False):
    """Create a matplotlib plot of score evolution."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        import seaborn as sns
    except ImportError:
        print("❌ Error: matplotlib or seaborn is not installed")
        print("📦 Install them with: uv pip install matplotlib seaborn")
        return False
    
    # Set seaborn style and context
    sns.set_theme(style="whitegrid", context="talk")
    sns.set_palette("husl")
    
    # Set style
    if style == 'dark':
        sns.set_theme(style="darkgrid", context="talk")
        plt.style.use('dark_background')
    elif style == 'ggplot':
        plt.style.use('ggplot')
    elif style == 'seaborn':
        sns.set_theme(style="whitegrid", context="talk")
    
    # Create figure and axis with better proportions
    fig, ax = plt.subplots(figsize=(16, 9))
    
    # Get all dates
    all_dates = set()
    for player_data in evolution.values():
        all_dates.update(player_data.keys())
    dates_sorted = sorted(all_dates)
    
    if not dates_sorted:
        print("⚠️  No data to plot")
        return False
    
    # Plot each player with seaborn color palette
    palette = sns.color_palette("husl", len(players))
    
    for idx, player in enumerate(players):
        player_lower = player.lower()
        if player_lower not in evolution:
            continue
        
        player_data = evolution[player_lower]
        real_name = REAL_NAMES.get(player_lower, player)
        
        # Prepare data for this player
        x_dates = []
        y_scores = []
        
        for date in dates_sorted:
            if date in player_data:
                x_dates.append(datetime.strptime(date, '%Y-%m-%d'))
                y_scores.append(player_data[date])
        
        if not x_dates:
            continue
        
        # Plot line with markers using seaborn palette and varied styles
        color = palette[idx % len(palette)]
        linestyle = LINE_STYLES[idx % len(LINE_STYLES)]
        marker = MARKERS[idx % len(MARKERS)]
        
        ax.plot(x_dates, y_scores, 
                marker=marker, 
                linewidth=3.5, 
                markersize=12,
                label=real_name,
                color=color,
                linestyle=linestyle,
                alpha=0.9,
                markeredgewidth=2.5,
                markeredgecolor='white',
                markerfacecolor=color,
                zorder=10 - idx)  # Higher zorder for earlier players (on top)
        
        # Add value labels on points with better styling
        for x, y in zip(x_dates, y_scores):
            ax.annotate(f'{y}', 
                       xy=(x, y), 
                       xytext=(0, 12),
                       textcoords='offset points',
                       ha='center',
                       fontsize=10,
                       fontweight='bold',
                       alpha=0.85,
                       bbox=dict(boxstyle='round,pad=0.4', 
                               facecolor=color, 
                               alpha=0.25,
                               edgecolor=color,
                               linewidth=1.5),
                       zorder=20)
    
    # Formatting with enhanced styling
    ax.set_xlabel('Date', fontsize=14, fontweight='bold', labelpad=10)
    ax.set_ylabel('Score (out of 20)', fontsize=14, fontweight='bold', labelpad=10)
    ax.set_title('Quiz Score Evolution Over Time', 
                fontsize=18, 
                fontweight='bold', 
                pad=20,
                loc='left')
    
    # Set y-axis limits and grid
    ax.set_ylim(-0.5, 20.5)
    ax.set_yticks(range(0, 21, 2))
    ax.yaxis.grid(True, alpha=0.3, linestyle='-', linewidth=1)
    ax.xaxis.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    plt.xticks(rotation=30, ha='right', fontsize=11)
    plt.yticks(fontsize=11)
    
    # Add legend with better styling
    legend = ax.legend(loc='upper left', 
                      bbox_to_anchor=(1.02, 1), 
                      fontsize=12,
                      framealpha=0.98,
                      shadow=True,
                      borderpad=1.2,
                      labelspacing=1,
                      handlelength=3,
                      title='Players',
                      title_fontsize=13)
    legend.get_frame().set_facecolor('white')
    legend.get_frame().set_edgecolor('gray')
    legend.get_frame().set_linewidth(1.5)
    
    # Add reference lines with labels
    ax.axhline(y=10, color='red', linestyle=':', alpha=0.4, linewidth=1.5, label='_nolegend_')
    ax.text(0.02, 10.3, '50% (10/20)', 
           transform=ax.get_yaxis_transform(), 
           fontsize=9, color='red', alpha=0.6, 
           verticalalignment='bottom')
    
    ax.axhline(y=15, color='green', linestyle=':', alpha=0.4, linewidth=1.5, label='_nolegend_')
    ax.text(0.02, 15.3, '75% (15/20)', 
           transform=ax.get_yaxis_transform(), 
           fontsize=9, color='green', alpha=0.6,
           verticalalignment='bottom')
    
    # Add subtle background shading for score ranges
    ax.axhspan(15, 20, alpha=0.05, color='green', label='_nolegend_')
    ax.axhspan(10, 15, alpha=0.05, color='yellow', label='_nolegend_')
    ax.axhspan(0, 10, alpha=0.05, color='red', label='_nolegend_')
    
    # Remove top and right spines for cleaner look
    sns.despine()
    
    # Tight layout
    plt.tight_layout()
    
    # Save or show
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✅ Plot saved to: {output_file}")
    
    if show:
        plt.show()
    
    if not show and not output_file:
        # Default: save to file
        default_output = FIGURES_DIR / "score_evolution.png"
        plt.savefig(default_output, dpi=300, bbox_inches='tight')
        print(f"✅ Plot saved to: {default_output}")
    
    plt.close()
    return True


def create_comparison_plot(evolution: Dict[str, Dict], players: List[str],
                          output_file: str = None, show: bool = False):
    """Create a subplot comparison with individual player trends."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        import seaborn as sns
    except ImportError:
        print("❌ Error: matplotlib or seaborn is not installed")
        print("📦 Install them with: uv pip install matplotlib seaborn")
        return False
    
    # Set seaborn style
    sns.set_theme(style="whitegrid", context="talk")
    
    # Filter players with data
    players_with_data = [p for p in players if p.lower() in evolution]
    n_players = len(players_with_data)
    
    if n_players == 0:
        print("⚠️  No data to plot")
        return False
    
    # Create subplots with better spacing
    n_cols = 3
    n_rows = (n_players + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 5 * n_rows))
    fig.patch.set_facecolor('white')
    
    if n_players == 1:
        axes = [axes]
    else:
        axes = axes.flatten()
    
    # Get all dates
    all_dates = set()
    for player_data in evolution.values():
        all_dates.update(player_data.keys())
    dates_sorted = sorted(all_dates)
    
    # Use seaborn color palette
    palette = sns.color_palette("husl", n_players)
    
    # Plot each player
    for idx, player in enumerate(players_with_data):
        player_lower = player.lower()
        player_data = evolution[player_lower]
        real_name = REAL_NAMES.get(player_lower, player)
        
        ax = axes[idx]
        
        # Prepare data
        x_dates = []
        y_scores = []
        
        for date in dates_sorted:
            if date in player_data:
                x_dates.append(datetime.strptime(date, '%Y-%m-%d'))
                y_scores.append(player_data[date])
        
        if not x_dates:
            ax.set_visible(False)
            continue
        
        # Plot with seaborn styling
        color = palette[idx % len(palette)]
        marker = MARKERS[idx % len(MARKERS)]
        linestyle = LINE_STYLES[idx % len(LINE_STYLES)]
        
        # Fill area under curve for better visibility
        ax.fill_between(x_dates, 0, y_scores, alpha=0.15, color=color)
        
        # Plot line
        ax.plot(x_dates, y_scores, 
               marker=marker, 
               linewidth=3.5, 
               markersize=12,
               color=color,
               linestyle=linestyle,
               markeredgewidth=2.5,
               markeredgecolor='white',
               markerfacecolor=color)
        
        # Add value labels with better styling
        for x, y in zip(x_dates, y_scores):
            ax.annotate(f'{y}', 
                       xy=(x, y), 
                       xytext=(0, 10),
                       textcoords='offset points',
                       ha='center',
                       fontsize=11,
                       fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.4', 
                               facecolor='white', 
                               alpha=0.85,
                               edgecolor=color,
                               linewidth=2))
        
        # Formatting with stats in title
        avg_score = sum(y_scores) / len(y_scores)
        trend = y_scores[-1] - y_scores[0] if len(y_scores) > 1 else 0
        trend_arrow = "↗" if trend > 0 else "↘" if trend < 0 else "→"
        
        ax.set_title(f'{real_name}\nAvg: {avg_score:.1f}  |  Trend: {trend:+.0f} {trend_arrow}', 
                    fontweight='bold',
                    fontsize=12,
                    pad=10)
        ax.set_ylim(-0.5, 20.5)
        ax.set_yticks(range(0, 21, 5))
        ax.yaxis.grid(True, alpha=0.3, linestyle='-')
        ax.xaxis.grid(True, alpha=0.2, linestyle='--')
        ax.set_axisbelow(True)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=40, ha='right', fontsize=9)
        
        # Add reference line at average
        ax.axhline(y=avg_score, color=color, linestyle='--', alpha=0.3, linewidth=2)
        
        # Remove spines
        sns.despine(ax=ax)
    
    # Hide unused subplots
    for idx in range(n_players, len(axes)):
        axes[idx].set_visible(False)
    
    plt.suptitle('Individual Player Score Trends', 
                fontsize=20, 
                fontweight='bold', 
                y=0.998,
                x=0.05,
                ha='left')
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    
    # Save or show
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✅ Comparison plot saved to: {output_file}")
    
    if show:
        plt.show()
    
    if not show and not output_file:
        default_output = FIGURES_DIR / "score_comparison.png"
        plt.savefig(default_output, dpi=300, bbox_inches='tight')
        print(f"✅ Comparison plot saved to: {default_output}")
    
    plt.close()
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Generate matplotlib plots of score evolution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Plot all tracked players
  uv run scripts/plot_evolution.py
  
  # Plot specific players
  uv run scripts/plot_evolution.py --players BastienZim louish jutabouret
  
  # Save to specific file
  uv run scripts/plot_evolution.py --output my_plot.png
  
  # Use dark theme
  uv run scripts/plot_evolution.py --style dark
  
  # Show interactively (don't just save)
  uv run scripts/plot_evolution.py --show
  
  # Create comparison subplots
  uv run scripts/plot_evolution.py --comparison
  
  # Both main plot and comparison
  uv run scripts/plot_evolution.py --both
        """
    )
    
    parser.add_argument('--players', nargs='+', 
                       help='Specific players to plot (default: all tracked)')
    parser.add_argument('--output', '-o', 
                       help='Output file path (default: score_evolution.png)')
    parser.add_argument('--style', choices=['default', 'dark', 'ggplot', 'seaborn'],
                       default='default',
                       help='Plot style theme')
    parser.add_argument('--show', action='store_true',
                       help='Display plot interactively')
    parser.add_argument('--comparison', action='store_true',
                       help='Create comparison subplots instead of single plot')
    parser.add_argument('--both', action='store_true',
                       help='Create both main plot and comparison')
    
    args = parser.parse_args()
    
    # Determine players
    players = args.players if args.players else DEFAULT_PLAYERS
    
    # Load data
    print("📊 Loading quiz data...")
    archives = load_all_archives()
    
    if not archives:
        print("❌ No archive data found!")
        print("💡 Make sure you have data in data/cache/archive/")
        return 1
    
    print(f"✅ Loaded {len(archives)} days of data")
    
    evolution = extract_player_evolution(archives, players)
    
    if not evolution:
        print("❌ No data found for specified players")
        return 1
    
    print(f"✅ Found data for {len(evolution)} player(s)")
    
    # Create plots
    success = False
    
    if args.both:
        # Create both plots
        print("\n📈 Creating main evolution plot...")
        output1 = args.output or str(FIGURES_DIR / "score_evolution.png")
        success1 = create_evolution_plot(evolution, players, output1, args.style, args.show)
        
        print("\n📊 Creating comparison subplots...")
        output2 = str(FIGURES_DIR / "score_comparison.png")
        success2 = create_comparison_plot(evolution, players, output2, args.show)
        
        success = success1 or success2
    elif args.comparison:
        print("\n📊 Creating comparison subplots...")
        success = create_comparison_plot(evolution, players, args.output, args.show)
    else:
        print("\n📈 Creating evolution plot...")
        success = create_evolution_plot(evolution, players, args.output, args.style, args.show)
    
    if success:
        print("\n✅ Done!")
        if not args.show:
            print("💡 Tip: Use --show to display interactively")
            print("💡 Tip: Use --comparison for individual player subplots")
            print("💡 Tip: Use --both for all visualizations")
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
