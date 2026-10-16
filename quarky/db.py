"""
Quarky Database & State Engine (data/quarky.db)
Stores leads, intelligence observations, outbox drafts, and push history.
"""

import os
import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional

DB_PATH = "data/quarky.db"

class QuarkyDB:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            # 1. B2C Leads
            cur.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    lead_id TEXT PRIMARY KEY,
                    source TEXT,                -- 'contact_list', 'reddit', 'threads', 'web'
                    identifier TEXT,            -- phone number, username, or profile URL
                    name TEXT,
                    target_app TEXT,            -- 'tracksub' or 'feelsright'
                    context_snippet TEXT,       -- their specific complaint or origin
                    status TEXT DEFAULT 'new',  -- 'new', 'qualified', 'drafted', 'pushed', 'converted'
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 2. Outbox (The Decision Desk)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS outbox (
                    outbox_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id TEXT UNIQUE,
                    target_app TEXT,
                    channel TEXT,               -- 'chrome_web', 'direct_sms', 'direct_dm'
                    pitch_text TEXT,
                    status TEXT DEFAULT 'pending_approval', -- 'pending_approval', 'approved', 'rejected', 'sent'
                    queued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sent_at TIMESTAMP,
                    FOREIGN KEY(lead_id) REFERENCES leads(lead_id)
                )
            """)
            # 3. Actions & Activity Log
            cur.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id TEXT,
                    action_type TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def add_lead(self, lead_id: str, source: str, identifier: str, target_app: str, context_snippet: str = "", name: str = "") -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR IGNORE INTO leads (lead_id, source, identifier, target_app, context_snippet, name)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (lead_id, source, identifier, target_app, context_snippet, name))
            conn.commit()
            return cur.rowcount > 0

    def get_leads_needing_pitch(self, limit: int = 50) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("""
                SELECT l.* FROM leads l
                LEFT JOIN outbox o ON l.lead_id = o.lead_id
                WHERE o.outbox_id IS NULL AND l.status = 'new'
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cur.fetchall()]

    def queue_outbox(self, lead_id: str, target_app: str, channel: str, pitch_text: str):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO outbox (lead_id, target_app, channel, pitch_text, status)
                VALUES (?, ?, ?, ?, 'pending_approval')
            """, (lead_id, target_app, channel, pitch_text))
            cur.execute("UPDATE leads SET status = 'drafted' WHERE lead_id = ?", (lead_id,))
            conn.commit()

    def get_pending_outbox(self, limit: int = 50) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("""
                SELECT o.*, l.identifier, l.source, l.context_snippet, l.name
                FROM outbox o
                JOIN leads l ON o.lead_id = l.lead_id
                WHERE o.status = 'pending_approval'
                ORDER BY o.queued_at ASC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cur.fetchall()]

    def approve_outbox(self, outbox_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("UPDATE outbox SET status = 'approved' WHERE outbox_id = ?", (outbox_id,))
            conn.commit()

    def reject_outbox(self, outbox_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("UPDATE outbox SET status = 'rejected' WHERE outbox_id = ?", (outbox_id,))
            conn.commit()

    def mark_sent(self, outbox_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("UPDATE outbox SET status = 'sent', sent_at = CURRENT_TIMESTAMP WHERE outbox_id = ?", (outbox_id,))
            cur.execute("""
                UPDATE leads SET status = 'pushed'
                WHERE lead_id = (SELECT lead_id FROM outbox WHERE outbox_id = ?)
            """, (outbox_id,))
            conn.commit()

    def count_sent_today(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM outbox WHERE status = 'sent' AND date(sent_at) = date('now')")
            return cur.fetchone()[0]

    def get_stats(self) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM leads")
            total_leads = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM outbox WHERE status = 'pending_approval'")
            pending = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM outbox WHERE status = 'sent'")
            sent = cur.fetchone()[0]
            return {"total_leads": total_leads, "pending_approval": pending, "pushed": sent}
