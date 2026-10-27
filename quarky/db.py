"""
db.py — SQLite ORM & state engine for Quarky
Stores leads with recency, archived status, and new-account eligibility.
"""
import sqlite3, os, uuid
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "quarky.db")

def _conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS leads (
            lead_id         TEXT PRIMARY KEY,
            source          TEXT NOT NULL,
            identifier      TEXT NOT NULL,
            target_app      TEXT NOT NULL,
            context_snippet TEXT,
            status          TEXT DEFAULT 'new',
            account_safe    INTEGER DEFAULT 1,
            recency_label   TEXT DEFAULT 'Recent active',
            is_archived     INTEGER DEFAULT 0,
            created_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS outbox (
            outbox_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id     TEXT NOT NULL,
            target_app  TEXT NOT NULL,
            channel     TEXT DEFAULT 'chrome_web',
            pitch_text  TEXT,
            status      TEXT DEFAULT 'pending_approval',
            queued_at   TEXT DEFAULT (datetime('now')),
            sent_at     TEXT,
            FOREIGN KEY (lead_id) REFERENCES leads(lead_id)
        );
        CREATE TABLE IF NOT EXISTS activity_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id     TEXT,
            action_type TEXT,
            details     TEXT,
            timestamp   TEXT DEFAULT (datetime('now'))
        );
        """)
        # Safe migration if columns don't exist
        for col, col_def in [
            ("account_safe", "INTEGER DEFAULT 1"),
            ("recency_label", "TEXT DEFAULT 'Recent active'"),
            ("is_archived", "INTEGER DEFAULT 0")
        ]:
            try:
                c.execute(f"ALTER TABLE leads ADD COLUMN {col} {col_def}")
            except Exception:
                pass

def add_lead(source, identifier, target_app, context_snippet, account_safe=1, recency_label='Recent active', is_archived=0):
    lead_id = str(uuid.uuid4())
    with _conn() as c:
        # deduplicate by identifier + target_app
        existing = c.execute(
            "SELECT lead_id FROM leads WHERE identifier=? AND target_app=?",
            (identifier, target_app)
        ).fetchone()
        if existing:
            return existing["lead_id"], False
        c.execute(
            """INSERT INTO leads 
               (lead_id, source, identifier, target_app, context_snippet, account_safe, recency_label, is_archived) 
               VALUES (?,?,?,?,?,?,?,?)""",
            (lead_id, source, identifier, target_app, context_snippet, account_safe, recency_label, is_archived)
        )
    log_activity(lead_id, "lead_added", f"source={source} app={target_app}")
    return lead_id, True

def get_leads(target_app=None, status=None):
    with _conn() as c:
        q = "SELECT * FROM leads WHERE 1=1"
        params = []
        if target_app:
            q += " AND target_app=?"; params.append(target_app)
        if status:
            q += " AND status=?"; params.append(status)
        q += " ORDER BY created_at DESC"
        return [dict(r) for r in c.execute(q, params).fetchall()]

def update_lead_status(lead_id, status):
    with _conn() as c:
        c.execute("UPDATE leads SET status=? WHERE lead_id=?", (status, lead_id))

def add_outbox(lead_id, target_app, pitch_text, channel="chrome_web"):
    with _conn() as c:
        # don't double-queue
        existing = c.execute(
            "SELECT outbox_id FROM outbox WHERE lead_id=? AND status='pending_approval'",
            (lead_id,)
        ).fetchone()
        if existing:
            return existing["outbox_id"]
        cur = c.execute(
            "INSERT INTO outbox (lead_id,target_app,channel,pitch_text) VALUES (?,?,?,?)",
            (lead_id, target_app, channel, pitch_text)
        )
        return cur.lastrowid

def get_outbox(target_app=None, status="pending_approval"):
    with _conn() as c:
        q = """SELECT o.*, l.source, l.identifier, l.context_snippet, 
                      l.account_safe, l.recency_label, l.is_archived 
               FROM outbox o 
               JOIN leads l ON o.lead_id=l.lead_id 
               WHERE 1=1"""
        params = []
        if target_app:
            q += " AND o.target_app=?"; params.append(target_app)
        if status:
            q += " AND o.status=?"; params.append(status)
        q += " ORDER BY o.queued_at DESC"
        return [dict(r) for r in c.execute(q, params).fetchall()]

def update_outbox_status(outbox_id, status):
    sent_at = datetime.utcnow().isoformat() if status == "sent" else None
    with _conn() as c:
        if sent_at:
            c.execute("UPDATE outbox SET status=?,sent_at=? WHERE outbox_id=?", (status, sent_at, outbox_id))
        else:
            c.execute("UPDATE outbox SET status=? WHERE outbox_id=?", (status, outbox_id))

def log_activity(lead_id, action_type, details=""):
    with _conn() as c:
        c.execute(
            "INSERT INTO activity_log (lead_id,action_type,details) VALUES (?,?,?)",
            (lead_id, action_type, details)
        )

def get_stats():
    with _conn() as c:
        total_leads   = c.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        pending       = c.execute("SELECT COUNT(*) FROM outbox WHERE status='pending_approval'").fetchone()[0]
        sent          = c.execute("SELECT COUNT(*) FROM outbox WHERE status='sent'").fetchone()[0]
        return {"total_leads": total_leads, "pending": pending, "sent": sent}
