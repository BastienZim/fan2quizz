"""Accumulate mistakes from multiple quiz sessions.

This script manages a historical log of all your mistakes across multiple
quiz sessions. Each time you run parse_results.py and generate a new
defi_du_jour_results.json, run this script to add those mistakes to your
cumulative mistakes database.

Usage:
    uv run scripts/accumulate_mistakes.py
    
This will:
1. Read the current data/results/defi_du_jour_results.json
2. Extract new mistakes
3. Add them to data/results/mistakes_history.json (preserving old data)
4. Regenerate the output/reports/mistakes_log.md and output/reports/mistakes_by_category.md with ALL mistakes
"""
import json
from pathlib import Path
from typing import List, Dict, Any

# Project root
ROOT = Path(__file__).parent.parent

# File paths
RESULTS_FILE = ROOT / "data" / "results" / "defi_du_jour_results.json"
HISTORY_FILE = ROOT / "data" / "results" / "mistakes_history.json"
MISTAKES_MD = ROOT / "output" / "reports" / "mistakes_log.md"
MISTAKES_BY_CAT = ROOT / "output" / "reports" / "mistakes_by_category.md"


def load_quiz_results(json_path: Path) -> Dict[str, Any]:
    """Load quiz results from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_mistakes(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract all incorrect answers from quiz data."""
    mistakes = []
    user_info = data.get('user_info', {})
    date = user_info.get('date', '').strip('"')
    questions = data.get('questions', [])
    
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


