"""Daily quiz report script.

Replicates the analysis from the Jupyter notebook `quizz_du_jour_exploration.ipynb`
but as a standalone CLI utility whose only required input is the date.

Usage:
    # Daily report for an explicit date
    python examples/daily_report.py 2025-10-14

    # Daily report for yesterday (date omitted -> defaults to yesterday)
    python examples/daily_report.py

    # Weekly report (ISO week Monday-Sunday containing the date)
    python examples/daily_report.py 2025-10-14 --week

    # With emoji badges
    python examples/daily_report.py 2025-10-14 --emojis

    # With Gen-Z banter column
    python examples/daily_report.py 2025-10-14 --genz

    # Convenience: both emojis + Gen-Z
    python examples/daily_report.py 2025-10-14 --fun

Caching:
    Archive results are cached under CACHE_DIR (defaults to ./cache/archive/) as JSON.
    Subsequent runs (daily or weekly) reuse cached results to avoid re-hitting the site.
    Use --refresh to force refetch for a specific date (overwrites cache) or --no-cache to ignore cache entirely.

Styling:
    Pass --emojis to decorate rows with medals (🥇🥈🥉), performance (🌟🔥👍🙂😢) and speed (⚡⏱️) indicators.
    Pass --genz (or --fun) to explicitly request styling (already default) – now two Gen-Z columns (FR + EN) always shown by default.
    Pass --fun as a shortcut to ensure both emojis and dual Gen-Z columns (redundant with default unless you disabled them elsewhere).
    Default: emojis ON, both Gen-Z columns (FR & EN) ON.

It will:
 1. Show which quiz (if any) is mapped locally to that date.
 2. Print the local derived leaderboard from stored attempts.
 3. Fetch the public archive page for the daily quiz and extract the embedded JSON payload
    of player results (rank, good_responses, elapsed_time, etc.).
 4. Summarize distribution stats (scores / durations).
 5. Display a small table for a configured set of selected players.

Only the date argument (YYYY-MM-DD) is required. All other settings are internal constants
 you can adjust below (DB path, selected players list, rate limiting, etc.).
"""

from __future__ import annotations

import sys
import json
import statistics
import random
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import re
from datetime import datetime, timedelta
import argparse

# Project-relative imports (assumes running from repo root or this file's directory)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.database import QuizDB  # type: ignore  # noqa: E402
from src.scraper import QuizypediaScraper  # type: ignore  # noqa: E402
from src.utils import RateLimiter  # type: ignore  # noqa: E402


# ---------------- Configuration ---------------- #
DB_PATH = ROOT / "db" / "quizypedia.db"
SELECTED_PLAYERS = [
    "jutabouret",
    "louish",
    "KylianMbappe",
    "BastienZim",
    "kamaiel",
]
QUIZ_TOTAL_FALLBACK = (
    20  # used when total question count cannot be inferred from archive entry
)
RATE_LIMIT_SECONDS = 0.2
CACHE_DIR = ROOT / "cache" / "archive"
EMOJIS_ENABLED = False  # toggled via --emojis flag
GENZ_ENABLED = False  # toggled via --genz flag
LANG = 'fr'  # output language ('fr' or 'en')

# Optional mapping from username (case-insensitive) to a "real" display name.
# Fill / adjust as needed. Keys are stored lowercased when used.
REAL_NAME_MAP = {
    "jutabouret": "Julien",
    "louish": "Louis",
    "kylianmbappe": "Clement",
    "bastienzim": "Bastien",
    "kamaiel": "Raphael",
    "pascal-condamine":"Pascal",
}


def eprint(*a, **k):  # small helper
    print(*a, file=sys.stderr, **k)


def validate_date(date_str: str) -> str:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise SystemExit(f"Invalid date '{date_str}'. Expected YYYY-MM-DD.")
    return date_str


def bracket_scan_payload(html: str) -> Optional[str]:
    """Locate the large JSON array of result objects embedded in the archive page.

    We look for the first occurrence of '[{"good_responses"' and then perform a bracket-depth
    scan until we return to depth 0. Returns the raw JSON-like substring or None.
    """
    marker = '[{"good_responses"'
    start = html.find(marker)
    if start == -1:
        return None
    depth = 0
    for i, ch in enumerate(html[start:], start=start):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return html[start : i + 1]
    return None


def parse_results(raw_payload: str) -> List[Dict[str, Any]]:
    cleaned = raw_payload.strip()
    if cleaned.endswith(";"):
        cleaned = cleaned[:-1]
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # remove // comments if any (defensive)
        cleaned2 = re.sub(r"//.*?\n", "\n", cleaned)
        return json.loads(cleaned2)


