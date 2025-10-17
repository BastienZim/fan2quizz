#!/usr/bin/env python3
"""Fetch today's Défi du jour HTML and save it for parsing.

This script scrapes the live daily quiz page from quizypedia.fr and saves
it as defi_du_jour_debug.html so you can parse your results.

IMPORTANT: You must complete the quiz on the website BEFORE running this script,
otherwise it will only fetch the questions without your answers.

Usage:
    uv run scripts/fetch_today_quiz.py                    # Uses credentials from .env
    uv run scripts/fetch_today_quiz.py --email ... --password ...  # Override credentials

Output:
    - defi_du_jour_debug.html (overwrites existing file with today's quiz)
"""
import sys
from pathlib import Path
import argparse

# Add parent directory to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fan2quizz.scraper import QuizypediaScraper
from fan2quizz.utils import RateLimiter


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


def fetch_and_save_today_quiz(email: str = None, password: str = None, cookie: str = None):
    """Fetch today's quiz HTML and save it.
    
    Args:
        email: Optional email for login
        password: Optional password for login
        cookie: Optional session cookie string
    """
    print("🔍 Fetching today's Défi du jour...")
    
    # Initialize scraper
    scraper = QuizypediaScraper(rate_limiter=RateLimiter(0.5))
    
    # Use cookie if provided (faster and more reliable)
    if cookie:
        print("🔐 Using session cookie from .env...")
        # Parse cookie string and set cookies
        for cookie_part in cookie.split(';'):
            cookie_part = cookie_part.strip()
            if '=' in cookie_part:
                name, value = cookie_part.split('=', 1)
                scraper.session.cookies.set(name.strip(), value.strip())
        print("✅ Session cookie loaded!")
    
    # Otherwise, login if credentials provided
    elif email and password:
        print(f"🔐 Logging in as {email}...")
        success = scraper.login(email, password, debug=True)
        if not success:
            print("❌ Login failed. Continuing without authentication...")
            print("⚠️  Note: Without login, you won't see your personal answers.")
        else:
            print("✅ Login successful!")
    else:
        print("⚠️  No credentials provided. Fetching without authentication...")
        print("   (You won't see your personal answers)")
    
    # Fetch today's quiz
    try:
        html = scraper.fetch_daily_live_html()
        print(f"✅ Fetched HTML ({len(html)} bytes)")
    except Exception as e:
        print(f"❌ Error fetching quiz: {e}")
        return 1
    
    # Save to file
    output_file = ROOT / "defi_du_jour_debug.html"
    output_file.write_text(html, encoding='utf-8')
    print(f"💾 Saved to: {output_file}")
    
    # Check if it contains quiz data
    if 'DC_DATA' in html:
        print("✅ Quiz data found in HTML!")
        
        # Try to extract date
        import re
        date_match = re.search(r'date:\s*"(\d{4}-\d{2}-\d{2})"', html)
        if date_match:
            quiz_date = date_match.group(1)
            print(f"📅 Quiz date: {quiz_date}")
    else:
        print("⚠️  Warning: Quiz data (DC_DATA) not found in HTML")
        print("   Make sure you've completed the quiz on the website first!")
    
    print("\n" + "="*60)
    print("🎯 Next steps:")
    print("   1. Run: uv run scripts/parse_results.py")
    print("   2. Run: uv run scripts/accumulate_mistakes.py")
    print("   Or simply run: uv run scripts/process_quiz.py")
    print("="*60)
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Fetch today's Défi du jour HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch using credentials from .env file (recommended)
  uv run scripts/fetch_today_quiz.py
  
  # Fetch with explicit credentials (overrides .env)
  uv run scripts/fetch_today_quiz.py --email you@example.com --password yourpass

Note: You must complete the quiz on quizypedia.fr BEFORE running this script.
      The script will automatically use credentials from .env if available.
        """
    )
    
    parser.add_argument(
        '--email',
        help='Email for login (optional, overrides .env)'
    )
    parser.add_argument(
        '--password',
        help='Password for login (optional, overrides .env)'
    )
    
    args = parser.parse_args()
    
    # Try to load from .env first
    env_email, env_password, env_cookie = load_env_credentials()
    
    # Use command line args if provided, otherwise use .env
    email = args.email or env_email
    password = args.password or env_password
    cookie = env_cookie  # Cookie is only from .env
    
    # Validate credentials
    if (args.email and not args.password) or (args.password and not args.email):
        print("❌ Error: Both --email and --password are required for login")
        return 1
    
    # Show what we're using
    if cookie:
        print("📋 Using credentials from .env (session cookie)")
    elif email and password:
        if args.email:
            print(f"📋 Using credentials from command line ({email})")
        else:
            print(f"📋 Using credentials from .env ({email})")
    else:
        print("⚠️  No credentials found in .env or command line")
    
    return fetch_and_save_today_quiz(email, password, cookie)


if __name__ == '__main__':
    sys.exit(main())
