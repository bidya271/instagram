"""
writer.py — Context-aware 1-to-1 conversion copywriter
Generates natural, high-converting peer replies tailored to each platform.
Optionally integrates with an LLM (Claude or Ollama) when available.
"""
import subprocess, os, json, random, re
from quarky import db
from quarky.strategist import load_blueprint

# ── Template library per archetype and platform ──────────────────────────────

TEMPLATES = {
    "utility_app": {
        "reddit": [
            "Saw your post about {pain_snippet}. I got fed up with bank-linking apps breaking and built {app_name} ({product_url}) — it lets you track recurring subscriptions without Plaid or bank passwords by importing screenshots. Free to try if you want to test it.",
            "Your frustration with bank-linking apps and surprise renewals is super relatable. Built {app_name} ({product_url}) specifically for this: zero bank logins, on-device privacy, and simple screenshot import. Might save you the headache.",
        ],
        "threads": [
            "Relating hard to your post on {pain_snippet}. We built {app_name} ({product_url}) to solve this without giving up bank logins. Just import screenshots or receipts directly.",
        ],
        "facebook": [
            "Regarding {pain_snippet} — if you don't want to link sensitive bank logins, {app_name} ({product_url}) tracks all recurring bills securely on-device with receipt & screenshot import.",
        ],
        "generic": [
            "Saw your post on {pain_snippet}. {app_name} was made exactly for this: clean tracking without invasive bank permissions. You can check it out here: {product_url}",
        ],
    },
    "intimacy_app": {
        "reddit": [
            "I came across your post about {pain_snippet} and wanted to mention {app_name} ({product_url}). It was built for exactly what you described: a quiet, 30-second daily check-in with no gamified streaks, no points, and total on-device privacy.",
            "Not sure if this helps, but {app_name} ({product_url}) was created specifically for {pain_snippet}. The whole idea is intentional daily emotional connection without feeling like therapy homework.",
        ],
        "threads": [
            "Relating to your post on {pain_snippet}. We built {app_name} ({product_url}) as a calm, 30-sec daily check-in for couples who want genuine connection without gamified streak anxiety. Free on iOS.",
        ],
        "facebook": [
            "For anyone dealing with {pain_snippet} — {app_name} ({product_url}) is a quiet, pressure-free daily check-in app designed specifically for busy and long-distance partners.",
        ],
        "generic": [
            "Saw your post on {pain_snippet}. {app_name} ({product_url}) provides a gentle, private way for couples to check in daily without notifications harassing you.",
        ],
    },
    "nonfiction_book": {
        "reddit": [
            "Based on what you're asking about {pain_snippet} — you might find {app_name} ({product_url}) genuinely eye-opening. It breaks down the unspoken status dynamics and moral signaling behind everyday decisions.",
            "If {pain_snippet} is what you're wrestling with, {app_name} ({product_url}) is worth picking up. It cuts through polite pretense and analyzes power incentives directly with rigorous research.",
        ],
        "threads": [
            "If you want a deep dive into {pain_snippet}, check out {app_name} ({product_url}). Covers how status games and hidden hypocrisy actually drive social behavior.",
        ],
        "facebook": [
            "Great discussion on {pain_snippet}. I recommend reading {app_name} ({product_url}) — it provides a rigorous, counter-intuitive look at human power dynamics and moral posturing.",
        ],
        "generic": [
            "Regarding {pain_snippet} — {app_name} ({product_url}) offers a fascinating analysis on power dynamics, hypocrisy, and status games.",
        ],
    },
    "generic": {
        "generic": [
            "Saw your post about {pain_snippet} — {app_name} might be exactly what you need. Key thing it does: {key_feature}. {product_url}",
        ],
    },
}

_LLM_CHECKED = False
_LLM_CMD = None

def _get_llm_cmd():
    global _LLM_CHECKED, _LLM_CMD
    if _LLM_CHECKED:
        return _LLM_CMD
    _LLM_CHECKED = True
    import shutil
    if shutil.which("claude"):
        try:
            r = subprocess.run(["claude", "-p", "hi"], capture_output=True, text=True, timeout=3)
            if r.returncode == 0:
                _LLM_CMD = "claude"
                return _LLM_CMD
        except Exception:
            pass
    if shutil.which("ollama"):
        try:
            r = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=2)
            if "llama" in r.stdout.lower():
                _LLM_CMD = "ollama"
                return _LLM_CMD
        except Exception:
            pass
    return None

