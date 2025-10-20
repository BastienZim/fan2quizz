#!/usr/bin/env python3
"""Manage historical quiz data archive.

This script helps you:
1. Check what dates you have data for
2. Identify missing dates
3. Download missing historical data

Usage:
    uv run scripts/manage_archive.py                    # Report on available data
    uv run scripts/manage_archive.py --download         # Download missing dates
    uv run scripts/manage_archive.py --from 2025-10-01  # Custom date range
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import argparse

# Add parent directory to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fan2quizz.scraper import QuizypediaScraper
from fan2quizz.utils import RateLimiter


def load_env_credentials():
    """Load credentials from .env file."""
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


def get_available_dates():
    """Get list of dates we have archive data for.
    
    Returns:
        list: List of datetime objects for available dates
    """
    archive_dir = ROOT / "data" / "cache" / "archive"
    if not archive_dir.exists():
        return []
    
    dates = []
    for file in archive_dir.glob("*.json"):
        if file.stem == ".gitkeep":
            continue
        try:
            date = datetime.strptime(file.stem, "%Y-%m-%d")
            dates.append(date)
        except ValueError:
            continue
    
    return sorted(dates)


def get_date_range(start_date=None, end_date=None):
    """Get date range to check.
    
    Args:
        start_date: Start date (datetime or None)
        end_date: End date (datetime or None, defaults to yesterday)
    
    Returns:
        tuple: (start_date, end_date) as datetime objects
    """
    if end_date is None:
        # Default to yesterday (today's data might not be complete)
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    
    if start_date is None:
        # Default to 30 days ago
        start_date = end_date - timedelta(days=30)
    
    return start_date, end_date


def get_all_dates_in_range(start_date, end_date):
    """Get all dates in a range.
    
    Args:
        start_date: Start date (datetime)
        end_date: End date (datetime)
    
    Returns:
        list: List of datetime objects for each date in range
    """
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)
    return dates


def bracket_scan_payload(html: str):
    """Extract JSON payload from archive HTML.
    
    Args:
        html: Archive page HTML
    
    Returns:
        str or None: JSON string or None if not found
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


def parse_results(raw_payload: str):
    """Parse JSON payload from archive HTML.
    
    Args:
        raw_payload: JSON string
    
    Returns:
        list: List of player results
    """
    cleaned = raw_payload.strip()
    if cleaned.endswith(';'):
        cleaned = cleaned[:-1]
    return json.loads(cleaned)


def fetch_leaderboard_for_date(scraper, date):
    """Fetch leaderboard data for a specific date.
    
    Args:
        scraper: QuizypediaScraper instance
        date: datetime object
    
    Returns:
        list or None: Leaderboard data or None if failed
    """
    try:
        date_str = date.strftime("%Y-%m-%d")
        print(f"  📥 Fetching {date_str}...", end=" ", flush=True)
        
        # Fetch archive HTML
        year, month, day = date.year, date.month, date.day
        html = scraper.get_daily_archive_html(year, month, day)
        
        # Extract JSON payload
        raw_payload = bracket_scan_payload(html)
        if not raw_payload:
            print("⚠️  No data available")
            return None
        
        # Parse JSON
        leaderboard = parse_results(raw_payload)
        
        if leaderboard and len(leaderboard) > 0:
            print(f"✅ ({len(leaderboard)} players)")
            return leaderboard
        else:
            print("⚠️  No data available")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def save_leaderboard_to_archive(date, leaderboard):
    """Save leaderboard data to archive.
    
    Args:
        date: datetime object
        leaderboard: List of player data
    """
    archive_dir = ROOT / "data" / "cache" / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    date_str = date.strftime("%Y-%m-%d")
    output_file = archive_dir / f"{date_str}.json"
    
    # Save in the same format as existing archive files
    archive_data = {
        'date': date_str,
        'fetched_at': datetime.now().isoformat() + 'Z',
        'count': len(leaderboard),
        'results': leaderboard
    }
    
    output_file.write_text(json.dumps(archive_data, indent=2, ensure_ascii=False), encoding='utf-8')


