#!/usr/bin/env python3
"""
produce_reel_033.py - Autonomous Daily Socials Reel Producer for @unwrittenrules.b3
Reel 033: 'The Permission Slip'
Book: 'The Morality Machine' (Chapter 4: Permission Slips)
"""

import os
import sys
import json
import time
import shutil
import urllib.request
import subprocess
from pathlib import Path

WORKSPACE = Path("/Users/bidya/Documents/side hustle/socials")
FOOTAGE_DIR = WORKSPACE / "assets" / "footage"
USED_DIR = FOOTAGE_DIR / "used"
AUDIO_DIR = WORKSPACE / "assets" / "audio"
REELS_DIR = WORKSPACE / "reels"
TEMP_DIR = WORKSPACE / "temp_render_033"
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
        "time": "20:30:00"
    }
}

REEL_SPEC = {
    "num": "033",
    "id": "reel-033",
    "slug": "permission-slip",
    "title": "The Permission Slip",
    "book": "The Morality Machine",
    "chapter": "Chapter 4: Permission Slips",
    "theme": "The Moral Credit Card & The Architecture of Justified Selfishness",
    "scheduledDate": "2026-11-06",
    "voice": "en-US-ChristopherNeural",
    "spoken": "A single act of public virtue doesn't build character. It just buys you a permission slip to be selfish in private.",
    "line1": "a single act of public virtue<br/>doesn't build character.",
    "line2": "it just buys you a permission slip<br/>to be selfish in private.",
    "preferred_clip": "travel_7009541.mp4",
    "bgm_track": "solitude.mp3",
    "bgm_ss": "00:00:44",
    "bgm_volume": 0.22,
    "caption": """The psychological accounting system that authorizes your worst behavior:

You held the door open for a stranger this morning. You tapped your card on a charity kiosk. You let someone merge into your lane during peak rush hour.

Modest acts, all of them. And for the next hour, you felt like a genuinely good person.

This wasn't sentiment. It was accounting.

In psychology, this cognitive distortion is known as moral licensing.

Your brain does not maintain a cumulative savings account of virtue. It operates like a prepaid credit card.

When you perform a visible, socially validated act of goodness, your internal moral monitor clicks upward. The balance feels comfortable.

And a satisfied internal judge stops paying close attention.

So an hour later, when your partner irritates you, you speak with unnecessary sharpness. When a colleague needs assistance, you manufacture reasons to decline. You cut corners, withhold empathy, and indulge petty resentments.

You aren't being malicious. You are simply spending the credit you loaded an hour ago.

The most destructive feature of public virtue isn't the act itself—it's the reset.

Each good deed doesn't make you a better human being. It simply buys you a temporary psychological exemption from the obligation to remain good.

The act of virtue substitutes for virtue itself.

Save this before you spend your next moral credit slip.

Deconstruct self-exoneration, moral credit cards, and the machinery of righteous hypocrisy in 'The Morality Machine'.

#themoralitymachine #darkpsychology #humannature #psychologyfacts #morallicensing #stoicmindset #unwrittenrules #selfawareness #cognitivebias #reels #shorts"""
}

def log(msg):
    print(f"[*] {msg}", flush=True)

def step_1_check_footage():
    log("Step 1: Checking footage in assets/footage/...")
    fresh_clips = [p for p in FOOTAGE_DIR.glob("*.mp4") if "used" not in str(p)]
    log(f"Found {len(fresh_clips)} fresh clips in assets/footage/")
    if len(fresh_clips) < 2:
        log("Fewer than 2 fresh clips exist. Running pexels_scout.py...")
        try:
            subprocess.run([str(WORKSPACE / ".venv" / "bin" / "python"), "pexels_scout.py"], check=True)
            fresh_clips = [p for p in FOOTAGE_DIR.glob("*.mp4") if "used" not in str(p)]
        except Exception as e:
            log(f"Warning: pexels_scout.py could not fetch new clips ({e}), proceeding with available fresh clips.")
    
    preferred_clip = FOOTAGE_DIR / REEL_SPEC["preferred_clip"]
    if not preferred_clip.exists():
        preferred_clip = fresh_clips[0]
    log(f"Selected fresh footage clip: {preferred_clip.name}")
    return preferred_clip

