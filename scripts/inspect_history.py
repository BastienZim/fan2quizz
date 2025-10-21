#!/usr/bin/env python3
"""Inspect and analyze your historical quiz data.

This script provides various analyses of your quiz history:
- Personal performance trends over time
- Mistakes analysis by category
- Comparison with other players
- Detailed statistics and insights

Usage:
    uv run scripts/inspect_history.py                  # Show overview
    uv run scripts/inspect_history.py --detailed       # Detailed analysis
    uv run scripts/inspect_history.py --mistakes       # Focus on mistakes
    uv run scripts/inspect_history.py --compare        # Compare with friends
    uv run scripts/inspect_history.py --date 2025-10-17  # Specific date
"""
import sys
import json
import statistics
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter
import argparse

ROOT = Path(__file__).resolve().parents[1]

# Configuration
CACHE_DIR = ROOT / "data" / "cache" / "archive"
MISTAKES_FILE = ROOT / "data" / "results" / "mistakes_history.json"
RESULTS_FILE = ROOT / "data" / "results" / "defi_du_jour_results.json"

# Friend list for comparison
FRIENDS = ["jutabouret", "louish", "KylianMbappe", "BastienZim", "kamaiel", 
           "phllbrn", "DestroyOps", "pascal-condamine", "ColonelProut", "fpCraft"]

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


def load_mistakes_history() -> List[Dict[str, Any]]:
    """Load mistakes history from JSON file."""
    if not MISTAKES_FILE.exists():
        return []
    return json.loads(MISTAKES_FILE.read_text())


def load_archive_data(date_str: str = None) -> List[Dict[str, Any]]:
    """Load archive data for a specific date or all available dates."""
    archives = []
    
    if date_str:
        archive_file = CACHE_DIR / f"{date_str}.json"
        if archive_file.exists():
            return [json.loads(archive_file.read_text())]
        return []
    
    # Load all archives
    for archive_file in sorted(CACHE_DIR.glob("*.json")):
        if archive_file.name != ".gitkeep":
            try:
                archives.append(json.loads(archive_file.read_text()))
            except:
                pass
    
    return archives


def get_personal_stats(archives: List[Dict[str, Any]], username: str = "BastienZim") -> List[Dict]:
    """Extract personal performance from archive data."""
    personal_history = []
    
    for archive in archives:
        date = archive.get("date")
        results = archive.get("results", [])
        
        # Find personal result
        for entry in results:
            if entry.get("user", "").lower() == username.lower():
                personal_history.append({
                    "date": date,
                    "score": entry.get("good_responses", 0),
                    "time": entry.get("elapsed_time", 0),
                    "rank": entry.get("rank", 0),
                    "total_players": len(results)
                })
                break
    
    return sorted(personal_history, key=lambda x: x["date"])


def analyze_mistakes(mistakes: List[Dict[str, Any]]) -> Dict:
    """Analyze mistakes by category, date, and patterns."""
    if not mistakes:
        return {}
    
    # Group by date
    by_date = defaultdict(list)
    for m in mistakes:
        by_date[m["date"]].append(m)
    
    # Group by category
    by_category = defaultdict(list)
    for m in mistakes:
        by_category[m["category"]].append(m)
    
    # Count categories
    category_counts = Counter(m["category"] for m in mistakes)
    
    return {
        "total_mistakes": len(mistakes),
        "unique_dates": len(by_date),
        "unique_categories": len(by_category),
        "by_date": dict(by_date),
        "by_category": dict(by_category),
        "category_counts": category_counts.most_common(),
        "dates": sorted(by_date.keys())
    }


def compare_with_friends(archives: List[Dict[str, Any]], friends: List[str]) -> Dict:
    """Compare performance with friends."""
    comparison = defaultdict(lambda: {"scores": [], "times": [], "ranks": []})
    
    for archive in archives:
        date = archive.get("date")
        results = archive.get("results", [])
        
        for entry in results:
            user = entry.get("user", "").lower()
            if user in [f.lower() for f in friends]:
                comparison[user]["scores"].append(entry.get("good_responses", 0))
                comparison[user]["times"].append(entry.get("elapsed_time", 0))
                comparison[user]["ranks"].append(entry.get("rank", 0))
    
    # Calculate averages
    summary = {}
    for user, data in comparison.items():
        if data["scores"]:
            summary[user] = {
                "avg_score": statistics.mean(data["scores"]),
                "avg_time": statistics.mean(data["times"]),
                "avg_rank": statistics.mean(data["ranks"]),
                "total_quizzes": len(data["scores"]),
                "best_score": max(data["scores"]),
                "best_rank": min(data["ranks"])
            }
    
    return summary


