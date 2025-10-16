#!/usr/bin/env python3
"""Complete workflow: Parse results and track mistakes.

This convenience script runs both parse_results.py and accumulate_mistakes.py
in sequence, making it easy to process a quiz session with one command.

Usage:
    uv run scripts/process_quiz.py
    
This will:
1. Parse defi_du_jour_debug.html
2. Extract mistakes from defi_du_jour_results.json
3. Add them to your historical log
4. Generate updated reports
"""
import subprocess
import sys
from pathlib import Path


def run_script(script_name: str, description: str) -> bool:
    """Run a Python script and return success status.
    
    Args:
        script_name: Name of the script to run (relative to scripts/)
        description: Human-readable description of what the script does
        
    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"📝 {description}")
    print(f"{'='*60}\n")
    
    script_path = Path(__file__).parent / script_name
    
    try:
        subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            capture_output=False
        )
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
    print("🎯 Quizz du Jour - Complete Processing Workflow")
    print("=" * 60)
    
    # Step 1: Parse results
    if not run_script("parse_results.py", "Step 1/2: Parsing quiz results"):
        print("\n❌ Failed to parse results. Make sure defi_du_jour_debug.html exists.")
        print("Tip: Save the quiz page HTML or run the scraper first.")
        return 1
    
    # Step 2: Accumulate mistakes
    if not run_script("accumulate_mistakes.py", "Step 2/2: Tracking mistakes"):
        print("\n❌ Failed to accumulate mistakes.")
        return 1
    
    print("\n" + "=" * 60)
    print("✅ COMPLETE! All processing finished successfully.")
    print("=" * 60)
    print("\n📖 Next steps:")
    print("   - Review mistakes_log.md (chronological)")
    print("   - Check mistakes_by_category.md (by topic)")
    print("   - Study your weak categories to improve!")
    print("\n💡 Tip: Run this script after each daily quiz to track progress over time.")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
