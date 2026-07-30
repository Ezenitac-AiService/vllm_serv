"""
SQLite Metrics Database Manager Module for vllm_serv (043-api-key-auth-toggle).
Manages async SQLite logging, WAL journal mode, 30-day retention cleanup, and SQL metrics aggregation.
"""

import os
import sqlite3
import datetime
from typing import Dict, Any, List

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "metrics.db")


class MetricsDB:
    """Manages SQLite metrics database with WAL mode and busy timeout."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        is_new_db = not os.path.exists(self.db_path)
        self._init_db()
        if is_new_db:
            try:
                from scripts.seed_db import seed_database
                seed_database(reset=False)
            except Exception:
                pass

    def _get_connection(self) -> sqlite3.Connection:
        """Returns SQLite connection with WAL mode and timeout=10.0 per C2 critique."""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Creates tables and indexes if not exists."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_key_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_key TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    endpoint TEXT NOT NULL,
                    status_code INTEGER NOT NULL,
                    prompt_tokens INTEGER DEFAULT 0,
                    completion_tokens INTEGER DEFAULT 0,
                    ttft_ms REAL DEFAULT 0.0,
                    tps REAL DEFAULT 0.0,
                    is_error INTEGER DEFAULT 0,
                    prompt_text TEXT,
                    completion_text TEXT,
                    thinking_text TEXT
                );
            """)
            # Migration check for existing databases
            try:
                conn.execute("ALTER TABLE api_key_logs ADD COLUMN prompt_text TEXT;")
            except Exception:
                pass
            try:
                conn.execute("ALTER TABLE api_key_logs ADD COLUMN completion_text TEXT;")
            except Exception:
                pass
            try:
                conn.execute("ALTER TABLE api_key_logs ADD COLUMN thinking_text TEXT;")
            except Exception:
                pass

            conn.execute("CREATE INDEX IF NOT EXISTS idx_api_key ON api_key_logs(api_key);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON api_key_logs(timestamp);")
            conn.commit()

    def log_request(
        self,
        api_key: str,
        endpoint: str,
        status_code: int,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        ttft_ms: float = 0.0,
        tps: float = 0.0,
        is_error: bool = False,
        prompt_text: str = None,
        completion_text: str = None,
        thinking_text: str = None
    ):
        """Logs a single API request asynchronously/synchronously with connection pooling and payload text."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO api_key_logs 
                    (api_key, endpoint, status_code, prompt_tokens, completion_tokens, ttft_ms, tps, is_error, prompt_text, completion_text, thinking_text)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        api_key,
                        endpoint,
                        status_code,
                        prompt_tokens,
                        completion_tokens,
                        ttft_ms,
                        tps,
                        1 if is_error else 0,
                        prompt_text,
                        completion_text,
                        thinking_text
                    )
                )
                conn.commit()
        except Exception as e:
            # Fallback safe logging
            print(f"[MetricsDB ERROR] Failed to log metrics: {e}")

    def cleanup_old_logs(self, days: int = 30):
        """Deletes metrics older than specified retention days (FR-005)."""
        cutoff = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            conn.execute("DELETE FROM api_key_logs WHERE timestamp < ?", (cutoff,))
            conn.commit()

    def get_aggregated_metrics(self) -> List[Dict[str, Any]]:
        """Returns aggregated SQL metrics per API key for dashboard & Top 5 charts."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    api_key,
                    COUNT(*) as request_count,
                    SUM(is_error) as error_count,
                    SUM(prompt_tokens) as prompt_tokens,
                    SUM(completion_tokens) as completion_tokens,
                    AVG(ttft_ms) as avg_ttft_ms,
                    AVG(tps) as avg_tps,
                    MAX(timestamp) as last_used_at
                FROM api_key_logs
                GROUP BY api_key
                ORDER BY (SUM(prompt_tokens) + SUM(completion_tokens)) DESC
            """)
            rows = cursor.fetchall()
            results = []
            for r in rows:
                p_tok = r["prompt_tokens"] or 0
                c_tok = r["completion_tokens"] or 0
                # FinOps cost estimation: (prompt * 0.0000005) + (completion * 0.0000015)
                est_cost = (p_tok * 0.0000005) + (c_tok * 0.0000015)
                results.append({
                    "api_key": r["api_key"],
                    "request_count": r["request_count"],
                    "error_count": r["error_count"] or 0,
                    "prompt_tokens": p_tok,
                    "completion_tokens": c_tok,
                    "avg_ttft_ms": round(r["avg_ttft_ms"] or 0.0, 1),
                    "avg_tps": round(r["avg_tps"] or 0.0, 1),
                    "estimated_cost_usd": round(est_cost, 4),
                    "last_used_at": r["last_used_at"] or ""
                })
            return results

    def get_payload_by_id(self, log_id: int) -> Dict[str, Any]:
        """Returns prompt_text, completion_text, and thinking_text for a specific log entry ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, api_key, endpoint, status_code, prompt_tokens, completion_tokens, ttft_ms, tps, prompt_text, completion_text, thinking_text, timestamp FROM api_key_logs WHERE id = ?",
                (log_id,)
            )
            row = cursor.fetchone()
            if not row:
                return {}
            return dict(row)


metrics_db = MetricsDB()
