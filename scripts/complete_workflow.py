#!/usr/bin/env python3
"""Complete workflow: Fetch today's quiz, parse results, and track mistakes.

This is the ultimate convenience script that handles the entire workflow:
1. Fetch today's quiz HTML from quizypedia.fr
2. Parse your results
3. Track your mistakes in the historical log

Usage:
    # Use credentials from .env (recommended)
    uv run scripts/complete_workflow.py
    
    # Override with explicit credentials
    uv run scripts/complete_workflow.py --email you@example.com --password yourpass
    
    # Skip fetching if you already have today's HTML
    uv run scripts/complete_workflow.py --skip-fetch

IMPORTANT: You must complete the quiz on quizypedia.fr BEFORE running this script!
"""
import subprocess
import sys
import argparse
from pathlib import Path


def load_env_credentials():
    """Load credentials from .env file if it exists.
    
    Returns:
        tuple: (email, password, cookie_string) or (None, None, None)
    """
    env_file = Path(__file__).resolve().parents[1] / ".env"
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


def run_script(script_name: str, description: str, args: list = None) -> bool:
    """Run a Python script and return success status.
    
    Args:
        script_name: Name of the script to run (relative to scripts/)
        description: Human-readable description of what the script does
        args: Additional arguments to pass to the script
        
    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'='*70}")
    print(f"📝 {description}")
    print(f"{'='*70}\n")
    
    script_path = Path(__file__).parent / script_name
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    try:
        subprocess.run(cmd, check=True, capture_output=False)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running {script_name}")
        print(f"Exit code: {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"\n❌ Script not found: {script_path}")
        return False


def main():
    """Run the complete quiz processing workflow."""
    parser = argparse.ArgumentParser(
        description="Complete workflow: Fetch, parse, and track today's quiz",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use credentials from .env file (recommended)
  uv run scripts/complete_workflow.py
  
  # Override with explicit credentials
  uv run scripts/complete_workflow.py --email you@example.com --password yourpass
  
  # Skip fetch, just parse and track (if you already have the HTML)
  uv run scripts/complete_workflow.py --skip-fetch

Note: You must complete the quiz on quizypedia.fr BEFORE running this script.
      The script will automatically use credentials from .env if available.
        """
    )
    
    parser.add_argument('--email', help='Email for login (optional, overrides .env)')
    parser.add_argument('--password', help='Password for login (optional, overrides .env)')
    parser.add_argument('--skip-fetch', action='store_true',
                       help='Skip fetching, assume HTML already exists')
    
    args = parser.parse_args()
    
    # Try to load from .env first
    env_email, env_password, env_cookie = load_env_credentials()
    
    # Use command line args if provided, otherwise use .env
    email = args.email or env_email
    password = args.password or env_password
    has_credentials = env_cookie or (email and password)
    
    print("🎯 Quizz du Jour - Complete Workflow")
    print("=" * 70)
    print("This will:")
    if not args.skip_fetch:
        if has_credentials:
            print("  1. Fetch today's quiz HTML from quizypedia.fr (authenticated)")
        else:
            print("  1. Fetch today's quiz HTML from quizypedia.fr (no auth)")
        print("  2. Parse your quiz results")
        print("  3. Track mistakes in historical log")
        print("  4. Generate updated reports")
    else:
        print("  1. Parse your quiz results (using existing HTML)")
        print("  2. Track mistakes in historical log")
        print("  3. Generate updated reports")
    print("=" * 70)
    
    # Validate credentials
    if (args.email and not args.password) or (args.password and not args.email):
        print("❌ Error: Both --email and --password are required for login")
        return 1
    
    step_num = 1
    total_steps = 3 if not args.skip_fetch else 2
    
    # Step 1: Fetch today's quiz (unless skipped)
    if not args.skip_fetch:
        fetch_args = []
        # Only pass explicit credentials if provided on command line
        if args.email and args.password:
            fetch_args = ['--email', args.email, '--password', args.password]
        # Otherwise fetch_today_quiz.py will use .env automatically
        
        if not run_script("fetch_today_quiz.py", 
                         f"Step {step_num}/{total_steps}: Fetching today's quiz from quizypedia.fr",
                         fetch_args):
            print("\n❌ Failed to fetch quiz.")
            print("💡 Tip: You can use --skip-fetch if you already have the HTML file.")
            return 1
        step_num += 1
    
    # Step 2: Parse results
    if not run_script("parse_results.py", 
                     f"Step {step_num}/{total_steps}: Parsing quiz results"):
        print("\n❌ Failed to parse results.")
        print("💡 Tip: Make sure defi_du_jour_debug.html exists and contains quiz data.")
        return 1
    step_num += 1
    
    # Step 3: Accumulate mistakes
    if not run_script("accumulate_mistakes.py", 
                     f"Step {step_num}/{total_steps}: Tracking mistakes"):
        print("\n❌ Failed to accumulate mistakes.")
        return 1
    
    print("\n" + "=" * 70)
    print("✅ COMPLETE! All processing finished successfully.")
    print("=" * 70)
    print("\n📖 Check these files:")
    print("   - mistakes_log.md (chronological list of all mistakes)")
    print("   - mistakes_by_category.md (mistakes grouped by topic)")
    print("   - mistakes_history.json (master database)")
    print("\n💡 Tip: Run this script after each daily quiz to track progress!")
    print("🎓 Study your weak categories to improve your score!")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