def mmss(seconds: Optional[int]) -> str:
    if seconds is None:
        return ""
    try:
        seconds = int(seconds)
    except Exception:
        return ""
    if seconds >= 60:
        return f"{seconds // 60}:{seconds % 60:02d}"
    return f"0:{seconds:02d}"


def generate_genz_daily(pct: Optional[float], rank_val: Optional[int], et_val: Optional[int]) -> tuple[str, str]:
    """Generate (fr_phrase, en_phrase) for a daily row."""
    pools_en = {
        'perfect_speed': ['SLAY ⚡', 'SPEED DEMON ⚡', 'FRAME PERFECT ⚡', 'GLITCHING ⚡'],
        'perfect': ['NO CAP 🌟', 'FLAWLESS 🌟', '100% LOCKED IN 🔐', 'CLUTCH 🌟'],
        't95': ['GOATED 🔥', 'HEATING UP 🔥', 'BUILT DIFFERENT 🔥', 'DIFF CLASS 💯'],
        't80': ['BIG VIBES 😎', 'VALID 😎', 'COOKING 👨‍🍳', 'STILL COOKING 🍳'],
        't60': ['MID FR 🫠', 'ALMOST THERE 🤏', 'KEEP GRINDING 🛠️', 'HOLD THE LINE 🧱'],
        'low': ['RIP 💀', 'FUMBLED 💀', 'DOWN BAD 💀', 'DUSTED 💀'],
        'low_rank': ['NPC ENERGY 💤', 'BACKGROUND CHARACTER 💤', 'LOWKEY AF 💤', 'WHERE U AT? 👀'],
    }
    pools_fr = {
        'perfect_speed': ['PERF ÉCLAIR ⚡', 'PARFAIT SPEED ⚡', 'IMBATTABLE ⚡', 'ULTRA RAPIDE ⚡'],
        'perfect': ['SANS FAUTE 🌟', 'PARFAIT 🌟', 'FULL LOCK 🔐', 'CLUTCH 🌟'],
        't95': ['EN FEU 🔥', 'TROP FORT 🔥', 'ÇA CHAUFFE 🔥', 'GOAT 🔥'],
        't80': ['SOLIDE 😎', 'VALIDÉ 😎', 'ÇA CUIT 👨‍🍳', 'ON CUISINE 🍳'],
        't60': ['MOYEN 😬', 'EN PROGRESSION 🤏', 'CONTINUE 🛠️', 'NE LÂCHE RIEN 💪'],
        'low': ['RIP 💀', 'AÏE 💀', 'DOWN BAD 💀', 'FLOP 💀'],
        'low_rank': ['PNJ 💤', 'FIGURANT 💤', 'ON TE VOIT PAS 👀', 'BACKGROUND 💤'],
    }
    en = fr = ''
    if isinstance(pct, (int, float)):
        if pct == 100 and et_val is not None and et_val <= 30:
            en = random.choice(pools_en['perfect_speed'])
            fr = random.choice(pools_fr['perfect_speed'])
        elif pct == 100:
            en = random.choice(pools_en['perfect'])
            fr = random.choice(pools_fr['perfect'])
        elif pct >= 95:
            en = random.choice(pools_en['t95'])
            fr = random.choice(pools_fr['t95'])
        elif pct >= 80:
            en = random.choice(pools_en['t80'])
            fr = random.choice(pools_fr['t80'])
        elif pct >= 60:
            en = random.choice(pools_en['t60'])
            fr = random.choice(pools_fr['t60'])
        else:
            en = random.choice(pools_en['low'])
            fr = random.choice(pools_fr['low'])
    if rank_val and rank_val > 50 and (not en or any(k in en for k in ['RIP','FUMBLED','DOWN BAD','DUSTED'])):
        en = random.choice(pools_en['low_rank'])
    if rank_val and rank_val > 50 and (not fr or any(k in fr for k in ['RIP','AÏE','DOWN BAD','FLOP'])):
        fr = random.choice(pools_fr['low_rank'])
    return fr, en


