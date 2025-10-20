#!/usr/bin/env python3
"""Fetch and log mistakes from historical quiz dates.

⚠️  IMPORTANT LIMITATIONS:

1. ARCHIVED QUIZZES (automatic):
   - The script can automatically fetch archived quiz pages
   - These contain questions and correct answers
   - chosen_index is -2 (means "not available" in archives)
   - Your personal answers are NOT available via automated scraping

2. PERSONAL ANSWERS (manual process):
   - To get YOUR specific wrong answers from past quizzes:
   - Go to: https://www.quizypedia.fr/defi-du-jour/archives/YYYY/MM/DD/
   - Click "Afficher les questions et les réponses" while logged in
   - Save the page as HTML
   - Then use parse_results.py on that saved HTML

This script is useful for:
- Getting questions and correct answers for study
- Identifying that you had mistakes on a date (from score)
- Quick overview of quiz content

For COMPLETE mistake tracking (with your wrong answers):
- Use the daily workflow on the quiz day, OR
- Manually save the HTML after clicking "Afficher les questions" and process it

Usage:
    # Check what dates you already have tracked
    uv run scripts/fetch_historical_mistakes.py --check
    
    # Fetch questions for a specific date (shows correct answers only)
    uv run scripts/fetch_historical_mistakes.py --date 2025-10-15
    
    # Fetch for date range
    uv run scripts/fetch_historical_mistakes.py --start 2025-10-06 --end 2025-10-15

Requirements:
    - Valid login credentials in .env file
    - Archive data available for the dates
"""
import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path to import fan2quizz module
sys.path.insert(0, str(Path(__file__).parent.parent))

from fan2quizz.scraper import QuizypediaScraper

ROOT = Path(__file__).parent.parent


def load_env_credentials():
    """Load credentials from .env file.
    
    Returns:
        dict: Dictionary with 'user', 'pass', and 'cookie' keys
    """
    env_file = ROOT / ".env"
    if not env_file.exists():
        return {'user': None, 'pass': None, 'cookie': None}
    
    env_vars = {}
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip()
    
    return {
        'user': env_vars.get('QUIZY_USER'),
        'pass': env_vars.get('QUIZY_PASS'),
        'cookie': env_vars.get('QUIZY_COOKIE')
    }


def bracket_scan_payload(html: str) -> Optional[str]:
    """Extract leaderboard JSON payload from HTML.
    
    Scans for the pattern '[{"good_responses"...' and extracts the full JSON array.
    """
    marker = '[{"good_responses"'
    start = html.find(marker)
    if start == -1:
        return None
    depth = 0
    for i, ch in enumerate(html[start:], start=start):
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                return html[start:i+1]
    return None


def parse_results(raw_payload: str) -> List[Dict]:
    """Parse leaderboard results from JSON string."""
    cleaned = raw_payload.strip()
    if cleaned.endswith(';'):
        cleaned = cleaned[:-1]
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        cleaned2 = re.sub(r"//.*?\n", "\n", cleaned)
        return json.loads(cleaned2)


def extract_dc_data_from_html(html: str) -> tuple[List[Dict], Dict]:
    """Extract DC_DATA and DC_USER from quiz HTML.
    
    Args:
        html: HTML content from quiz page
        
    Returns:
        tuple: (questions list, user_info dict)
        
    Raises:
        ValueError: If DC_DATA or DC_USER not found
    """
    # Find the DC_DATA variable
    match = re.search(r'var DC_DATA = (\[.*?\]);', html, re.DOTALL)
    if not match:
        raise ValueError("DC_DATA not found in HTML - quiz data may not be available for this date")
    
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
    
    # Try to extract date from HTML
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', html)
    if date_match:
        user_info['date'] = date_match.group(1)
    
    return questions, user_info


def extract_mistakes_from_quiz(questions: List[Dict], user_info: Dict, date: str) -> List[Dict]:
    """Extract mistakes from quiz data.
    
    Args:
        questions: List of question dictionaries from DC_DATA
        user_info: Dictionary from DC_USER
        date: Date string (YYYY-MM-DD)
        
    Returns:
        List of mistake dictionaries
    """
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


def load_mistakes_history(path: Path) -> List[Dict]:
    """Load existing mistakes history."""
    if not path.exists():
        return []
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"⚠️  Warning: Could not parse {path}, starting fresh")
        return []


