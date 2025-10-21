#!/usr/bin/env python3
"""Generate a comprehensive weekly mistakes report.

This script fetches quiz data from the last 7 days (or a custom date range),
extracts your mistakes, and generates detailed reports showing:
- Overall performance statistics
- Daily breakdown with scores
- All mistakes grouped by date
- Mistakes grouped by category
- Summary and trends

Usage:
    # Last 7 days (default)
    uv run scripts/weekly_mistakes_report.py
    
    # Specific date range
    uv run scripts/weekly_mistakes_report.py --start 2025-10-14 --end 2025-10-20
    
    # Last 14 days
    uv run scripts/weekly_mistakes_report.py --days 14
    
    # Custom output file
    uv run scripts/weekly_mistakes_report.py --output my_report.md
    
    # Show progress while fetching
    uv run scripts/weekly_mistakes_report.py --verbose

Output:
    - WEEKLY_MISTAKES_REPORT.md (or custom filename)
    - Optionally updates mistakes_history.json
"""

import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

# Add parent directory to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fan2quizz.scraper import QuizypediaScraper  # noqa: E402
from fan2quizz.utils import RateLimiter  # noqa: E402

# Cache directory for HTML files
CACHE_DIR = ROOT / "data" / "cache" / "quiz_html"


def get_cache_path(year: int, month: int, day: int) -> Path:
    """Get cache file path for a specific date."""
    date_str = f"{year:04d}-{month:02d}-{day:02d}"
    return CACHE_DIR / f"{date_str}.html"


def load_cached_html(year: int, month: int, day: int) -> Optional[str]:
    """Load cached HTML if it exists."""
    cache_path = get_cache_path(year, month, day)
    if cache_path.exists():
        try:
            return cache_path.read_text(encoding='utf-8')
        except Exception:
            return None
    return None


def save_cached_html(html: str, year: int, month: int, day: int):
    """Save HTML to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = get_cache_path(year, month, day)
    try:
        cache_path.write_text(html, encoding='utf-8')
    except Exception:
        pass  # Cache write failure is not critical


def load_env_credentials():
    """Load credentials from .env file if it exists."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return None, None, None
    
    env_vars = {}
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip()
    
    return (
        env_vars.get('QUIZY_USER'),
        env_vars.get('QUIZY_PASS'),
        env_vars.get('QUIZY_COOKIE')
    )


def parse_date(date_str: str) -> Tuple[int, int, int]:
    """Parse date string to (year, month, day)."""
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return (dt.year, dt.month, dt.day)
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")


def generate_date_range(start_date: datetime, end_date: datetime) -> List[datetime]:
    """Generate list of dates between start and end (inclusive)."""
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)
    return dates


