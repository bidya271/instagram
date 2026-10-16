#!/usr/bin/env python3
"""
auto_refill_queue.py
Maintains a full 10-post scheduled pipeline in Buffer across Instagram, YouTube Shorts, and TikTok.
Whenever an active post publishes and opens a slot in the Buffer queue (or if the plan limit is upgraded),
this script automatically pushes the next pre-rendered reel from the GitHub Media Vault into the calendar.
"""

import os
import sys
import json
import time
import urllib.request
from pathlib import Path

WORKSPACE = Path("/Users/bidya/Documents/side hustle/socials")
MANIFEST_FILE = WORKSPACE / "scheduled_2weeks_manifest.json"
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

ORGANIZATION_ID = "6ad0f05d0aa16fcee71cbdb4"

def get_scheduled_count(channel_id):
    try:
        res = call_buffer_mcp("list_posts", {
            "channelIds": [channel_id],
            "organizationId": ORGANIZATION_ID,
            "status": ["scheduled"]
        })
        if isinstance(res, dict) and "edges" in res:
            return len(res["edges"])
        elif isinstance(res, list):
            return len(res)
    except Exception as e:
        print(f"    [!] Error checking scheduled count for channel {channel_id}: {e}")
    return 10  # fallback assume full

def buffer_create_post(channel_id, due_at, text, video_url, title, service):
    metadata = {}
    if service == "instagram":
        metadata = {"instagram": {"type": "reel", "shouldShareToFeed": True}}
    elif service == "youtube":
        metadata = {"youtube": {"categoryId": "22", "title": f"{title} #shorts"}}
    elif service == "tiktok":
        metadata = {"tiktok": {"title": title}}

    arguments = {
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

    try:
        res = call_buffer_mcp("create_post", arguments)
        if isinstance(res, dict) and "id" in res:
            return res["id"], None
        return None, res.get("error", str(res))
    except Exception as e:
        return None, str(e)

def refill_queue():
    if not MANIFEST_FILE.exists():
        print(f"[!] Manifest not found at {MANIFEST_FILE}")
        return

    with open(MANIFEST_FILE, "r") as f:
        manifest = json.load(f)

    print("\n=======================================================")
    print("BUFFER AUTO-REFILL QUEUE CONTROLLER")
    print("=======================================================\n")

    # Check status of each channel
    channel_counts = {}
    for chan_name, info in CHANNELS.items():
        count = get_scheduled_count(info["id"])
        channel_counts[chan_name] = count
        print(f"[*] Channel {chan_name.upper()}: {count}/10 scheduled posts active.")

    changes_made = False

    for item in manifest:
        reel_id = item["id"]
        due_date = item["scheduledDate"]
        title = item["title"]
        caption = item.get("caption", "")
        media_url = item["mediaUrl"]
        buffer_posts = item.setdefault("bufferPosts", {})

        # Check if this reel needs scheduling on any channel
        needs_push = False
        for chan_name, info in CHANNELS.items():
            post_id = buffer_posts.get(chan_name, "")
            if not post_id or str(post_id).startswith("error:"):
                # Slot needed
                if channel_counts[chan_name] < 10:
                    needs_push = True
                    break

        if not needs_push:
            continue

        print(f"\n[+] Found unqueued reel ready to push: {reel_id} ({due_date}) - '{title}'")
        for chan_name, info in CHANNELS.items():
            current_id = buffer_posts.get(chan_name, "")
            if current_id and not str(current_id).startswith("error:"):
                print(f"    [✓] {chan_name.upper()} already scheduled: {current_id}")
                continue

            if channel_counts[chan_name] >= 10:
                print(f"    [-] {chan_name.upper()} queue full (10/10). Waiting for older post to publish.")
                continue

            due_at = f"{due_date}T{info['time']}+02:00"
            text = caption
            if chan_name == "youtube":
                text = text.replace("#reels", "#shorts")

            print(f"    [*] Pushing to {chan_name.upper()} at {due_at}...")
            new_id, err = buffer_create_post(info["id"], due_at, text, media_url, title, info["service"])
            if new_id:
                print(f"    [✓] SUCCESS: {chan_name.upper()} scheduled ID {new_id}")
                buffer_posts[chan_name] = new_id
                channel_counts[chan_name] += 1
                changes_made = True
            else:
                print(f"    [!] FAILED: {chan_name.upper()}: {err}")
                buffer_posts[chan_name] = f"error: {err}"
            time.sleep(1.2)

        # Update status
        all_scheduled = all(not str(v).startswith("error:") for v in buffer_posts.values())
        item["status"] = "scheduled_in_buffer" if all_scheduled else "vaulted_awaiting_buffer_slot"

    if changes_made:
        with open(MANIFEST_FILE, "w") as f:
            json.dump(manifest, f, indent=2)
        print("\n[✓] Manifest updated with new post IDs!")
    else:
        print("\n[-] All channels are at maximum capacity (10/10) or all reels already queued.")

if __name__ == "__main__":
    refill_queue()
