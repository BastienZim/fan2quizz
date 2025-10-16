"""SQLite persistence layer for quizzes, attempts and daily leaderboard."""

from __future__ import annotations

import os
import sqlite3
from typing import Iterable, Optional, List, Dict, Any, Tuple

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS quizzes (
  id INTEGER PRIMARY KEY,
  url TEXT UNIQUE,
  title TEXT,
  description TEXT,
  tags TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS questions (
  id INTEGER PRIMARY KEY,
  quiz_id INTEGER REFERENCES quizzes(id) ON DELETE CASCADE,
  qindex INTEGER,
  question_text TEXT,
  choices TEXT,
  correct_index INTEGER
);
CREATE TABLE IF NOT EXISTS attempts (
  id INTEGER PRIMARY KEY,
  quiz_id INTEGER REFERENCES quizzes(id) ON DELETE CASCADE,
  player TEXT,
  score INTEGER,
  total INTEGER,
  answers TEXT,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_seconds INTEGER,
    external_rank INTEGER
);
CREATE INDEX IF NOT EXISTS idx_attempts_quiz ON attempts(quiz_id);
CREATE INDEX IF NOT EXISTS idx_attempts_player ON attempts(player);
CREATE TABLE IF NOT EXISTS daily_quizzes (
  date TEXT PRIMARY KEY,
  quiz_id INTEGER REFERENCES quizzes(id) ON DELETE CASCADE
);
CREATE VIRTUAL TABLE IF NOT EXISTS quizzes_fts USING fts5(title, description, tags, content='quizzes', content_rowid='id');
"""


class QuizDB:
    def __init__(self, path: str):
        # Ensure parent directory exists to avoid 'unable to open database file'
        dir_path = os.path.dirname(path)
        if dir_path and not os.path.isdir(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.executescript(SCHEMA)
        self._run_migrations()
        self.conn.commit()

    # Quiz storage
    def insert_quiz(self, url: str, title: str, description: str, tags: Iterable[str]) -> int:
        tags_s = ','.join(tags)
        cur = self.conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO quizzes (url, title, description, tags) VALUES (?,?,?,?)",
            (url, title, description, tags_s),
        )
        self.conn.commit()
        rowid = cur.lastrowid
        if rowid:
            self.conn.execute(
                "INSERT INTO quizzes_fts(rowid, title, description, tags) VALUES (?,?,?,?)",
                (rowid, title, description, tags_s),
            )
            self.conn.commit()
        else:
            rowid = self.get_quiz_id_by_url(url) or 0
        return rowid

    def get_quiz_id_by_url(self, url: str) -> Optional[int]:
        cur = self.conn.execute("SELECT id FROM quizzes WHERE url=?", (url,))
        r = cur.fetchone()
        return r[0] if r else None

    def insert_question(self, quiz_id: int, qindex: int, question_text: str, choices: Iterable[str], correct_index: Optional[int]):
        choices_s = '||'.join(choices)
        self.conn.execute(
            "INSERT INTO questions (quiz_id, qindex, question_text, choices, correct_index) VALUES (?,?,?,?,?)",
            (quiz_id, qindex, question_text, choices_s, correct_index),
        )
        self.conn.commit()

    # Search
    def search_quizzes(self, q: str, limit: int = 10):
        cur = self.conn.execute(
            "SELECT q.id, q.title, q.url FROM quizzes q JOIN quizzes_fts f ON q.id=f.rowid WHERE quizzes_fts MATCH ? LIMIT ?",
            (q, limit),
        )
        return cur.fetchall()

    # Attempts
    def record_attempt(self, quiz_id: int, player: str, answers: Iterable[int]):
        answers_list = list(answers)
        score = self._compute_score(quiz_id, answers_list)
        self.conn.execute(
            "INSERT INTO attempts (quiz_id, player, score, total, answers) VALUES (?,?,?,?,?)",
            (quiz_id, player, score, len(answers_list), ','.join(map(str, answers_list))),
        )
        self.conn.commit()
        return score

    def _compute_score(self, quiz_id: int, answers: List[int]) -> int:
        cur = self.conn.execute(
            "SELECT correct_index FROM questions WHERE quiz_id=? ORDER BY qindex",
            (quiz_id,),
        )
        corrects = [r[0] for r in cur.fetchall()]
        return sum(1 for i, a in enumerate(answers) if i < len(corrects) and corrects[i] is not None and a == corrects[i])

    def leaderboard_for_date(self, date: str) -> List[Tuple[str, int, int]]:
        cur = self.conn.execute(
            "SELECT player, MAX(score) as best, MAX(total) as total FROM attempts a JOIN daily_quizzes d ON a.quiz_id=d.quiz_id WHERE d.date=? GROUP BY player ORDER BY best DESC, player",
            (date,),
        )
        return cur.fetchall()

    def daily_table(self, date: str):
        """Return richer leaderboard rows for a date.

        Output columns:
          player, best_score, total, attempts, best_duration, external_rank
        """
        cur = self.conn.execute(
            """
            SELECT a.player,
                   MAX(a.score) as best_score,
                   MAX(a.total) as total,
                   COUNT(*) as attempts,
                   MIN(CASE WHEN a.score = (
                        SELECT MAX(a2.score) FROM attempts a2 JOIN daily_quizzes d2 ON a2.quiz_id=d2.quiz_id WHERE d2.date = d.date AND a2.player = a.player
                   ) THEN COALESCE(a.duration_seconds, 999999) END) as best_duration,
                   MIN(CASE WHEN a.score = (
                        SELECT MAX(a2.score) FROM attempts a2 JOIN daily_quizzes d2 ON a2.quiz_id=d2.quiz_id WHERE d2.date = d.date AND a2.player = a.player
                   ) THEN a.external_rank END) as external_rank
            FROM attempts a
            JOIN daily_quizzes d ON a.quiz_id = d.quiz_id
            WHERE d.date=?
            GROUP BY a.player
            ORDER BY best_score DESC, best_duration ASC, a.player
            """,
            (date,),
        )
        return cur.fetchall()

    # Player-centric retrieval
    def best_attempt_for_date_player(self, date: str, player: str):
        cur = self.conn.execute(
            """
            SELECT a.id, a.score, a.total, a.duration_seconds, a.external_rank, a.answers, a.attempted_at, a.quiz_id
            FROM attempts a
            JOIN daily_quizzes d ON a.quiz_id = d.quiz_id
            WHERE d.date=? AND a.player=?
            ORDER BY a.score DESC, a.duration_seconds ASC, a.attempted_at ASC
            LIMIT 1
            """,
            (date, player),
        )
        return cur.fetchone()

    # Daily quiz
    def set_daily_quiz(self, date: str, quiz_id: int):
        self.conn.execute(
            "INSERT INTO daily_quizzes(date, quiz_id) VALUES(?,?) ON CONFLICT(date) DO UPDATE SET quiz_id=excluded.quiz_id",
            (date, quiz_id),
        )
        self.conn.commit()

    def get_daily_quiz(self, date: str) -> Optional[int]:
        cur = self.conn.execute("SELECT quiz_id FROM daily_quizzes WHERE date=?", (date,))
        row = cur.fetchone()
        return row[0] if row else None

    # Export
    def get_quiz(self, quiz_id: int) -> Optional[Dict[str, Any]]:
        cur = self.conn.execute(
            "SELECT id, url, title, description, tags FROM quizzes WHERE id=?",
            (quiz_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        q_cur = self.conn.execute(
            "SELECT qindex, question_text, choices, correct_index FROM questions WHERE quiz_id=? ORDER BY qindex",
            (quiz_id,),
        )
        questions = []
        for qindex, qtext, choices_s, correct_index in q_cur.fetchall():
            questions.append({
                'qindex': qindex,
                'question_text': qtext,
                'choices': choices_s.split('||'),
                'correct_index': correct_index,
            })
        return {
            'id': row[0],
            'url': row[1],
            'title': row[2],
            'description': row[3],
            'tags': row[4].split(',') if row[4] else [],
            'questions': questions,
        }

    def update_attempt_meta(self, attempt_id: int, duration: int | None, external_rank: int | None):
        sets = []
        params = []
        if duration is not None:
            sets.append("duration_seconds = ?")
            params.append(duration)
        if external_rank is not None:
            sets.append("external_rank = ?")
            params.append(external_rank)
        if not sets:
            return
        params.append(attempt_id)
        self.conn.execute(f"UPDATE attempts SET {', '.join(sets)} WHERE id=?", params)
        self.conn.commit()

    def close(self):
        self.conn.close()

    # --- migrations ---
    def _run_migrations(self):
        """Idempotent schema migrations for new columns."""
        cur = self.conn.execute("PRAGMA table_info(attempts)")
        cols = {r[1] for r in cur.fetchall()}
        # Add duration_seconds column if missing
        if 'duration_seconds' not in cols:
            self.conn.execute("ALTER TABLE attempts ADD COLUMN duration_seconds INTEGER")
        if 'external_rank' not in cols:
            self.conn.execute("ALTER TABLE attempts ADD COLUMN external_rank INTEGER")