def generate_genz_week(avg_score: Optional[float], best_rank: Optional[int], best_time: Optional[int]) -> tuple[str, str]:
    """Generate (fr_phrase, en_phrase) for a weekly aggregate row."""
    pools_en = {
        'perfect': ['PERMA SLAY 🛡️', 'ETERNAL SLAY 🛡️', 'UNTOUCHABLE 🌟'],
        't95': ['ABS GOAT 🔥', 'CERTIFIED GOAT 🔥', 'DIFF 🔥'],
        't80': ['VALID 😎', 'STURDY 😎', 'LOCKED IN 🔐'],
        't60': ['KINDA MID 🫠', 'STILL COOKING 🍳', 'WORK IN PROGRESS 🛠️'],
        'low': ['DOWN BAD 💀', 'MOLDY 💀', 'SLEEPING 💀'],
        'top_rank': ['TOP FR FR 🚀', 'ELITE 🚀', 'ASCENDING 🚀'],
        'speed': ['SPEEDRUN ⚡', 'WARP ⚡', 'BLINK ⚡'],
    }
    pools_fr = {
        'perfect': ['SLAY PERMA 🛡️', 'TOUJOURS AU TOP 🛡️', 'INTOUCHABLE 🌟'],
        't95': ['GOAT 🔥', 'CHEF 🔥', 'ELITE 🔥'],
        't80': ['VALIDÉ 😎', 'STABLE 😎', 'SOLIDE 😎'],
        't60': ['ASSEZ MID 🫠', 'EN CUISSON 🍳', 'EN TRAVAUX 🛠️'],
        'low': ['DOWN BAD 💀', 'SOMBRE 💀', 'FLOP 💀'],
        'top_rank': ['TOP FR 🚀', 'ELITE 🚀', 'EN FUSÉE 🚀'],
        'speed': ['SPEEDRUN ⚡', 'HYPER ⚡', 'FUSÉE ⚡'],
    }
    en = fr = ''
    if isinstance(avg_score, (int, float)):
        ratio = avg_score / QUIZ_TOTAL_FALLBACK
        if ratio >= 1:
            en = random.choice(pools_en['perfect'])
            fr = random.choice(pools_fr['perfect'])
        elif ratio >= 0.95:
            en = random.choice(pools_en['t95'])
            fr = random.choice(pools_fr['t95'])
        elif ratio >= 0.80:
            en = random.choice(pools_en['t80'])
            fr = random.choice(pools_fr['t80'])
        elif ratio >= 0.60:
            en = random.choice(pools_en['t60'])
            fr = random.choice(pools_fr['t60'])
        else:
            en = random.choice(pools_en['low'])
            fr = random.choice(pools_fr['low'])
    if best_rank and best_rank <= 3:
        en = random.choice(pools_en['top_rank'])
        fr = random.choice(pools_fr['top_rank'])
    if best_time and best_time <= 30 and en:
        en += ' + ' + random.choice(pools_en['speed'])
    if best_time and best_time <= 30 and fr:
        fr += ' + ' + random.choice(pools_fr['speed'])
    return fr, en