def print_overview(personal_stats: List[Dict], mistakes_analysis: Dict):
    """Print overview of personal performance."""
    print("=" * 80)
    print("📊 QUIZ HISTORY OVERVIEW")
    print("=" * 80)
    
    if not personal_stats and not mistakes_analysis:
        print("\n⚠️  No historical data found.")
        print("💡 Make sure you have:")
        print("   - Archive files in data/cache/archive/")
        print("   - Mistakes logged in mistakes_history.json")
        return
    
    # Personal stats
    if personal_stats:
        print(f"\n📅 Quizzes Completed: {len(personal_stats)}")
        print(f"   Date Range: {personal_stats[0]['date']} → {personal_stats[-1]['date']}")
        
        avg_score = statistics.mean(s["score"] for s in personal_stats)
        avg_time = statistics.mean(s["time"] for s in personal_stats)
        avg_rank = statistics.mean(s["rank"] for s in personal_stats)
        
        best_quiz = max(personal_stats, key=lambda x: x["score"])
        worst_quiz = min(personal_stats, key=lambda x: x["score"])
        
        print(f"\n🎯 Performance Metrics:")
        print(f"   Average Score: {avg_score:.1f}/20")
        print(f"   Average Time: {avg_time:.0f} seconds ({avg_time/60:.1f} minutes)")
        print(f"   Average Rank: {avg_rank:.0f}")
        
        print(f"\n🏆 Best Quiz: {best_quiz['date']}")
        print(f"   Score: {best_quiz['score']}/20, Time: {best_quiz['time']}s, Rank: {best_quiz['rank']}")
        
        print(f"\n📉 Toughest Quiz: {worst_quiz['date']}")
        print(f"   Score: {worst_quiz['score']}/20, Time: {worst_quiz['time']}s, Rank: {worst_quiz['rank']}")
    
    # Mistakes analysis
    if mistakes_analysis:
        print(f"\n❌ Mistakes Summary:")
        print(f"   Total Mistakes: {mistakes_analysis['total_mistakes']}")
        print(f"   Unique Categories: {mistakes_analysis['unique_categories']}")
        print(f"   Mistake Rate: {mistakes_analysis['total_mistakes'] / (len(personal_stats) * 20) * 100:.1f}%" if personal_stats else "")
        
        print(f"\n🎯 Top 5 Problem Categories:")
        for i, (category, count) in enumerate(mistakes_analysis['category_counts'][:5], 1):
            print(f"   {i}. {category}: {count} mistake(s)")


def print_detailed_analysis(personal_stats: List[Dict], mistakes_analysis: Dict):
    """Print detailed analysis with trends and insights."""
    print("\n" + "=" * 80)
    print("📈 DETAILED PERFORMANCE ANALYSIS")
    print("=" * 80)
    
    if not personal_stats:
        print("\n⚠️  No personal performance data available.")
        return
    
    # Score trend
    print("\n📊 Score Trend (last 7 quizzes):")
    recent = personal_stats[-7:]
    for stat in recent:
        bar = "█" * stat["score"] + "░" * (20 - stat["score"])
        print(f"   {stat['date']}: {bar} {stat['score']}/20 ({stat['time']}s, rank {stat['rank']})")
    
    # Calculate improvement
    if len(personal_stats) >= 3:
        first_three = statistics.mean(s["score"] for s in personal_stats[:3])
        last_three = statistics.mean(s["score"] for s in personal_stats[-3:])
        improvement = last_three - first_three
        
        print(f"\n📈 Improvement Analysis:")
        print(f"   First 3 quizzes avg: {first_three:.1f}/20")
        print(f"   Last 3 quizzes avg: {last_three:.1f}/20")
        if improvement > 0:
            print(f"   Improvement: +{improvement:.1f} points! 🎉")
        elif improvement < 0:
            print(f"   Change: {improvement:.1f} points 📉")
        else:
            print(f"   Stable performance 😐")
    
    # Time analysis
    times = [s["time"] for s in personal_stats]
    print(f"\n⏱️  Time Analysis:")
    print(f"   Fastest: {min(times)}s")
    print(f"   Slowest: {max(times)}s")
    print(f"   Average: {statistics.mean(times):.0f}s")
    print(f"   Median: {statistics.median(times):.0f}s")


def print_mistakes_focus(mistakes_analysis: Dict):
    """Print detailed mistakes analysis."""
    print("\n" + "=" * 80)
    print("❌ MISTAKES DEEP DIVE")
    print("=" * 80)
    
    if not mistakes_analysis:
        print("\n✅ No mistakes recorded yet!")
        return
    
    print(f"\n📚 By Category ({mistakes_analysis['unique_categories']} categories):")
    for category, count in mistakes_analysis['category_counts'][:10]:
        print(f"   • {category}: {count} mistake(s)")
    
    print(f"\n📅 By Date:")
    for date in mistakes_analysis['dates']:
        mistakes = mistakes_analysis['by_date'][date]
        print(f"\n   {date}: {len(mistakes)} mistake(s)")
        for m in mistakes[:3]:  # Show first 3
            print(f"      - {m['category']}: {m['question'][:60]}...")