def _clean_snippet(context: str) -> str:
    """Extract a clean, natural phrase describing the user's problem."""
    parts = context.split("|")
    title = parts[0].strip()
    title = re.sub(r'^@[a-zA-Z0-9_]+:\s*', '', title)
    title = re.sub(r'^[A-Za-z0-9\s&]+:\s*', '', title)
    title = title.rstrip('?.! ')
    return title[:90]

def _llm_pitch(context: str, blueprint: dict, lead: dict):
    llm_tool = _get_llm_cmd()
    if not llm_tool:
        return None

    product_url = blueprint.get("product_url", blueprint.get("input", ""))
    app_name = blueprint.get("slug", "our tool").replace("_", " ").title()

    prompt = f"""You are an empathetic, authentic peer reply copywriter.
Write a single, natural, helpful comment replying to this discussion post:

PLATFORM: {lead.get('source', 'web')}
PROSPECT POST:
{context[:500]}

PRODUCT: {blueprint.get('description', '')} ({app_name})
PRODUCT URL: {product_url}
TONE: {blueprint.get('pitch_tone', 'helpful')}
ARCHETYPE: {blueprint.get('archetype', 'generic')}

Rules:
- 2 to 3 sentences maximum
- Sound like a real helpful human who built/discovered this, NOT a marketer or bot
- Mention the product URL naturally: {product_url}
- Zero emojis, zero hashtags, zero sales buzzwords

Reply:"""

    cmd = ["claude", "-p", prompt] if llm_tool == "claude" else ["ollama", "run", "llama3", prompt]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None

def draft_pitch(lead: dict, blueprint: dict) -> str:
    archetype = blueprint.get("archetype", "generic")
    source = lead.get("source", "generic")

    # Try LLM first
    llm_result = _llm_pitch(lead.get("context_snippet", ""), blueprint, lead)
    if llm_result:
        return llm_result

    # Fallback to template library
    arch_templates = TEMPLATES.get(archetype, TEMPLATES["generic"])
    platform_templates = arch_templates.get(source, arch_templates.get("generic", TEMPLATES["generic"]["generic"]))

    pain_snippet = _clean_snippet(lead.get("context_snippet", ""))
    app_name = blueprint.get("slug", "this product").replace("_", " ").title()
    app_desc = blueprint.get("description", blueprint.get("slug", "this app"))[:80]

    product_url = blueprint.get("product_url", "")
    if not product_url or not product_url.startswith("http"):
        if blueprint.get("input", "").startswith("http"):
            product_url = blueprint["input"]
        elif blueprint.get("slug") == "tracksub":
            product_url = "https://tracksub.app"
        elif blueprint.get("slug") == "feelsright":
            product_url = "https://feelsright.me"
        elif "book" in blueprint.get("slug", ""):
            product_url = "https://thehiddengames.com"
        else:
            product_url = f"https://{blueprint.get('slug', 'product')}.app"

    words = app_desc.split()
    key_feature = " ".join(words[:8]) if len(words) > 4 else app_desc

    template = random.choice(platform_templates)
    return template.format(
        pain_snippet=pain_snippet,
        app_name=app_name,
        app_desc=app_desc,
        key_feature=key_feature,
        product_url=product_url,
    )

def run_draft(app_slug: str, verbose: bool = True) -> int:
    """
    Drafts pitches for all 'new' leads for the given app slug.
    Returns number of outbox items created.
    """
    db.init_db()
    blueprint = load_blueprint(app_slug)
    if not blueprint:
        print(f"[writer] No blueprint for '{app_slug}'.")
        return 0

    leads = db.get_leads(target_app=app_slug, status="new")
    if verbose:
        print(f"[writer] Drafting pitches for {len(leads)} leads ({app_slug})...")

    count = 0
    for lead in leads:
        pitch = draft_pitch(lead, blueprint)
        db.add_outbox(lead["lead_id"], app_slug, pitch)
        db.update_lead_status(lead["lead_id"], "drafted")
        db.log_activity(lead["lead_id"], "pitch_drafted", f"len={len(pitch)}")
        count += 1
        if verbose:
            print(f"  ✓ drafted [{lead['source']}]: {lead['context_snippet'][:50]}...")

    if verbose:
        print(f"[writer] {count} pitches drafted for '{app_slug}'.")
    return count
