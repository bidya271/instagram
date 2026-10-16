#!/usr/bin/env python3
"""
pexels_scout.py - Automated browser-level stock video harvester for @unwrittenrules.b3.
Extracts native vertical 1080x1920 HD and 2160x3840 UHD master footage from Pexels without requiring API keys.
"""

import os
import re
import sys
import json
import random
from pathlib import Path
from curl_cffi import requests

WORKSPACE = Path("/Users/bidya/Documents/side hustle/socials")
FOOTAGE_DIR = WORKSPACE / "assets" / "footage"
USED_DIR = FOOTAGE_DIR / "used"
HISTORY_FILE = FOOTAGE_DIR / "download_history.json"

MOODY_SEARCH_QUERIES = [
    "travel",
    "moody landscape",
    "foggy mountain",
    "rainy night city",
    "ocean waves storm",
    "dark forest mist",
    "cinematic highway night",
    "sunset clouds time lapse",
    "atmospheric street rain"
]

def load_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(list(history), f, indent=2)

def fetch_best_vertical_clip(query=None, target_filename=None):
    FOOTAGE_DIR.mkdir(parents=True, exist_ok=True)
    USED_DIR.mkdir(parents=True, exist_ok=True)
    history = load_history()

    if not query:
        query = random.choice(MOODY_SEARCH_QUERIES)

    encoded_query = requests.utils.quote(query)
    search_url = f"https://www.pexels.com/search/videos/{encoded_query}/?orientation=portrait"
    
    print(f"[*] Browsing Pexels for vertical '{query}' footage via Chrome impersonation...")
    session = requests.Session(impersonate="chrome")
    headers = {
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.pexels.com/",
    }
    
    resp = session.get(search_url, headers=headers)
    if resp.status_code != 200:
        print(f"[!] Pexels search returned HTTP {resp.status_code}")
        return None

    # Find all direct video URLs
    raw_mp4s = re.findall(r'https://videos\.pexels\.com/video-files/(\d+)/[^\s"\'<>]+\.mp4', resp.text)
    full_urls = re.findall(r'https://videos\.pexels\.com/video-files/\d+/[^\s"\'<>]+\.mp4', resp.text)
    
    # Categorize by quality: UHD (2160x3840) > HD (1080x1920)
    uhd_clips = []
    hd_clips = []
    
    for u in set(full_urls):
        match = re.search(r'/video-files/(\d+)/', u)
        if not match:
            continue
        vid_id = match.group(1)
        if vid_id in history:
            continue
            
        if "2160_3840" in u or "1440_2560" in u:
            uhd_clips.append((vid_id, u))
        elif "1080_1920" in u:
            hd_clips.append((vid_id, u))

    candidates = uhd_clips if uhd_clips else hd_clips
    if not candidates:
        print("[!] No new high-definition vertical clips found for this query.")
        return None

    selected_id, selected_url = random.choice(candidates)
    quality_label = "4K UHD" if "2160_3840" in selected_url else "1080p HD"
    print(f"[+] Found {quality_label} vertical video (ID: {selected_id}): {selected_url}")

    if not target_filename:
        clean_q = re.sub(r'[^a-zA-Z0-9]+', '_', query.lower()).strip('_')
        target_filename = f"{clean_q}_{selected_id}.mp4"

    dest_path = FOOTAGE_DIR / target_filename
    print(f"[*] Downloading to {dest_path}...")
    
    video_resp = session.get(selected_url, stream=True)
    if video_resp.status_code != 200:
        print(f"[!] Failed to download video stream (HTTP {video_resp.status_code})")
        return None

    with open(dest_path, "wb") as f:
        for chunk in video_resp.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)

    history.add(selected_id)
    save_history(history)
    print(f"[SUCCESS] Downloaded {dest_path.name} ({dest_path.stat().st_size / (1024*1024):.2f} MB)")
    return str(dest_path)

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else None
    res = fetch_best_vertical_clip(q)
    if res:
        print("Ready:", res)
    else:
        sys.exit(1)
