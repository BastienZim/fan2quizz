#!/usr/bin/env python3
"""Display your personal mistakes from a specific day's quiz.

This script fetches the archive page for a specific date, extracts the quiz
data (including questions, your answers, and correct answers), and displays
only the questions you got wrong.

Usage:
    uv run scripts/show_mistakes_by_date.py 2025-10-20
    uv run scripts/show_mistakes_by_date.py 2025/10/20
    uv run scripts/show_mistakes_by_date.py 20/10/2025
    uv run scripts/show_mistakes_by_date.py                    # Uses yesterday's date
    uv run scripts/show_mistakes_by_date.py --all              # Show all questions, not just mistakes
    
    # Without authentication (limited info)
    uv run scripts/show_mistakes_by_date.py 2025-10-20 --no-auth

The script automatically uses credentials from .env file if available.
"""

import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

# Add parent directory to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fan2quizz.scraper import QuizypediaScraper  # noqa: E402
from fan2quizz.utils import RateLimiter  # noqa: E402

# Cache directory for HTML files
CACHE_DIR = ROOT / "data" / "cache" / "quiz_html"


def load_env_credentials():
    """Load credentials from .env file if it exists.
    
    Returns:
        tuple: (email, password, cookie_string) or (None, None, None)
    """
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


def parse_date_arg(date_str: Optional[str]) -> Tuple[int, int, int]:
    """Parse a date string in various formats.
    
    Accepts:
        - 2025-10-20
        - 2025/10/20
        - 20/10/2025
        - None (returns yesterday)
    
    Returns:
        tuple: (year, month, day)
    """
    if date_str is None:
        yesterday = datetime.now() - timedelta(days=1)
        return (yesterday.year, yesterday.month, yesterday.day)
    
    # Try different formats
    formats = [
        r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # 2025-10-20 or 2025/10/20
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # 20/10/2025 or 20-10-2025
    ]
    
    for fmt in formats:
        match = re.match(fmt, date_str)
        if match:
            if len(match.group(1)) == 4:  # Year first
                year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            else:  # Day first
                day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
            return (year, month, day)
    
    raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD, YYYY/MM/DD, or DD/MM/YYYY")


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


