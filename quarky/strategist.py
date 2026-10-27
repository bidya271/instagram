"""
strategist.py — Analyzes any product & generates GTM blueprints (Whom, Where, How)
"""
import json, os, re, urllib.request, urllib.parse

PROFILES_DIR = os.path.join(os.path.dirname(__file__), "profiles")

ARCHETYPES = {
    "utility_app": {
        "target_audience": "Budget-conscious consumers, tech workers, digital nomads, and people fatigued by subscription leakages.",
        "pain_keywords": ["subscription", "bills", "track", "expense", "budget", "cancel", "overspend", "money", "receipt"],
        "platforms": ["reddit", "threads", "facebook"],
        "subreddits": ["r/personalfinance", "r/frugal", "r/financialindependence", "r/androidapps", "r/iosapps", "r/mildlyinfuriating"],
        "threads_queries": ["subscription tracker app", "forgot to cancel subscription", "best app to track bills"],
        "facebook_groups": ["Personal Finance & Budgeting Hacks", "Frugal Living Tips & Deals", "App Addicts & Lifehacks"],
        "buying_signals": ["recommend an app for tracking", "best app to manage", "struggling to keep track", "alternative to", "cancel forgotten subscriptions"],
        "pitch_tone": "empathetic, practical, zero-fluff, peer-to-peer recommendation",
        "pitch_angle": "Focus on zero-friction screenshot import without giving away bank passwords.",
    },
    "intimacy_app": {
        "target_audience": "Couples in long-distance relationships (LDR), busy partners struggling with daily emotional check-ins, intentional relationship builders.",
        "pain_keywords": ["relationship", "couple", "partner", "connection", "communication", "therapy", "streak", "feelings", "long distance", "ldr"],
        "platforms": ["threads", "reddit", "facebook"],
        "subreddits": ["r/relationship_advice", "r/relationships", "r/dating", "r/Marriage", "r/LongDistance", "r/mentalhealth"],
        "threads_queries": ["couples check-in app", "long distance relationship communication", "relationship habits daily"],
        "facebook_groups": ["Long Distance Relationships (LDR) Support Group", "Couples Seeking Stronger Connection", "Relationship Advice & Marriage Mindset"],
        "buying_signals": ["app for couples", "how to improve relationship", "feel disconnected", "struggling to communicate", "daily check-in for couples"],
        "pitch_tone": "warm, private, gentle, non-judgmental",
        "pitch_angle": "A quiet 30-second daily prompt with no streaks, no gamification, and complete privacy.",
    },
    "nonfiction_book": {
        "target_audience": "Intellectual readers, ambitious operators, founders, psychologists, and thinkers interested in power dynamics, human hypocrisy, and evolutionary sociology.",
        "pain_keywords": ["book", "read", "recommend", "human nature", "power", "psychology", "philosophy", "self-improvement", "hypocrisy", "status games", "machiavellian"],
        "platforms": ["reddit", "threads", "facebook"],
        "subreddits": ["r/suggestmeabook", "r/booksuggestions", "r/philosophy", "r/psychology", "r/selfimprovement", "r/books"],
        "threads_queries": ["books about human nature", "books on power dynamics and psychology", "best non-fiction books 2026"],
        "facebook_groups": ["Nonfiction Book Club & Recommendations", "Psychology, Philosophy & Deep Reads", "Books on Power, Strategy & Human Nature"],
        "buying_signals": ["what book should I read", "recommend a book about", "books like 48 laws of power", "books about human hypocrisy", "good read on power dynamics"],
        "pitch_tone": "intellectual, curiosity-driven, insight-first",
        "pitch_angle": "Highlight the uncomfortable truth about unspoken status dynamics and moral signaling.",
    },
    "generic": {
        "target_audience": "Early adopters, founders, niche communities seeking specialized solutions.",
        "pain_keywords": [],
        "platforms": ["reddit", "threads", "facebook"],
        "subreddits": ["r/Entrepreneur", "r/smallbusiness", "r/startups", "r/SideProject"],
        "threads_queries": ["recommendation for", "alternative to", "software tool for"],
        "facebook_groups": ["Entrepreneur & Founders Network", "Productivity & Tech Tools Discussion"],
        "buying_signals": ["recommend", "alternative to", "help with", "looking for"],
        "pitch_tone": "direct, benefit-first, helpful",
        "pitch_angle": "Demonstrate clear solving of their immediate bottleneck without aggressive sales tactics.",
    },
}

def _detect_archetype(text: str) -> str:
    text_lower = text.lower()
    scores = {}
    for archetype, data in ARCHETYPES.items():
        if archetype == "generic":
            continue
        score = sum(1 for kw in data["pain_keywords"] if kw in text_lower)
        scores[archetype] = score
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "generic"

def _fetch_og_description(url: str) -> str:
    """Try to pull og:description or meta description from a URL."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            html = resp.read(8000).decode("utf-8", errors="ignore")
        m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', html, re.I)
        if not m:
            m = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\'](.*?)["\']', html, re.I)
        return m.group(1).strip() if m else ""
    except Exception:
        return ""

def generate_blueprint(product_input: str, app_slug: str = None) -> dict:
    """
    Accepts a free-text description or URL and returns a GTM blueprint dict,
    also saved to profiles/{slug}.json.
    """
    description = product_input.strip()
    urls = re.findall(r'https?://[^\s]+', product_input)
    product_url = urls[0] if urls else ""
    if product_url:
        og = _fetch_og_description(product_url)
        if og:
            description = f"{product_input} — {og}"

    archetype_key = _detect_archetype(description + " " + (app_slug or ""))
    archetype = ARCHETYPES[archetype_key]

    # Derive slug
    if not app_slug:
        words = re.sub(r"[^a-z0-9 ]", "", description.lower()).split()[:3]
        app_slug = "_".join(words) if words else "product"

    blueprint = {
        "slug": app_slug,
        "input": product_input,
        "product_url": product_url or (f"https://{app_slug}.app" if not product_input.startswith("http") else product_input),
        "description": description,
        "archetype": archetype_key,
        "target_audience": archetype["target_audience"],
        "platforms": archetype["platforms"],
        "subreddits": archetype["subreddits"],
        "threads_queries": archetype.get("threads_queries", []),
        "facebook_groups": archetype.get("facebook_groups", []),
        "buying_signals": archetype["buying_signals"],
        "pitch_tone": archetype["pitch_tone"],
        "pitch_angle": archetype["pitch_angle"],
        "pain_keywords": archetype["pain_keywords"],
    }

    os.makedirs(PROFILES_DIR, exist_ok=True)
    profile_path = os.path.join(PROFILES_DIR, f"{app_slug}.json")
    with open(profile_path, "w") as f:
        json.dump(blueprint, f, indent=2)

    return blueprint

def load_blueprint(app_slug: str):
    path = os.path.join(PROFILES_DIR, f"{app_slug}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

def list_blueprints() -> list[dict]:
    os.makedirs(PROFILES_DIR, exist_ok=True)
    results = []
    for fname in sorted(os.listdir(PROFILES_DIR)):
        if fname.endswith(".json"):
            with open(os.path.join(PROFILES_DIR, fname)) as f:
                try:
                    results.append(json.load(f))
                except Exception:
                    pass
    return results
