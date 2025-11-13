"""Minimal daily quiz report script (cleaned version).

Features kept:
 - Fetch & cache archive JSON for a date (default: yesterday)
 - Show local quiz mapping + local leaderboard
 - Distribution stats
 - Selected players table (emojis + dual FR/EN Gen‑Z banter)

Removed: weekly aggregation, legacy exploratory code, language toggle.

Usage examples:
  uv run scripts/daily_report.py                # yesterday
  uv run scripts/daily_report.py 2025-10-14
  uv run scripts/daily_report.py 2025-10-14 --no-cache --refresh
  uv run scripts/daily_report.py --fun          # emojis + genz (default if no flags)
"""

from __future__ import annotations

import sys
import json
import re
import random
import statistics
import argparse
from pathlib import Path
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING
import signal

if TYPE_CHECKING:  # pragma: no cover - for linters / IDEs only
    pass

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------- Configuration ---------------- #
DB_PATH = ROOT / "data" / "db" / "quizypedia.db"
CACHE_DIR = ROOT / "data" / "cache" / "archive"
FIGURES_DIR = ROOT / "data" / "figures"
PLAYERS_CONFIG_PATH = ROOT / "data" / "players.json"
RATE_LIMIT_SECONDS = 0.2
QUIZ_TOTAL_FALLBACK = 20

