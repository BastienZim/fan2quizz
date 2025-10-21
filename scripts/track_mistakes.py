"""Track and analyze mistakes from Quizz du Jour.

This script extracts all incorrect answers from defi_du_jour_results.json files
and creates a comprehensive document to help improve at Quizypedia.

For each mistake, it shows:
- Date of the quiz
- Category/Theme of the question
- The question text
- Your incorrect answer
- The correct answer

Usage:
    uv run scripts/track_mistakes.py
    
Output:
    - output/reports/mistakes_log.md: Markdown document with all mistakes
    - data/results/mistakes_log.json: JSON file with structured mistake data
"""
import json
from pathlib import Path
from typing import List, Dict, Any

# Project root
ROOT = Path(__file__).parent.parent

# File paths
RESULTS_FILE = ROOT / "data" / "results" / "defi_du_jour_results.json"
MISTAKES_MD = ROOT / "output" / "reports" / "mistakes_log.md"
MISTAKES_BY_CAT = ROOT / "output" / "reports" / "mistakes_by_category.md"
MISTAKES_JSON = ROOT / "data" / "results" / "mistakes_log.json"


def load_quiz_results(json_path: Path) -> Dict[str, Any]:
    """Load quiz results from JSON file.
    
    Args:
        json_path: Path to the quiz results JSON file
        
    Returns:
        Dictionary containing user_info and questions
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_mistakes(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract all incorrect answers from quiz data.
    
    Args:
        data: Quiz results dictionary
        
    Returns:
        List of mistake dictionaries
    """
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


def format_mistakes_markdown(mistakes: List[Dict[str, Any]]) -> str:
    """Format mistakes as a Markdown document.
    
    Args:
        mistakes: List of mistake dictionaries
        
    Returns:
        Formatted Markdown string
    """
    md = "# 📚 Quizz du Jour - Mistakes Log\n\n"
    md += "This document tracks all incorrect answers to help you improve at Quizypedia.\n\n"
    md += f"**Total Mistakes Tracked:** {len(mistakes)}\n\n"
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
        
        for i, mistake in enumerate(date_mistakes, 1):
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
    """Format mistakes grouped by category.
    
    Args:
        mistakes: List of mistake dictionaries
        
    Returns:
        Formatted Markdown string
    """
    md = "# 📊 Mistakes by Category\n\n"
    
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
    MISTAKES_JSON.parent.mkdir(parents=True, exist_ok=True)
    
    if not RESULTS_FILE.exists():
        print(f"❌ Error: {RESULTS_FILE} not found")
        print("Please make sure you have run the parse_results.py script first.")
        return
    
    print("📖 Loading quiz results...")
    data = load_quiz_results(RESULTS_FILE)
    
    print("🔍 Extracting mistakes...")
    mistakes = extract_mistakes(data)
    
    if not mistakes:
        print("🎉 No mistakes found! Perfect score!")
        return
    
    print(f"📝 Found {len(mistakes)} mistakes")
    
    # Generate chronological mistakes log
    print("📄 Generating mistakes log (chronological)...")
    md_content = format_mistakes_markdown(mistakes)
    MISTAKES_MD.write_text(md_content, encoding='utf-8')
    print(f"✅ Saved to {MISTAKES_MD}")
    
    # Generate category-based analysis
    print("📊 Generating mistakes by category...")
    category_content = format_mistakes_by_category(mistakes)
    MISTAKES_BY_CAT.write_text(category_content, encoding='utf-8')
    print(f"✅ Saved to {MISTAKES_BY_CAT}")
    
    # Save JSON for further processing
    with open(MISTAKES_JSON, 'w', encoding='utf-8') as f:
        json.dump(mistakes, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved JSON to {MISTAKES_JSON}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    date = data.get('user_info', {}).get('date', '').strip('"')
    score = data.get('user_info', {}).get('good_responses', 0)
    print(f"Date: {date}")
    print(f"Score: {score}/20")
    print(f"Mistakes: {len(mistakes)}")
    
    # Category breakdown
    by_category = {}
    for mistake in mistakes:
        cat = mistake['category']
        by_category[cat] = by_category.get(cat, 0) + 1
    
    if by_category:
        print("\nMistakes by category:")
        for cat, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {cat}: {count}")
    
    print("\n📖 Review your mistakes in:")
    print(f"   - {MISTAKES_MD} (chronological)")
    print(f"   - {MISTAKES_BY_CAT} (by category)")


if __name__ == '__main__':
    main()
