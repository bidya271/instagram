#!/usr/bin/env python3
"""
produce_reel_019.py - Autonomous Socials Reel Producer for @unwrittenrules.b3.
Produces Reel 019: 'The Asymmetry of Grace / The Fundamental Attribution Error'
From: 'The Ideology of Hypocrisy' (Chapter 2)
"""

import os
import sys
import json
import time
import shutil
import subprocess
import urllib.request
from pathlib import Path

WORKSPACE = Path("/Users/bidya/Documents/side hustle/socials")
FOOTAGE_DIR = WORKSPACE / "assets" / "footage"
USED_DIR = FOOTAGE_DIR / "used"
AUDIO_DIR = WORKSPACE / "assets" / "audio"
REELS_DIR = WORKSPACE / "reels"
TEMP_DIR = WORKSPACE / "temp_render_019"
CLEANUP_TRASH = Path(os.path.expanduser("~/.Trash/socials_temp_cleanup"))

BUFFER_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN", "kT3VN2dNEG0GDfVTnYlr-6SB0MpUuwEK89bBVWmFdwU")

CHANNELS = {
    "instagram": {
        "id": "6ad106c2778b240e2f1b3b33",
        "service": "instagram",
        "time": "17:00:00"
    },
    "youtube": {
        "id": "6ad106eb778b240e2f1b44d4",
        "service": "youtube",
        "time": "18:25:00"
    },
    "tiktok": {
        "id": "6ad106fe778b240e2f1b46ee",
        "service": "tiktok",
        "time": "22:33:00"
    }
}

REEL_CONFIG = {
    "num": "019",
    "id": "reel-019",
    "slug": "asymmetry-of-grace",
    "date": "2026-10-31",
    "book": "The Ideology of Hypocrisy",
    "theme": "The Asymmetry of Grace / The Fundamental Attribution Error",
    "footage": "moody_landscape_27546122.mp4",
    "bgm": "solitude_full.mp3",
    "audioPreset": "Preset 2A (Solitude Intro)",
    "beats": {
        "b1": "You judge everyone else by their actions, but you judge yourself by your intentions.",
        "b2": "When someone else fails, you call it a character flaw. When you make the same mistake, you blame your circumstances.",
        "b3_head": "You grant yourself an infinite reservoir of context, while denying that grace to the room.",
        "b3_sub": "The double standard is not an ethical flaw. It is your ego's primary survival weapon."
    },
    "caption": """You judge everyone else by their actions, but you judge yourself by your intentions.

When another person makes a mistake, cuts into your lane, or misses a deadline, your brain makes an instantaneous calculation: you decide they are incompetent, selfish, or reckless. You treat their behavior as an unvarnished reflection of their character.

When you make the exact same mistake, your cognitive machinery performs an instantaneous about-face. You point to the brutal weight of circumstance. You were exhausted. You had an emergency. You were dealing with impossible constraints.

You grant yourself an infinite reservoir of context, nuance, and grace, while denying that very same grace to everyone around you.

Social psychologists call this the Actor-Observer Asymmetry. It isn't a conscious moral failure; it is an automated biological shield evolved to protect your self-esteem while judging competitors.

Save this before you judge someone today.

Explore the evolution of tactical deception and double standards in 'The Ideology of Hypocrisy'.

#unwrittenrules #theideologyofhypocrisy #darkpsychology #psychologyfacts #humanbehavior #cognitivebias #stoicmindset #selfawareness #reels #shorts"""
}

def run_cmd(cmd, desc):
    print(f"[*] {desc}...")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] Error in {desc}:\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}")
        raise RuntimeError(f"Step failed: {desc}")
    return res.stdout

def get_dur(file_path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)
    ])
    return float(out.strip())

def buffer_create_post(channel_id, due_at, text, video_url, title, service):
    metadata = {}
    if service == "instagram":
        metadata = {"instagram": {"type": "reel", "shouldShareToFeed": True}}
    elif service == "youtube":
        metadata = {"youtube": {"categoryId": "22", "title": f"{title} #shorts"}}
    elif service == "tiktok":
        metadata = {"tiktok": {"title": title}}

    payload = {
        "jsonrpc": "2.0",
        "id": int(time.time() * 1000),
        "method": "tools/call",
        "params": {
            "name": "create_post",
            "arguments": {
                "channelId": channel_id,
                "schedulingType": "automatic",
                "mode": "customScheduled",
                "dueAt": due_at,
                "text": text,
                "assets": [
                    {
                        "video": {
                            "url": video_url,
                            "metadata": {
                                "title": title
                            }
                        }
                    }
                ],
                "metadata": metadata
            }
        }
    }

    req = urllib.request.Request(
        "https://mcp.buffer.com/mcp",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {BUFFER_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read().decode("utf-8")
            res_obj = json.loads(data)
            if "result" in res_obj and "content" in res_obj["result"]:
                inner = json.loads(res_obj["result"]["content"][0]["text"])
                return inner.get("id"), None
            return None, data
    except Exception as e:
        return None, str(e)

if __name__ == "__main__":
    print(f"Reel 019 Config ready: {REEL_CONFIG['id']}")