def extract_dc_data_from_html(html: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Extract the DC_DATA and DC_USER JavaScript variables from the HTML."""
    # Find the DC_DATA variable
    match = re.search(r'var DC_DATA = (\[.*?\]);', html, re.DOTALL)
    if not match:
        raise ValueError("DC_DATA not found in HTML")
    
    data_json = match.group(1)
    questions = json.loads(data_json)
    
    # Find DC_USER data
    user_match = re.search(r'var DC_USER = \{([^}]+)\};', html)
    user_info = {}
    if user_match:
        user_str = user_match.group(1)
        for line in user_str.split(','):
            line = line.strip()
            if ':' in line:
                key, val = line.split(':', 1)
                key = key.strip()
                val = val.strip()
                try:
                    user_info[key] = int(val)
                except (ValueError, TypeError):
                    user_info[key] = val
    
    return questions, user_info


def extract_mistakes(questions: List[Dict[str, Any]], date: str) -> List[Dict[str, Any]]:
    """Extract all incorrect answers from quiz questions."""
    mistakes = []
    
    for i, question in enumerate(questions, 1):
        correct_index = question.get('response_index')
        chosen_index = question.get('chosen_index')
        
        # Skip if correct or if chosen_index is missing
        if chosen_index is None or correct_index == chosen_index:
            continue
        
        # Extract question details
        category = question.get('theme_title', 'Unknown Category')
        question_text = question.get('question', '')
        
        # Get hints if available
        hints = question.get('hints', [])
        hint_text = []
        for hint in hints:
            hint_type = hint.get('type', '')
            hint_value = hint.get('value', '')
            if hint_type and hint_value:
                hint_text.append(f"{hint_type}: {hint_value}")
        
        # Get answer choices
        proposed_responses = question.get('proposed_responses', [])
        
        correct_answer = 'Unknown'
        chosen_answer = 'Unknown'
        
        if 0 <= correct_index < len(proposed_responses):
            correct_answer = proposed_responses[correct_index].get('response', 'Unknown')
        
        if 0 <= chosen_index < len(proposed_responses):
            chosen_answer = proposed_responses[chosen_index].get('response', 'Unknown')
        
        mistake = {
            'date': date,
            'question_number': i,
            'category': category,
            'question': question_text,
            'hints': hint_text,
            'your_answer': chosen_answer,
            'correct_answer': correct_answer,
            'all_choices': [r.get('response', '') for r in proposed_responses]
        }
        
        mistakes.append(mistake)
    
    return mistakes


def fetch_quiz_data(scraper: QuizypediaScraper, date: datetime, verbose: bool = False, use_cache: bool = True) -> Optional[Dict[str, Any]]:
    """Fetch quiz data for a specific date."""
    year, month, day = date.year, date.month, date.day
    date_str = date.strftime('%Y-%m-%d')
    
    if verbose:
        print(f"  Fetching {date_str}...", end=' ', flush=True)
    
    try:
        # Try to load from cache first
        html = None
        if use_cache:
            html = load_cached_html(year, month, day)
            if html and verbose:
                print("(cached)", end=' ', flush=True)
        
        # Fetch from server if not in cache
        if html is None:
            html = scraper.get_daily_archive_html(year, month, day)
            # Save to cache for future use
            if use_cache:
                save_cached_html(html, year, month, day)
        
        questions, user_info = extract_dc_data_from_html(html)
        mistakes = extract_mistakes(questions, date_str)
        
        # Calculate score
        total_questions = len(questions)
        correct_count = total_questions - len(mistakes)
        
        if verbose:
            print(f"✓ ({correct_count}/{total_questions})")
        
        return {
            'date': date_str,
            'total_questions': total_questions,
            'correct': correct_count,
            'mistakes_count': len(mistakes),
            'mistakes': mistakes,
            'time': user_info.get('elapsed_time', 'N/A')
        }
    except Exception as e:
        if verbose:
            print(f"✗ (Error: {e})")
        return None


def generate_markdown_report(quiz_data: List[Dict[str, Any]], start_date: str, end_date: str) -> str:
    """Generate a markdown report from quiz data."""
    # Filter out None entries
    quiz_data = [q for q in quiz_data if q is not None]
    
    if not quiz_data:
        return "# Weekly Mistakes Report\n\nNo quiz data available for the specified period.\n"
    
    # Calculate statistics
    total_quizzes = len(quiz_data)
    total_questions = sum(q['total_questions'] for q in quiz_data)
    total_correct = sum(q['correct'] for q in quiz_data)
    total_mistakes = sum(q['mistakes_count'] for q in quiz_data)
    accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
    avg_score = total_correct / total_quizzes if total_quizzes > 0 else 0
    
    # Group mistakes by category
    mistakes_by_category = defaultdict(list)
    all_mistakes = []
    for quiz in quiz_data:
        for mistake in quiz['mistakes']:
            mistakes_by_category[mistake['category']].append(mistake)
            all_mistakes.append(mistake)
    
    # Sort categories by mistake count
    sorted_categories = sorted(mistakes_by_category.items(), key=lambda x: len(x[1]), reverse=True)
    
    # Build report
    report = []
    report.append("# 📋 Weekly Mistakes Report")
    report.append(f"**Period:** {start_date} to {end_date}")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("")
    report.append("---")
    report.append("")
    
    # Executive Summary
    report.append("## 📊 Executive Summary")
    report.append("")
    report.append(f"- **Quizzes Completed:** {total_quizzes}")
    report.append(f"- **Total Questions:** {total_questions}")
    report.append(f"- **Total Correct:** {total_correct}")
    report.append(f"- **Total Mistakes:** {total_mistakes}")
    report.append(f"- **Accuracy Rate:** {accuracy:.1f}%")
    report.append(f"- **Average Score:** {avg_score:.1f}/20 per quiz")
    report.append("")
    report.append("---")
    report.append("")
    
    # Daily Breakdown
    report.append("## 📅 Daily Breakdown")
    report.append("")
    report.append("| Date | Score | Mistakes | Time |")
    report.append("|------|-------|----------|------|")
    for quiz in sorted(quiz_data, key=lambda x: x['date']):
        date = quiz['date']
        score = f"{quiz['correct']}/{quiz['total_questions']}"
        mistakes = quiz['mistakes_count']
        time = quiz['time']
        time_str = f"{time}s" if isinstance(time, int) else str(time)
        emoji = "✅" if mistakes == 0 else "⚠️" if mistakes <= 5 else "❌"
        report.append(f"| {date} | {emoji} {score} | {mistakes} | {time_str} |")
    report.append("")
    report.append("---")
    report.append("")
    
    # Mistakes by Category
    report.append("## 🎯 Mistakes by Category")
    report.append("")
    report.append("Categories where you made the most mistakes:")
    report.append("")
    for i, (category, mistakes) in enumerate(sorted_categories[:10], 1):
        report.append(f"{i}. **{category}** - {len(mistakes)} mistake(s)")
    report.append("")
    report.append("---")
    report.append("")
    
    # All Mistakes Detailed
    report.append("## ❌ All Mistakes (Detailed)")
    report.append("")
    
    # Group by date
    mistakes_by_date = defaultdict(list)
    for mistake in all_mistakes:
        mistakes_by_date[mistake['date']].append(mistake)
    
    for date in sorted(mistakes_by_date.keys()):
        report.append(f"### 📆 {date}")
        report.append("")
        
        for mistake in mistakes_by_date[date]:
            report.append(f"#### Question {mistake['question_number']}: {mistake['category']}")
            report.append("")
            report.append(f"**Question:** {mistake['question']}")
            report.append("")
            
            if mistake['hints']:
                report.append("**Hints:**")
                for hint in mistake['hints']:
                    report.append(f"- {hint}")
                report.append("")
            
            report.append("**Choices:**")
            for i, choice in enumerate(mistake['all_choices'], 1):
                marker = ""
                if choice == mistake['correct_answer']:
                    marker = " ✅ **CORRECT**"
                elif choice == mistake['your_answer']:
                    marker = " ❌ **YOUR ANSWER**"
                report.append(f"{i}. {choice}{marker}")
            report.append("")
            report.append(f"💭 **You answered:** {mistake['your_answer']}")
            report.append(f"✓ **Correct answer:** {mistake['correct_answer']}")
            report.append("")
            report.append("---")
            report.append("")
    
    # Category Breakdown
    report.append("## 📚 Mistakes by Category (Detailed)")
    report.append("")
    
    for category, mistakes in sorted_categories:
        report.append(f"### {category} ({len(mistakes)} mistake(s))")
        report.append("")
        
        for mistake in mistakes:
            report.append(f"**[{mistake['date']}] Q{mistake['question_number']}:** {mistake['question']}")
            report.append(f"- ❌ Your answer: {mistake['your_answer']}")
            report.append(f"- ✅ Correct: {mistake['correct_answer']}")
            report.append("")
        
        report.append("---")
        report.append("")
    
    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a comprehensive weekly mistakes report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Last 7 days (default)
  uv run scripts/weekly_mistakes_report.py
  
  # Specific date range
  uv run scripts/weekly_mistakes_report.py --start 2025-10-14 --end 2025-10-20
  
  # Last 14 days
  uv run scripts/weekly_mistakes_report.py --days 14
  
  # Custom output file
  uv run scripts/weekly_mistakes_report.py --output my_report.md

Note: The script automatically uses credentials from .env file.
        """
    )
    
    parser.add_argument(
        '--start',
        help='Start date (YYYY-MM-DD). Default: 7 days ago'
    )
    parser.add_argument(
        '--end',
        help='End date (YYYY-MM-DD). Default: yesterday'
    )
    parser.add_argument(
        '--days',
        type=int,
        help='Number of days to look back (alternative to --start/--end)'
    )
    parser.add_argument(
        '--output',
        default='WEEKLY_MISTAKES_REPORT.md',
        help='Output filename (default: WEEKLY_MISTAKES_REPORT.md)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show progress while fetching'
    )
    parser.add_argument(
        '--update-history',
        action='store_true',
        help='Also update mistakes_history.json with fetched data'
    )
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Skip cache, always fetch fresh from server'
    )
    
    args = parser.parse_args()
    
    # Determine date range
    if args.days:
        end_date = datetime.now() - timedelta(days=1)
        start_date = end_date - timedelta(days=args.days - 1)
    elif args.start and args.end:
        start_date = datetime.strptime(args.start, '%Y-%m-%d')
        end_date = datetime.strptime(args.end, '%Y-%m-%d')
    elif args.start:
        start_date = datetime.strptime(args.start, '%Y-%m-%d')
        end_date = datetime.now() - timedelta(days=1)
    elif args.end:
        end_date = datetime.strptime(args.end, '%Y-%m-%d')
        start_date = end_date - timedelta(days=6)
    else:
        # Default: last 7 days
        end_date = datetime.now() - timedelta(days=1)
        start_date = end_date - timedelta(days=6)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    print(f"📅 Generating report for {start_str} to {end_str}")
    print()
    
    # Load credentials and authenticate
    email, password, cookie = load_env_credentials()
    
    scraper = QuizypediaScraper(rate_limiter=RateLimiter(0.5))
    
    if cookie:
        if args.verbose:
            print("🔐 Using session cookie from .env")
        for cookie_part in cookie.split(';'):
            cookie_part = cookie_part.strip()
            if '=' in cookie_part:
                name, value = cookie_part.split('=', 1)
                scraper.session.cookies.set(name.strip(), value.strip())
    elif email and password:
        if args.verbose:
            print(f"🔐 Logging in as {email}...")
        success = scraper.login(email, password, debug=False)
        if not success:
            print("❌ Login failed. Some data may be incomplete.")
        elif args.verbose:
            print("✅ Login successful!")
    else:
        print("⚠️  No credentials found in .env file")
        print("   Results may be incomplete")
    
    # Generate date range
    dates = generate_date_range(start_date, end_date)
    
    print(f"🔍 Fetching data for {len(dates)} days...")
    if args.verbose:
        print()
    
    # Fetch quiz data for each date
    quiz_data = []
    for date in dates:
        data = fetch_quiz_data(scraper, date, verbose=args.verbose, use_cache=not args.no_cache)
        if data:
            quiz_data.append(data)
    
    if not args.verbose:
        print(f"✅ Fetched {len(quiz_data)}/{len(dates)} quizzes")
    print()
    
    # Generate report
    print("📝 Generating report...")
    report = generate_markdown_report(quiz_data, start_str, end_str)
    
    # Save report
    output_path = ROOT / args.output
    output_path.write_text(report, encoding='utf-8')
    print(f"✅ Report saved to: {output_path}")
    
    # Update history if requested
    if args.update_history:
        print()
        print("📚 Updating mistakes_history.json...")
        history_path = ROOT / 'mistakes_history.json'
        
        # Load existing history
        if history_path.exists():
            with open(history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = []
        
        # Add new mistakes
        existing_dates = {m['date'] for m in history}
        new_mistakes = []
        for quiz in quiz_data:
            for mistake in quiz['mistakes']:
                if mistake['date'] not in existing_dates:
                    new_mistakes.append(mistake)
        
        if new_mistakes:
            history.extend(new_mistakes)
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            print(f"✅ Added {len(new_mistakes)} new mistakes to history")
        else:
            print("ℹ️  No new mistakes to add (already in history)")
    
    print()
    print("=" * 60)
    print("📊 Summary:")
    print(f"   - Quizzes analyzed: {len(quiz_data)}")
    print(f"   - Total mistakes found: {sum(q['mistakes_count'] for q in quiz_data)}")
    print(f"   - Report saved to: {args.output}")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