def print_selected_players(results: List[Dict[str, Any]]):
    wanted = {p.lower(): p for p in SELECTED_PLAYERS}
    rows = []
    for obj in results:
        uname = obj.get("user") or obj.get("player") or ""
        if uname.lower() in wanted:
            rows.append(
                {
                    "player": uname,
                    "rank": obj.get("rank"),
                    "good_responses": obj.get("good_responses"),
                    "total": QUIZ_TOTAL_FALLBACK,
                    "elapsed_time": obj.get("elapsed_time"),
                    "real_name": REAL_NAME_MAP.get(uname.lower()),
                }
            )

    if not rows:
        print("\nJoueurs sélectionnés : aucun trouvé dans l'archive." if LANG=='fr' else "\nSelected Players: none found in archive data.")
        missing = SELECTED_PLAYERS
    else:
        # compute pct & format + optional emoji badges
        for r in rows:
            gr = r["good_responses"]
            tot = r["total"]
            pct = (gr / tot * 100) if isinstance(gr, int) and tot else None
            r["pct"] = None if pct is None else round(pct, 1)
            r["elapsed_fmt"] = mmss(r.get("elapsed_time"))
            if EMOJIS_ENABLED:
                # Medal based on rank
                rank = r.get("rank") if isinstance(r.get("rank"), int) else None
                medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, "") if rank else ""
                # Performance based on percentage
                perf = ""
                if isinstance(r["pct"], (int, float)):
                    if r["pct"] == 100:
                        perf = "🌟"
                    elif r["pct"] >= 95:
                        perf = "🔥"
                    elif r["pct"] >= 80:
                        perf = "👍"
                    elif r["pct"] >= 60:
                        perf = "🙂"
                    else:
                        perf = "😢"
                # Speed based on elapsed time
                speed = ""
                et = r.get("elapsed_time")
                if isinstance(et, int):
                    if et <= 30:
                        speed = "⚡"
                    elif et <= 60:
                        speed = "⏱️"
                r["badges"] = medal + perf + speed
            else:
                r["badges"] = ""
            # Dual-language Gen-Z banter columns
            if GENZ_ENABLED:
                pct_val = r.get('pct')
                rank_val = r.get('rank') if isinstance(r.get('rank'), int) else None
                et_val = r.get('elapsed_time') if isinstance(r.get('elapsed_time'), int) else None
                fr_phrase, en_phrase = generate_genz_daily(pct_val, rank_val, et_val)
                r['genz_fr'] = fr_phrase
                r['genz_en'] = en_phrase
            else:
                r['genz_fr'] = ''
                r['genz_en'] = ''
        rows.sort(
            key=lambda r: (
                r["rank"] if isinstance(r.get("rank"), int) else 10**9,
                r["player"],
            )
        )

        # Pretty print with rich if available
        try:
            from rich.console import Console
            from rich.table import Table
            from rich import box

            console = Console()
            title = (f"Joueurs sélectionnés ({len(rows)})" if LANG=='fr' else f"Selected Players ({len(rows)})")
            table = Table(
                title=title,
                box=box.MINIMAL_DOUBLE_HEAD,
                header_style="bold cyan",
            )
            base_cols = [
                (("rang" if LANG=='fr' else "rank"), "bold yellow", "right"),
                (("joueur" if LANG=='fr' else "player"), "white", "left"),
                (("nom" if LANG=='fr' else "name"), "cyan", "left"),
                (("score" if LANG=='fr' else "good"), "bright_green", "right"),
                ("total", "green", "right"),
                ("pct%", "magenta", "right"),
                (("temps" if LANG=='fr' else "time"), "blue", "right"),
                ("badges", "bold", "left"),
            ]
            if GENZ_ENABLED:
                base_cols.append(("gen-z fr", "italic magenta", "left"))
                base_cols.append(("gen-z en", "italic magenta", "left"))
            for col, style, justify in base_cols:
                table.add_column(col, justify=justify, style=style)
            for r in rows:
                values = [
                    str(r.get("rank", "")),
                    r.get("player", ""),
                    r.get("real_name") or "",
                    str(r.get("good_responses", "")),
                    str(r.get("total", "")),
                    (
                        f"{r['pct']:.1f}%"
                        if isinstance(r.get("pct"), (int, float))
                        else ""
                    ),
                    r.get("elapsed_fmt", ""),
                    r.get("badges", ""),
                ]
                if GENZ_ENABLED:
                    values.append(r.get('genz_fr',''))
                    values.append(r.get('genz_en',''))
                table.add_row(*values)
            console.print(table)
        except Exception:
            # Plain fallback
            print("\nJoueurs sélectionnés:" if LANG=='fr' else "\nSelected Players:")
            header = f"{('RANG' if LANG=='fr' else 'RANK'):>4} {('JOUEUR' if LANG=='fr' else 'PLAYER'):<15} {('NOM' if LANG=='fr' else 'NAME'):<15} {'SCORE':>7} {'%':>6} {('TEMPS' if LANG=='fr' else 'TIME'):>6} {'BADGES':<8}"
            if GENZ_ENABLED:
                header += f" {'GEN-Z FR':<14} {'GEN-Z EN':<14}"
            print(header)
            print("-" * len(header))
            for r in rows:
                pct_display = (
                    f"{r['pct']:.1f}%" if isinstance(r.get("pct"), (int, float)) else ""
                )
                score_disp = f"{r.get('good_responses', '')}/{r.get('total', '')}"
                row_str = f"{str(r.get('rank', '')):>4} {r.get('player', ''):<15} {(r.get('real_name') or ''):<15} {score_disp:>7} {pct_display:>6} {r.get('elapsed_fmt', ''):>6} {r.get('badges', ''):<8}"
                if GENZ_ENABLED:
                    row_str += f" {r.get('genz_fr',''):<14} {r.get('genz_en',''):<14}"
                print(row_str)
        found_lower = {r["player"].lower() for r in rows}
        missing = [p for p in SELECTED_PLAYERS if p.lower() not in found_lower]

    if missing:
        print(("Joueurs manquants:" if LANG=='fr' else "Missing players:"), ", ".join(missing))


def summarize_distribution(results: List[Dict[str, Any]]):
    scores = [
        r.get("good_responses")
        for r in results
        if isinstance(r.get("good_responses"), int)
    ]
    durations = [
        r.get("elapsed_time") for r in results if isinstance(r.get("elapsed_time"), int)
    ]
    if scores:
        if LANG=='fr':
            print(f"Scores : n={len(scores)} min={min(scores)} max={max(scores)} moyenne={statistics.mean(scores):.2f}")
        else:
            print(f"Scores: n={len(scores)} min={min(scores)} max={max(scores)} mean={statistics.mean(scores):.2f}")
    else:
        print("Scores : aucune entrée numérique" if LANG=='fr' else "Scores: no numeric entries")
    if durations:
        if LANG=='fr':
            print(f"Durées : n={len(durations)} min={min(durations)} max={max(durations)} médiane={statistics.median(durations)}")
        else:
            print(f"Durations: n={len(durations)} min={min(durations)} max={max(durations)} median={statistics.median(durations)}")
    else:
        print("Durées : aucune entrée numérique" if LANG=='fr' else "Durations: no numeric entries")