def load_historical_mistakes() -> List[Dict[str, Any]]:
    """Load existing historical mistakes."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_historical_mistakes(mistakes: List[Dict[str, Any]]):
    """Save historical mistakes to file."""
    # Ensure directory exists
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(mistakes, f, indent=2, ensure_ascii=False)


def format_mistakes_markdown(mistakes: List[Dict[str, Any]]) -> str:
    """Format mistakes as a Markdown document."""
    md = "# 📚 Quizz du Jour - Complete Mistakes Log\n\n"
    md += "This document tracks ALL incorrect answers across all quiz sessions.\n\n"
    md += f"**Total Mistakes Tracked:** {len(mistakes)}\n\n"
    
    # Get unique dates
    dates = sorted(set(m['date'] for m in mistakes), reverse=True)
    md += f"**Quiz Sessions:** {len(dates)}\n\n"
    md += "---\n\n"
    
    # Group mistakes by date
    mistakes_by_date = {}
    for mistake in mistakes:
        date = mistake['date']
        if date not in mistakes_by_date:
            mistakes_by_date[date] = []
        mistakes_by_date[date].append(mistake)
    
    # Sort dates in reverse chronological order
    sorted_dates = sorted(mistakes_by_date.keys(), reverse=True)
    
    for date in sorted_dates:
        date_mistakes = mistakes_by_date[date]
        md += f"## 📅 {date}\n\n"
        md += f"**Mistakes:** {len(date_mistakes)}\n\n"
        
        for mistake in date_mistakes:
            md += f"### Question {mistake['question_number']} - {mistake['category']}\n\n"
            md += f"**Question:** {mistake['question']}\n\n"
            
            if mistake['hints']:
                md += "**Hints:**\n"
                for hint in mistake['hints']:
                    md += f"- {hint}\n"
                md += "\n"
            
            md += "**Choices:**\n"
            for j, choice in enumerate(mistake['all_choices']):
                marker = ""
                if choice == mistake['your_answer']:
                    marker = " ❌ (Your answer)"
                elif choice == mistake['correct_answer']:
                    marker = " ✅ (Correct)"
                md += f"{j}. {choice}{marker}\n"
            md += "\n"
            
            md += "---\n\n"
    
    return md


def format_mistakes_by_category(mistakes: List[Dict[str, Any]]) -> str:
    """Format mistakes grouped by category."""
    md = "# 📊 Mistakes by Category - Complete History\n\n"
    
    # Group by category
    by_category = {}
    for mistake in mistakes:
        cat = mistake['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(mistake)
    
    # Sort categories by number of mistakes (descending)
    sorted_categories = sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True)
    
    md += "## Summary\n\n"
    md += f"**Total Categories with Mistakes:** {len(by_category)}\n\n"
    md += "| Category | Mistakes |\n"
    md += "|----------|----------|\n"
    for cat, cat_mistakes in sorted_categories:
        md += f"| {cat} | {len(cat_mistakes)} |\n"
    md += "\n---\n\n"
    
    # Detailed view by category
    for cat, cat_mistakes in sorted_categories:
        md += f"## {cat}\n\n"
        md += f"**Total mistakes in this category:** {len(cat_mistakes)}\n\n"
        
        for mistake in cat_mistakes:
            md += f"### {mistake['date']} - Question {mistake['question_number']}\n\n"
            md += f"**Q:** {mistake['question']}\n\n"
            
            if mistake['hints']:
                for hint in mistake['hints']:
                    md += f"*{hint}*\n\n"
            
            md += f"- ❌ Your answer: **{mistake['your_answer']}**\n"
            md += f"- ✅ Correct answer: **{mistake['correct_answer']}**\n\n"
            md += "---\n\n"
    
    return md


def main():
    """Main execution function."""
    # Ensure output directories exist
    MISTAKES_MD.parent.mkdir(parents=True, exist_ok=True)
    
    if not RESULTS_FILE.exists():
        print(f"❌ Error: {RESULTS_FILE} not found")
        print("Please run parse_results.py first to generate quiz results.")
        return
    
    print("📖 Loading current quiz results...")
    data = load_quiz_results(RESULTS_FILE)
    
    print("🔍 Extracting new mistakes...")
    new_mistakes = extract_mistakes(data)
    
    current_date = data.get('user_info', {}).get('date', '').strip('"')
    print(f"📅 Quiz date: {current_date}")
    print(f"📝 New mistakes found: {len(new_mistakes)}")
    
    # Load historical data
    print("📚 Loading historical mistakes...")
    all_mistakes = load_historical_mistakes()
    
    # Check if this date already exists
    existing_dates = set(m['date'] for m in all_mistakes)
    if current_date in existing_dates:
        print(f"⚠️  Warning: Mistakes for {current_date} already exist in history.")
        response = input("Do you want to replace them? (y/n): ")
        if response.lower() == 'y':
            # Remove old mistakes for this date
            all_mistakes = [m for m in all_mistakes if m['date'] != current_date]
            print(f"🗑️  Removed old mistakes for {current_date}")
        else:
            print("❌ Aborted. Historical data unchanged.")
            return
    
    # Add new mistakes
    all_mistakes.extend(new_mistakes)
    
    # Sort by date (newest first)
    all_mistakes.sort(key=lambda x: x['date'], reverse=True)
    
    print(f"💾 Saving historical data ({len(all_mistakes)} total mistakes)...")
    save_historical_mistakes(all_mistakes)
    
    # Generate reports
    print("📄 Generating complete mistakes log...")
    md_content = format_mistakes_markdown(all_mistakes)
    MISTAKES_MD.write_text(md_content, encoding='utf-8')
    print(f"✅ Saved to {MISTAKES_MD}")
    
    print("📊 Generating mistakes by category...")
    category_content = format_mistakes_by_category(all_mistakes)
    MISTAKES_BY_CAT.write_text(category_content, encoding='utf-8')
    print(f"✅ Saved to {MISTAKES_BY_CAT}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    dates = sorted(set(m['date'] for m in all_mistakes), reverse=True)
    print(f"Total quiz sessions: {len(dates)}")
    print(f"Total mistakes: {len(all_mistakes)}")
    
    # Category breakdown
    by_category = {}
    for mistake in all_mistakes:
        cat = mistake['category']
        by_category[cat] = by_category.get(cat, 0) + 1
    
    print(f"Categories with mistakes: {len(by_category)}")
    
    if by_category:
        print("\nTop 10 categories with most mistakes:")
        top_categories = sorted(by_category.items(), key=lambda x: x[1], reverse=True)[:10]
        for i, (cat, count) in enumerate(top_categories, 1):
            print(f"  {i}. {cat}: {count}")
    
    print(f"\n📖 Added {len(new_mistakes)} new mistakes to your learning log!")
    print("Review your complete history in:")
    print(f"   - {MISTAKES_MD} (chronological)")
    print(f"   - {MISTAKES_BY_CAT} (by category)")


if __name__ == '__main__':
    main()