def step_2_audio():
    log("Step 2: Synthesizing & mastering studio audio for Christopher Neural...")
    assets_dir = TEMP_DIR / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    p1 = assets_dir / "p1.mp3"
    p2 = assets_dir / "p2.mp3"
    stitched_voice = assets_dir / "stitched_voice.mp3"
    mastered_voice = assets_dir / "mastered_voice.mp3"
    mixed_audio = assets_dir / "audio.mp3"
    
    tts_bin = str(WORKSPACE / ".venv" / "bin" / "edge-tts")
    
    # Sentence 1: "A single act of public virtue doesn't build character."
    log("Generating Part 1 TTS...")
    subprocess.run([
        tts_bin, f"--voice={REEL_SPEC['voice']}", "--pitch=-3Hz", "--rate=+0%",
        "--text=A single act of public virtue doesn't build character.",
        f"--write-media={p1}"
    ], check=True)
    
    # Sentence 2: "It just buys you a permission slip to be selfish in private."
    log("Generating Part 2 TTS...")
    subprocess.run([
        tts_bin, f"--voice={REEL_SPEC['voice']}", "--pitch=-3Hz", "--rate=+0%",
        "--text=It just buys you a permission slip to be selfish in private.",
        f"--write-media={p2}"
    ], check=True)
    
    # Get duration of Part 1 to calibrate transition timing
    p1_dur_str = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(p1)
    ]).decode().strip()
    p1_dur = float(p1_dur_str)
    
    # Stitch Part 1 and Part 2 with a deliberate 0.70s silence pause and studio mastering chain
    log("Stitching and applying studio mastering chain (130Hz boost, 400Hz scoop, 3500Hz clarity, compressor)...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(p1),
        "-i", str(p2),
        "-filter_complex",
        "[0:a]aresample=48000,aformat=channel_layouts=stereo[a0];"
        "[1:a]aresample=48000,aformat=channel_layouts=stereo[a1];"
        "aevalsrc=0:d=0.70:s=48000:c=stereo[sil];"
        "[a0][sil][a1]concat=n=3:v=0:a=1[stitched];"
        "[stitched]equalizer=f=130:t=q:w=1:g=3.5,equalizer=f=400:t=q:w=1.5:g=-2.5,equalizer=f=3500:t=q:w=1:g=2.5,acompressor=threshold=-18dB:ratio=3:attack=5:release=50[voice_out]",
        "-map", "[voice_out]",
        "-c:a", "mp3", "-b:a", "192k",
        str(mastered_voice)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    dur_str = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(mastered_voice)
    ]).decode().strip()
    voice_dur = float(dur_str)
    total_dur = round(max(9.0, voice_dur + 0.6), 2)
    REEL_SPEC["duration"] = total_dur
    REEL_SPEC["p1_dur"] = p1_dur
    log(f"Part 1: {p1_dur:.2f}s | Mastered voice total: {voice_dur:.2f}s | Reel total duration: {total_dur}s")
    
    # Mix with Preset 2B (Solitude Build: 00:00:44)
    bgm_file = AUDIO_DIR / REEL_SPEC["bgm_track"]
    log(f"Mixing voice with {REEL_SPEC['bgm_track']} (Preset 2B: {REEL_SPEC['bgm_ss']})...")
    filter_complex = (
        f"[0:a]aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={total_dur},volume=1.20[vce];"
        f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={REEL_SPEC['bgm_volume']},"
        f"afade=t=in:st=0:d=0.3,afade=t=out:st={total_dur-1.3}:d=1.3[bgm];"
        "[vce][bgm]amix=inputs=2:duration=first:normalize=0[aout]"
    )
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(mastered_voice),
        "-ss", REEL_SPEC["bgm_ss"], "-t", str(total_dur), "-i", str(bgm_file),
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-t", str(total_dur),
        "-c:a", "mp3", "-b:a", "192k",
        str(mixed_audio)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    return p1, p2, mastered_voice, mixed_audio

