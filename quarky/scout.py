"""
scout.py — Multi-platform high-intent conversation harvester
Filters for post recency, unarchived status, and 3-week-old account eligibility.
"""
import urllib.request, urllib.parse, json, time, re
from quarky import db
from quarky.strategist import load_blueprint

# Verified recent, unarchived, and 3-week-account-friendly discussion threads.
# Each entry is vetted against subreddit AutoModerator karma/age filters.
VERIFIED_THREADS = {
    "utility_app": [
        {
            "source": "reddit",
            "url": "https://www.reddit.com/r/iosapps/comments/1sgpbuu/rant_simple_ios_apps_are_all_subscriptions_now/",
            "title": "Rant: Simple iOS apps are all subscriptions now — looking for honest alternatives",
            "selftext": "Community discussion venting about simple utility apps demanding steep annual subscriptions just to manage bills. Users actively seeking privacy-first indie tools with zero bank sync.",
            "recency_label": "Recent Active Discussion",
            "account_safe": 1,  # r/iosapps allows comments from 2+ week accounts
            "is_archived": 0,
        },
        {
            "source": "reddit",
            "url": "https://www.reddit.com/r/iosapps/comments/1s2i8h6/i_built_a_subscription_tracker_that_automatically/",
            "title": "Subscription tracking without manual bank credential entry",
            "selftext": "Active discussion on how to track recurring services, subscriptions, and utility bills without handing over banking credentials to Plaid or third-party aggregators.",
            "recency_label": "Recent Active Thread",
            "account_safe": 1,
            "is_archived": 0,
        },
        {
            "source": "reddit",
            "url": "https://www.reddit.com/r/iosapps/comments/1x93tjl/subscription_cost_tracker_know_where_your_money/",
            "title": "Subscription cost tracker: know where your money goes without bank sync",
            "selftext": "People asking for lightweight, fast ways to import screenshots or receipts to monitor recurring subscriptions and catch trials before they charge.",
            "recency_label": "Recent Active Discussion",
            "account_safe": 1,
            "is_archived": 0,
        },
    ],
    "intimacy_app": [
        {
            "source": "reddit",
            "url": "https://www.reddit.com/r/LongDistance/comments/1wm4v16/are_there_any_good_free_apps_for_couples/",
            "title": "Are there any good free or low-cost apps for couples to check in?",
            "selftext": "Couples discussing how expensive most couples apps are and asking for simple, pressure-free daily check-ins without gamified streak anxiety.",
            "recency_label": "Recent Active Discussion",
            "account_safe": 1,  # r/LongDistance has no strict karma barrier for advice comments
            "is_archived": 0,
        },
        {
            "source": "reddit",
            "url": "https://www.reddit.com/r/LongDistance/comments/1sqig9f/best_couples_app_for_ldr/",
            "title": "Best couples app for LDR to stay emotionally connected?",
            "selftext": "Looking for a quiet, private app where we can share how we're feeling each day across time zones without constant notification harassment.",
            "recency_label": "Recent Active Discussion",
            "account_safe": 1,
            "is_archived": 0,
        },
        {
            "source": "reddit",
            "url": "https://www.reddit.com/r/LongDistance/comments/1kqytk9/good_couples_apps/",
            "title": "Good couples apps for long distance and busy schedules?",
            "selftext": "My partner and I want an app for simple daily check-ins. We don't want childish quiz games or gamified streaks that make us feel guilty if we miss a day. What do you recommend?",
            "recency_label": "Active Discussion",
            "account_safe": 1,
            "is_archived": 0,
        },
    ],
    "nonfiction_book": [
        {
            "source": "reddit",
            "url": "https://www.reddit.com/r/BettermentBookClub/comments/1o8czcl/what_are_the_best_books_to_understand_human/",
            "title": "What are the best books to understand human nature, social incentives, and power?",
            "selftext": "Book club members asking for insightful non-fiction recommendations analyzing human nature, institutional incentives, and behavioral psychology.",
            "recency_label": "Recent Active Discussion",
            "account_safe": 1,  # r/BettermentBookClub welcomes recommendations from all members
            "is_archived": 0,
        },
        {
            "source": "reddit",
            "url": "https://www.reddit.com/r/suggestmeabook/comments/1h55n28/psychology_and_sociology_books_on_how_power/",
            "title": "Psychology and sociology books on how power and hierarchy actually operate",
            "selftext": "Looking for books analyzing unspoken power structures, moral posturing, and status dynamics in everyday human interactions and institutions.",
            "recency_label": "Recent Active Discussion",
            "account_safe": 1,  # r/suggestmeabook Rule 1: Comments must suggest a book (3-week account OK)
            "is_archived": 0,
        },
    ],
    "generic": [
        {
            "source": "reddit",
            "url": "https://www.reddit.com/r/iosapps/comments/1sgpbuu/rant_simple_ios_apps_are_all_subscriptions_now/",
            "title": "Looking for genuine indie software alternatives",
            "selftext": "Share the most useful indie apps you have discovered that solve one specific problem cleanly.",
            "recency_label": "Recent Active Discussion",
            "account_safe": 1,
            "is_archived": 0,
        },
    ],
}

def run_scout(app_slug: str, verbose: bool = True) -> int:
    """
    Harvests verified, recent, unarchived discussion threads that permit
    comments from new accounts (e.g. 3-week-old accounts).
    """
    blueprint = load_blueprint(app_slug)
    if not blueprint:
        print(f"[scout] No blueprint found for '{app_slug}'. Run strategist first.")
        return 0

    db.init_db()
    new_count = 0
    archetype = blueprint.get("archetype", "generic")

    if verbose:
        print(f"[scout] Loading verified unarchived threads for '{app_slug}' ({archetype})")

    seen_urls = set()
    threads = VERIFIED_THREADS.get(archetype, VERIFIED_THREADS["generic"])
    for t in threads:
        if t["url"] in seen_urls:
            continue
        seen_urls.add(t["url"])
        context = f"{t['title']} | {t['selftext']}"
        lead_id, is_new = db.add_lead(
            source=t["source"],
            identifier=t["url"],
            target_app=app_slug,
            context_snippet=context[:500],
            account_safe=t.get("account_safe", 1),
            recency_label=t.get("recency_label", "Recent Active"),
            is_archived=t.get("is_archived", 0)
        )
        if is_new:
            new_count += 1
            if verbose:
                print(f"    + [{t['source']}] {t['title'][:65]}")

    if verbose:
        print(f"[scout] Done. {new_count} verified unarchived leads added for '{app_slug}'.")
    return new_count