def show_local_leaderboard(db: QuizDB, date_str: str):
    quiz_id = db.get_daily_quiz(date_str)
    if quiz_id is None:
        print((f"Aucun quiz quotidien associé localement pour {date_str} (utilisez la CLI pour le définir)." if LANG=='fr' else f"No daily quiz mapped locally for {date_str} (set via CLI if desired)."))
        return None
    quiz = db.get_quiz(quiz_id)
    if quiz:
        print(f"Date {date_str} -> quiz_id={quiz_id}: {quiz['title']}")
        print(f"Tags: {', '.join(quiz['tags'])}")
        print(f"Questions: {len(quiz['questions'])}")
    table = db.daily_table(date_str)
    if not table:
        print("No local attempts recorded for this date.")
    else:
        print("\nClassement local dérivé:" if LANG=='fr' else "\nLocal Derived Leaderboard:")
        print(f"{'#':>3} {('JOUEUR' if LANG=='fr' else 'PLAYER'):<15} {('MEIL' if LANG=='fr' else 'BEST'):>5} {'TOT':>3} {('ESS' if LANG=='fr' else 'ATT'):>3} {('TEMPS' if LANG=='fr' else 'DUR'):>6} {'EXT':>4}")
        print("-" * 50)
        for rank, row in enumerate(table, start=1):
            player, best_score, total, attempts, best_duration, external_rank = row
            dur_disp = "" if best_duration in (None, 999999) else mmss(best_duration)
            print(
                f"{rank:>3} {player:<15} {best_score:>5} {total:>3} {attempts:>3} {dur_disp:>6} {str(external_rank or ''):>4}"
            )
    return quiz_id


def cache_path_for(date_str: str) -> Path:
    return CACHE_DIR / f"{date_str}.json"


