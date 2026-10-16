import re
import random
import time
import json
from pathlib import Path
from curl_cffi import requests

FOOTAGE_DIR = Path("assets/footage")
USED_DIR = FOOTAGE_DIR / "used"
HISTORY_FILE = FOOTAGE_DIR / "download_history.json"

FOOTAGE_DIR.mkdir(parents=True, exist_ok=True)
USED_DIR.mkdir(parents=True, exist_ok=True)

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

QUERIES = [
    ("foggy_mountain", "foggy mountain vertical"),
    ("dark_forest", "dark forest mist vertical"),
    ("ocean_storm", "ocean waves dark storm vertical"),
    ("night_traffic", "night city traffic lights vertical"),
    ("moody_waterfall", "dark moody waterfall vertical"),
    ("snow_pines", "winter snow forest pines vertical"),
    ("minimal_architecture", "brutalist architecture minimalist vertical"),
    ("desert_dunes", "desert sand dunes wind vertical"),
    ("coastal_cliffs", "dramatic ocean cliffs fog vertical"),
    ("atmospheric_rain", "rain street puddle reflection vertical"),
    ("cloudy_sky", "dark stormy clouds time lapse vertical"),
    ("deep_canyon", "deep mountain canyon mist vertical")
]

history = load_history()
session = requests.Session(impersonate="chrome")
headers = {
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.pexels.com/"
}

harvested = []

for slug, query in QUERIES:
    # Check if we already have enough fresh files in assets/footage
    existing_fresh = [f for f in FOOTAGE_DIR.glob("*.mp4") if f.is_file() and f.parent != USED_DIR]
    if len(existing_fresh) >= 15:
        print(f"[*] Already have {len(existing_fresh)} fresh footage files. Stopping harvester.")
        break

    print(f"\n[*] Searching Pexels for: '{query}'...")
    encoded_query = requests.utils.quote(query)
    search_url = f"https://www.pexels.com/search/videos/{encoded_query}/?orientation=portrait"
    
    try:
        resp = session.get(search_url, headers=headers, timeout=15)
        if resp.status_code != 200:
            print(f"[!] HTTP {resp.status_code}")
            continue

        full_urls = re.findall(r'https://videos\.pexels\.com/video-files/\d+/[^\s"\'<>]+\.mp4', resp.text)
        candidates = []
        for u in set(full_urls):
            match = re.search(r'/video-files/(\d+)/', u)
            if not match:
                continue
            vid_id = match.group(1)
            if vid_id in history:
                continue
            if "2160_3840" in u or "1440_2560" in u or "1080_1920" in u:
                candidates.append((vid_id, u))

        if not candidates:
            print("[!] No matching fresh candidates.")
            continue

        # Prefer UHD/4K over 1080p
        candidates.sort(key=lambda x: ("2160_3840" in x[1] or "1440_2560" in x[1]), reverse=True)
        vid_id, url = candidates[0]
        quality = "4K/UHD" if ("2160_3840" in url or "1440_2560" in url) else "1080p"
        print(f"[+] Selected {quality} video {vid_id}...")

        target_file = FOOTAGE_DIR / f"{slug}_{vid_id}.mp4"
        dl = session.get(url, stream=True, timeout=30)
        if dl.status_code == 200:
            with open(target_file, "wb") as f:
                for chunk in dl.iter_content(chunk_size=131072):
                    if chunk:
                        f.write(chunk)
            history.add(vid_id)
            save_history(history)
            harvested.append(target_file)
            print(f"[SUCCESS] Downloaded {target_file.name} ({target_file.stat().st_size / (1024*1024):.2f} MB)")
            time.sleep(1.5)
        else:
            print(f"[!] Download failed: HTTP {dl.status_code}")

    except Exception as e:
        print(f"[!] Error: {e}")

print(f"\n[DONE] Total newly harvested: {len(harvested)}")
