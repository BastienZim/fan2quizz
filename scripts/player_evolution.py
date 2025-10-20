#!/usr/bin/env python3
"""Track player score evolution over time.

This script shows how players' scores evolve day by day, making it easy
to spot trends, improvements, and compare trajectories.

Usage:
    uv run scripts/player_evolution.py                    # All tracked players
    uv run scripts/player_evolution.py --player BastienZim  # Specific player
    uv run scripts/player_evolution.py --players BastienZim louish kamaiel  # Multiple
    uv run scripts/player_evolution.py --table             # Table format
    uv run scripts/player_evolution.py --csv output.csv    # Export to CSV
"""
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "data" / "cache" / "archive"

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


def extract_player_evolution(archives: List[Dict], players: List[str]) -> Dict[str, Dict[str, Any]]:
    """Extract score evolution for specified players.
    
    Returns:
        Dict mapping player -> {date -> {score, time, rank, total_players}}
    """
    evolution = defaultdict(dict)
    
    for archive in archives:
        date = archive.get("date")
        results = archive.get("results", [])
        total_players = len(results)
        
        # Extract data for each tracked player
        for entry in results:
            user = entry.get("user", "")
            if user.lower() in [p.lower() for p in players]:
                evolution[user.lower()][date] = {
                    "score": entry.get("good_responses", 0),
                    "time": entry.get("elapsed_time", 0),
                    "rank": entry.get("rank", 0),
                    "total_players": total_players
                }
    
    return dict(evolution)


def print_evolution_chart(evolution: Dict[str, Dict], players: List[str]):
    """Print a visual chart of score evolution."""
    print("=" * 100)
    print("📈 PLAYER SCORE EVOLUTION")
    print("=" * 100)
    
    # Get all dates
    all_dates = set()
    for player_data in evolution.values():
        all_dates.update(player_data.keys())
    dates = sorted(all_dates)
    
    if not dates:
        print("\n⚠️  No data available for the specified players.")
        return
    
    print(f"\n📅 Date Range: {dates[0]} → {dates[-1]} ({len(dates)} days)")
    print(f"👥 Players: {len(evolution)}")
    print()
    
    # Print for each player
    for player in players:
        player_lower = player.lower()
        if player_lower not in evolution:
            continue
        
        player_data = evolution[player_lower]
        real_name = REAL_NAMES.get(player_lower, player)
        
        print(f"\n{'='*100}")
        print(f"👤 {real_name} ({player})")
        print(f"{'='*100}")
        
        scores = []
        for date in dates:
            if date in player_data:
                data = player_data[date]
                score = data["score"]
                time = data["time"]
                rank = data["rank"]
                
                # Visual bar
                bar = "█" * score + "░" * (20 - score)
                
                # Score change indicator
                if scores:
                    diff = score - scores[-1]
                    if diff > 0:
                        change = f"(+{diff})"
                    elif diff < 0:
                        change = f"({diff})"
                    else:
                        change = "(=)"
                else:
                    change = ""
                
                scores.append(score)
                
                print(f"   {date}: {bar} {score:2d}/20 {change:5s} | {time:3d}s | Rank: {rank:4d}")
            else:
                print(f"   {date}: {'─'*40} --/-- (no data)")
        
        if scores:
            avg = sum(scores) / len(scores)
            best = max(scores)
            worst = min(scores)
            trend = scores[-1] - scores[0] if len(scores) > 1 else 0
            
            print(f"\n   📊 Stats:")
            print(f"      Games Played: {len(scores)}/{len(dates)}")
            print(f"      Average: {avg:.1f}/20")
            print(f"      Best: {best}/20")
            print(f"      Worst: {worst}/20")
            if len(scores) > 1:
                trend_arrow = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
                print(f"      Trend: {trend:+.1f} {trend_arrow}")


def print_evolution_table(evolution: Dict[str, Dict], players: List[str]):
    """Print evolution in table format."""
    print("=" * 120)
    print("📊 SCORE EVOLUTION TABLE")
    print("=" * 120)
    
    # Get all dates
    all_dates = set()
    for player_data in evolution.values():
        all_dates.update(player_data.keys())
    dates = sorted(all_dates)
    
    if not dates:
        print("\n⚠️  No data available.")
        return
    
    # Print header
    print(f"\n{'Player':<15}", end="")
    for date in dates:
        print(f" {date[5:]:>10}", end="")  # Just MM-DD
    print("  Avg")
    print("-" * 120)
    
    # Print each player's row
    for player in players:
        player_lower = player.lower()
        if player_lower not in evolution:
            continue
        
        player_data = evolution[player_lower]
        real_name = REAL_NAMES.get(player_lower, player)
        
        scores = []
        print(f"{real_name:<15}", end="")
        
        for date in dates:
            if date in player_data:
                score = player_data[date]["score"]
                scores.append(score)
                print(f" {score:>2d}/20 {' ':>3}", end="")
            else:
                print(f" {'--':>10}", end="")
        
        if scores:
            avg = sum(scores) / len(scores)
            print(f"  {avg:4.1f}")
        else:
            print(f"  {'--':>4}")
    
    print()