def print_comparison(comparison: Dict):
    """Print comparison with friends."""
    print("\n" + "=" * 80)
    print("👥 COMPARISON WITH FRIENDS")
    print("=" * 80)
    
    if not comparison:
        print("\n⚠️  No friend data available.")
        return
    
    # Sort by average score
    sorted_friends = sorted(comparison.items(), key=lambda x: x[1]["avg_score"], reverse=True)
    
    print(f"\n🏆 Leaderboard (Average Score):")
    for i, (user, stats) in enumerate(sorted_friends, 1):
        real_name = REAL_NAMES.get(user, user)
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        print(f"   {emoji} {i}. {real_name:12} - {stats['avg_score']:.1f}/20 "
              f"(avg rank: {stats['avg_rank']:.0f}, {stats['total_quizzes']} quizzes)")
    
    # Find your position
    your_pos = next((i for i, (u, _) in enumerate(sorted_friends, 1) if u.lower() == "bastienzim"), None)
    if your_pos:
        if your_pos == 1:
            print(f"\n🎉 You're #1! Keep it up!")
        elif your_pos <= 3:
            print(f"\n🔥 You're in the top 3! Close to #1!")
        else:
            gap = sorted_friends[0][1]["avg_score"] - comparison["bastienzim"]["avg_score"]
            print(f"\n💪 You're #{your_pos}. Gap to #1: {gap:.1f} points")


def print_date_specific(date_str: str, archives: List[Dict[str, Any]], mistakes: List[Dict]):
    """Print information for a specific date."""
    print("=" * 80)
    print(f"📅 QUIZ DETAILS: {date_str}")
    print("=" * 80)
    
    if not archives:
        print(f"\n⚠️  No archive data found for {date_str}")
        return
    
    archive = archives[0]
    results = archive.get("results", [])
    
    # Find personal result
    personal = None
    for entry in results:
        if entry.get("user", "").lower() == "bastienzim":
            personal = entry
            break
    
    if personal:
        print(f"\n🎯 Your Performance:")
        print(f"   Score: {personal['good_responses']}/20")
        print(f"   Time: {personal['elapsed_time']}s ({personal['elapsed_time']/60:.1f} minutes)")
        print(f"   Rank: {personal['rank']}/{len(results)}")
    
    # Show mistakes for this date
    date_mistakes = [m for m in mistakes if m["date"] == date_str]
    if date_mistakes:
        print(f"\n❌ Your Mistakes ({len(date_mistakes)}):")
        for i, m in enumerate(date_mistakes, 1):
            print(f"\n   {i}. {m['category']}")
            print(f"      Q: {m['question']}")
            for hint in m.get('hints', []):
                print(f"      💡 {hint}")
            print(f"      Your answer: {m['your_answer']}")
            print(f"      Correct: {m['correct_answer']}")
    
    # Show top performers
    print(f"\n🏆 Top 10 Players:")
    for entry in results[:10]:
        print(f"   {entry['rank']:2d}. {entry['user']:20} - {entry['good_responses']}/20 ({entry['elapsed_time']}s)")


def main():
    parser = argparse.ArgumentParser(
        description="Inspect and analyze your quiz history",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run scripts/inspect_history.py                  # Show overview
  uv run scripts/inspect_history.py --detailed       # Detailed analysis
  uv run scripts/inspect_history.py --mistakes       # Focus on mistakes
  uv run scripts/inspect_history.py --compare        # Compare with friends
  uv run scripts/inspect_history.py --date 2025-10-17  # Specific date
  uv run scripts/inspect_history.py --all            # Show everything
        """
    )
    
    parser.add_argument('--detailed', action='store_true', help='Show detailed analysis')
    parser.add_argument('--mistakes', action='store_true', help='Focus on mistakes')
    parser.add_argument('--compare', action='store_true', help='Compare with friends')
    parser.add_argument('--date', help='Show specific date (YYYY-MM-DD)')
    parser.add_argument('--all', action='store_true', help='Show all analyses')
    
    args = parser.parse_args()
    
    # Load data
    mistakes = load_mistakes_history()
    archives = load_archive_data(args.date)
    
    mistakes_analysis = analyze_mistakes(mistakes)
    personal_stats = get_personal_stats(archives)
    
    # Show specific date
    if args.date:
        print_date_specific(args.date, archives, mistakes)
        return 0
    
    # Show analyses based on flags
    if args.all:
        print_overview(personal_stats, mistakes_analysis)
        print_detailed_analysis(personal_stats, mistakes_analysis)
        print_mistakes_focus(mistakes_analysis)
        comparison = compare_with_friends(archives, FRIENDS)
        print_comparison(comparison)
    elif args.detailed:
        print_detailed_analysis(personal_stats, mistakes_analysis)
    elif args.mistakes:
        print_mistakes_focus(mistakes_analysis)
    elif args.compare:
        comparison = compare_with_friends(archives, FRIENDS)
        print_comparison(comparison)
    else:
        # Default: show overview
        print_overview(personal_stats, mistakes_analysis)
    
    print("\n" + "=" * 80)
    print("💡 TIP: Use flags for more details:")
    print("   --detailed    Full performance trends")
    print("   --mistakes    Deep dive into mistakes")
    print("   --compare     See how you rank against friends")
    print("   --all         Show everything!")
    print("=" * 80)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