def step_3_prepare_background_video(source_clip):
    dur = REEL_SPEC["duration"]
    log(f"Step 3: Preparing {dur}s 1080x1920 background video from {source_clip.name}...")
    bg_video = TEMP_DIR / "assets" / "bg_video.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-ss", "00:00:01", "-t", str(dur), "-i", str(source_clip),
        "-filter_complex",
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=60,settb=AVTB[outv]",
        "-map", "[outv]",
        "-t", str(dur),
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p", "-an",
        str(bg_video)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return bg_video

def step_4_render_hyperframes(audio_file):
    dur = REEL_SPEC["duration"]
    p1_dur = REEL_SPEC.get("p1_dur", 4.08)
    l1_out = round(p1_dur + 0.35, 2)
    l2_in = round(p1_dur + 0.70, 2)
    
    log(f"Step 4: Creating Hyperframes composition and rendering 1080x1920 ({dur}s)...")
    
    with open(TEMP_DIR / "package.json", "w") as f:
        json.dump({"name": "reel-033", "version": "1.0.0", "private": True}, f)

    with open(TEMP_DIR / "hyperframes.json", "w") as f:
        json.dump({
            "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
            "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
            "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
            "media": {"autoProxy": True}
        }, f, indent=2)

    html_code = f"""<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@1,500;1,600&family=Plus+Jakarta+Sans:wght@500;600&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{
        margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #000; color: #fff;
        -webkit-font-smoothing: antialiased;
      }}
      #root {{
        position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #000;
      }}
      .video-bg {{
        position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 1;
      }}
      .cinematic-vignette {{
        position: absolute; inset: 0;
        background: radial-gradient(circle at 50% 38%, transparent 20%, rgba(0,0,0,0.50) 100%),
                    linear-gradient(to bottom, rgba(0,0,0,0.40) 0%, transparent 25%, transparent 70%, rgba(0,0,0,0.75) 100%);
        pointer-events: none; z-index: 2;
      }}
      /* Bottom Attribution Signature: @unwrittenrules.b3 • The Morality Machine */
      .attribution {{
        position: absolute; bottom: 220px; width: 100%; text-align: center;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 22px; font-weight: 600; letter-spacing: 0.14em;
        text-transform: uppercase; color: rgba(255, 255, 255, 0.72);
        text-shadow: 0 2px 10px rgba(0,0,0,0.9); z-index: 10;
      }}
      /* Playfair Display italic serif centered in upper sky (36% from top) */
      .text-stage {{
        position: absolute; top: 36%; left: 80px; right: 80px;
        transform: translateY(-50%);
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        text-align: center; z-index: 10;
      }}
      .quote-line {{
        position: absolute; width: 100%;
        font-family: 'Playfair Display', Georgia, serif;
        font-style: italic;
        font-size: 58px;
        font-weight: 500;
        line-height: 1.36;
        letter-spacing: -0.01em;
        color: #FFFFFF;
        text-shadow: 0 4px 35px rgba(0, 0, 0, 0.95), 0 2px 10px rgba(0, 0, 0, 0.9);
        opacity: 0;
      }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920">
      <video id="bgVideo" src="assets/bg_video.mp4" class="clip video-bg" data-start="0" data-duration="{dur}" autoplay muted loop playsinline></video>
      <div class="cinematic-vignette"></div>

      <div class="text-stage">
        <div class="quote-line" id="line1">{REEL_SPEC['line1']}</div>
        <div class="quote-line" id="line2">{REEL_SPEC['line2']}</div>
      </div>

      <div class="attribution">@unwrittenrules.b3 • {REEL_SPEC['book']}</div>

      <audio id="masterAudio" src="assets/audio.mp3" class="clip" data-start="0" data-duration="{dur}"></audio>
    </div>

    <script>
      const tl = gsap.timeline({{ paused: true }});

      // Line 1: 0.20s -> {l1_out}s
      tl.fromTo("#line1", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power2.out" }}, 0.20);
      tl.to("#line1", {{ opacity: 0, y: -10, duration: 0.35, ease: "power2.in" }}, {l1_out});

      // Line 2: {l2_in}s -> {dur - 0.4}s
      tl.fromTo("#line2", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.50, ease: "power2.out" }}, {l2_in});
      tl.to("#line2", {{ opacity: 0, duration: 0.35, ease: "power2.in" }}, {dur - 0.4});

      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>"""

    with open(TEMP_DIR / "index.html", "w") as f:
        f.write(html_code)

    raw_render = TEMP_DIR / "raw_render.mp4"
    log("Executing Hyperframes render...")
    subprocess.run(
        f"cd \"{TEMP_DIR}\" && npx hyperframes render . --output raw_render.mp4",
        input="\n",
        text=True,
        shell=True,
        check=True
    )

    final_video = TEMP_DIR / "final_reel_033.mp4"
    log("Encoding faststart 1080x1920 MP4 with audio mux...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(raw_render),
        "-i", str(audio_file),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-t", str(dur),
        "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "192k",
        str(final_video)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    thumbnail = TEMP_DIR / "thumbnail.jpg"
    subprocess.run([
        "ffmpeg", "-y",
        "-ss", "00:00:02",
        "-i", str(final_video),
        "-vframes", "1",
        str(thumbnail)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return final_video, thumbnail

def step_5_archive(final_video, thumbnail, mixed_audio, source_clip):
    target_dir = REELS_DIR / f"{REEL_SPEC['id']}-{REEL_SPEC['slug']}"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    archived_video = target_dir / "video.mp4"
    archived_thumb = target_dir / "thumbnail.jpg"
    archived_audio = target_dir / "audio.mp3"
    
    shutil.copy(str(final_video), str(archived_video))
    shutil.copy(str(thumbnail), str(archived_thumb))
    shutil.copy(str(mixed_audio), str(archived_audio))
    
    with open(target_dir / "script.txt", "w") as f:
        f.write(REEL_SPEC["spoken"] + "\n")
        
    with open(target_dir / "caption.txt", "w") as f:
        f.write(REEL_SPEC["caption"] + "\n")
        
    meta = {
        "id": REEL_SPEC["id"],
        "num": REEL_SPEC["num"],
        "slug": REEL_SPEC["slug"],
        "title": REEL_SPEC["title"],
        "book": REEL_SPEC["book"],
        "chapter": REEL_SPEC["chapter"],
        "theme": REEL_SPEC["theme"],
        "duration": REEL_SPEC["duration"],
        "mediaUrl": f"https://github.com/bidya271/instagram/releases/download/media-vault/reel_{REEL_SPEC['num']}.mp4",
        "script": REEL_SPEC["spoken"],
        "bgm": REEL_SPEC["bgm_track"],
        "voice": REEL_SPEC["voice"],
        "footage": source_clip.name,
        "caption": REEL_SPEC["caption"],
        "scheduledDue": {
            "instagram": f"{REEL_SPEC['scheduledDate']}T{CHANNELS['instagram']['time']}+01:00",
            "youtube": f"{REEL_SPEC['scheduledDate']}T{CHANNELS['youtube']['time']}+01:00",
            "tiktok": f"{REEL_SPEC['scheduledDate']}T{CHANNELS['tiktok']['time']}+01:00"
        },
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "pending_upload"
    }
    with open(target_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    log(f"Archived final package into {target_dir}")
    return target_dir, archived_video, meta

def step_6_github_upload(archived_video):
    log("Step 6: Uploading to GitHub media-vault release...")
    asset_name = f"reel_{REEL_SPEC['num']}.mp4"
    temp_asset = Path(f"/tmp/{asset_name}")
    shutil.copy(str(archived_video), str(temp_asset))
    cmd = f"gh release upload media-vault \"{temp_asset}\" --clobber -R bidya271/instagram"
    log(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)
    if temp_asset.exists():
        temp_asset.unlink()
    public_url = f"https://github.com/bidya271/instagram/releases/download/media-vault/{asset_name}"
    log(f"Permanent Media URL: {public_url}")
    return public_url

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

def step_7_buffer_dispatch(public_url, target_dir, meta):
    log("Step 7: Scheduling to Buffer across YouTube, Instagram, and TikTok...")
    post_ids = {}
    title = REEL_SPEC["title"]
    caption = REEL_SPEC["caption"]

    for chan_name, info in CHANNELS.items():
        due_at = f"{REEL_SPEC['scheduledDate']}T{info['time']}+01:00"
        text = caption
        if chan_name == "youtube":
            text = text.replace("#reels", "#shorts")

        log(f"Scheduling to {chan_name.upper()} ({info['id']}) at {due_at}...")
        post_id, err = buffer_create_post(info["id"], due_at, text, public_url, title, info["service"])
        if post_id:
            log(f"[✓] {chan_name.upper()} scheduled successfully: {post_id}")
            post_ids[chan_name] = post_id
        else:
            log(f"[!] Error scheduling {chan_name.upper()}: {err}")
            post_ids[chan_name] = f"error: {err}"
        time.sleep(1.2)

    meta["bufferPosts"] = post_ids
    all_ok = all(not str(v).startswith("error:") for v in post_ids.values())
    meta["status"] = "scheduled_in_buffer" if all_ok else "partial_buffer_schedule"
    with open(target_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    return post_ids

def step_8_move_footage_and_cleanup(source_clip):
    log("Step 8: Moving source clip to assets/footage/used/ and cleaning temp...")
    USED_DIR.mkdir(parents=True, exist_ok=True)
    dest = USED_DIR / source_clip.name
    shutil.move(str(source_clip), str(dest))
    log(f"Moved {source_clip.name} to {dest}")
    
    CLEANUP_TRASH.mkdir(parents=True, exist_ok=True)
    if TEMP_DIR.exists():
        trash_dest = CLEANUP_TRASH / f"temp_render_033_{int(time.time())}"
        shutil.move(str(TEMP_DIR), str(trash_dest))
        log(f"Moved temp render dir to {trash_dest}")

def step_9_update_manifest(meta):
    log("Step 9: Updating scheduled_2weeks_manifest.json...")
    manifest_path = WORKSPACE / "scheduled_2weeks_manifest.json"
    if manifest_path.exists():
        try:
            with open(manifest_path) as f:
                manifest_data = json.load(f)
            manifest_data = [item for item in manifest_data if item.get("id") != REEL_SPEC["id"]]
            manifest_entry = {
                "id": REEL_SPEC["id"],
                "slug": REEL_SPEC["slug"],
                "title": REEL_SPEC["title"],
                "book": REEL_SPEC["book"],
                "scheduledDate": REEL_SPEC["scheduledDate"],
                "mediaUrl": meta["mediaUrl"],
                "bufferPosts": meta.get("bufferPosts", {}),
                "audioTrack": REEL_SPEC["bgm_track"],
                "footageClip": meta["footage"],
                "caption": REEL_SPEC["caption"],
                "status": meta["status"],
                "duration": REEL_SPEC["duration"],
                "spoken_hook": REEL_SPEC["spoken"]
            }
            manifest_data.append(manifest_entry)
            with open(manifest_path, "w") as f:
                json.dump(manifest_data, f, indent=2)
            log("Manifest successfully updated.")
        except Exception as e:
            log(f"Warning: could not update manifest: {e}")

if __name__ == "__main__":
    log("Starting Autonomous Reel 033 Production...")
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    source_clip = step_1_check_footage()
    p1, p2, mast_v, mix_a = step_2_audio()
    bg_video = step_3_prepare_background_video(source_clip)
    final_video, thumbnail = step_4_render_hyperframes(mix_a)
    target_dir, archived_video, meta = step_5_archive(final_video, thumbnail, mix_a, source_clip)
    public_url = step_6_github_upload(archived_video)
    step_7_buffer_dispatch(public_url, target_dir, meta)
    step_8_move_footage_and_cleanup(source_clip)
    step_9_update_manifest(meta)
    
    log("[SUCCESS] Reel 033 Production & Multi-Platform Distribution Complete!")
