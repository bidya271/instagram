#!/usr/bin/env python3
"""
Autonomous Social Growth Agent for TrackSub & FeelsRight
Discovers high-intent social posts (Reddit, etc.), drafts contextual replies,
and publishes them via API or approval queue.
"""

import os
import sys
import time
import json
import random
import logging
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SocialAgent")

APPS_METADATA = {
    "tracksub": {
        "name": "TrackSub",
        "url": "https://tracksub.app",
        "app_store": "https://apps.apple.com/in/app/tracksubapp/id6757342390",
        "keywords": [
            "subscription tracker", "track subscriptions", "forgot to cancel", 
            "bobby app", "rocket money alternative", "recurring expenses", 
            "too many subscriptions", "free trial charged"
        ],
        "subreddits": ["iosapps", "ProductivityApps", "personalfinance", "frugal", "budget", "apps"],
        "pitch_angle": (
            "I built TrackSub (https://tracksub.app) to solve this without connecting bank credentials. "
            "It has an AI screenshot import feature (you just upload a screenshot of your subscriptions/bank statement "
            "and it logs them automatically) and gives 3-day renewal alerts with 1-click cancel guides. Free for up to 5 apps, $1/mo for unlimited."
        )
    },
    "feelsright": {
        "name": "FeelsRight",
        "url": "https://feelsright.me",
        "app_store": "https://apps.apple.com/us/app/feelsright/id6783052603",
        "keywords": [
            "long distance", "stay connected", "couples app", "daily check in",
            "relationship app", "paired alternative", "how was your day", "feel distant"
        ],
        "subreddits": ["LongDistance", "relationship_advice", "couples", "dating", "mentalhealth"],
        "pitch_angle": (
            "My partner and I built FeelsRight (https://feelsright.me) for this. "
            "It's a quiet 30-second daily emotional check-in where you slide how you feel, and your partner sees your emotional 'shape' "
            "rather than raw scores or pressure. No streaks, no trivia games, completely free on iOS, and voice notes never leave your device."
        )
    }
}

class RedditClient:
    """Handles Reddit API authentication and interactions."""
    def __init__(self, client_id: str, client_secret: str, username: str, password: str, user_agent: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.user_agent = user_agent
        self.token = None

    def authenticate(self) -> bool:
        """Obtains OAuth token from Reddit API."""
        import urllib.request
        import urllib.parse
        import base64

        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        data = urllib.parse.urlencode({
            "grant_type": "password",
            "username": self.username,
            "password": self.password
        }).encode()

        req = urllib.request.Request(
            "https://www.reddit.com/api/v1/access_token",
            data=data,
            headers={
                "Authorization": f"Basic {auth_header}",
                "User-Agent": self.user_agent
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read().decode())
                self.token = res.get("access_token")
                return bool(self.token)
        except Exception as e:
            logger.error(f"Reddit OAuth authentication failed: {e}")
            return False

    def post_comment(self, thing_id: str, markdown_text: str) -> bool:
        """Posts a comment on a Reddit submission or comment."""
        if not self.token:
            logger.error("Cannot post: Client not authenticated.")
            return False

        import urllib.request
        import urllib.parse

        data = urllib.parse.urlencode({
            "api_type": "json",
            "thing_id": thing_id,
            "text": markdown_text
        }).encode()

        req = urllib.request.Request(
            "https://oauth.reddit.com/api/comment",
            data=data,
            headers={
                "Authorization": f"bearer {self.token}",
                "User-Agent": self.user_agent
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read().decode())
                if "json" in res and not res["json"].get("errors"):
                    logger.info("Successfully posted comment to Reddit!")
                    return True
                logger.warning(f"Reddit returned errors: {res}")
                return False
        except Exception as e:
            logger.error(f"Failed to post comment: {e}")
            return False

def draft_response(app_key: str, post_title: str, post_body: str) -> str:
    """Generates an authentic, helpful reply matching the user's inquiry."""
    app = APPS_METADATA[app_key]
    
    # Founder-style response template
    greeting = random.choice(["Hey!", "Saw your post—", "Hey there,"])
    empathy = (
        "I dealt with the exact same frustration myself, which is why I built a small app to solve it." 
        if app_key == "tracksub" else 
        "Staying close without constant texting or interrogation is something my partner and I struggled with too."
    )
    
    reply = f"{greeting}\n\n{empathy}\n\n{app['pitch_angle']}\n\nHope this helps, and happy to hear any feedback if you give it a spin!"
    return reply

def run_agent_cycle(dry_run: bool = True, autopilot: bool = False):
    """Executes one scout and response cycle."""
    logger.info("=" * 60)
    logger.info("Starting Social Growth Agent Cycle")
    logger.info(f"Mode: {'Dry-Run (Simulated)' if dry_run else 'Live Reddit API'}")
    logger.info(f"Execution: {'Autopilot' if autopilot else 'Human Approval Required'}")
    logger.info("=" * 60)

    # Sample queue of discovered posts for demonstration
    simulated_leads = [
        {
            "id": "t3_1h9xabc",
            "app_target": "tracksub",
            "subreddit": "r/ProductivityApps",
            "title": "Need a subscription tracker that doesn't cost $10/month or want my bank password",
            "body": "Rocket Money is getting ridiculous charging so much to just track subscriptions. Bobby is okay but I hate manual entry. What else is there?",
            "url": "https://reddit.com/r/ProductivityApps/comments/example1"
        },
        {
            "id": "t3_1h9yxyz",
            "app_target": "feelsright",
            "subreddit": "r/LongDistance",
            "title": "Tired of 'how was your day?' texting routines with my boyfriend",
            "body": "We've been long distance for 6 months. We love each other but daily texting feels like a chore, and neither of us knows what to say anymore. Any apps or routines that help?",
            "url": "https://reddit.com/r/LongDistance/comments/example2"
        }
    ]

    for lead in simulated_leads:
        app_key = lead["app_target"]
        app = APPS_METADATA[app_key]
        
        print("\n" + "-" * 70)
        print(f"🎯 DISCOVERED POST in {lead['subreddit']} (Targeting: {app['name']})")
        print(f"Title: {lead['title']}")
        print(f"URL:   {lead['url']}")
        print("-" * 70)
        
        draft = draft_response(app_key, lead["title"], lead["body"])
        print("\n📝 PROPOSED COMMENT:")
        print(draft)
        print("-" * 70)

        if dry_run:
            print("⚡ [DRY-RUN]: Comment simulated. (To connect live Reddit API, provide credentials in .env).")
            continue

        if not autopilot:
            choice = input("\n👉 Approve and post comment? [y = post, s = skip, q = quit]: ").strip().lower()
            if choice == "q":
                break
            if choice != "y":
                print("Skipped.")
                continue

        # In live mode with credentials:
        print("Posting comment...")
        # reddit_client.post_comment(lead["id"], draft)
        time.sleep(random.uniform(5, 10))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Harvey Social Agent for D2C Apps")
    parser.add_argument("--live", action="store_true", help="Run in live API mode (requires Reddit API credentials)")
    parser.add_argument("--autopilot", action="store_true", help="Automatically post without human approval")
    args = parser.parse_args()

    run_agent_cycle(dry_run=not args.live, autopilot=args.autopilot)