def save_mistakes_history(path: Path, mistakes: List[Dict]):
    """Save mistakes history to JSON file."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(mistakes, f, ensure_ascii=False, indent=2)


def get_available_dates_with_mistakes(history: List[Dict]) -> set:
    """Get set of dates that already have mistakes logged."""
    return {m['date'] for m in history}


def fetch_mistakes_for_date(scraper: QuizypediaScraper, date_str: str, username: str) -> Optional[List[Dict]]:
    """Fetch mistakes for a specific date.
    
    Args:
        scraper: Authenticated QuizypediaScraper instance
        date_str: Date in YYYY-MM-DD format
        username: Your quizypedia username to look up your score
        
    Returns:
        List of mistakes or None if quiz not available
    """
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        print(f"\n📅 Fetching quiz for {date_str}...")
        
        # Fetch the HTML from archives
        html = scraper.get_daily_archive_html(date.year, date.month, date.day)
        
        # Try to extract your actual score from the leaderboard embedded in the HTML
        # This will help us determine if you actually had mistakes
        
        your_score = None
        try:
            raw_payload = bracket_scan_payload(html)
            if raw_payload:
                results = parse_results(raw_payload)
                for player in results:
                    if player.get('user', '').lower() == username.lower():
                        your_score = player.get('good_responses')
                        break
        except Exception:
            pass
        
        # Extract quiz data
        questions, user_info = extract_dc_data_from_html(html)
        total = len(questions)
        
        # If we found your score in the leaderboard, use it
        # Otherwise fall back to user_info (which won't be personalized in archives)
        if your_score is not None:
            score = your_score
        else:
            score = user_info.get('good_responses', 0)
        
        time_sec = user_info.get('elapsed_time', 0)
        
        print(f"   Score: {score}/{total}")
        print(f"   Time: {time_sec}s")
        
        # Check if we have a perfect score
        if score == total:
            print("   🎉 Perfect score - no mistakes!")
            return []
        
        # Extract mistakes
        # Note: chosen_index won't be available in archives, so your_answer will be "Unknown"
        mistakes = extract_mistakes_from_quiz(questions, user_info, date_str)
        
        # If we got all questions marked as mistakes but score says otherwise,
        # we can't reliably extract which ones were actually wrong
        if len(mistakes) == total and score > 0:
            print("   ⚠️  Archive doesn't contain your personal answers")
            print(f"   ⚠️  Based on score: you got {total - score} wrong out of {total}")
            print("   ⚠️  Cannot determine which specific questions you missed")
            return None
        
        print(f"   Mistakes found: {len(mistakes)}")
        
        return mistakes
        
    except ValueError as e:
        print(f"   ⚠️  {e}")
        return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def check_existing_dates(history_path: Path):
    """Display what dates already have mistakes logged."""
    history = load_mistakes_history(history_path)
    
    if not history:
        print("\n📋 No mistakes logged yet in mistakes_history.json")
        return
    
    dates_with_mistakes = sorted(set(m['date'] for m in history))
    mistake_counts = {}
    for m in history:
        date = m['date']
        mistake_counts[date] = mistake_counts.get(date, 0) + 1
    
    print("\n📋 Dates with mistakes already logged:")
    print("=" * 60)
    for date in dates_with_mistakes:
        count = mistake_counts[date]
        print(f"   ✓ {date} ({count} mistake{'s' if count != 1 else ''})")
    print(f"\nTotal: {len(dates_with_mistakes)} dates with {len(history)} mistakes")


def parse_date_range(start: str, end: str) -> List[str]:
    """Generate list of dates between start and end (inclusive)."""
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')
    
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    
    return dates


def main():
    parser = argparse.ArgumentParser(
        description='Fetch historical quiz mistakes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check what dates you already have
  %(prog)s --check
  
  # Fetch mistakes for a specific date
  %(prog)s --date 2025-10-15
  
  # Fetch for multiple dates
  %(prog)s --date 2025-10-15 --date 2025-10-14 --date 2025-10-13
  
  # Fetch for a date range
  %(prog)s --start 2025-10-06 --end 2025-10-15
  
  # Skip dates that already have mistakes
  %(prog)s --start 2025-10-06 --end 2025-10-15 --skip-existing
        """
    )
    
    parser.add_argument('--date', action='append', help='Specific date to fetch (YYYY-MM-DD). Can be used multiple times.')
    parser.add_argument('--start', help='Start date for range (YYYY-MM-DD)')
    parser.add_argument('--end', help='End date for range (YYYY-MM-DD)')
    parser.add_argument('--username', default='BastienZim', help='Your Quizypedia username (default: BastienZim)')
    parser.add_argument('--check', action='store_true', help='Check what dates already have mistakes logged')
    parser.add_argument('--skip-existing', action='store_true', help='Skip dates that already have mistakes')
    parser.add_argument('--regenerate', action='store_true', help='Regenerate study guide after fetching')
    
    args = parser.parse_args()
    
    history_path = Path('mistakes_history.json')
    
    # Check mode
    if args.check:
        check_existing_dates(history_path)
        return 0
    
    # Determine dates to fetch
    dates_to_fetch = []
    
    if args.date:
        dates_to_fetch.extend(args.date)
    
    if args.start and args.end:
        dates_to_fetch.extend(parse_date_range(args.start, args.end))
    elif args.start or args.end:
        print("❌ Error: --start and --end must be used together")
        return 1
    
    if not dates_to_fetch:
        print("❌ Error: No dates specified. Use --date, --start/--end, or --check")
        parser.print_help()
        return 1
    
    # Remove duplicates and sort
    dates_to_fetch = sorted(set(dates_to_fetch))
    
    # Load existing history
    history = load_mistakes_history(history_path)
    existing_dates = get_available_dates_with_mistakes(history)
    
    # Filter out existing if requested
    if args.skip_existing:
        original_count = len(dates_to_fetch)
        dates_to_fetch = [d for d in dates_to_fetch if d not in existing_dates]
        skipped = original_count - len(dates_to_fetch)
        if skipped > 0:
            print(f"\n⏭️  Skipping {skipped} date(s) with existing mistakes")
    
    if not dates_to_fetch:
        print("\n✅ All specified dates already have mistakes logged!")
        return 0
    
    print(f"\n🎯 Fetching mistakes for {len(dates_to_fetch)} date(s)...")
    print("=" * 60)
    
    # Load credentials and create scraper
    creds = load_env_credentials()
    scraper = QuizypediaScraper()
    
    # Login with cookie if available, otherwise username/password
    if creds['cookie']:
        print("\n🔐 Using session cookie...")
        scraper.set_cookies_from_header(f"sessionid={creds['cookie']}")
    elif creds['user'] and creds['pass']:
        print("\n🔐 Logging in...")
        if not scraper.login(creds['user'], creds['pass'], debug=False):
            print("❌ Login failed. Check your credentials in .env file.")
            return 1
        print("✅ Logged in successfully")
    else:
        print("❌ No credentials found in .env file.")
        print("   Please add QUIZY_COOKIE or QUIZY_USER + QUIZY_PASS")
        return 1
    
    # Fetch mistakes for each date
    new_mistakes_count = 0
    successful_dates = []
    
    for date_str in dates_to_fetch:
        mistakes = fetch_mistakes_for_date(scraper, date_str, args.username)
        
        if mistakes is None:
            continue
        
        if len(mistakes) == 0:
            print("   🎉 Perfect score - no mistakes!")
        else:
            # Add to history
            history.extend(mistakes)
            new_mistakes_count += len(mistakes)
            successful_dates.append(date_str)
    
    # Save updated history
    if new_mistakes_count > 0:
        # Sort by date and question number
        history.sort(key=lambda x: (x['date'], x['question_number']))
        save_mistakes_history(history_path, history)
        
        print("\n" + "=" * 60)
        print(f"✅ Added {new_mistakes_count} mistake(s) from {len(successful_dates)} date(s)")
        print(f"📝 Updated {history_path}")
        print("=" * 60)
        
        # Regenerate study guide if requested
        if args.regenerate:
            print("\n📚 Regenerating study guide...")
            try:
                import subprocess
                subprocess.run([
                    sys.executable,
                    'scripts/generate_failed_questions.py',
                    '--order', 'category',
                    '--stats'
                ], check=True)
                print("✅ Study guide regenerated")
            except Exception as e:
                print(f"⚠️  Could not regenerate study guide: {e}")
                print("   Run manually: uv run scripts/generate_failed_questions.py")
    else:
        print("\n✅ No new mistakes found")
    
    print("\n💡 Next steps:")
    print("   - Review mistakes_history.json")
    print("   - Generate study guide: uv run scripts/generate_failed_questions.py")
    print("   - Check by date: uv run scripts/generate_failed_questions.py --filter 2025-10-15")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
