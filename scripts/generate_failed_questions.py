#!/usr/bin/env python3
"""Generate failed questions study guide with flexible ordering and filtering.

Usage:
    uv run scripts/generate_failed_questions.py                    # Default: by date (newest first)
    uv run scripts/generate_failed_questions.py --order date       # By date
    uv run scripts/generate_failed_questions.py --order category   # By category
    uv run scripts/generate_failed_questions.py --order question   # By question number
    uv run scripts/generate_failed_questions.py --filter "October 20"  # Filter by date
    uv run scripts/generate_failed_questions.py --filter "Écrivains"   # Filter by category
    uv run scripts/generate_failed_questions.py --category "Histoire"  # Filter by domain
    uv run scripts/generate_failed_questions.py --show-mistakes    # Include your wrong answers
    uv run scripts/generate_failed_questions.py --output study.md  # Custom output file
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any

ROOT = Path(__file__).resolve().parents[1]

# File paths
MISTAKES_FILE = ROOT / "data" / "results" / "mistakes_history.json"
DEFAULT_OUTPUT = ROOT / "output" / "reports" / "FAILED_QUESTIONS_EXHAUSTIVE.md"


# Category to domain mapping
DOMAIN_MAP = {
    "Arts": ["Écrivains", "Personnages masculins d'opéras", "Peinture", "Actrices", "Shakespeare"],
    "Culture": ["Pâtisseries", "Répliques des Guignols", "Oscars"],
    "Histoire": ["Événements du XIIIe siècle", "Chanceliers", "Exécutions", "Titanic", "Prix Nobel"],
    "Géographie": ["La Haute-Garonne", "Quartiers de villes", "Villes de la côte"],
    "Musique": ["Groupes musicaux", "Célèbres chanteurs"],
    "Sports": ["Joueurs de l'équipe", "Records de sélections", "Champions internationaux"],
    "Sciences": ["Pathologies", "Plantes connues", "Reconnaissance de fleurs", "Rides"],
    "Mythologie": ["Personnages légendaires"]
}

# Learning notes for each category
LEARNING_NOTES = {
    "Pâtisseries et desserts français (1)": "La nonnette est une spécialité de Dijon (Côte-d'Or), un petit gâteau au miel souvent fourré de confiture ou de crème.",
    "Écrivains français du XIXe siècle (2)": "Pierre Loti (1850-1923) est un écrivain et officier de marine français, connu pour ses romans exotiques. 'Pêcheur d'Islande' (1886) et 'Ramuntcho' (1897) sont deux de ses œuvres majeures.",
    "Personnages masculins d'opéras": "Mario Cavaradossi est le personnage principal masculin de l'opéra 'Tosca' de Giacomo Puccini (1900). C'est un peintre romain, amant de la chanteuse Floria Tosca.",
    "Événements du XIIIe siècle": "Louis IX (Saint Louis) est mort le 25 août 1270 à Tunis lors de la huitième croisade. Il a été canonisé en 1297.",
    "Groupes musicaux anglo-saxons des années 70-80 (3)": "The B-52's est un groupe de new wave américain formé en 1976 à Athens, Géorgie. 'Rock Lobster' (1978), 'Planet Claire' (1979) et 'Love Shack' (1989) sont leurs titres les plus célèbres.",
    "Pathologies et lésions de la peau (2)": "Le purpura est une lésion cutanée caractérisée par des taches rouges ou violacées causées par une extravasation de sang.",
    "La Haute-Garonne en 13 questions": "La Haute-Garonne (31) a pour chef-lieu Toulouse, où se trouvent la Place du Capitole et la basilique Saint-Sernin. Peyragudes est une station de ski de la Haute-Garonne.",
    "Joueurs de l'équipe allemande de football (2)": "Mesut Özil est un footballeur allemand d'origine turque, né en 1988. Champion du monde 2014, il a joué pour Werder Brême, le Real Madrid, Arsenal et Fenerbahçe.",
    "Répliques des Guignols de l'info (2)": "'On m'aurait menti ?' est la réplique culte de la marionnette de Richard Virenque dans Les Guignols de l'info, en référence à l'affaire Festina et au dopage dans le cyclisme.",
    "Peinture française à la Kunsthalle de Hambourg": "Rosa Bonheur (1822-1899) était une peintre et sculptrice française, spécialisée dans les représentations animalières. Elle est l'une des artistes féminines les plus célèbres du XIXe siècle.",
    "Chanceliers de l'Allemagne fédérale": "Friedrich Merz est un homme politique allemand, président de la CDU depuis 2022.",
    "Reconnaissance de fleurs (1)": "L'aconit (Aconitum) est une plante herbacée vivace très toxique de la famille des Renonculacées, caractérisée par ses fleurs en forme de casque.",
    "Célèbres chanteurs de groupes rock (2)": "David Lee Roth était le chanteur principal de Van Halen de 1974 à 1985, puis de 1996 à aujourd'hui. Il est connu pour son style énergique et son showmanship.",
    "Personnages légendaires du cycle thébain": "Dans la mythologie grecque, Harmonie est la fille d'Arès et d'Aphrodite. Elle épousa Cadmos, fondateur de Thèbes. Le collier maudit qu'elle reçut causa de nombreux malheurs.",
    "Villes de la côte est des États-Unis (hors Floride)": "New Haven est une ville du Connecticut, célèbre pour abriter l'Université Yale (fondée en 1701), l'une des universités les plus prestigieuses des États-Unis.",
    "Œuvres de Shakespeare": "'La Mégère apprivoisée' (The Taming of the Shrew) est une comédie de Shakespeare écrite vers 1594. Catharina est la 'mégère' que Petruchio tente d'apprivoiser.",
    "Records de sélections en équipe de France": "Fabien Pelous détient le record de sélections en équipe de France de rugby à XV avec 118 sélections entre 1995 et 2007.",
    "Rides au nom imagé": "Les 'rides du lapin' (bunny lines en anglais) sont de fines rides qui apparaissent sur les côtés du nez quand on fronce le nez, rappelant le mouvement d'un lapin.",
    "Actrices belges": "Émilie Dequenne est une actrice belge née en 1981. Elle s'est révélée dans 'Rosetta' des frères Dardenne (Palme d'or 1999).",
    "Champions internationaux des différentes disciplines de l'athlétisme (2)": "Jan Železný (République tchèque) est considéré comme le plus grand lanceur de javelot de l'histoire avec un record du monde de 98,48 m (1996).",
    "Quartiers de villes françaises": "Cimiez est un quartier historique de Nice situé sur une colline, connu pour ses arènes romaines et le musée Matisse.",
    "Plantes connues sous plusieurs noms (1)": "Le colchique (Colchicum autumnale) est une plante toxique qui fleurit en automne. Ses surnoms 'tue-chien' et 'safran bâtard' font référence à sa toxicité.",
    "Exécutions en place de Grève": "Georges Cadoudal (1771-1804) était un chef chouan breton. Il fut exécuté place de Grève le 25 juin 1804 pour avoir participé à un complot contre Napoléon Bonaparte.",
    "Le Titanic en 10 questions": "Le Titanic a quitté Southampton (Angleterre) le 10 avril 1912 pour son voyage inaugural vers New York. Il a coulé le 15 avril 1912.",
    "Prix Nobel de physiologie ou de médecine (1)": "Robert Koch (1843-1910) était un médecin et microbiologiste allemand. Il a reçu le prix Nobel de médecine en 1905 pour ses recherches sur la tuberculose.",
    "Oscars de la meilleure chanson originale (2)": "'Streets of Philadelphia' a été écrite et interprétée par Bruce Springsteen pour le film 'Philadelphia' (1993). La chanson a remporté l'Oscar en 1994."
}


def load_mistakes() -> List[Dict[str, Any]]:
    """Load mistakes from JSON file."""
    if not MISTAKES_FILE.exists():
        print(f"❌ No {MISTAKES_FILE} file found!")
        return []
    
    with open(MISTAKES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def filter_mistakes(mistakes: List[Dict], filter_text: str = None, domain: str = None) -> List[Dict]:
    """Filter mistakes by text or domain."""
    if not filter_text and not domain:
        return mistakes
    
    filtered = []
    for mistake in mistakes:
        # Filter by text (in date or category)
        if filter_text:
            if filter_text.lower() in mistake['date'].lower() or \
               filter_text.lower() in mistake['category'].lower():
                filtered.append(mistake)
                continue
        
        # Filter by domain
        if domain:
            category = mistake['category']
            for domain_name, keywords in DOMAIN_MAP.items():
                if domain.lower() in domain_name.lower():
                    if any(keyword.lower() in category.lower() for keyword in keywords):
                        filtered.append(mistake)
                        break
    
    return filtered if filtered else mistakes


def sort_mistakes(mistakes: List[Dict], order: str) -> List[Dict]:
    """Sort mistakes by specified order."""
    if order == 'date':
        return sorted(mistakes, key=lambda x: (x['date'], x['question_number']), reverse=True)
    elif order == 'category':
        return sorted(mistakes, key=lambda x: (x['category'], x['date'], x['question_number']))
    elif order == 'question':
        return sorted(mistakes, key=lambda x: (x['date'], x['question_number']))
    else:
        return mistakes


def format_question(mistake: Dict, show_mistakes: bool, show_choices: bool, question_num: int) -> str:
    """Format a single question."""
    output = f"### Question {question_num} - {mistake['category']}\n\n"
    output += f"**📅 Date:** {mistake['date']}\n\n"
    output += f"**❓ Question:** {mistake['question']}\n\n"
    
    if mistake.get('hints'):
        output += f"**💡 Hint:** {', '.join(mistake['hints'])}\n\n"
    
    if show_mistakes:
        output += f"**❌ Your Answer:** {mistake['your_answer']}\n\n"
    
    output += f"**✅ Correct Answer:** {mistake['correct_answer']}\n\n"
    
    if show_choices and mistake.get('all_choices'):
        output += "**📋 All Choices:**\n"
        for choice in mistake['all_choices']:
            if choice == mistake['correct_answer']:
                marker = "✓"
            elif show_mistakes and choice == mistake['your_answer']:
                marker = "✗"
            else:
                marker = "•"
            output += f"- {marker} {choice}\n"
        output += "\n"
    
    if mistake['category'] in LEARNING_NOTES:
        output += f"**📝 Note:** {LEARNING_NOTES[mistake['category']]}\n\n"
    
    output += "---\n\n"
    
    return output


def generate_by_date(mistakes: List[Dict], show_mistakes: bool, show_choices: bool) -> str:
    """Generate output grouped by date."""
    output = ""
    
    by_date = defaultdict(list)
    for mistake in mistakes:
        by_date[mistake['date']].append(mistake)
    
    for date in sorted(by_date.keys(), reverse=True):
        dt = datetime.strptime(date, '%Y-%m-%d')
        formatted_date = dt.strftime('%B %d, %Y')
        questions = by_date[date]
        
        output += f"## {formatted_date} ({len(questions)} questions)\n\n"
        
        for i, q in enumerate(questions, 1):
            output += format_question(q, show_mistakes, show_choices, q['question_number'])
    
    return output


def generate_by_category(mistakes: List[Dict], show_mistakes: bool, show_choices: bool) -> str:
    """Generate output grouped by category."""
    output = ""
    
    by_category = defaultdict(list)
    for mistake in mistakes:
        by_category[mistake['category']].append(mistake)
    
    for category in sorted(by_category.keys()):
        questions = by_category[category]
        output += f"## {category} ({len(questions)} question{'s' if len(questions) > 1 else ''})\n\n"
        
        for i, q in enumerate(questions, 1):
            output += format_question(q, show_mistakes, show_choices, i)
    
    return output


def generate_sequential(mistakes: List[Dict], show_mistakes: bool, show_choices: bool) -> str:
    """Generate output as sequential list."""
    output = ""
    
    for i, mistake in enumerate(mistakes, 1):
        output += format_question(mistake, show_mistakes, show_choices, i)
    
    return output


def generate_toc(mistakes: List[Dict], order: str) -> str:
    """Generate table of contents."""
    toc = "## Table of Contents\n\n"
    
    if order == 'date':
        by_date = defaultdict(int)
        for mistake in mistakes:
            by_date[mistake['date']] += 1
        
        for date in sorted(by_date.keys(), reverse=True):
            dt = datetime.strptime(date, '%Y-%m-%d')
            formatted_date = dt.strftime('%B %d, %Y')
            anchor = formatted_date.lower().replace(' ', '-').replace(',', '')
            toc += f"- [{formatted_date} ({by_date[date]} questions)](#-{anchor})\n"
    
    elif order == 'category':
        by_category = defaultdict(int)
        for mistake in mistakes:
            by_category[mistake['category']] += 1
        
        for category in sorted(by_category.keys()):
            anchor = category.lower().replace(' ', '-').replace('(', '').replace(')', '').replace('é', 'e').replace('à', 'a').replace('è', 'e')
            toc += f"- [{category} ({by_category[category]} question{'s' if by_category[category] > 1 else ''})](#-{anchor})\n"
    
    toc += "\n---\n\n"
    return toc


def generate_stats(mistakes: List[Dict]) -> str:
    """Generate statistics section."""
    stats = "## 📊 Statistics\n\n"
    
    # By date
    by_date = defaultdict(int)
    for mistake in mistakes:
        by_date[mistake['date']] += 1
    
    stats += "**By Date:**\n"
    for date in sorted(by_date.keys(), reverse=True):
        dt = datetime.strptime(date, '%Y-%m-%d')
        formatted_date = dt.strftime('%B %d, %Y')
        stats += f"- {formatted_date}: {by_date[date]} questions\n"
    
    # By category
    by_category = defaultdict(int)
    for mistake in mistakes:
        by_category[mistake['category']] += 1
    
    stats += "\n**By Category:**\n"
    for category in sorted(by_category.keys()):
        stats += f"- {category}: {by_category[category]} question{'s' if by_category[category] > 1 else ''}\n"
    
    stats += "\n---\n\n"
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Generate failed questions study guide with flexible ordering",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default: by date (newest first), correct answers only
  uv run scripts/generate_failed_questions.py
  
  # Order by category
  uv run scripts/generate_failed_questions.py --order category
  
  # Show all multiple choice options
  uv run scripts/generate_failed_questions.py --show-choices
  
  # Filter by date
  uv run scripts/generate_failed_questions.py --filter "October 20"
  
  # Filter by category keyword
  uv run scripts/generate_failed_questions.py --filter "Écrivains"
  
  # Filter by domain
  uv run scripts/generate_failed_questions.py --domain Histoire
  
  # Show your wrong answers
  uv run scripts/generate_failed_questions.py --show-mistakes
  
  # Complete view: mistakes + all choices
  uv run scripts/generate_failed_questions.py --show-mistakes --show-choices
  
  # Combine options
  uv run scripts/generate_failed_questions.py --order category --domain Arts --show-choices
  
  # Custom output file
  uv run scripts/generate_failed_questions.py --output my_study_guide.md
        """
    )
    
    parser.add_argument(
        '--order',
        choices=['date', 'category', 'question'],
        default='date',
        help='Order of questions (default: date)'
    )
    
    parser.add_argument(
        '--filter',
        type=str,
        help='Filter by text (in date or category)'
    )
    
    parser.add_argument(
        '--domain',
        type=str,
        choices=['Arts', 'Culture', 'Histoire', 'Géographie', 'Musique', 'Sports', 'Sciences', 'Mythologie'],
        help='Filter by domain'
    )
    
    parser.add_argument(
        '--show-mistakes',
        action='store_true',
        help='Include your wrong answers in the output'
    )
    
    parser.add_argument(
        '--show-choices',
        action='store_true',
        help='Include all multiple choice options (default: only show correct answer)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='FAILED_QUESTIONS_EXHAUSTIVE.md',
        help='Output file name (default: FAILED_QUESTIONS_EXHAUSTIVE.md)'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Include statistics section'
    )
    
    args = parser.parse_args()
    
    # Load mistakes
    print("📂 Loading mistakes history...")
    mistakes = load_mistakes()
    
    if not mistakes:
        return 1
    
    print(f"✅ Loaded {len(mistakes)} questions")
    
    # Filter
    if args.filter or args.domain:
        mistakes = filter_mistakes(mistakes, args.filter, args.domain)
        print(f"🔍 Filtered to {len(mistakes)} questions")
    
    # Sort
    mistakes = sort_mistakes(mistakes, args.order)
    print(f"📋 Ordered by: {args.order}")
    
    # Generate header
    title = "Failed Questions"
    if args.filter:
        title += f" - Filtered by '{args.filter}'"
    if args.domain:
        title += f" - Domain: {args.domain}"
    
    if args.show_mistakes:
        title += " (with mistakes shown)"
    else:
        title += " - Study Guide"
    
    output = f"# 📚 {title}\n\n"
    output += f"**Total Questions:** {len(mistakes)}  \n"
    output += f"**Ordered By:** {args.order.title()}  \n"
    
    if args.filter:
        output += f"**Filter:** {args.filter}  \n"
    if args.domain:
        output += f"**Domain:** {args.domain}  \n"
    
    output += f"**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M')}\n\n"
    output += "---\n\n"
    
    # Generate TOC
    output += generate_toc(mistakes, args.order)
    
    # Generate stats if requested
    if args.stats:
        output += generate_stats(mistakes)
    
    # Generate content
    print("📝 Generating content...")
    if args.order == 'date':
        output += generate_by_date(mistakes, args.show_mistakes, args.show_choices)
    elif args.order == 'category':
        output += generate_by_category(mistakes, args.show_mistakes, args.show_choices)
    else:
        output += generate_sequential(mistakes, args.show_mistakes, args.show_choices)
    
    # Write to file
    output_file = Path(args.output) if args.output else DEFAULT_OUTPUT
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(output, encoding='utf-8')
    
    print(f"✅ Generated: {output_file}")
    print(f"📊 Total lines: {len(output.splitlines())}")
    print(f"💾 File size: {len(output)} bytes")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
