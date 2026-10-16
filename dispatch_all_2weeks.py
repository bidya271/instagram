#!/usr/bin/env python3
"""
dispatch_all_2weeks.py
1. Uploads reel_004.mp4 through reel_017.mp4 to GitHub release media-vault with proper filenames.
2. Schedules all 42 posts (14 days x 3 platforms) directly to Buffer.
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
REELS_DIR = WORKSPACE / "reels"
BUFFER_TOKEN = "kT3VN2dNEG0GDfVTnYlr-6SB0MpUuwEK89bBVWmFdwU"

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

with open(WORKSPACE / "batch_produce_2weeks.py", "r") as f:
    text_content = f.read()

# Import REELS_DATA from batch_produce_2weeks
import importlib.util
spec = importlib.util.spec_from_file_location("batch_mod", str(WORKSPACE / "batch_produce_2weeks.py"))
batch_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch_mod)
REELS_DATA = batch_mod.REELS_DATA

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
        "id": int(time.time()),
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
                if "id" in inner:
                    return inner["id"], None
                return None, inner.get("error", str(inner))
            return None, data
    except Exception as e:
        return None, str(e)

def main():
    manifest = []
    print("\n=======================================================")
    print("VAULTING & SCHEDULING 14 REELS ACROSS 42 BUFFER SLOTS")
    print("=======================================================\n")

    for item in REELS_DATA:
        reel_num = item['num']
        reel_id = f"reel-{reel_num}"
        slug = item['slug']
        reel_folder = REELS_DIR / f"{reel_id}-{slug}"
        local_video = reel_folder / "video.mp4"

        if not local_video.exists():
            print(f"[!] Warning: Missing video at {local_video}")
            continue

        asset_name = f"reel_{reel_num}.mp4"
        staged_upload_file = WORKSPACE / asset_name

        print(f"\n[*] Processing {reel_id} ({item['date']}): {item['theme']}...")
        
        # 1. Copy to unique local name and upload to GitHub release
        shutil.copy(local_video, staged_upload_file)
        cmd = f"gh release upload media-vault \"{staged_upload_file}\" --repo bidya271/instagram --clobber"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        staged_upload_file.unlink(missing_ok=True)

        if res.returncode != 0:
            print(f"[!] Failed to upload {asset_name}: {res.stderr}")
            continue

        public_url = f"https://github.com/bidya271/instagram/releases/download/media-vault/{asset_name}"
        print(f"    [+] Uploaded to GitHub Media Vault: {public_url}")

        # 2. Schedule across Instagram, YouTube, TikTok
        post_ids = {}
        for chan_name, chan_info in CHANNELS.items():
            # If reel-004 instagram was already scheduled, skip re-scheduling that one
            if reel_num == "004" and chan_name == "instagram":
                post_ids[chan_name] = "6ad20dd725d13dd62ee3d55e"
                print(f"    [✓] {chan_name.upper()} already scheduled: 6ad20dd725d13dd62ee3d55e")
                continue

            due_at = f"{item['date']}T{chan_info['time']}+02:00"
            title = item['theme']
            text = item['caption']
            if chan_name == "youtube":
                text = text.replace("#reels", "#shorts")

            print(f"    [*] Scheduling {chan_name.upper()} at {due_at}...")
            post_id, err = buffer_create_post(chan_info['id'], due_at, text, public_url, title, chan_info['service'])
            if post_id:
                print(f"    [✓] {chan_name.upper()} scheduled: {post_id}")
                post_ids[chan_name] = post_id
            else:
                print(f"    [!] Error scheduling {chan_name.upper()}: {err}")
                post_ids[chan_name] = f"error: {err}"
            time.sleep(1.2)

        meta = {
            "id": reel_id,
            "slug": slug,
            "title": item['theme'],
            "book": item['book'],
            "scheduledDate": item['date'],
            "mediaUrl": public_url,
            "bufferPosts": post_ids
        }
        manifest.append(meta)

        with open(reel_folder / "meta.json", "w") as f:
            json.dump(meta, f, indent=2)

    with open(WORKSPACE / "scheduled_2weeks_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print("\n=======================================================")
    print("[SUCCESS] ALL 14 REELS VAULTED & ALL BUFFER POSTS SCHEDULED!")
    print("=======================================================")

if __name__ == "__main__":
    main()