def report_available_data(start_date, end_date):
    """Generate report of available data.
    
    Args:
        start_date: Start date (datetime)
        end_date: End date (datetime)
    
    Returns:
        tuple: (available_dates, missing_dates)
    """
    print(f"\n📊 Archive Data Report")
    print(f"{'='*60}")
    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    available_dates = get_available_dates()
    all_dates = get_all_dates_in_range(start_date, end_date)
    
    # Filter to dates in range
    available_in_range = [d for d in available_dates if start_date <= d <= end_date]
    missing_dates = [d for d in all_dates if d not in available_dates]
    
    print(f"\n✅ Available: {len(available_in_range)} days")
    if available_in_range:
        print(f"   First: {available_in_range[0].strftime('%Y-%m-%d')}")
        print(f"   Last:  {available_in_range[-1].strftime('%Y-%m-%d')}")
        
        # Show available dates
        print(f"\n   Dates with data:")
        for date in available_in_range:
            print(f"     ✓ {date.strftime('%Y-%m-%d (%A)')}")
    
    print(f"\n❌ Missing: {len(missing_dates)} days")
    if missing_dates:
        # Show missing dates
        print(f"\n   Dates without data:")
        for date in missing_dates:
            print(f"     ✗ {date.strftime('%Y-%m-%d (%A)')}")
    
    print(f"\n{'='*60}")
    
    return available_in_range, missing_dates


def download_missing_data(missing_dates):
    """Download data for missing dates.
    
    Args:
        missing_dates: List of datetime objects for missing dates
    
    Returns:
        int: Number of successfully downloaded dates
    """
    if not missing_dates:
        print("\n✅ No missing data to download!")
        return 0
    
    print(f"\n📥 Downloading data for {len(missing_dates)} missing date(s)...")
    
    # Load credentials
    email, password, cookie = load_env_credentials()
    
    if not cookie and not (email and password):
        print("❌ No credentials found in .env file!")
        print("   Please add QUIZY_COOKIE or QUIZY_USER + QUIZY_PASS")
        return 0
    
    # Initialize scraper
    scraper = QuizypediaScraper(rate_limiter=RateLimiter(1.0))  # 1 second between requests
    
    # Setup authentication
    if cookie:
        print("🔐 Using session cookie...")
        for cookie_part in cookie.split(';'):
            cookie_part = cookie_part.strip()
            if '=' in cookie_part:
                name, value = cookie_part.split('=', 1)
                scraper.session.cookies.set(name.strip(), value.strip())
    elif email and password:
        print(f"🔐 Logging in as {email}...")
        if not scraper.login(email, password):
            print("❌ Login failed!")
            return 0
        print("✅ Login successful!")
    
    # Download each missing date
    success_count = 0
    for i, date in enumerate(missing_dates, 1):
        print(f"\n[{i}/{len(missing_dates)}]", end=" ")
        
        leaderboard = fetch_leaderboard_for_date(scraper, date)
        
        if leaderboard:
            save_leaderboard_to_archive(date, leaderboard)
            success_count += 1
    
    print(f"\n\n✅ Successfully downloaded {success_count}/{len(missing_dates)} date(s)")
    
    return success_count


def main():
    parser = argparse.ArgumentParser(
        description="Manage historical quiz data archive",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check what data you have
  uv run scripts/manage_archive.py
  
  # Download missing data
  uv run scripts/manage_archive.py --download
  
  # Custom date range
  uv run scripts/manage_archive.py --from 2025-10-01 --to 2025-10-20
  
  # Check last 7 days
  uv run scripts/manage_archive.py --days 7
  
  # Download last 14 days
  uv run scripts/manage_archive.py --days 14 --download
        """
    )
    
    parser.add_argument(
        '--from',
        dest='start_date',
        type=str,
        help='Start date (YYYY-MM-DD). Defaults to 30 days ago'
    )
    
    parser.add_argument(
        '--to',
        dest='end_date',
        type=str,
        help='End date (YYYY-MM-DD). Defaults to yesterday'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        help='Number of days to check (from today backwards)'
    )
    
    parser.add_argument(
        '--download',
        action='store_true',
        help='Download missing data (default: just report)'
    )
    
    args = parser.parse_args()
    
    # Parse dates
    start_date = None
    end_date = None
    
    if args.days:
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        start_date = end_date - timedelta(days=args.days - 1)
    else:
        if args.start_date:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        if args.end_date:
            end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
    
    start_date, end_date = get_date_range(start_date, end_date)
    
    # Generate report
    available_dates, missing_dates = report_available_data(start_date, end_date)
    
    # Download if requested
    if args.download:
        if missing_dates:
            print("\n" + "="*60)
            response = input("\n❓ Download missing data? [y/N]: ").strip().lower()
            if response in ['y', 'yes']:
                download_missing_data(missing_dates)
            else:
                print("❌ Download cancelled")
        else:
            print("\n✅ All data already available!")
    else:
        if missing_dates:
            print("\n💡 Tip: Add --download to fetch missing dates")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
