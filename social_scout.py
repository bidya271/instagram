#!/usr/bin/env python3
"""
Social Mention Scout for TrackSub & FeelsRight
Scouts online discussions (Reddit, forums, Google discussions) for high-intent D2C users
who are actively searching for subscription trackers or relationship connection apps.
"""

import sys
import json
import argparse
from typing import List, Dict

CAMPAIGN_CONFIGS = {
    "tracksub": {
        "app_name": "TrackSub",
        "url": "https://tracksub.app",
        "description": "Never miss a subscription payment again. Track renewals, AI screenshot import, and 1-click cancel guides.",
        "search_queries": [
            "site:reddit.com inurl:comments \"subscription tracker\"",
            "site:reddit.com inurl:comments \"app to track subscriptions\"",
            "site:reddit.com inurl:comments \"forgot to cancel free trial\"",
            "site:reddit.com inurl:comments \"manage recurring subscriptions\"",
            "site:reddit.com inurl:comments \"too many subscriptions to keep track of\"",
            "site:reddit.com inurl:comments \"alternative to Rocket Money\"",
            "site:reddit.com inurl:comments \"Bobby app alternative\"",
        ],
        "target_subreddits": [
            "r/personalfinance",
            "r/frugal",
            "r/budget",
            "r/apps",
            "r/iosapps",
            "r/androidapps",
            "r/sidehustle"
        ],
        "reply_framework": (
            "Hey! If you're looking for a clean, privacy-focused way to track renewals without linking your bank account, "
            "check out TrackSub (https://tracksub.app). "
            "You can drop in a screenshot of your subscriptions and the AI parses it automatically, plus it gives you direct "
            "cancellation guides so you don't have to hunt for hidden 'cancel' buttons."
        )
    },
    "feelsright": {
        "app_name": "FeelsRight",
        "url": "https://feelsright.me",
        "description": "A thirty-second daily check-in that quietly shows the people you love how you're really doing.",
        "search_queries": [
            "site:reddit.com inurl:comments \"apps for long distance couples\"",
            "site:reddit.com inurl:comments \"daily check in app couples\"",
            "site:reddit.com inurl:comments \"how to stay connected long distance\"",
            "site:reddit.com inurl:comments \"app to share mood with partner\"",
            "site:reddit.com inurl:comments \"relationship apps like Paired or Official\"",
            "site:reddit.com inurl:comments \"how was your day feels repetitive\"",
        ],
        "target_subreddits": [
            "r/LongDistance",
            "r/relationship_advice",
            "r/dating",
            "r/couples",
            "r/mentalhealth",
            "r/iosapps"
        ],
        "reply_framework": (
            "We had the exact same issue staying close without feeling like a chore or interrogating each other. "
            "We built FeelsRight (https://feelsright.me / iOS App Store) to solve this: it's a 30-second daily check-in "
            "that reveals your emotional shape without raw scores, streaks, or pressure. It's completely free and 100% "
            "privacy-first (voice notes never leave your device)."
        )
    }
}

def display_scout_playbook(app_key: str):
    config = CAMPAIGN_CONFIGS[app_key]
    print("=" * 70)
    print(f"🎯 SOCIAL MENTION SCOUT: {config['app_name'].upper()}")
    print("=" * 70)
    print(f"App URL: {config['url']}")
    print(f"Goal: Find active users asking for solutions and engage naturally.\n")

    print("📌 TARGET COMMUNITIES & SUBREDDITS:")
    for sub in config["target_subreddits"]:
        print(f"  • {sub}")
    print()

    print("🔍 HIGH-INTENT SEARCH QUERIES (Run these in Google or Reddit search):")
    for q in config["search_queries"]:
        print(f"  → {q}")
    print()

    print("💬 PROVEN AUTHENTIC REPLY TEMPLATE (Do not spam; customize per thread):")
    print("-" * 70)
    print(config["reply_framework"])
    print("-" * 70)
    print("\n💡 Tip: Reddit accounts get banned if you post raw links with 0 karma.")
    print("Answer the person's question first, share your genuine story as the builder, and invite feedback!\n")

def main():
    parser = argparse.ArgumentParser(description="Social Mention Scout for D2C Apps")
    parser.add_argument("--app", choices=["tracksub", "feelsright", "both"], default="both", help="Select app campaign")
    args = parser.parse_args()

    if args.app == "both":
        display_scout_playbook("tracksub")
        display_scout_playbook("feelsright")
    else:
        display_scout_playbook(args.app)

if __name__ == "__main__":
    main()
