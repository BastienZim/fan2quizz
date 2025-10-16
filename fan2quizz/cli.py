"""Command-line interface entry points for fan2quizz."""

from pathlib import Path


def parse_results_main():
    """Entry point for parse-results command."""
    scripts_dir = Path(__file__).parent.parent / "scripts"
    script_path = scripts_dir / "parse_results.py"
    
    # Execute the script
    with open(script_path) as f:
        code = compile(f.read(), script_path, 'exec')
        exec(code, {'__name__': '__main__', '__file__': str(script_path)})


def daily_report_main():
    """Entry point for daily-report command."""
    scripts_dir = Path(__file__).parent.parent / "scripts"
    script_path = scripts_dir / "daily_report.py"
    
    # Execute the script
    with open(script_path) as f:
        code = compile(f.read(), script_path, 'exec')
        exec(code, {'__name__': '__main__', '__file__': str(script_path)})


if __name__ == "__main__":
    print("This module provides CLI entry points.")
    print("Available commands after 'pip install -e .':")
    print("  - parse-results")
    print("  - daily-report")
