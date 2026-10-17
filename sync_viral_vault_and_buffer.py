#!/usr/bin/env python3
"""
sync_viral_vault_and_buffer.py
1. Uploads rendered 7-second viral videos (reel_004.mp4 - reel_017.mp4) to GitHub Media Vault.
2. Updates scheduled posts on Buffer (Instagram, YouTube, TikTok) via edit_post so they point to the new 7s videos and verified captions.
3. Updates scheduled_2weeks_manifest.json.
"""

import os
import sys
import json
import time
import shutil
import subprocess
import urllib.request
from pathlib import Path

from viral_script_engine import VIRAL_REELS

WORKSPACE = Path("/Users/bidya/Documents/side hustle/socials")
REELS_DIR = WORKSPACE / "reels"
MANIFEST_FILE = WORKSPACE / "scheduled_2weeks_manifest.json"
BUFFER_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN", "kT3VN2dNEG0GDfVTnYlr-6SB0MpUuwEK89bBVWmFdwU")

CHANNELS = {
    "instagram": {
        "id": "6ad106c2778b240e2f1b3b33",
        "service": "instagram"
    },
    "youtube": {
        "id": "6ad106eb778b240e2f1b44d4",
        "service": "youtube"
    },
    "tiktok": {
        "id": "6ad106fe778b240e2f1b46ee",
        "service": "tiktok"
    }
}

def call_buffer_mcp(method_name, arguments):
    payload = {
        "jsonrpc": "2.0",
        "id": int(time.time() * 1000),
        "method": "tools/call",
        "params": {
            "name": method_name,
            "arguments": arguments
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
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read().decode("utf-8")
        res_obj = json.loads(data)
        if "result" in res_obj and "content" in res_obj["result"]:
            inner = json.loads(res_obj["result"]["content"][0]["text"])
            return inner
        return res_obj

def buffer_edit_post(post_id, text, video_url, title, service):
    metadata = {}
    if service == "instagram":
        metadata = {"instagram": {"type": "reel", "shouldShareToFeed": True}}
    elif service == "youtube":
        metadata = {"youtube": {"categoryId": "22", "title": f"{title} #shorts"}}
    elif service == "tiktok":
        metadata = {"tiktok": {"title": title}}

    arguments = {
        "postId": post_id,
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

    try:
        res = call_buffer_mcp("edit_post", arguments)
        if isinstance(res, dict) and "id" in res:
            return res["id"], None
        return None, res.get("error", str(res))
    except Exception as e:
        return None, str(e)

def sync_all():
    print("\n=======================================================")
    print("SYNCING 7-SECOND VIRAL REELS TO GITHUB VAULT & BUFFER")
    print("=======================================================\n")

    with open(MANIFEST_FILE, "r") as f:
        manifest = json.load(f)

    manifest_by_num = {item["id"].replace("reel-", ""): item for item in manifest}

    for item in VIRAL_REELS:
        num = item["num"]
        reel_id = f"reel-{num}"
        slug = item["slug"]
        video_path = REELS_DIR / f"{reel_id}-{slug}" / "video.mp4"

        # Fallback to older folder name if slug changed
        if not video_path.exists():
            matched_dirs = list(REELS_DIR.glob(f"{reel_id}-*"))
            if matched_dirs:
                video_path = matched_dirs[0] / "video.mp4"

        if not video_path.exists():
            print(f"[!] Warning: video not found for {reel_id} at {video_path}")
            continue

        asset_name = f"reel_{num}.mp4"
        staged_file = WORKSPACE / asset_name
        shutil.copy(video_path, staged_file)

        print(f"[*] Uploading {reel_id} ({item['rule_badge']}) to GitHub Media Vault...")
        cmd = f"gh release upload media-vault \"{staged_file}\" --repo bidya271/instagram --clobber"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        staged_file.unlink(missing_ok=True)

        if res.returncode != 0:
            print(f"    [!] GitHub upload error: {res.stderr}")
            continue

        public_url = f"https://github.com/bidya271/instagram/releases/download/media-vault/{asset_name}"
        print(f"    [+] Vaulted: {public_url}")

        # Update Buffer posts if already scheduled
        man_entry = manifest_by_num.get(num)
        if man_entry and "bufferPosts" in man_entry:
            posts = man_entry["bufferPosts"]
            for chan_name, info in CHANNELS.items():
                post_id = posts.get(chan_name, "")
                if post_id and not str(post_id).startswith("error:"):
                    print(f"    [*] Updating Buffer {chan_name.upper()} post {post_id}...")
                    caption = item["caption"]
                    if chan_name == "youtube":
                        caption = caption.replace("#unwrittenrules", "#shorts")

                    eid, err = buffer_edit_post(post_id, caption, public_url, item["title"], info["service"])
                    if eid:
                        print(f"    [✓] {chan_name.upper()} post updated successfully!")
                    else:
                        print(f"    [!] Failed to update {chan_name.upper()}: {err}")
                    time.sleep(1.0)

        # Update manifest record
        if man_entry:
            man_entry["title"] = item["title"]
            man_entry["book"] = item["book"]
            man_entry["rule_badge"] = item["rule_badge"]
            man_entry["duration"] = 7.0
            man_entry["caption"] = item["caption"]
            man_entry["spoken_hook"] = item["spoken_hook"]
            man_entry["mediaUrl"] = public_url

    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2)

    print("\n=======================================================")
    print("[SUCCESS] ALL 7-SECOND VIRAL REELS VAULTED & BUFFER UPDATED!")
    print("=======================================================\n")

if __name__ == "__main__":
    sync_all()
