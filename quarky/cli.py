"""
Quarky CLI — Autonomous B2C Sales & Lead Machine for TrackSub and FeelsRight
Commands:
  import  - Ingest user/phone contact lists into the leads pipeline
  scout   - Find high-intent B2C discussion leads
  draft   - Generate personalized pitches for leads
  outbox  - The Decisions Desk: review, approve, and execute pushes
  stats   - Display live pipeline metrics
  run     - Autonomous heartbeat cycle
"""

import os
import csv
import sys
import yaml
import time
import argparse
from typing import Dict

from quarky.db import QuarkyDB
from quarky.writer import generate_pitch
from quarky.pusher import push_chrome_social, push_direct_sms, push_direct_whatsapp
from quarky.scout import run_scout_cycle

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

def load_config() -> Dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}

def cmd_import(args, db: QuarkyDB, config: Dict):
    filepath = args.file
    target_app = args.app
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return

    added = 0
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            item = row[0].strip()
            name = row[1].strip() if len(row) > 1 else ""
            if item:
                lead_id = f"contact_{abs(hash(item))}"
                if db.add_lead(lead_id, source="contact_list", identifier=item, target_app=target_app, name=name):
                    added += 1

    print(f"✅ Imported {added} new leads for {target_app.upper()} into Quarky.")

def cmd_scout(args, db: QuarkyDB, config: Dict):
    print("🔍 Quarky Scouting high-intent B2C discussions...")
    new_count = run_scout_cycle(db)
    print(f"✨ Scout complete. {new_count} new leads added.")

def cmd_draft(args, db: QuarkyDB, config: Dict):
    unpitched = db.get_leads_needing_pitch()
    print(f"📝 Drafting pitches for {len(unpitched)} leads...")
    for lead in unpitched:
        pitch = generate_pitch(lead, config)
        channel = "direct_sms" if lead["source"] == "contact_list" else "chrome_web"
        db.queue_outbox(lead["lead_id"], lead["target_app"], channel, pitch)
    print("✅ All pitches queued in Outbox for approval.")

def cmd_outbox(args, db: QuarkyDB, config: Dict):
    pending = db.get_pending_outbox()
    if not pending:
        print("📭 Outbox is empty. No pitches waiting for approval.")
        return

    print("=" * 70)
    print(f"📬 QUARKY OUTBOX ({len(pending)} pitches waiting for your approval)")
    print("=" * 70)

    for item in pending:
        print(f"\nLead:    {item['identifier']} ({item['source']})")
        print(f"App:     {item['target_app'].upper()}")
        if item.get("context_snippet"):
            print(f"Context: {item['context_snippet']}")
        print("\n--- Pitch Draft ---")
        print(item["pitch_text"])
        print("-" * 70)

        if args.approve_all:
            db.approve_outbox(item["outbox_id"])
            print("  Approved.")
            continue

        choice = input("👉 Decision [a = approve & push, r = reject, s = skip, q = quit]: ").strip().lower()
        if choice == "q":
            break
        elif choice == "r":
            db.reject_outbox(item["outbox_id"])
            print("  ❌ Rejected.")
        elif choice == "a":
            db.approve_outbox(item["outbox_id"])
            # Execute push
            if item["channel"] == "chrome_web":
                push_chrome_social(item["identifier"], item["pitch_text"])
                print("  🚀 Opened in Chrome & copied pitch to clipboard.")
            elif item["channel"] == "direct_sms":
                link = push_direct_whatsapp(item["identifier"], item["pitch_text"])
                print(f"  🚀 Push link ready: {link}")
            db.mark_sent(item["outbox_id"])
            print("  ✅ Marked as Sent.")

def cmd_stats(args, db: QuarkyDB, config: Dict):
    stats = db.get_stats()
    sent_today = db.count_sent_today()
    print("=" * 50)
    print("📊 QUARKY B2C PIPELINE METRICS")
    print("=" * 50)
    print(f"Total Leads Harvested:  {stats['total_leads']}")
    print(f"Pending Outbox Review:  {stats['pending_approval']}")
    print(f"Total Pushed:           {stats['pushed']}")
    print(f"Pushed Today:           {sent_today}")
    print("=" * 50)

def cmd_run(args, db: QuarkyDB, config: Dict):
    print("============================================================")
    print("🤖 Quarky Autonomous B2C Cycle Starting...")
    print("============================================================")
    # 1. Scout
    cmd_scout(args, db, config)
    # 2. Draft
    cmd_draft(args, db, config)
    # 3. Outbox
    cmd_stats(args, db, config)
    if args.autopilot:
        print("⚡ Autopilot enabled: auto-approving outbox...")
        pending = db.get_pending_outbox()
        for item in pending:
            db.approve_outbox(item["outbox_id"])
            db.mark_sent(item["outbox_id"])
        print(f"🚀 Pushed {len(pending)} pitches.")
    else:
        print("\n👉 Pitches are waiting in Outbox. Run: python -m quarky outbox")

def main():
    parser = argparse.ArgumentParser(description="Quarky — Autonomous B2C Sales Machine")
    subparsers = parser.add_subparsers(dest="command")

    # Import
    p_import = subparsers.add_parser("import", help="Import contacts/phone list")
    p_import.add_argument("file", help="Path to CSV or TXT file")
    p_import.add_argument("--app", choices=["tracksub", "feelsright"], required=True, help="Target app")

    # Scout
    subparsers.add_parser("scout", help="Scout high-intent leads")

    # Draft
    subparsers.add_parser("draft", help="Draft pitches for leads")

    # Outbox
    p_outbox = subparsers.add_parser("outbox", help="Review and approve outbox pitches")
    p_outbox.add_argument("--approve-all", action="store_true", help="Approve all drafts immediately")

    # Stats
    subparsers.add_parser("stats", help="Show pipeline statistics")

    # Run
    p_run = subparsers.add_parser("run", help="Run full pipeline cycle")
    p_run.add_argument("--autopilot", action="store_true", help="Auto-push without review")

    args = parser.parse_args()
    db = QuarkyDB()
    config = load_config()

    if args.command == "import":
        cmd_import(args, db, config)
    elif args.command == "scout":
        cmd_scout(args, db, config)
    elif args.command == "draft":
        cmd_draft(args, db, config)
    elif args.command == "outbox":
        cmd_outbox(args, db, config)
    elif args.command == "stats":
        cmd_stats(args, db, config)
    elif args.command == "run":
        cmd_run(args, db, config)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
