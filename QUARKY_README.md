# Quarky — B2C GTM & Lead Acquisition Engine

## Quick Start

```bash
# 1. Analyze your product (creates a GTM blueprint)
python3 -m quarky analyze "TrackSub – subscription tracker app. No bank linking, AI screenshot import." --slug tracksub

# 2. Run the full pipeline (scout leads + draft pitches)
python3 -m quarky run --app tracksub

# 3. Open the web dashboard to review & approve pitches
python3 -m quarky serve
# → http://localhost:7777
```

## Commands

| Command | Description |
|---|---|
| `python3 -m quarky analyze "<product>"` | Generate a GTM blueprint for a product |
| `python3 -m quarky scout --app <slug>` | Harvest leads from Reddit |
| `python3 -m quarky draft --app <slug>` | Draft pitches for new leads |
| `python3 -m quarky run --app <slug>` | Scout + draft in one go |
| `python3 -m quarky serve` | Start the web dashboard |
| `python3 -m quarky stats` | Show pipeline stats |
| `python3 -m quarky profiles` | List saved product profiles |

## Workflow

1. **Analyze** → saves blueprint to `quarky/profiles/<slug>.json`
2. **Scout** → finds high-intent Reddit posts matching your buying signals
3. **Draft** → generates a 1-to-1 pitch for each lead  
4. **Review** → approve or reject in the dashboard at `localhost:7777`
5. **Push** → opens the thread in Chrome and copies pitch to clipboard; just paste

## LLM-Enhanced Pitches

Quarky auto-detects `claude` CLI (Claude Code) or `ollama` for personalized pitches.  
If neither is available, it falls back to high-quality templates.

Install Claude Code: https://claude.ai/code  
Install Ollama: https://ollama.com

## Directory Structure

```
quarky/
├── quarky/
│   ├── profiles/          # GTM blueprints per product
│   ├── web/               # Dashboard UI (HTML/CSS/JS)
│   ├── db.py              # SQLite ORM
│   ├── strategist.py      # Product analysis + archetype detection
│   ├── scout.py           # Reddit lead harvester
│   ├── writer.py          # Pitch copywriter
│   ├── pusher.py          # Chrome bridge + clipboard
│   ├── server.py          # Local API server (port 7777)
│   └── cli.py             # CLI entry point
├── data/
│   └── quarky.db          # SQLite database (auto-created)
└── README.md
```

## Requirements

- Python 3.9+ (no third-party packages required)
- macOS: pbcopy + Google Chrome for 1-click push
- Linux: xclip or xsel for clipboard
- Optional: `claude` CLI or `ollama` for LLM-enhanced pitches
