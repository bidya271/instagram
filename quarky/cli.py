"""
cli.py — Command-line interface for Quarky
Usage: python3 -m quarky [command] [options]
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from quarky import db
from quarky.strategist import generate_blueprint, list_blueprints

USAGE = """
Quarky — B2C GTM & Lead Acquisition Engine
===========================================

Commands:
  serve                   Start the web dashboard (http://localhost:7777)
  analyze <product>       Analyze a product and generate a GTM blueprint
  analyze <product> --slug <slug>
  scout [--app <slug>]    Run the scout engine (harvests leads from Reddit)
  draft [--app <slug>]    Draft pitches for all new leads
  run [--app <slug>]      Full loop: scout + draft (repeatable)
  stats                   Show pipeline stats
  profiles                List all saved product profiles
  help                    Show this message

Examples:
  python3 -m quarky analyze "TrackSub - subscription tracker app, no bank linking"
  python3 -m quarky analyze "TrackSub" --slug tracksub
  python3 -m quarky scout --app tracksub
  python3 -m quarky draft --app tracksub
  python3 -m quarky run --app tracksub
  python3 -m quarky serve
"""

def _get_arg(args, flag, position=None):
    if flag in args:
        idx = args.index(flag)
        if idx + 1 < len(args):
            return args[idx + 1]
    if position is not None and position < len(args):
        return args[position]
    return None

def main():
    args = sys.argv[1:]
    if not args or args[0] in ("help", "--help", "-h"):
        print(USAGE)
        return

    cmd = args[0]
    db.init_db()

    if cmd == "serve":
        from quarky.server import run
        run()

    elif cmd == "analyze":
        product = _get_arg(args, "--product", 1)
        if not product:
            print("Usage: quarky analyze <product description or URL> [--slug <slug>]")
            sys.exit(1)
        slug = _get_arg(args, "--slug")
        blueprint = generate_blueprint(product, slug)
        print(f"\n✅ Blueprint generated for '{blueprint['slug']}'")
        print(f"   Archetype : {blueprint['archetype']}")
        print(f"   Platforms : {', '.join(blueprint['platforms'])}")
        print(f"   Subreddits: {', '.join(blueprint['subreddits'][:3])}...")
        print(f"   Tone      : {blueprint['pitch_tone']}")
        print(f"   Saved to  : quarky/profiles/{blueprint['slug']}.json")

    elif cmd == "scout":
        app_slug = _get_arg(args, "--app")
        if not app_slug:
            profiles = list_blueprints()
            if not profiles:
                print("No profiles found. Run 'quarky analyze' first.")
                sys.exit(1)
            app_slug = profiles[0]["slug"]
            print(f"No --app specified. Using '{app_slug}'.")
        from quarky.scout import run_scout
        run_scout(app_slug)

    elif cmd == "draft":
        app_slug = _get_arg(args, "--app")
        if not app_slug:
            profiles = list_blueprints()
            if not profiles:
                print("No profiles. Run 'quarky analyze' first.")
                sys.exit(1)
            app_slug = profiles[0]["slug"]
        from quarky.writer import run_draft
        run_draft(app_slug)

    elif cmd == "run":
        app_slug = _get_arg(args, "--app")
        if not app_slug:
            profiles = list_blueprints()
            if not profiles:
                print("No profiles. Run 'quarky analyze' first.")
                sys.exit(1)
            app_slug = profiles[0]["slug"]
        from quarky.scout import run_scout
        from quarky.writer import run_draft
        print(f"[run] Full pipeline for '{app_slug}'")
        run_scout(app_slug)
        run_draft(app_slug)
        stats = db.get_stats()
        print(f"\n📊 Stats: {stats['total_leads']} leads | {stats['pending']} pending | {stats['sent']} sent")

    elif cmd == "stats":
        stats = db.get_stats()
        print(f"\n📊 Quarky Pipeline Stats")
        print(f"   Total leads  : {stats['total_leads']}")
        print(f"   Pending pitches: {stats['pending']}")
        print(f"   Sent         : {stats['sent']}")

    elif cmd == "profiles":
        profiles = list_blueprints()
        if not profiles:
            print("No profiles yet. Run 'quarky analyze <product>'.")
        for p in profiles:
            print(f"  • {p['slug']:20} [{p['archetype']}] — {p['description'][:60]}")

    else:
        print(f"Unknown command: {cmd}")
        print(USAGE)
        sys.exit(1)

if __name__ == "__main__":
    main()