def export_to_csv(evolution: Dict[str, Dict], players: List[str], filename: str):
    """Export evolution data to CSV."""
    import csv
    
    # Get all dates
    all_dates = set()
    for player_data in evolution.values():
        all_dates.update(player_data.keys())
    dates = sorted(all_dates)
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Header
        header = ["Player", "Real Name"] + dates + ["Average", "Best", "Worst", "Games Played"]
        writer.writerow(header)
        
        # Data rows
        for player in players:
            player_lower = player.lower()
            if player_lower not in evolution:
                continue
            
            player_data = evolution[player_lower]
            real_name = REAL_NAMES.get(player_lower, player)
            
            row = [player, real_name]
            scores = []
            
            for date in dates:
                if date in player_data:
                    score = player_data[date]["score"]
                    scores.append(score)
                    row.append(score)
                else:
                    row.append("")
            
            # Stats
            if scores:
                row.append(f"{sum(scores) / len(scores):.1f}")
                row.append(max(scores))
                row.append(min(scores))
                row.append(len(scores))
            else:
                row.extend(["", "", "", 0])
            
            writer.writerow(row)
    
    print(f"✅ Exported to {filename}")


def print_comparison_summary(evolution: Dict[str, Dict], players: List[str]):
    """Print a summary comparison of all players."""
    print("\n" + "=" * 100)
    print("🏆 PLAYER COMPARISON SUMMARY")
    print("=" * 100)
    
    stats = []
    for player in players:
        player_lower = player.lower()
        if player_lower not in evolution:
            continue
        
        player_data = evolution[player_lower]
        scores = [data["score"] for data in player_data.values()]
        times = [data["time"] for data in player_data.values()]
        ranks = [data["rank"] for data in player_data.values()]
        
        if scores:
            stats.append({
                "player": player,
                "real_name": REAL_NAMES.get(player_lower, player),
                "avg_score": sum(scores) / len(scores),
                "best_score": max(scores),
                "worst_score": min(scores),
                "avg_time": sum(times) / len(times),
                "avg_rank": sum(ranks) / len(ranks),
                "games": len(scores),
                "trend": scores[-1] - scores[0] if len(scores) > 1 else 0
            })
    
    # Sort by average score
    stats.sort(key=lambda x: x["avg_score"], reverse=True)
    
    print(f"\n{'Rank':<6}{'Player':<15}{'Avg':<8}{'Best':<7}{'Worst':<7}{'Games':<8}{'Trend':<8}{'Avg Rank'}")
    print("-" * 100)
    
    for i, s in enumerate(stats, 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i:2d}."
        trend_arrow = "📈" if s["trend"] > 0 else "📉" if s["trend"] < 0 else "➡️"
        
        print(f"{emoji:<6}{s['real_name']:<15}"
              f"{s['avg_score']:5.1f}   "
              f"{s['best_score']:4.0f}   "
              f"{s['worst_score']:4.0f}   "
              f"{s['games']:5d}   "
              f"{s['trend']:+4.0f} {trend_arrow}  "
              f"{s['avg_rank']:6.0f}")


def main():
    parser = argparse.ArgumentParser(
        description="Track player score evolution over time",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show evolution for all default players
  uv run scripts/player_evolution.py
  
  # Show specific player
  uv run scripts/player_evolution.py --player BastienZim
  
  # Show multiple specific players
  uv run scripts/player_evolution.py --players BastienZim louish kamaiel
  
  # Table format (compact)
  uv run scripts/player_evolution.py --table
  
  # Export to CSV
  uv run scripts/player_evolution.py --csv evolution.csv
  
  # Just show comparison summary
  uv run scripts/player_evolution.py --summary
        """
    )
    
    parser.add_argument('--player', help='Track single player')
    parser.add_argument('--players', nargs='+', help='Track multiple specific players')
    parser.add_argument('--table', action='store_true', help='Show in table format')
    parser.add_argument('--csv', metavar='FILE', help='Export to CSV file')
    parser.add_argument('--summary', action='store_true', help='Show comparison summary only')
    
    args = parser.parse_args()
    
    # Determine which players to track
    if args.player:
        players = [args.player]
    elif args.players:
        players = args.players
    else:
        players = DEFAULT_PLAYERS
    
    # Load data
    archives = load_all_archives()
    evolution = extract_player_evolution(archives, players)
    
    if not evolution:
        print("⚠️  No data found for the specified players.")
        print(f"Available archives: {len(archives)}")
        return 1
    
    # Display based on options
    if args.csv:
        export_to_csv(evolution, players, args.csv)
    elif args.summary:
        print_comparison_summary(evolution, players)
    elif args.table:
        print_evolution_table(evolution, players)
        print_comparison_summary(evolution, players)
    else:
        print_evolution_chart(evolution, players)
        print_comparison_summary(evolution, players)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