# Load player configuration from JSON file
def load_players_config() -> Tuple[List[str], Dict[str, str]]:
    """Load selected players and real name mapping from players.json.
    
    Returns:
        Tuple of (selected_players_list, real_name_map_dict)
    """
    try:
        with open(PLAYERS_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        selected = config.get('selected', [])
        real_names = config.get('real_names', {})
        return selected, real_names
    except FileNotFoundError:
        eprint(f"[WARNING] Players config file not found: {PLAYERS_CONFIG_PATH}")
        eprint("[WARNING] Using empty player lists")
        return [], {}
    except json.JSONDecodeError as e:
        eprint(f"[WARNING] Invalid JSON in players config: {e}")
        eprint("[WARNING] Using empty player lists")
        return [], {}

SELECTED_PLAYERS, REAL_NAME_MAP = load_players_config()

# Quiz categories for radar chart
QUIZ_CATEGORIES = [
    "Culture classique",
    "Culture moderne", 
    "Culture générale",
    "Géographie",
    "Histoire",
    "Animaux et plantes",
    "Sciences et techniques",
    "Sport"
]

EMOJIS_ENABLED = False
GENZ_ENABLED = False
GENZ_EN_ENABLED = False  # English Gen-Z disabled by default
LANG = 'fr'  # kept for backwards compatibility but no toggle now
KIND_ENABLED = False  # Option to show only kind comments in genz_fr


def eprint(*a, **k):
    print(*a, file=sys.stderr, **k)


def log(msg: str):
    """Standard stdout log helper with simple timestamp."""
    now = datetime.now(UTC).strftime('%H:%M:%S')
    print(f"[{now}] {msg}")


def validate_date(date_str: str) -> str:
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise SystemExit(f"Invalid date '{date_str}'. Expected YYYY-MM-DD.")
    return date_str


def bracket_scan_payload(html: str) -> Optional[str]:
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


def parse_results(raw_payload: str) -> List[Dict[str, Any]]:
    cleaned = raw_payload.strip()
    if cleaned.endswith(';'):
        cleaned = cleaned[:-1]
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        cleaned2 = re.sub(r"//.*?\n", "\n", cleaned)
        return json.loads(cleaned2)


def mmss(seconds: Optional[int]) -> str:
    if seconds is None:
        return ''
    try:
        seconds = int(seconds)
    except Exception:
        return ''
    if seconds >= 60:
        return f"{seconds//60}:{seconds%60:02d}"
    return f"0:{seconds:02d}"


def generate_genz_daily(pct: Optional[float], rank_val: Optional[int], et_val: Optional[int]) -> tuple[str,str]:
    pools_en = {
        'perfect_speed': ['SLAY ⚡','SPEED DEMON ⚡','FRAME PERFECT ⚡','GLITCHING ⚡'],
        'perfect': ['NO CAP 🌟','FLAWLESS 🌟','LOCKED IN 🔐','CLUTCH 🌟'],
        't95': ['GOATED 🔥','HEATING UP 🔥','BUILT DIFFERENT 🔥','DIFF CLASS 💯'],
        't80': ['BIG VIBES 😎','VALID 😎','COOKING 👨‍🍳','STILL COOKING 🍳'],
        't60': ['MID FR 🫠','ALMOST THERE 🤏','KEEP GRINDING 🛠️','HOLD THE LINE 🧱'],
        'low': ['RIP 💀','FUMBLED 💀','DOWN BAD 💀','DUSTED 💀'],
        'low_rank': ['NPC ENERGY 💤','BACKGROUND NPC 💤','LOWKEY AF 💤','WHERE U AT? 👀'],
    }
    pools_fr = {
        'perfect_speed': [
            'PERF ÉCLAIR ⚡','PARFAIT SPEED ⚡','IMBATTABLE ⚡','ULTRA RAPIDE ⚡','SONIC VIBE ⚡','TURBO MODE ⚡','FLASH MCQUEEN ⚡','VITESSE LUMIÈRE ⚡',
            'HYPERDRIVE ⚡','MODE FUSÉE 🚀','FULL SPEED 🚀','WARP DRIVE ⚡','INSTANTANÉ ⚡','ZERO LATENCE ⚡','PIXEL PERFECT ⚡','SPAM CLICK ⚡',
            'SPEEDRUNNER 🏃‍♂️','SPLIT PARFAIT 🧭','RÉFLEXES OP 🧠','MÉTÉORE ⚡','TRACE DE LUMIÈRE ✨','TEMPS CRAQUÉ 🕒'
        ],
        'perfect': [
            'SANS FAUTE 🌟','PARFAIT 🌟','FULL LOCK 🔐','CLUTCH 🌟','20/20 🌟','IMPECCABLE 🌟','MASTERCLASS 🌟','LÉGENDE 🌟','100% VALIDÉ ✅',
            'BROKEN 💥','TIER S+ 💥','CHEAT CODE 💻','NO MISS 🎯','ULTIME 🌟','FLAWLESS RUN 🧊','ABSOLU 🌟','GOD MODE 👑','TROP PROPRE 🧼',
            'SCRIPTÉ 🤖','FRAME CLEAN 🪞','AUCUNE ERREUR ❌','TRANQUILLE IMPERIAL 👑','AU-DESSUS DU LOT ⛰️'
        ],
        't95': [
            'EN FEU 🔥','TROP FORT 🔥','ÇA CHAUFFE 🔥','GOAT 🔥','MEGA CHAUD 🔥','ÉNORME 🔥','MONSTRUEUX 💪','GÉANT 🔥','T\'ES CHAUD 🔥',
            'LAVE ACTIVE 🌋','PAS LOIN DU PARFAIT 🎯','SURDUIT 🔥','TU PILES 🚀','MÉCHANT NIVEAU 😈','SURVOLTÉ ⚡','BANGER 🔥','TROP SOLIDE 🧱',
            'LIMIT BREAK 💥','PRÈS DU PALAIS 👑','TU RÈGLES ÇA 🔧','ULTRA CLEAN 🧊'
        ],
        't80': [
            'SOLIDE 😎','VALIDÉ 😎','ÇA CUIT 👨‍🍳','ON CUISINE 🍳','BG 😎','STYLÉ 😎','TRANQUILLE 😎','BIEN JOUÉ 👍','PROPRE 😎','ÇA PASSE 👌',
            'TU PROGRESSES 📈','BON GRIND 🛠️','STABLE 🧱','RAS 👍','CARRÉ 🟥','FAIT LE JOB 🧾','OPTIMISÉ ⚙️','TU GARDES LE RYTHME 🥁','PAS MAL 😏',
            'TU TIENS LA ROUTE 🚗','ÇA TOURNE 🔁','LA FORME ✅','C’EST CLEAN 🧼'
        ],
        't60': [
            'MOYEN 😬','EN PROGRESSION 🤏','CONTINUE 🛠️','NE LÂCHE RIEN 💪','PEUT MIEUX FAIRE 📈','BIENTÔT LÀ 🤏','ON Y CROIT 🙏','PRESQUE 🤷','ALLEZ 💪','REVIENS PLUS FORT 💯',
            'TU GRIND 🪓','PAS FINI 🔄','EN CONSTRUCTION 🏗️','ROUTE LONGUE 🛣️','CHAUFFE MOTEUR 🚗','BUILD EN COURS 🧱','EN RÉGLAGE 🔧','APPROCHE 🛰️','EN CHANTIER 🚧',
            'PAS FOU MAIS ÇA VIENT 🤞','EN CHARGE 🔋','MODE TRAINING 🏋️'
        ],
        'low': [
            'RIP 💀','AÏE 💀','DOWN BAD 💀','FLOP 💀','RATÉ 💀','GAME OVER 💀','OUPS 💀','PAS OUF 💀','AÏEAÏEAÏE 😬','YIKES 😬',
            'RECALÉ ❌','COFFRE VIDE 📦','SANS DÉGÂTS 🩹','GLISSADE 🛷','TU TOMBES 🕳️','FLOP SECO 💀','MAL CHAUD 🌧️','TOUT SEC 🏜️','FREEZE 🧊',
            'SOUS-EAU 🌊','ÇA RAM 🔄','MAL ALIGNÉ 📐','FRAPPE FANTÔME 👻'
        ],
        'low_rank': [
            'PNJ 💤','FIGURANT 💤','ON TE VOIT PAS 👀','BACKGROUND 💤','FANTÔME 👻','INVISIBLE 👻','T\'ES OÙ? 👀','ABSENT 💤','EN ROUE LIBRE 🛞','PERDU 🗺️',
            'MODE OBSERVER 👀','SPECTATE ONLY 🎥','AFK 💤','ALT+TAB 🖥️','SHADOW MODE 🌑','SILENCIEUX 🤫','LATENT 🕰️','HORS CHAMP 🎬',
            'COUCHE BETA 🧪','CAMOUFLÉ 🥷','EN PAUSE ⏸️'
        ],
    }
    en = fr = ''
    if isinstance(pct, (int, float)):
        # Adjusted thresholds (-15 percentage points) to make higher tier messages easier to obtain.
        # Original: perfect_speed (100 + fast), perfect (100), t95, t80, t60, else low
        # New cutoffs: t95 -> >=80, t80 -> >=65, t60 -> >=45
        if pct == 100 and et_val is not None and et_val <= 30:
            en = random.choice(pools_en['perfect_speed'])
            fr = random.choice(pools_fr['perfect_speed'])
        elif pct == 100:
            en = random.choice(pools_en['perfect'])
            fr = random.choice(pools_fr['perfect'])
        elif pct >= 80:  # was 95
            en = random.choice(pools_en['t95'])
            fr = random.choice(pools_fr['t95'])
        elif pct >= 65:  # was 80
            en = random.choice(pools_en['t80'])
            fr = random.choice(pools_fr['t80'])
        elif pct >= 45:  # was 60
            en = random.choice(pools_en['t60'])
            fr = random.choice(pools_fr['t60'])
        else:
            en = random.choice(pools_en['low'])
            fr = random.choice(pools_fr['low'])
    if rank_val and rank_val > 50 and (not en or 'RIP' in en or 'DOWN BAD' in en):
        en = random.choice(pools_en['low_rank'])
    if rank_val and rank_val > 50 and (not fr or 'RIP' in fr or 'DOWN BAD' in fr):
        fr = random.choice(pools_fr['low_rank'])
    return fr, en


LAST_SELECTED_ROWS: List[Dict[str, Any]] = []  # populated after selected players built

def print_selected_players(results: List[Dict[str, Any]]):
    global LAST_SELECTED_ROWS
    wanted = {p.lower(): p for p in SELECTED_PLAYERS}
    rows: List[Dict[str, Any]] = []
    for obj in results:
        uname = obj.get('user') or obj.get('player') or ''
        if uname.lower() in wanted:
            rows.append({
                'player': uname,
                'rank': obj.get('rank'),
                'good_responses': obj.get('good_responses'),
                'total': QUIZ_TOTAL_FALLBACK,
                'elapsed_time': obj.get('elapsed_time'),
                'real_name': REAL_NAME_MAP.get(uname.lower()),
            })
    if not rows:
        print("\nJoueurs sélectionnés : aucun trouvé dans l'archive.")
        LAST_SELECTED_ROWS = []
        return

    # Compute derived metrics
    for r in rows:
        gr = r['good_responses']
        tot = r['total']
        pct = (gr / tot * 100) if isinstance(gr, int) and tot else None
        r['pct'] = round(pct, 1) if isinstance(pct, float) else None
        r['elapsed_fmt'] = mmss(r.get('elapsed_time'))
    # Determine local leaderboard ordering (score desc, time asc, fallback by global rank asc)
    def local_key(r: Dict[str, Any]):
        score = r.get('good_responses')
        # negative score for descending, None -> very low
        score_key = -(score if isinstance(score, int) else -1)
        t = r.get('elapsed_time')
        time_key = t if isinstance(t, int) else 10**9
        global_rank = r.get('rank') if isinstance(r.get('rank'), int) else 10**9
        return (score_key, time_key, global_rank)

    local_sorted = sorted(rows, key=local_key)
    # Assign medals to local top 3
    for idx, r in enumerate(local_sorted):
        if idx == 0:
            r['local_medal'] = '🥇'
        elif idx == 1:
            r['local_medal'] = '🥈'
        elif idx == 2:
            r['local_medal'] = '🥉'
        else:
            r['local_medal'] = ''
    # Now compute badges (using local medal) & gen-z
    for r in rows:
        perf = ''
        speed = ''
        if EMOJIS_ENABLED:
            if isinstance(r['pct'], (int, float)):
                if r['pct'] == 100:
                    perf = '🌟'
                elif r['pct'] >= 95:
                    perf = '🔥'
                elif r['pct'] >= 80:
                    perf = '👍'
                elif r['pct'] >= 60:
                    perf = '🙂'
                else:
                    perf = '😢'
            et = r.get('elapsed_time')
            if isinstance(et, int):
                if et <= 30:
                    speed = '⚡'
                elif et <= 60:
                    speed = '⏱️'
        # OLD:
        # r['badges'] = r.get('local_medal', '') + perf + speed
        # NEW: if a medal is present, show ONLY the medal (no extra emojis)
        if r.get('local_medal'):
            r['badges'] = r['local_medal']
        else:
            r['badges'] = (perf + speed) if EMOJIS_ENABLED else ''
        if GENZ_ENABLED:
            fr_phrase, en_phrase = generate_genz_daily(r.get('pct'), r.get('rank'), r.get('elapsed_time'))
            if KIND_ENABLED:
                # Replace genz_fr with only kind comments
                kind_comments = [
                    "Bravo ! 🌟", "Super effort ! 💪", "Bien joué ! 👏", "Tu progresses ! 📈", "Continue comme ça ! ✨",
                    "Excellente participation ! 🎯", "Tu t'améliores ! 🚀", "Félicitations ! 🎉", "Belle performance ! 💎",
                    "Courage ! 💙", "On croit en toi ! 🌈", "Tu assures ! 🔥", "Top ! ⭐", "Respect ! 🙌", "Chapeau ! 🎩",
                    "C'est vraiment bien ! 😊", "Tu donnes le meilleur ! 💯", "Magnifique ! ✨", "Incroyable effort ! 🌠",
                    "Tu es sur la bonne voie ! 🛤️", "Fantastique ! 🎊", "Impressionnant ! 💫", "Tu te surpasses ! 🏆",
                    "Quelle détermination ! 💪", "Tu es un champion ! 🥇", "Merveilleux ! 🌺", "Superbe travail ! 🎨"
                ]
                fr_phrase = random.choice(kind_comments)
            r['genz_fr'] = fr_phrase
            r['genz_en'] = en_phrase
        else:
            r['genz_fr'] = ''
            r['genz_en'] = ''
    # Display order: local leaderboard (so medals match ordering)
    rows = local_sorted
    
    try:
        from rich.console import Console
        from rich.table import Table
        from rich import box
        console=Console()
        title=f"Joueurs sélectionnés ({len(rows)})"
        table=Table(title=title, box=box.MINIMAL_DOUBLE_HEAD, header_style='bold cyan')
        base=[["rang","bold yellow","right"],["joueur","white","left"],["nom","cyan","left"],["score","green","right"],["total","green","right"],["pct%","magenta","right"],["temps","blue","right"],["badges","bold","left"]]
        if GENZ_ENABLED:
            kind_title = 'encouragements' if KIND_ENABLED else 'gen-z fr'
            base.append((kind_title,'italic magenta','left'))
            if GENZ_EN_ENABLED:
                base.append(('gen-z en','italic magenta','left'))
        for c, s, j in base:
            table.add_column(c, style=s, justify=j)
        for r in rows:
            vals=[str(r.get('rank','')), r.get('player',''), r.get('real_name') or '', str(r.get('good_responses','')), str(r.get('total','')), (f"{r['pct']:.1f}%" if isinstance(r.get('pct'),(int,float)) else ''), r.get('elapsed_fmt',''), r.get('badges','')]
            if GENZ_ENABLED:
                vals.append(r.get('genz_fr', ''))
                if GENZ_EN_ENABLED:
                    vals.append(r.get('genz_en', ''))
            table.add_row(*vals)
        console.print(table)
    except Exception:
        print("\nJoueurs sélectionnés:")
        header=f"{'RANG':>4} {'JOUEUR':<15} {'NOM':<12} {'SCORE':>7} {'%':>6} {'TEMPS':>6} {'BADGES':<8}"
        if GENZ_ENABLED:
            kind_header = " ENCOURAGEMENTS" if KIND_ENABLED else " GENZ_FR"
            header += kind_header
            if GENZ_EN_ENABLED:
                header += " GENZ_EN"
        print(header)
        print('-'*len(header))
        for r in rows:
            pctd=(f"{r['pct']:.1f}%" if isinstance(r.get('pct'),(int,float)) else '')
            line=f"{str(r.get('rank','')):>4} {r.get('player',''):<15} {(r.get('real_name') or ''):<12} {str(r.get('good_responses','')):>7} {pctd:>6} {r.get('elapsed_fmt',''):>6} {r.get('badges',''):<8}"
            if GENZ_ENABLED:
                line += f" {r.get('genz_fr','')}"
                if GENZ_EN_ENABLED:
                    line += f" {r.get('genz_en','')}"
            print(line)

    LAST_SELECTED_ROWS = rows  # store final (ordered) rows for saving/interrupt use


def summarize_distribution(results: List[Dict[str, Any]]):
    scores=[r.get('good_responses') for r in results if isinstance(r.get('good_responses'),int)]
    durations=[r.get('elapsed_time') for r in results if isinstance(r.get('elapsed_time'),int)]
    if scores:
        print(f"Scores : n={len(scores)} min={min(scores)} max={max(scores)} moyenne={statistics.mean(scores):.2f}")
    else:
        print("Scores : aucune entrée numérique")
    if durations:
        print(f"Durées : n={len(durations)} min={min(durations)} max={max(durations)} médiane={statistics.median(durations)}")
    else:
        print("Durées : aucune entrée numérique")


def show_local_leaderboard(db, date_str: str):
    quiz_id=db.get_daily_quiz(date_str)
    if quiz_id is None:
        print(f"Aucun quiz quotidien associé localement pour {date_str}.")
        return None
    quiz=db.get_quiz(quiz_id)
    if quiz:
        print(f"Date {date_str} -> quiz_id={quiz_id}: {quiz['title']}")
        print(f"Tags: {', '.join(quiz['tags'])}")
        print(f"Questions: {len(quiz['questions'])}")
    table=db.daily_table(date_str)
    if not table:
        print("Aucune tentative locale enregistrée pour cette date.")
    else:
        print("\nClassement local dérivé:")
        print(f"{'#':>3} {'JOUEUR':<15} {'MEIL':>5} {'TOT':>3} {'ESS':>3} {'TEMPS':>6} {'EXT':>4}")
        print('-'*50)
        for rank,row in enumerate(table,start=1):
            player,best_score,total,attempts,best_duration,external_rank=row
            dur_disp='' if best_duration in (None,999999) else mmss(best_duration)
            print(f"{rank:>3} {player:<15} {best_score:>5} {total:>3} {attempts:>3} {dur_disp:>6} {str(external_rank or ''):>4}")
    return quiz_id


def cache_path_for(date_str: str) -> Path: return CACHE_DIR / f"{date_str}.json"


def fetch_daily_results(scraper, date_str: str, *, use_cache: bool=True, refresh: bool=False) -> Optional[Tuple[List[Dict[str,Any]], bool]]:
    """Return (results, from_cache). Adds detailed logging for cache/network lifecycle."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cp = cache_path_for(date_str)

    def _fmt_age(secs: float) -> str:
        if secs < 60:
            return f"{int(secs)}s"
        minutes = secs / 60
        if minutes < 60:
            return f"{minutes:.1f}m"
        hours = minutes / 60
        if hours < 24:
            return f"{hours:.1f}h"
        days = hours / 24
        return f"{days:.1f}d"

    # Attempt cache read
    if use_cache and not refresh:
        if cp.is_file():
            log(f"[CACHE] Lecture du fichier: {cp}")
            try:
                raw = cp.read_text(encoding='utf-8')
                data = json.loads(raw)
                if isinstance(data, dict) and isinstance(data.get('results'), list):
                    fetched_at = data.get('fetched_at')
                    age_txt = "âge inconnu"
                    if fetched_at:
                        try:
                            ts = datetime.fromisoformat(fetched_at.rstrip('Z'))
                            age = (datetime.now(UTC) - ts).total_seconds()
                            age_txt = _fmt_age(age)
                        except Exception:
                            pass
                    log(f"[CACHE] Succès (entries={len(data['results'])}, âge={age_txt})")
                    return data['results'], True
                else:
                    log("[CACHE] Structure inattendue, ignorée.")
            except Exception as e:
                log(f"[CACHE] Lecture/parse échouée ({e}); on passe au réseau.")
        else:
            log(f"[CACHE] Aucun cache pour {date_str} ({cp.name})")

    if refresh:
        log(f"[CACHE] --refresh demandé: on ignore le cache existant pour {date_str}")

    # Network fetch
    y, m, d = map(int, date_str.split('-'))
    log("[FETCH] Téléchargement de la page d'archive distante…")
    try:
        html = scraper.get_daily_archive_html(y, m, d)
        log(f"[FETCH] Réception OK (taille HTML={len(html)} octets)")
    except Exception as e:
        eprint(f"[FETCH] Échec téléchargement: {e}")
        return None

    # Payload extraction
    log("[PARSE] Recherche du tableau JSON embarqué…")
    raw = bracket_scan_payload(html)
    if not raw:
        eprint("[PARSE] Aucune payload détectée.")
        return None
    log(f"[PARSE] Segment brut détecté (longueur={len(raw)} caractères)")

    # JSON parse
    try:
        results = parse_results(raw)
        log(f"[PARSE] Décodage JSON OK ({len(results)} enregistrements)")
    except Exception as e:
        eprint(f"[PARSE] Échec décodage JSON: {e}")
        return None

    # Cache write
    if use_cache:
        if refresh:
            log("[SAVE] Écriture (rafraîchissement forcé)…")
        else:
            log("[SAVE] Écriture du cache (nouvelle entrée)…")
        try:
            cp.write_text(
                json.dumps(
                    {
                        'date': date_str,
                        'fetched_at': datetime.now(UTC).isoformat(),
                        'count': len(results),
                        'results': results
                    },
                    ensure_ascii=False,
                    indent=2
                ),
                encoding='utf-8'
            )
            log(f"[SAVE] OK -> {cp}")
        except Exception as e:
            eprint(f"[SAVE] Échec écriture cache: {e}")

    return results, False


def create_category_difficulty_radar(date_str: str, quiz_html_path: Optional[Path] = None,
                                     output_path: Optional[Path] = None, show: bool = False) -> bool:
    """Create an accessible, readable radar chart of category difficulty.

    Improvements vs. previous version:
    - Colorblind‑friendly palette (no pure red/green dependence)
    - Subtle alternating background rings for easier radial reading
    - Direct numeric labels near each axis point
    - Cleaner legend describing semantic difficulty bands
    - Higher contrast axis labels & improved font sizing
    - Removed visually noisy solid traffic‑light circles

    Difficulty: simulated (2.0–4.5) pending real data integration.
    Scale: 0 (hard) -> 5 (easy).
    """
    try:
        import math
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        log("[RADAR] matplotlib non installé (uv pip install matplotlib)")
        return False

    # Replace difficulty scores by raw counts of questions per category.
    # We attempt to parse the daily quiz HTML (DC_DATA) and count main_category_id occurrences.
    # Mapping main_category_id -> canonical category label.
    CAT_ID_NAME = {
        1: "Culture classique",
        2: "Culture moderne",
        3: "Culture générale",
        4: "Géographie",
        5: "Histoire",
        6: "Animaux et plantes",
        7: "Sciences et techniques",
        8: "Sport",
    }

    # Initialize counts
    category_counts: Dict[str, int] = {name: 0 for name in CAT_ID_NAME.values()}

    # Determine HTML path (fallback to default debug file)
    if quiz_html_path is None:
        default_path = ROOT / 'data' / 'html' / 'defi_du_jour_debug.html'
        if default_path.is_file():
            quiz_html_path = default_path

    if quiz_html_path and quiz_html_path.is_file():
        try:
            html_text = quiz_html_path.read_text(encoding='utf-8', errors='ignore')
            # Fast counting: occurrences of pattern "main_category_id": X
            for cid, label in CAT_ID_NAME.items():
                pattern = f'"main_category_id": {cid}'
                count = html_text.count(pattern)
                category_counts[label] = count
            total_found = sum(category_counts.values())
            if total_found == 0:
                log("[RADAR] Aucun identifiant de catégorie détecté dans le HTML, fallback simulation.")
                # Fallback: uniform distribution if parsing failed
                for k in category_counts.keys():
                    category_counts[k] = 0
            else:
                log(f"[RADAR] Catégories détectées (total questions={total_found}): " + 
                    ", ".join(f"{k}={v}" for k,v in category_counts.items()))
        except Exception as e:
            log(f"[RADAR] Erreur parsing HTML ({e}), fallback distribution vide.")
    else:
        log("[RADAR] Fichier HTML quotidien introuvable, utilisation de compteurs nuls.")

    # Values are raw counts (number of questions per category)
    # If all zeros, attempt a gentle placeholder so the chart is not degenerate.
    if all(v == 0 for v in category_counts.values()):
        # Provide placeholder approximate even distribution (will be obvious as synthetic)
        placeholder_total = 20
        per = placeholder_total // len(category_counts)
        remainder = placeholder_total - per * len(category_counts)
        for i, k in enumerate(category_counts.keys()):
            category_counts[k] = per + (1 if i < remainder else 0)
        log("[RADAR] Distribution synthétique utilisée (HTML absent).")

    categories = list(category_counts.keys())
    values = list(category_counts.values())

    categories = list(category_counts.keys())
    values = list(category_counts.values())
    num_vars = len(categories)

    # Angles for axes (start at 12 o'clock, clockwise)
    angles = [n / float(num_vars) * 2 * math.pi for n in range(num_vars)]
    angles += angles[:1]
    values += values[:1]

    # Figure / axis
    fig, ax = plt.subplots(figsize=(9.5, 9), subplot_kw=dict(projection='polar'))
    fig.patch.set_facecolor('white')
    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)

    # Readability: alternating radial bands
    # Dynamic radial max based on highest count (with +1 headroom)
    radial_max = max(values) + 1
    # Ensure minimal radial scale (avoid too compressed charts)
    if radial_max < 6:
        radial_max = 6
    ax.set_ylim(0, radial_max)
    band_colors = ['#f7f9fb', '#edf1f5']  # subtle alternating ring colors
    for i in range(1, radial_max + 1):
        if i % 2 == 0:
            ax.fill_between(angles, i - 1, i, color=band_colors[((i // 2) % 2)], alpha=0.9, zorder=0)

    # Grid & radial ticks
    yticks = list(range(1, radial_max + 1))
    ax.set_yticks(yticks)
    ax.set_yticklabels([str(y) for y in yticks], fontsize=9, color='#555555')
    ax.tick_params(axis='y', labelsize=10)
    ax.grid(linewidth=0.6, alpha=0.55)

    # Axis labels (wrap long ones manually if needed)
    def wrap(lbl: str) -> str:
        if len(lbl) > 18 and ' ' in lbl:
            parts = lbl.split(' ')
            mid = len(parts) // 2
            return ' '.join(parts[:mid]) + '\n' + ' '.join(parts[mid:])
        return lbl
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([wrap(c) for c in categories], fontsize=11, fontweight='bold', color='#222222')

    # Color palette (colorblind‑friendly / Okabe-Ito style subset)
    # (Palette placeholder kept for potential future multi-series overlay)
    line_color = '#264b99'  # outline color
    fill_color = '#5b8fd9'  # fill color

    # Draw main polygon
    ax.plot(angles, values, color=line_color, linewidth=2.8, marker='o', markersize=8,
            markerfacecolor=fill_color, markeredgecolor='white')
    ax.fill(angles, values, color=fill_color, alpha=0.28)

    # Value annotations near each category (not duplicating closing point)
    for ang, val, cat in zip(angles[:-1], values[:-1], categories):
        r = val
        # Offset outward slightly for clarity
        ax.text(ang, r + (radial_max * 0.02), f"{val}", ha='center', va='center', fontsize=10,
                fontweight='bold', color='#1f2d3d')

    # Semantic difficulty legend (no reliance on red/green alone)
    legend_patches = [
        mpatches.Patch(facecolor=fill_color, alpha=0.3, label='Nombre de questions par catégorie')
    ]
    ax.legend(handles=legend_patches, loc='upper right', bbox_to_anchor=(1.18, 1.08), fontsize=10,
              frameon=True, title='Répartition', title_fontsize=11)

    # Title & subtitle
    total_questions = sum(values[:-1])  # exclude duplicated last value
    plt.title(f"Répartition des questions par catégorie\n{date_str}", fontsize=16, fontweight='bold', pad=18)
    fig.text(0.5, 0.04, f'Total questions: {total_questions} · Source: parsing daily quiz HTML',
             ha='center', fontsize=10, color='#555555', style='italic')

    # Save / show
    if output_path is None:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        output_path = FIGURES_DIR / f"category_difficulty_{date_str}.png"

    plt.tight_layout(pad=2.0)
    if show:
        plt.show()
    try:
        fig.savefig(output_path, dpi=160, bbox_inches='tight')
        log(f"[RADAR] Graphique sauvegardé: {output_path}")
        return True
    except Exception as e:
        eprint(f"[RADAR] Erreur sauvegarde: {e}")
        return False
    finally:
        plt.close(fig)


def run_daily(date_str: str, *, use_cache: bool, refresh: bool, generate_radar: bool = False, 
              show_radar: bool = False) -> int:
    from fan2quizz.database import QuizDB  # type: ignore
    from fan2quizz.scraper import QuizypediaScraper  # type: ignore
    from fan2quizz.utils import RateLimiter  # type: ignore
    print(f"== Rapport quotidien du quiz pour {date_str} ==")
    db = QuizDB(str(DB_PATH))
    show_local_leaderboard(db, date_str)
    print("\nRécupération de la page d'archive publique...")
    scraper = QuizypediaScraper(rate_limiter=RateLimiter(RATE_LIMIT_SECONDS))
    fetched = fetch_daily_results(scraper, date_str, use_cache=use_cache, refresh=refresh)
    if fetched is None:
        print("Aucun résultat disponible pour cette date.")
        return 0
    results, from_cache = fetched
    # Source line now redundant since detailed logs exist, but keep brief summary:
    print("Source finale : " + ("cache" if from_cache else "réseau"))
    print(f"Analyse de {len(results)} entrées.")
    print("\nStatistiques de distribution :")
    summarize_distribution(results)
    print_selected_players(results)
    
    # Generate category difficulty radar chart if requested
    if generate_radar:
        print("\n📊 Génération du graphique radar de difficulté par catégorie...")
        success = create_category_difficulty_radar(date_str, show=show_radar)
        if not success:
            print("⚠️  Impossible de générer le graphique radar.")
    
    return 0


def slack_table(rows: List[Dict[str, Any]]) -> str:
    """
    Build a Slack-friendly monospaced table (ASCII pipes) wrapped in triple backticks.
    Slack does NOT render Markdown tables, so we render a fixed-width ASCII table.
    """
    if not rows:
        return "```\n(Aucune donnée)\n```"
    cols = ['rank', 'player', 'good_responses', 'total', 'pct', 'elapsed_fmt', 'badges']
    if GENZ_ENABLED:
        cols.append('genz_fr')
        if GENZ_EN_ENABLED:
            cols.append('genz_en')

    header_labels = {
        'rank': '#',
        'player': 'joueur',
        'good_responses': 'sc',
        'total': 'tot',
        'pct': '%',
        'elapsed_fmt': 'tps',
        'badges': '🏅',
        'genz_fr': 'genz_fr',
        'genz_en': 'genz_en'
    }

    # Prepare display rows (truncate long gen-z phrases)
    disp = []
    for r in rows:
        pct_str = f"{r['pct']:.1f}%" if isinstance(r.get('pct'), (int, float)) else ''
        row = {
            'rank': r.get('rank', ''),
            'player': r.get('player', ''),
            'good_responses': r.get('good_responses', ''),
            'total': r.get('total', ''),
            'pct': pct_str,
            'elapsed_fmt': r.get('elapsed_fmt', ''),
            'badges': r.get('badges', ''),
            'genz_fr': r.get('genz_fr', ''),
            'genz_en': r.get('genz_en', '')
        }
        if GENZ_ENABLED:
            if len(row['genz_fr']) > 22:
                row['genz_fr'] = row['genz_fr'][:19] + '…'
            if len(row['genz_en']) > 22:
                row['genz_en'] = row['genz_en'][:19] + '…'
        disp.append(row)

    # Display width helpers (accounts for wide emojis when wcwidth available)
    try:  # optional dependency
        from wcwidth import wcswidth  # type: ignore
        def dwidth(txt: str) -> int:
            w = wcswidth(txt)
            return w if w >= 0 else len(txt)
    except Exception:  # fallback
        def dwidth(txt: str) -> int:  # type: ignore
            return len(txt)

    min_width = {
        'rank': 2, 'player': 6, 'good_responses': 2, 'total': 3,
        'pct': 3, 'elapsed_fmt': 3, 'badges': 2, 'genz_fr': 7, 'genz_en': 7
    }
    max_width = {'player': 14, 'genz_fr': 22, 'genz_en': 22}

    # Pre-truncate values exceeding max_width for consistent width calculation
    def truncate_val(s: str, col: str) -> str:
        limit = max_width.get(col)
        if not limit:
            return s
        if dwidth(s) <= limit:
            return s
        # truncate preserving display width
        acc = ''
        for ch in s:
            if dwidth(acc + ch + '…') > limit:
                break
            acc += ch
        return acc + '…'

    # Apply truncation to header & rows for width computation stage
    trunc_disp = []
    for r in disp:
        nr = {}
        for c in cols:
            nr[c] = truncate_val(str(r[c]), c)
        trunc_disp.append(nr)
    trunc_header = {c: truncate_val(header_labels.get(c, c), c) for c in cols}

    widths: Dict[str, int] = {}
    for c in cols:
        content_w = max([dwidth(row[c]) for row in trunc_disp] + [dwidth(trunc_header[c])])
        content_w = max(content_w, min_width.get(c, 1))
        widths[c] = content_w

    def pad_cell(s: str, col: str, right_align: bool) -> str:
        s_trunc = truncate_val(s, col)
        w = dwidth(s_trunc)
        pad = widths[col] - w
        if pad <= 0:
            return s_trunc
        return (' ' * pad + s_trunc) if right_align else (s_trunc + ' ' * pad)

    def fmt(val: Any, col: str) -> str:
        s = str(val)
        align_right = col in ('rank', 'good_responses', 'total', 'pct', 'elapsed_fmt')
        return pad_cell(s, col, align_right)

    # Build lines
    sep = "+".join('-' * (widths[c] + 2) for c in cols)
    sep = f"+{sep}+"
    header_cells = [fmt(header_labels.get(c, c), c) for c in cols]
    header_line = "| " + " | ".join(header_cells) + " |"
    lines = ["```", sep, header_line, sep]
    for r in disp:
        line = "| " + " | ".join(fmt(r[c], c) for c in cols) + " |"
        lines.append(line)
    lines.append(sep)
    lines.append("```")
    return "\n".join(lines)


def serialize_rows(rows: List[Dict[str, Any]], fmt: str) -> str:
    if not rows:
        return ""
    # Column order
    cols = ['rank','player','real_name','good_responses','total','pct','elapsed_fmt','badges']
    if GENZ_ENABLED:
        cols.append('genz_fr')
        if GENZ_EN_ENABLED:
            cols.append('genz_en')
    if fmt == 'json':
        return json.dumps(rows, ensure_ascii=False, indent=2)
    if fmt in ('csv','tsv'):
        sep = ',' if fmt == 'csv' else '\t'
        out = [sep.join(cols)]
        for r in rows:
            line=[]
            for c in cols:
                val = r.get(c, '')
                if val is None:
                    val = ''
                sval = str(val)
                if sep == ',' and (',' in sval or '"' in sval):
                    sval = '"' + sval.replace('"','""') + '"'
                line.append(sval)
            out.append(sep.join(line))
        return "\n".join(out)
    if fmt == 'md':
        header = "| " + " | ".join(cols) + " |"
        sep = "| " + " | ".join(['---']*len(cols)) + " |"
        lines=[header, sep]
        for r in rows:
            lines.append("| " + " | ".join(str(r.get(c,'')) for c in cols) + " |")
        return "\n".join(lines)
    # txt (plain aligned)
    widths={c: max(len(c), *(len(str(r.get(c,''))) for r in rows)) for c in cols}
    lines=[" ".join(c.upper().ljust(widths[c]) for c in cols)]
    for r in rows:
        lines.append(" ".join(str(r.get(c,'')).ljust(widths[c]) for c in cols))
    return "\n".join(lines)


def save_table(path: Path, rows: List[Dict[str, Any]]):
    if not rows:
        log("[SAVE-TABLE] Pas de lignes à sauvegarder.")
        return
    ext = path.suffix.lower().lstrip('.')
    fmt = ext if ext in ('csv','tsv','json','md','txt') else 'txt'
    data = serialize_rows(rows, fmt)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding='utf-8')
    log(f"[SAVE-TABLE] Table enregistrée: {path} (format={fmt}, lignes={len(rows)})")


def copy_table_clipboard(rows: List[Dict[str, Any]], *, slack: bool = False):
    try:
        import pyperclip  # type: ignore
    except Exception:
        log("[CLIPBOARD] pyperclip non installé (uv add pyperclip)")
        return
    if slack:
        text = slack_table(rows)
    else:
        text = serialize_rows(rows, 'txt')
    pyperclip.copy(text)
    log("[CLIPBOARD] Table copiée dans le presse-papiers." + (" (Slack)" if slack else ""))


def build_arg_parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(description="Daily quiz report")
    p.add_argument('date',nargs='?',default=None,help='Date YYYY-MM-DD (default: yesterday)')
    p.add_argument('--no-cache',action='store_true',help='Disable local cache usage')
    p.add_argument('--refresh',action='store_true',help='Force refresh even if cached')
    p.add_argument('--cache-dir',help='Override cache directory')
    p.add_argument('--emojis',action='store_true',help='Enable emoji badges')
    p.add_argument('--genz',action='store_true',help='Enable Gen-Z banter')
    p.add_argument('--genz-en',action='store_true',help='Enable English Gen-Z column (requires --genz or --fun)')
    p.add_argument('--fun',action='store_true',help='Shortcut: enable both emojis + genz')
    p.add_argument('--kind', action='store_true', help='Replace genz_fr with only kind comments')
    p.add_argument('--save-table', help='Chemin fichier pour sauvegarder la table (auto format by extension)')
    p.add_argument('--clipboard', action='store_true', help='Copier la table finale dans le presse-papiers (texte brut)')
    p.add_argument('--clipboard-slack', action='store_true', help='Copier la table formatée pour Slack')
    p.add_argument('--slack-print', action='store_true', help='Afficher directement la table Slack sur stdout')
    p.add_argument('--radar', action='store_true', help='Générer le graphique radar de difficulté par catégorie')
    p.add_argument('--show-radar', action='store_true', help='Afficher le graphique radar interactivement (implique --radar)')
    return p


def main(argv: List[str]) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv[1:])

    interrupted = {'flag': False}

    def on_sigint(sig, frame):
        interrupted['flag'] = True
        print("\n[INTERRUPTION] Ctrl+C détecté, tentative de sauvegarde avant sortie...")
        if args.save_table and LAST_SELECTED_ROWS:
            try:
                save_table(Path(args.save_table), LAST_SELECTED_ROWS)
            except Exception as e:
                eprint(f"[INT-SAVE] Échec sauvegarde: {e}")
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, on_sigint)

    if args.date is None:
        from datetime import date as _date
        date_str=(_date.today()-timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        date_str=validate_date(args.date)
    global CACHE_DIR,EMOJIS_ENABLED,GENZ_ENABLED,GENZ_EN_ENABLED,KIND_ENABLED
    if args.cache_dir:
        CACHE_DIR = Path(args.cache_dir)
    if not (args.emojis or args.genz or args.fun):
        EMOJIS_ENABLED = True
        GENZ_ENABLED = True
    else:
        EMOJIS_ENABLED = bool(args.emojis or args.fun)
        GENZ_ENABLED = bool(args.genz or args.fun)
    # English Gen-Z only enabled if explicitly requested
    GENZ_EN_ENABLED = bool(args.genz_en and GENZ_ENABLED)
    KIND_ENABLED = bool(args.kind)
    use_cache = not args.no_cache
    refresh = bool(args.refresh)
    
    # Radar chart options
    generate_radar = args.radar or args.show_radar
    show_radar = args.show_radar
    
    try:
        code = run_daily(date_str, use_cache=use_cache, refresh=refresh, 
                        generate_radar=generate_radar, show_radar=show_radar)
    except KeyboardInterrupt:
        print("[INTERRUPTION] Arrêt par utilisateur.")
        return 130

    # Post-run save / clipboard
    if args.save_table and LAST_SELECTED_ROWS:
        save_table(Path(args.save_table), LAST_SELECTED_ROWS)
    if args.clipboard and LAST_SELECTED_ROWS:
        copy_table_clipboard(LAST_SELECTED_ROWS, slack=False)
    if args.clipboard_slack and LAST_SELECTED_ROWS:
        copy_table_clipboard(LAST_SELECTED_ROWS, slack=True)
    if args.slack_print and LAST_SELECTED_ROWS:
        print("\nTable Slack:\n")
        print(slack_table(LAST_SELECTED_ROWS))
    return code


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main(sys.argv))
