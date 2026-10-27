#!/usr/bin/env python3
"""
produce_reel_027.py - Autonomous Socials Reel Producer for @unwrittenrules.b3
Produces Reel 027: 'The Geography of Envy'
Book: 'Status: The Currency of Envy' (Chapter 7: Why We Compare / The Proximate Peer Comparison Trap)
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
TEMP_DIR = WORKSPACE / "temp_render_027"
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
    "num": "027",
    "id": "reel-027",
    "slug": "geography-of-envy",
    "title": "The Geography of Envy",
    "book": "Status: The Currency of Envy",
    "chapter": "Chapter 7: Why We Compare",
    "theme": "Upward Social Comparison & Proximate Peer Rivalry",
    "duration": 7.00,
    "scheduledDate": "2026-10-31",
    "spoken": "You do not envy the billionaire on a yacht. You envy the peer who started at the exact same desk.",
    "line1": "you do not envy the billionaire on a yacht.",
    "line2": "you envy the peer who started at the exact same desk.",
    "preferred_clip": "rainy_night_city_30284434.mp4",
    "bgm_track": "solitude.mp3",
    "bgm_ss": "00:00:00",
    "bgm_volume": 0.20,
    "caption": """The unspoken geometry of human envy:

You do not lose sleep over the lifestyle of a tech billionaire on the other side of the planet. Their wealth is so completely disconnected from your reality that your nervous system categorizes them as an abstraction.

You lose sleep over the person who sat two cubicles down from you.

The college roommate who bought the house in the hills. The high school peer who secured the executive title. The colleague who joined the company at the exact same grade and was promoted six months earlier.

Aristotle called this the potter's curse: potters do not envy kings, potters envy potters.

Envy is never triggered by distance. Envy is triggered by proximity.

When someone starts at the exact same line as you and pulls ahead, their success destroys your excuses. It forces you to confront the gap between your potential and your reality.

Save this before you compare your path to anyone today.

Deconstruct social comparison and the architecture of peer rivalry in 'Status: The Currency of Envy'.

#currencyofenvy #status #darkpsychology #humanbehavior #stoicmindset #unwrittenrules #peerpressure #envy #reels #shorts #psychologyfacts"""
}


def log(msg):
    print(f"[*] {msg}")


def step_1_check_footage():
    log("Step 1: Checking footage in assets/footage/...")
    fresh_clips = [p for p in FOOTAGE_DIR.glob("*.mp4") if "used" not in str(p)]
    log(f"Found {len(fresh_clips)} fresh clips in assets/footage/")
    if len(fresh_clips) < 2:
        log("Fewer than 2 fresh clips exist. Running pexels_scout.py...")
        subprocess.run([str(WORKSPACE / ".venv" / "bin" / "python"), "pexels_scout.py"], check=True)
        fresh_clips = [p for p in FOOTAGE_DIR.glob("*.mp4") if "used" not in str(p)]
    
    preferred_clip = FOOTAGE_DIR / REEL_SPEC["preferred_clip"]
    if not preferred_clip.exists():
        preferred_clip = fresh_clips[0]
    log(f"Selected fresh footage clip: {preferred_clip.name}")
    return preferred_clip