def extract_dc_data_from_html(html: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Extract the DC_DATA and DC_USER JavaScript variables from the HTML.
    
    Args:
        html: HTML content from the archive page
        
    Returns:
        tuple: (questions list, user_info dict)
        
    Raises:
        ValueError: If DC_DATA variable is not found in the HTML
    """
    # Find the DC_DATA variable
    match = re.search(r'var DC_DATA = (\[.*?\]);', html, re.DOTALL)
    if not match:
        raise ValueError("DC_DATA not found in HTML. The page might not have loaded correctly, or you need to be logged in.")
    
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


def format_mistakes(questions: List[Dict[str, Any]], user_info: Dict[str, Any], show_all: bool = False):
    """Format and display the quiz mistakes.
    
    Args:
        questions: List of question dictionaries from DC_DATA
        user_info: Dictionary of user stats from DC_USER
        show_all: If True, show all questions; if False, show only mistakes
    """
    print("=" * 80)
    print("DÉFI DU JOUR - Your Mistakes" if not show_all else "DÉFI DU JOUR - All Questions")
    print("=" * 80)
    
    correct_count = user_info.get('good_responses', 'N/A')
    total_count = len(questions)
    mistakes_count = total_count - correct_count if isinstance(correct_count, int) else 'N/A'
    
    print(f"\n📊 Score: {correct_count}/{total_count}")
    if isinstance(mistakes_count, int):
        print(f"❌ Mistakes: {mistakes_count}")
    print(f"⏱️  Time: {user_info.get('elapsed_time', 'N/A')} seconds")
    
    # Filter questions
    mistake_questions = []
    for i, q in enumerate(questions, 1):
        correct_index = q.get('response_index')
        chosen_index = q.get('chosen_index')
        
        if show_all or chosen_index != correct_index:
            mistake_questions.append((i, q))
    
    if not mistake_questions:
        print("\n🎉 Perfect score! No mistakes to show.")
        return
    
    print("\n" + "=" * 80)
    if show_all:
        print(f"ALL QUESTIONS ({len(mistake_questions)} total):")
    else:
        print(f"MISTAKES ONLY ({len(mistake_questions)} mistakes):")
    print("=" * 80)
    
    for question_num, q in mistake_questions:
        theme = q.get('theme_title', 'Unknown theme')
        question = q.get('question', 'Unknown question')
        hints = q.get('hints', [])
        proposed_responses = q.get('proposed_responses', [])
        correct_index = q.get('response_index')
        chosen_index = q.get('chosen_index')
        
        # Determine if it's correct or wrong
        is_correct = chosen_index == correct_index
        status_emoji = "✅" if is_correct else "❌"
        
        print(f"\n{'─' * 80}")
        print(f"{status_emoji} Question {question_num}: {theme}")
        print(f"{'─' * 80}")
        print(f"❓ {question}")
        
        # Display hints
        if hints:
            for hint in hints:
                hint_type = hint.get('type', '')
                hint_value = hint.get('value', '')
                print(f"   💡 {hint_type}: {hint_value}")
        
        # Display choices
        print("\n   Choices:")
        for j, resp in enumerate(proposed_responses):
            response_text = resp.get('response', '')
            marker = ""
            
            if j == correct_index:
                marker = " ✓ CORRECT"
            if j == chosen_index:
                if j == correct_index:
                    marker += " (YOUR ANSWER)"
                else:
                    marker = " ✗ YOUR ANSWER (WRONG)"
            
            print(f"   {j + 1}. {response_text}{marker}")
        
        # Summary
        if not is_correct:
            correct_answer = proposed_responses[correct_index].get('response', '') if correct_index is not None else 'N/A'
            your_answer = proposed_responses[chosen_index].get('response', 'N/A') if chosen_index is not None else 'No answer'
            print(f"\n   💭 You answered: {your_answer}")
            print(f"   ✓ Correct answer: {correct_answer}")


def main():
    parser = argparse.ArgumentParser(
        description="Display your personal mistakes from a specific day's quiz",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show mistakes from October 20, 2025
  uv run scripts/show_mistakes_by_date.py 2025-10-20
  uv run scripts/show_mistakes_by_date.py 2025/10/20
  uv run scripts/show_mistakes_by_date.py 20/10/2025
  
  # Show yesterday's mistakes
  uv run scripts/show_mistakes_by_date.py
  
  # Show all questions (not just mistakes)
  uv run scripts/show_mistakes_by_date.py 2025-10-20 --all
  
  # Fetch without authentication (will show limited info)
  uv run scripts/show_mistakes_by_date.py 2025-10-20 --no-auth

Note: The script automatically uses credentials from .env file if available.
        """
    )
    
    parser.add_argument(
        'date',
        nargs='?',
        help='Date in format YYYY-MM-DD, YYYY/MM/DD, or DD/MM/YYYY (default: yesterday)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Show all questions, not just mistakes'
    )
    parser.add_argument(
        '--no-auth',
        action='store_true',
        help='Skip authentication (may show limited info)'
    )
    parser.add_argument(
        '--save',
        metavar='FILE',
        help='Save the HTML to a file (optional)'
    )
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Skip cache, always fetch fresh from server'
    )
    
    args = parser.parse_args()
    
    # Parse date
    try:
        year, month, day = parse_date_arg(args.date)
    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1
    
    date_str = f"{year:04d}-{month:02d}-{day:02d}"
    print(f"📅 Fetching quiz for {date_str}...")
    
    # Initialize scraper
    scraper = QuizypediaScraper(rate_limiter=RateLimiter(0.5))
    
    # Load credentials and authenticate
    if not args.no_auth:
        email, password, cookie = load_env_credentials()
        
        if cookie:
            print("🔐 Using session cookie from .env...")
            for cookie_part in cookie.split(';'):
                cookie_part = cookie_part.strip()
                if '=' in cookie_part:
                    name, value = cookie_part.split('=', 1)
                    scraper.session.cookies.set(name.strip(), value.strip())
            print("✅ Session cookie loaded!")
        elif email and password:
            print(f"🔐 Logging in as {email}...")
            success = scraper.login(email, password, debug=False)
            if not success:
                print("❌ Login failed. Continuing without authentication...")
                print("⚠️  Note: Without login, you may see limited or no results.")
            else:
                print("✅ Login successful!")
        else:
            print("⚠️  No credentials found in .env file")
            print("   Create a .env file with QUIZY_USER, QUIZY_PASS, or QUIZY_COOKIE")
    
    # Try to load from cache first
    html = None
    
    if not args.no_cache:
        html = load_cached_html(year, month, day)
        if html:
            print(f"📂 Loaded from cache ({len(html)} bytes)")
    
    # Fetch from server if not in cache
    if html is None:
        try:
            print("🌐 Fetching archive page from server...")
            html = scraper.get_daily_archive_html(year, month, day)
            print(f"✅ Fetched HTML ({len(html)} bytes)")
            
            # Save to cache for future use
            save_cached_html(html, year, month, day)
            print("💾 Cached for future use")
        except Exception as e:
            print(f"❌ Error fetching archive: {e}")
            return 1
    
    # Optionally save HTML to custom location
    if args.save:
        save_path = Path(args.save)
        save_path.write_text(html, encoding='utf-8')
        print(f"💾 Saved HTML to: {save_path}")
    
    # Extract quiz data
    try:
        questions, user_info = extract_dc_data_from_html(html)
    except ValueError as e:
        print(f"❌ Error parsing quiz data: {e}")
        print("\n💡 Tips:")
        print("   - Make sure you're authenticated (credentials in .env)")
        print("   - Check that the date is correct")
        print("   - Try visiting the URL in your browser:")
        print(f"     https://www.quizypedia.fr/defi-du-jour/archives/{year:04d}/{month:02d}/{day:02d}/")
        return 1
    
    # Display results
    format_mistakes(questions, user_info, show_all=args.all)
    
    print("\n" + "=" * 80)
    print("✨ Done!")
    print("=" * 80)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
