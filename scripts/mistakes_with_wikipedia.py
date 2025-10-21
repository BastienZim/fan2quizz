#!/usr/bin/env python3
"""
Generate a mistake report with Wikipedia links for each failed question.

This script takes the mistakes history and enriches it with relevant Wikipedia
links to help users learn more about the topics they got wrong.

Features:
- Loads mistakes from mistakes_history.json
- Searches Wikipedia for relevant articles based on the correct answer
- Generates a comprehensive Markdown report with clickable links
- Supports filtering by date range
- Groups mistakes by category

Usage examples:
    uv run scripts/mistakes_with_wikipedia.py
    uv run scripts/mistakes_with_wikipedia.py --days 7
    uv run scripts/mistakes_with_wikipedia.py --player BastienZim
    uv run scripts/mistakes_with_wikipedia.py --output custom_report.md
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
import urllib.parse
import urllib.request
 


ROOT = Path(__file__).resolve().parents[1]
MISTAKES_FILE = ROOT / "data" / "results" / "mistakes_history.json"
OUTPUT_DIR = ROOT / "output" / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --- Wikipedia Helper Class ---
class WikiHelper:
    def __init__(self, lang: str = "fr"):
        self.lang = lang
        self.cache = {}

    def link(self, topic: str) -> str:
        from urllib.parse import quote
        return f"https://{self.lang}.wikipedia.org/wiki/{quote(topic.replace(' ', '_'))}"

    def search_api(self, query: str) -> str:
        import urllib.request
        import urllib.parse
        import json
        api_url = f"https://{self.lang}.wikipedia.org/w/api.php"
        params = {
            "action": "opensearch",
            "search": query,
            "limit": 1,
            "namespace": 0,
            "format": "json"
        }
        url = f"{api_url}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Fan2Quizz/1.0 (Educational Quiz Assistant; Python script)'
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
            if len(data) >= 4 and len(data[3]) > 0:
                return data[3][0]
        except Exception as e:
            print(f"⚠️  Error searching Wikipedia for '{query}': {e}")
        return None

    def markdown_link(self, topic: str) -> str:
        # Use cache if available
        if topic in self.cache:
            return self.cache[topic]
        url = self.search_api(topic)
        if url:
            link = f"[📖 Wikipedia: {topic}]({url})"
            self.cache[topic] = link
            import time
            time.sleep(0.1)
            return link
        else:
            self.cache[topic] = "_No Wikipedia page found_"
            return "_No Wikipedia page found_"

    def get_summary_api(self, topic: str, sentences: int = 2) -> Optional[str]:
        """Get summary from Wikipedia API."""
        import urllib.request
        import urllib.parse
        import json
        
        api_url = f"https://{self.lang}.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "exsentences": sentences,
            "titles": topic
        }
        url = f"{api_url}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Fan2Quizz/1.0 (Educational Quiz Assistant; Python script)'
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                if page_id != '-1' and 'extract' in page_data:
                    return page_data['extract']
        except Exception:
            pass
        return None

    def fetch_wikipedia_summary(self, topic: str, sentences: int = 2) -> str:
        """Fetch Wikipedia summary with better error handling."""
        try:
            import wikipedia  # optional dep
            wikipedia.set_lang(self.lang)
            try:
                return wikipedia.summary(topic, sentences=sentences)
            except wikipedia.DisambiguationError as e:
                return f"Topic is ambiguous. Try one of: {', '.join(e.options[:5])}..."
            except wikipedia.PageError:
                return "No page found."
        except Exception:
            # library not installed or other issue → gentle fallback
            return f"(Wikipedia not available) See: https://{self.lang}.wikipedia.org/wiki/{topic.replace(' ', '_')}"

    def summary(self, topic: str, sentences: int = 2) -> str:
        """Get summary with fallback to API if wikipedia package not available."""
        # Try the improved fetch method first
        result = self.fetch_wikipedia_summary(topic, sentences)
        
        # If wikipedia library is not available, try REST API
        if result.startswith("(Wikipedia not available)"):
            s = self.get_summary_api(topic, sentences)
            return s if s else ""
        
        return result


def search_wikipedia(query: str, lang: str = "fr") -> Optional[str]:
    """
    Search Wikipedia and return the URL of the most relevant article.
    
    Args:
        query: Search query (typically the correct answer)
        lang: Wikipedia language code (default: "fr" for French)
    
    Returns:
        URL of the Wikipedia page or None if not found
    """
    try:
        # Wikipedia API endpoint
        api_url = f"https://{lang}.wikipedia.org/w/api.php"
        
        # Search parameters
        params = {
            "action": "opensearch",
            "search": query,
            "limit": 1,
            "namespace": 0,
            "format": "json"
        }
        
        # Build URL
        url = f"{api_url}?{urllib.parse.urlencode(params)}"
        
        # Create request with User-Agent header (required by Wikipedia)
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Fan2Quizz/1.0 (Educational Quiz Assistant; Python script)'
            }
        )
        
        # Make request with timeout
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        # Parse response: [query, [titles], [descriptions], [urls]]
        if len(data) >= 4 and len(data[3]) > 0:
            return data[3][0]  # Return first URL
        
        return None
    except Exception as e:
        print(f"⚠️  Error searching Wikipedia for '{query}': {e}")
        return None





def load_mistakes() -> List[Dict[str, Any]]:
    """Load mistakes from the history file."""
    if not MISTAKES_FILE.exists():
        print(f"❌ Mistakes file not found: {MISTAKES_FILE}")
        return []
    
    try:
        with open(MISTAKES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading mistakes: {e}")
        return []


def filter_mistakes_by_date(mistakes: List[Dict], days: Optional[int] = None) -> List[Dict]:
    """
    Filter mistakes to only include those from the last N days.
    
    Args:
        mistakes: List of mistake dictionaries
        days: Number of days to look back (None = all time)
    
    Returns:
        Filtered list of mistakes
    """
    if days is None:
        return mistakes
    
    cutoff_date = datetime.now() - timedelta(days=days)
    filtered = []
    
    for mistake in mistakes:
        try:
            mistake_date = datetime.strptime(mistake['date'], '%Y-%m-%d')
            if mistake_date >= cutoff_date:
                filtered.append(mistake)
        except (ValueError, KeyError):
            # If date parsing fails, include the mistake
            filtered.append(mistake)
    
    return filtered


def group_mistakes_by_category(mistakes: List[Dict]) -> Dict[str, List[Dict]]:
    """Group mistakes by category."""
    grouped = defaultdict(list)
    for mistake in mistakes:
        category = mistake.get('category', 'Unknown Category')
        grouped[category].append(mistake)
    return dict(grouped)


def generate_markdown_report(mistakes: List[Dict], output_file: Path, 
                            include_wikipedia: bool = True,
                            group_by_category: bool = False) -> bool:
    """
    Generate a Markdown report of mistakes with Wikipedia links.
    
    Args:
        mistakes: List of mistake dictionaries
        output_file: Path to output Markdown file
        include_wikipedia: Whether to include Wikipedia links
        group_by_category: Whether to group mistakes by category
    
    Returns:
        True if successful
    """
    if not mistakes:
        print("⚠️  No mistakes to report!")
        return False
    
    print(f"📝 Generating report with {len(mistakes)} mistake(s)...")
    
    # Wikipedia helper
    wiki = WikiHelper(lang="fr")
    
    # Start building the report
    lines = []
    lines.append("# 📚 Mistake Report with Wikipedia Resources\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"**Total Mistakes:** {len(mistakes)}\n")
    lines.append("---\n")
    
    if group_by_category:
        # Group by category
        grouped = group_mistakes_by_category(mistakes)
        lines.append(f"\n**Categories:** {len(grouped)}\n")
        
        for category, cat_mistakes in sorted(grouped.items()):
            lines.append(f"\n## 📂 {category}\n")
            lines.append(f"**{len(cat_mistakes)} mistake(s)**\n")
            for mistake in cat_mistakes:
                lines.extend(_format_mistake(mistake, wiki, include_wikipedia))
    else:
        # Chronological order
        lines.append("\n## 📅 Mistakes by Date\n")
        
        for mistake in mistakes:
            lines.extend(_format_mistake(mistake, wiki, include_wikipedia))
    
    # Write to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"✅ Report saved to: {output_file}")
        return True
    except Exception as e:
        print(f"❌ Error writing report: {e}")
        return False


def _format_mistake(mistake: Dict, wiki_cache: Dict, include_wikipedia: bool) -> List[str]:
    """
    Format a single mistake as Markdown lines.
    
    Args:
        mistake: Mistake dictionary
        wiki_cache: Cache for Wikipedia links
        include_wikipedia: Whether to include Wikipedia links
    
    Returns:
        List of formatted lines
    """
    lines = []
    
    # Header with date and question number
    date = mistake.get('date', 'Unknown Date')
    question_num = mistake.get('question_number', '?')
    lines.append(f"\n### ❌ Question {question_num} — {date}\n")
    
    # Category
    category = mistake.get('category', 'Unknown Category')
    lines.append(f"**Category:** {category}\n")
    
    # Question
    question = mistake.get('question', '').strip()
    if question:
        lines.append(f"\n**Question:** {question}\n")
    
    # Hints
    hints = mistake.get('hints', [])
    if hints:
        lines.append("\n**Hints:**\n")
        for hint in hints:
            lines.append(f"- {hint}\n")
    
    # Answers
    your_answer = mistake.get('your_answer', 'Unknown')
    correct_answer = mistake.get('correct_answer', 'Unknown')
    
    lines.append(f"\n- ❌ **Your Answer:** {your_answer}\n")
    lines.append(f"- ✅ **Correct Answer:** {correct_answer}\n")
    
    # All choices (if available)
    all_choices = mistake.get('all_choices', [])
    if all_choices:
        lines.append(f"\n**All Choices:** {', '.join(all_choices)}\n")
    
    # Wikipedia summary and link
    if include_wikipedia:
        lines.append("\n**Learn More:**\n")
        
        # Get and display summary for the correct answer
        summary = wiki_cache.summary(correct_answer, sentences=2)
        if summary:
            lines.append(f"\n{summary}\n")
        
        # Add Wikipedia link
        wiki_link = wiki_cache.markdown_link(correct_answer)
        lines.append(f"\n- {wiki_link}\n")
        
        # Try to get link for the category/topic as well
        if category and category != "Unknown Category":
            topic = category.split('(')[0].strip()
            if topic and topic != correct_answer:
                topic_link = wiki_cache.markdown_link(topic)
                lines.append(f"- Category: {topic_link}\n")
    
    lines.append("\n---\n")
    
    return lines


def generate_summary_stats(mistakes: List[Dict]) -> Dict[str, Any]:
    """Generate summary statistics about mistakes."""
    if not mistakes:
        return {}
    
    # Count by category
    by_category = defaultdict(int)
    for mistake in mistakes:
        category = mistake.get('category', 'Unknown')
        by_category[category] += 1
    
    # Sort by frequency
    sorted_categories = sorted(by_category.items(), key=lambda x: x[1], reverse=True)
    
    # Date range
    dates = [m.get('date') for m in mistakes if m.get('date')]
    date_range = (min(dates), max(dates)) if dates else None
    
    return {
        'total_mistakes': len(mistakes),
        'unique_categories': len(by_category),
        'top_categories': sorted_categories[:5],
        'date_range': date_range
    }


def print_summary(stats: Dict[str, Any]):
    """Print summary statistics to console."""
    if not stats:
        return
    
    print("\n" + "="*60)
    print("📊 SUMMARY STATISTICS")
    print("="*60)
    print(f"Total Mistakes: {stats['total_mistakes']}")
    print(f"Unique Categories: {stats['unique_categories']}")
    
    if stats.get('date_range'):
        start, end = stats['date_range']
        print(f"Date Range: {start} to {end}")
    
    print("\nTop 5 Categories:")
    for category, count in stats.get('top_categories', []):
        print(f"  • {category}: {count} mistake(s)")
    
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generate mistake report with Wikipedia links",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate full report with Wikipedia links
  uv run scripts/mistakes_with_wikipedia.py
  
  # Last 7 days only
  uv run scripts/mistakes_with_wikipedia.py --days 7
  
  # Last 30 days only
  uv run scripts/mistakes_with_wikipedia.py --days 30
  
  # Group by category instead of chronological
  uv run scripts/mistakes_with_wikipedia.py --group-by-category
  
  # Without Wikipedia links (faster)
  uv run scripts/mistakes_with_wikipedia.py --no-wikipedia
  
  # Custom output file
  uv run scripts/mistakes_with_wikipedia.py --output my_mistakes.md
  
  # Show summary statistics only
  uv run scripts/mistakes_with_wikipedia.py --summary-only
        """
    )
    
    parser.add_argument('--days', type=int,
                       help='Only include mistakes from last N days (default: all time)')
    parser.add_argument('--output', '-o',
                       help='Output file path (default: mistakes_with_wikipedia.md)')
    parser.add_argument('--no-wikipedia', action='store_true',
                       help='Skip Wikipedia link generation (faster)')
    parser.add_argument('--group-by-category', action='store_true',
                       help='Group mistakes by category instead of chronological order')
    parser.add_argument('--summary-only', action='store_true',
                       help='Only show summary statistics, do not generate report')
    
    args = parser.parse_args()
    
    # Load mistakes
    print("📖 Loading mistakes history...")
    mistakes = load_mistakes()
    
    if not mistakes:
        print("❌ No mistakes found!")
        return 1
    
    print(f"✅ Loaded {len(mistakes)} total mistake(s)")
    
    # Filter by date if requested
    if args.days:
        mistakes = filter_mistakes_by_date(mistakes, args.days)
        print(f"📅 Filtered to {len(mistakes)} mistake(s) from last {args.days} days")
    
    if not mistakes:
        print("⚠️  No mistakes match the specified criteria")
        return 1
    
    # Generate and show summary statistics
    stats = generate_summary_stats(mistakes)
    print_summary(stats)
    
    # If summary only, exit here
    if args.summary_only:
        return 0
    
    # Determine output file
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = OUTPUT_DIR / "mistakes_with_wikipedia.md"
    
    # Generate report
    success = generate_markdown_report(
        mistakes,
        output_file,
        include_wikipedia=not args.no_wikipedia,
        group_by_category=args.group_by_category
    )
    
    if success:
        print("\n✅ Done! Report generated successfully.")
        print(f"📄 View report: {output_file}")
        if not args.no_wikipedia:
            print("💡 Tip: Use --no-wikipedia for faster generation without links")
        print("💡 Tip: Use --days 7 to see only recent mistakes")
        print("💡 Tip: Use --group-by-category for topic-based organization")
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