def fetch_daily_results(
    scraper: QuizypediaScraper,
    date_str: str,
    *,
    use_cache: bool = True,
    refresh: bool = False,
) -> Optional[Tuple[List[Dict[str, Any]], bool]]:
    """Fetch and parse archive results for a single date with on-disk caching.

    Cache format (JSON): {"date": str, "fetched_at": ISO8601, "count": int, "results": [...]}.
    Returns (results_list, from_cache) or None if not retrievable.
    When from_cache is True no network request was performed.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cp = cache_path_for(date_str)
    if use_cache and not refresh and cp.is_file():
        try:
            data = json.loads(cp.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("results"), list):
                return data["results"], True
        except Exception:
            pass  # fall through to refetch
    year, month, day = map(int, date_str.split("-"))
    try:
        html = scraper.get_daily_archive_html(year, month, day)
    except Exception as e:
        eprint(f"Fetch failed for {date_str}: {e}")
        return None
    raw_payload = bracket_scan_payload(html)
    if not raw_payload:
        eprint(f"No payload found for {date_str}")
        return None
    try:
        results = parse_results(raw_payload)
    except Exception as e:
        eprint(f"Parse failed for {date_str}: {e}")
        return None
    # Write cache
    if use_cache:
        try:
            from datetime import datetime as _dt

            cp.write_text(
                json.dumps(
                    {
                        "date": date_str,
                        "fetched_at": _dt.utcnow().isoformat() + "Z",
                        "count": len(results),
                        "results": results,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
        except Exception as e:
            eprint(f"Cache write failed for {date_str}: {e}")
    return results, False


def week_dates(anchor: str) -> List[str]:
    d = datetime.strptime(anchor, "%Y-%m-%d")
    monday = d - timedelta(days=d.weekday())  # ISO week Monday
    return [(monday + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]


def aggregate_selected_week(
    results_by_date: Dict[str, List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    agg: Dict[str, Dict[str, Any]] = {}
    for date_str, results in results_by_date.items():
        if not results:
            continue
        idx = {(r.get("user") or r.get("player") or "").lower(): r for r in results}
        for player in SELECTED_PLAYERS:
            pl_key = player.lower()
            entry = idx.get(pl_key)
            if not entry:
                continue
            rec = agg.setdefault(
                pl_key,
                {
                    "player": player,
                    "real_name": REAL_NAME_MAP.get(pl_key),
                    "days": 0,
                    "ranks": [],
                    "scores": [],
                    "durations": [],
                    "dates": [],
                },
            )
            rec["days"] += 1
            rec["dates"].append(date_str)
            if isinstance(entry.get("rank"), int):
                rec["ranks"].append(entry["rank"])
            if isinstance(entry.get("good_responses"), int):
                rec["scores"].append(entry["good_responses"])
            if isinstance(entry.get("elapsed_time"), int):
                rec["durations"].append(entry["elapsed_time"])
    # compute metrics
    rows = []
    for rec in agg.values():
        ranks = rec["ranks"]
        scores = rec["scores"]
        durs = rec["durations"]
        row = {
            "player": rec["player"],
            "real_name": rec["real_name"],
            "days": rec["days"],
            "avg_rank": round(sum(ranks) / len(ranks), 2) if ranks else None,
            "best_rank": min(ranks) if ranks else None,
            "avg_score": round(sum(scores) / len(scores), 2) if scores else None,
            "max_score": max(scores) if scores else None,
            "avg_time": round(sum(durs) / len(durs)) if durs else None,
            "best_time": min(durs) if durs else None,
        }
        if EMOJIS_ENABLED:
            medal = (
                {1: "🥇", 2: "🥈", 3: "🥉"}.get(row["best_rank"], "")
                if row["best_rank"]
                else ""
            )
            perf = ""
            if row["avg_score"] is not None:
                ratio = row["avg_score"] / QUIZ_TOTAL_FALLBACK
                if ratio >= 1:
                    perf = "🌟"
                elif ratio >= 0.95:
                    perf = "🔥"
                elif ratio >= 0.80:
                    perf = "👍"
                elif ratio >= 0.60:
                    perf = "🙂"
                else:
                    perf = "😢"
            speed = ""
            if row["best_time"] is not None:
                bt = row["best_time"]
                if bt <= 30:
                    speed = "⚡"
                elif bt <= 60:
                    speed = "⏱️"
            row["badges"] = medal + perf + speed
        else:
            row["badges"] = ""
        # Gen-Z weekly phrase (optional with randomness)
        if GENZ_ENABLED:
            avg_score = row.get('avg_score')
            best_rank = row.get('best_rank')
            best_time = row.get('best_time')
            if LANG=='fr':
                pools_w = {
                    'perfect': ['SLAY PERMA 🛡️', 'TOUJOURS AU TOP 🛡️', 'INTOUCHABLE 🌟'],
                    't95': ['GOAT 🔥', 'CHEF 🔥', 'ELITE 🔥'],
                    't80': ['VALIDÉ 😎', 'STABLE 😎', 'SOLIDE 😎'],
                    't60': ['ASSEZ MID 🫠', 'EN CUISSON 🍳', 'EN TRAVAUX 🛠️'],
                    'low': ['DOWN BAD 💀', 'SOMBRE 💀', 'FLOP 💀'],
                    'top_rank': ['TOP FR 🚀', 'ELITE 🚀', 'EN FUSÉE 🚀'],
                    'speed': ['SPEEDRUN ⚡', 'HYPER ⚡', 'FUSÉE ⚡'],
                }
            else:
                pools_w = {
                    'perfect': ['PERMA SLAY 🛡️', 'ETERNAL SLAY 🛡️', 'UNTOUCHABLE 🌟'],
                    't95': ['ABS GOAT 🔥', 'CERTIFIED GOAT 🔥', 'DIFF 🔥'],
                    't80': ['VALID 😎', 'STURDY 😎', 'LOCKED IN 🔐'],
                    't60': ['KINDA MID 🫠', 'STILL COOKING 🍳', 'WORK IN PROGRESS 🛠️'],
                    'low': ['DOWN BAD 💀', 'MOLDY 💀', 'SLEEPING 💀'],
                    'top_rank': ['TOP FR FR 🚀', 'ELITE 🚀', 'ASCENDING 🚀'],
                    'speed': ['SPEEDRUN ⚡', 'WARP ⚡', 'BLINK ⚡'],
                }
            phrase = ''
            if isinstance(avg_score, (int, float)):
                ratio = avg_score / QUIZ_TOTAL_FALLBACK
                if ratio >= 1:
                    phrase = random.choice(pools_w['perfect'])
                elif ratio >= 0.95:
                    phrase = random.choice(pools_w['t95'])
                elif ratio >= 0.80:
                    phrase = random.choice(pools_w['t80'])
                elif ratio >= 0.60:
                    phrase = random.choice(pools_w['t60'])
                else:
                    phrase = random.choice(pools_w['low'])
            if best_rank and best_rank <= 3:
                phrase = random.choice(pools_w['top_rank'])
            if best_time and best_time <= 30 and phrase:
                phrase += ' + ' + random.choice(pools_w['speed'])
            row['genz'] = phrase
        else:
            row['genz'] = ''
        rows.append(row)
    rows.sort(
        key=lambda r: (r["avg_rank"] if r["avg_rank"] is not None else 1e9, r["player"])
    )
    return rows


def print_weekly_tables(
    dates: List[str], results_by_date: Dict[str, List[Dict[str, Any]]]
):
    # Summary per day
    per_day = []
    for ds in dates:
        res = results_by_date.get(ds) or []
        scores = [
            r.get("good_responses")
            for r in res
            if isinstance(r.get("good_responses"), int)
        ]
        participants = len(res)
        top = max(scores) if scores else None
        mean = round(statistics.mean(scores), 2) if scores else None
        per_day.append(
            {
                "date": ds,
                "participants": participants,
                "top": top,
                "mean": mean,
            }
        )
    # Selected players aggregate
    selected_rows = aggregate_selected_week(results_by_date)

    # Use rich if available
    try:
        from rich.console import Console
        from rich.table import Table
        from rich import box

        console = Console()
        # Daily summary table
        t1 = Table(
            title="Weekly Daily Summary",
            box=box.MINIMAL_DOUBLE_HEAD,
            header_style="bold cyan",
        )
        for col in ["date", "participants", "top", "mean"]:
            t1.add_column(col, justify="center")
        for row in per_day:
            t1.add_row(
                row["date"],
                str(row["participants"]),
                str(row["top"] or ""),
                str(row["mean"] or ""),
            )
        console.print(t1)
        # Selected players weekly aggregate
        t2 = Table(
            title="Selected Players Weekly Aggregate",
            box=box.MINIMAL_DOUBLE_HEAD,
            header_style="bold cyan",
        )
        cols = [
            "player","name","days","avg_rank","best_rank","avg_score","max_score","avg_time","best_time","badges"
        ]
        if GENZ_ENABLED:
            cols.extend(["gen-z fr","gen-z en"])
        for col in cols:
            t2.add_column(col, justify="center")

        def fmt_time(v):
            return mmss(v) if isinstance(v, int) else ""

        for r in selected_rows:
            row_vals = [
                r["player"],
                r.get("real_name") or "",
                str(r["days"]),
                str(r["avg_rank"] or ""),
                str(r["best_rank"] or ""),
                str(r["avg_score"] or ""),
                str(r["max_score"] or ""),
                fmt_time(r["avg_time"]),
                fmt_time(r["best_time"]),
                r.get("badges", ""),
            ]
            if GENZ_ENABLED:
                row_vals.extend([r.get('genz_fr',''), r.get('genz_en','')])
            t2.add_row(*row_vals)
        console.print(t2)
    except Exception:
        # Plain fallback
        print("\nWeekly Daily Summary:")
        header = f"{'DATE':<10} {'PART':>4} {'TOP':>4} {'MEAN':>6}"
        print(header)
        print("-" * len(header))
        for row in per_day:
            print(
                f"{row['date']:<10} {row['participants']:>4} {str(row['top'] or ''):>4} {str(row['mean'] or ''):>6}"
            )
        print("\nSelected Players Weekly Aggregate:")
        header2 = (
            f"{'PLAYER':<15} {'NAME':<15} {'DAYS':>4} {'AVG_R':>6} {'BEST_R':>6} {'AVG_S':>6} {'MAX_S':>6} {'AVG_T':>6} {'BEST_T':>6} {'BADGES':<8}"
            + (" {'GEN-Z':<14}" if GENZ_ENABLED else "")
        )
        print(header2)
        print("-" * len(header2))

        def tdisp(v):
            return mmss(v) if isinstance(v, int) else ""

        for r in selected_rows:
            base = f"{r['player']:<15} {(r.get('real_name') or ''):<15} {r['days']:>4} {str(r['avg_rank'] or ''):>6} {str(r['best_rank'] or ''):>6} {str(r['avg_score'] or ''):>6} {str(r['max_score'] or ''):>6} {tdisp(r['avg_time']):>6} {tdisp(r['best_time']):>6} {r.get('badges', ''):<8}"
            if GENZ_ENABLED:
                base += f" {r.get('genz', ''):<14}"
            print(base)


def run_daily(date_str: str, *, use_cache: bool, refresh: bool) -> int:
    year, month, day = map(int, date_str.split("-"))
    print(f"== Rapport quotidien du quiz pour {date_str} ==" if LANG=='fr' else f"== Daily Quiz Report for {date_str} ==")
    db = QuizDB(str(DB_PATH))
    show_local_leaderboard(db, date_str)
    print("\nRécupération de la page d'archive publique..." if LANG=='fr' else "\nFetching public archive page...")
    scraper = QuizypediaScraper(rate_limiter=RateLimiter(RATE_LIMIT_SECONDS))
    fetched = fetch_daily_results(
        scraper, date_str, use_cache=use_cache, refresh=refresh
    )
    if fetched is None:
        print("No results available for this date.")
        return 0
    results, from_cache = fetched
    print(("Source : " if LANG=='fr' else "Source: ") + ("cache" if from_cache else ("réseau" if LANG=='fr' else "network")))
    print((f"Analyse de {len(results)} entrées." if LANG=='fr' else f"Parsed {len(results)} ranking entries."))
    print("\nStatistiques de distribution :" if LANG=='fr' else "\nDistribution Stats:")
    summarize_distribution(results)
    print_selected_players(results)
    return 0


def run_week(anchor_date: str, *, use_cache: bool, refresh: bool) -> int:
    dates = week_dates(anchor_date)
    print(f"== Rapport hebdomadaire (Lun-Dim) incluant {anchor_date} ==" if LANG=='fr' else f"== Weekly Quiz Report (Mon-Sun) containing {anchor_date} ==")
    print(("Dates de la semaine :" if LANG=='fr' else "Week dates:"), ", ".join(dates))
    scraper = QuizypediaScraper(rate_limiter=RateLimiter(RATE_LIMIT_SECONDS))
    results_by_date: Dict[str, List[Dict[str, Any]]] = {}
    cache_hits = 0
    net_fetches = 0
    for ds in dates:
        print(f"\n[Jour {ds}] Chargement des résultats..." if LANG=='fr' else f"\n[Day {ds}] Loading results...")
        fetched = fetch_daily_results(scraper, ds, use_cache=use_cache, refresh=refresh)
        if fetched is None:
            results_by_date[ds] = []
            continue
        res, from_cache = fetched
        if from_cache:
            cache_hits += 1
            print(f"{('Analyse' if LANG=='fr' else 'Parsed')} {len(res)} {('entrées' if LANG=='fr' else 'entries')} (cache)")
        else:
            net_fetches += 1
            print(f"{('Analyse' if LANG=='fr' else 'Parsed')} {len(res)} {('entrées' if LANG=='fr' else 'entries')} ({'réseau' if LANG=='fr' else 'network'})")
        results_by_date[ds] = res
    if LANG=='fr':
        print(f"\nRésumé des récupérations hebdo : cache={cache_hits} réseau={net_fetches}")
    else:
        print(f"\nWeekly fetch summary: cache_hits={cache_hits} network_fetches={net_fetches}")
    print_weekly_tables(dates, results_by_date)
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Daily / Weekly quiz report")
    p.add_argument(
        "date",
        nargs="?",
        default=None,
        help="Anchor date YYYY-MM-DD (daily report for that date or week containing it). If omitted, defaults to yesterday.",
    )
    g = p.add_mutually_exclusive_group()
    g.add_argument(
        "--week",
        action="store_true",
        help="Generate a weekly report (Mon-Sun containing the date)",
    )
    p.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable local cache usage (always fetch)",
    )
    p.add_argument(
        "--refresh",
        action="store_true",
        help="Force re-fetch even if cached (updates cache)",
    )
    p.add_argument(
        "--cache-dir", help="Override cache directory (default ./cache/archive/)"
    )
    p.add_argument(
        "--emojis",
        action="store_true",
        help="Enable emoji badges (medals/performance/speed)",
    )
    p.add_argument(
        "--genz", action="store_true", help="Add a Gen-Z banter phrase column"
    )
    p.add_argument(
        "--fun", action="store_true", help="Shortcut: enable both --emojis and --genz"
    )
    p.add_argument(
        "--lang",
        choices=["fr", "en"],
        default="fr",
        help="Output language: fr (défaut) or en",
    )
    return p


def main(argv: List[str]) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv[1:])
    if args.date is None:
        from datetime import date as _date
        date_str = (_date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        date_str = validate_date(args.date)
    # Override cache dir if provided
    global CACHE_DIR
    if args.cache_dir:
        CACHE_DIR = Path(args.cache_dir)
    use_cache = not args.no_cache
    refresh = bool(args.refresh)
    global EMOJIS_ENABLED, GENZ_ENABLED
    # Styling defaults: if user provided no styling flags, enable both by default
    # Language selection
    global LANG
    LANG = args.lang
    # Styling defaults: emojis always on by default; gen-z only auto-on for French.
    if not (args.emojis or args.genz or args.fun):
        EMOJIS_ENABLED = True
        GENZ_ENABLED = True
    else:
        EMOJIS_ENABLED = bool(args.emojis or args.fun)
        GENZ_ENABLED = bool(args.genz or args.fun)
    if args.week:
        return run_week(date_str, use_cache=use_cache, refresh=refresh)
    return run_daily(date_str, use_cache=use_cache, refresh=refresh)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv))
