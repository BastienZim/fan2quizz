"""Parse Défi du jour results from saved HTML.

This script extracts quiz data from the HTML file saved by scrape_quizypedia_defi_du_jour.py
and formats it into a human-readable report showing:
- Your score and time
- Each question with your answer vs the correct answer
- Success/failure indicators

The quiz data is embedded in JavaScript variables (DC_DATA and DC_USER) in the HTML.

Usage:
    python parse_defi_results.py

Output:
    - Console: Formatted quiz results with emojis
    - File: defi_du_jour_results.json (structured JSON data)
"""
import json
import re
from pathlib import Path

def extract_dc_data_from_html(html_path):
    """Extract the DC_DATA JavaScript variable from the HTML.
    
    Args:
        html_path: Path to the HTML file saved by the scraper
        
    Returns:
        tuple: (questions list, user_info dict)
        
    Raises:
        ValueError: If DC_DATA variable is not found in the HTML
    """
    html = Path(html_path).read_text(encoding='utf-8')
    
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

def format_results(questions, user_info):
    """Format the quiz results nicely.
    
    Args:
        questions: List of question dictionaries from DC_DATA
        user_info: Dictionary of user stats from DC_USER
    """
    print("=" * 80)
    print("DÉFI DU JOUR - Results")
    print("=" * 80)
    print(f"\nCorrect Answers: {user_info.get('good_responses', 'N/A')}/20")
    print(f"Time Elapsed: {user_info.get('elapsed_time', 'N/A')} seconds")
    print("\n" + "=" * 80)
    print("DETAILED ANSWERS:")
    print("=" * 80)
    
    for i, q in enumerate(questions, 1):
        theme = q.get('theme_title', 'Unknown theme')
        question = q.get('question', 'Unknown question')
        hints = q.get('hints', [])
        proposed_responses = q.get('proposed_responses', [])
        correct_index = q.get('response_index')
        chosen_index = q.get('chosen_index')
        
        print(f"\n{'─' * 80}")
        print(f"Question {i}: {theme}")
        print(f"{'─' * 80}")
        print(f"❓ {question}")
        
        if hints:
            for hint in hints:
                hint_type = hint.get('type', '')
                hint_value = hint.get('value', '')
                print(f"   💡 {hint_type}: {hint_value}")
        
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
            
            print(f"   {j}. {response_text}{marker}")
        
        if chosen_index == correct_index:
            print("\n   ✅ You got this one right!")
        else:
            correct_answer = proposed_responses[correct_index].get('response', '') if correct_index is not None else 'N/A'
            your_answer = proposed_responses[chosen_index].get('response', 'N/A') if chosen_index is not None else 'No answer'
            print("\n   ❌ You got this one wrong")
            print(f"   Your answer: {your_answer}")
            print(f"   Correct answer: {correct_answer}")

if __name__ == "__main__":
    html_file = "defi_du_jour_debug.html"
    questions, user_info = extract_dc_data_from_html(html_file)
    format_results(questions, user_info)
    
    # Also save as JSON
    output = {
        "user_info": user_info,
        "questions": questions
    }
    output_file = Path("defi_du_jour_results.json")
    output_file.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n\n{'=' * 80}")
    print(f"Full results saved to: {output_file}")
    print(f"{'=' * 80}")