def step_2_audio():
    log("Step 2: Synthesizing & mastering studio audio...")
    assets_dir = TEMP_DIR / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    raw_voice = assets_dir / "raw_voice.mp3"
    mastered_voice = assets_dir / "mastered_voice.mp3"
    mixed_audio = assets_dir / "audio.mp3"
    
    # 1. Edge TTS
    log("Generating Christopher Neural speech...")
    subprocess.run([
        str(WORKSPACE / ".venv" / "bin" / "edge-tts"),
        "--voice=en-US-ChristopherNeural",
        "--pitch=-4Hz",
        "--rate=+5%",
        f"--text={REEL_SPEC['spoken']}",
        f"--write-media={raw_voice}"
    ], check=True)
    
    # 2. Studio Mastering Chain from REEL_PRODUCTION_STANDARD.md
    log("Applying studio mastering chain: 130Hz boost, 400Hz scoop, 3500Hz clarity, compressor...")
    subprocess.run([
        "ffmpeg", "-y", "-i", str(raw_voice),
        "-af", "equalizer=f=130:t=q:w=1:g=3.5,equalizer=f=400:t=q:w=1.5:g=-2.5,equalizer=f=3500:t=q:w=1:g=2.5,acompressor=threshold=-18dB:ratio=3:attack=5:release=50",
        "-b:a", "192k", str(mastered_voice)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 3. Audio Mixing with Preset 2A (Solitude Intro)
    bgm_file = AUDIO_DIR / REEL_SPEC["bgm_track"]
    log(f"Mixing with {REEL_SPEC['bgm_track']} (Preset 2A)...")
    filter_complex = (
        "[0:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.18[vce];"
        f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={REEL_SPEC['bgm_volume']},"
        "afade=t=in:st=0:d=0.2,afade=t=out:st=5.8:d=1.2[bgm];"
        "[vce][bgm]amix=inputs=2:duration=first:normalize=0[aout]"
    )
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(mastered_voice),
        "-ss", REEL_SPEC["bgm_ss"], "-t", "7.00", "-i", str(bgm_file),
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-t", "7.00",
        "-c:a", "mp3", "-b:a", "192k",
        str(mixed_audio)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    return raw_voice, mastered_voice, mixed_audio


def step_3_prepare_background_video(source_clip):
    log("Step 3: Preparing 7.00s 1080x1920 background video...")
    bg_video = TEMP_DIR / "assets" / "bg_video.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-ss", "00:00:01", "-t", "7.00", "-i", str(source_clip),
        "-filter_complex",
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=60,settb=AVTB[outv]",
        "-map", "[outv]",
        "-t", "7.00",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p", "-an",
        str(bg_video)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return bg_video


def step_4_render_hyperframes(audio_file):
    log("Step 4: Creating Hyperframes composition and rendering 1080x1920...")
    with open(TEMP_DIR / "package.json", "w") as f:
        json.dump({"name": "reel-027", "version": "1.0.0", "private": True}, f)

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
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;1,500;1,600&family=Plus+Jakarta+Sans:wght@500;600&display=swap" rel="stylesheet">
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
        background: radial-gradient(circle at 50% 38%, transparent 20%, rgba(0,0,0,0.45) 100%),
                    linear-gradient(to bottom, rgba(0,0,0,0.3) 0%, transparent 25%, transparent 70%, rgba(0,0,0,0.7) 100%);
        pointer-events: none; z-index: 2;
      }}
      /* Bottom Attribution Signature: @unwrittenrules.b3 • Current Book Title */
      .attribution {{
        position: absolute; bottom: 220px; width: 100%; text-align: center;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 24px; font-weight: 600; letter-spacing: 0.14em;
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
    <div id="root" data-composition-id="main" data-start="0" data-duration="7.0" data-width="1080" data-height="1920">
      <video id="bgVideo" src="assets/bg_video.mp4" class="clip video-bg" data-start="0" data-duration="7.0" autoplay muted loop playsinline></video>
      <div class="cinematic-vignette"></div>

      <div class="text-stage">
        <div class="quote-line" id="line1">{REEL_SPEC['line1']}</div>
        <div class="quote-line" id="line2">{REEL_SPEC['line2']}</div>
      </div>

      <div class="attribution">@unwrittenrules.b3 • {REEL_SPEC['book']}</div>

      <audio id="masterAudio" src="assets/audio.mp3" class="clip" data-start="0" data-duration="7.0"></audio>
    </div>

    <script>
      const tl = gsap.timeline({{ paused: true }});

      // Line 1: 0.15s -> 2.65s (Spoken: 0.00s -> 2.09s, silence 2.09s -> 3.12s)
      tl.fromTo("#line1", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power2.out" }}, 0.15);
      tl.to("#line1", {{ opacity: 0, y: -10, duration: 0.35, ease: "power2.in" }}, 2.65);

      // Line 2: 3.10s -> 6.65s (Spoken: 3.12s -> 6.00s)
      tl.fromTo("#line2", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power2.out" }}, 3.10);
      tl.to("#line2", {{ opacity: 0, duration: 0.30, ease: "power2.in" }}, 6.65);

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
        shell=True,
        check=True
    )

    final_video = TEMP_DIR / "final_reel_027.mp4"
    log("Encoding faststart 1080x1920 MP4 with audio mux...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(raw_render),
        "-i", str(audio_file),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-t", "7.00",
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


def step_5_archive(final_video, thumbnail, raw_voice, mastered_voice, mixed_audio, source_clip):
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
        "voice": "en-US-ChristopherNeural",
        "footage": source_clip.name,
        "caption": REEL_SPEC["caption"],
        "scheduledDue": {
            "instagram": f"{REEL_SPEC['scheduledDate']}T{CHANNELS['instagram']['time']}+02:00",
            "youtube": f"{REEL_SPEC['scheduledDate']}T{CHANNELS['youtube']['time']}+02:00",
            "tiktok": f"{REEL_SPEC['scheduledDate']}T{CHANNELS['tiktok']['time']}+02:00"
        },
        "status": "pending_upload"
    }
    with open(target_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    log(f"Archived final package into {target_dir}")
    return target_dir, archived_video, meta


def step_6_github_upload(archived_video):
    log("Step 6: Uploading to GitHub media-vault release...")
    asset_name = f"reel_{REEL_SPEC['num']}.mp4"
    cmd = f"gh release upload media-vault \"{archived_video}#{asset_name}\" --clobber -R bidya271/instagram"
    log(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)
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
        due_at = f"{REEL_SPEC['scheduledDate']}T{info['time']}+02:00"
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
        trash_dest = CLEANUP_TRASH / f"temp_render_027_{int(time.time())}"
        shutil.move(str(TEMP_DIR), str(trash_dest))
        log(f"Moved temp render dir to {trash_dest}")


if __name__ == "__main__":
    log("Starting Autonomous Reel 027 Production...")
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    source_clip = step_1_check_footage()
    raw_v, mast_v, mix_a = step_2_audio()
    bg_video = step_3_prepare_background_video(source_clip)
    final_video, thumbnail = step_4_render_hyperframes(mix_a)
    target_dir, archived_video, meta = step_5_archive(final_video, thumbnail, raw_v, mast_v, mix_a, source_clip)
    public_url = step_6_github_upload(archived_video)
    step_7_buffer_dispatch(public_url, target_dir, meta)
    step_8_move_footage_and_cleanup(source_clip)
    
    log("[SUCCESS] Reel 027 Production & Multi-Platform Distribution Complete!")
