#!/usr/bin/env python3
"""
produce_reel_030_v2.py - High-Retention Emotional & Scenic Reel Producer
Reel 030: 'The Rat Race Illusion'
Vocal Style: Slow, vulnerable British intimate narration (RyanNeural) matching viral TikTok benchmark
Music: Warm emotional acoustic piano + gentle water stream ambience
Footage: Pure flowing forest water stream
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
TEMP_DIR = WORKSPACE / "temp_render_030_v2"

REEL_SPEC = {
    "num": "030",
    "id": "reel-030",
    "slug": "the-rat-race-treadmill",
    "title": "The Rat Race Illusion",
    "book": "The Architecture of Greed",
    "chapter": "Chapter 8: The Endless Treadmill",
    "theme": "Rat Race Burnout & Emotional Relief",
    "duration": 7.50,
    "scheduledDate": "2026-11-03",
    "voice": "en-GB-RyanNeural",
    "voice_rate": "-10%",
    "voice_pitch": "-1Hz",
    "spoken": "The rat race has no finish line... The only prize for running faster... is a faster treadmill.",
    "line1": "the rat race has no finish line...",
    "line2": "the only prize for running faster, is a faster treadmill.",
    "footage_clip": "forest_water_stream_39528850.mp4",
    "caption": """The hardest truth of modern ambition:

We were told to keep running. We were told that if we just sacrificed enough weekends and survived the exhaustion, we would finally reach peace.

The truth? The rat race has no finish line.

The only prize for running faster is a faster treadmill.

Save this before you spend another year sprinting toward a mirage.

Protect your peace. That's the only victory that actually counts.

Deconstruct the psychology of infinite scoreboards in 'The Architecture of Greed'.

#thearchitectureofgreed #unwrittenrules #ratrace #innerpeace #stoicmindset #burnout #peaceofmind #reels #shorts #motivation"""
}

def log(msg):
    print(f"[*] {msg}")

def step_1_audio():
    log("Step 1: Generating vulnerable, slow narration and ambient acoustic mix...")
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    assets_dir = TEMP_DIR / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    raw_voice = assets_dir / "raw_voice.mp3"
    mastered_voice = assets_dir / "mastered_voice.mp3"
    mixed_audio = assets_dir / "audio.mp3"
    
    # 1. Edge-TTS with RyanNeural, slow and intimate
    subprocess.run([
        str(WORKSPACE / ".venv" / "bin" / "edge-tts"),
        f"--voice={REEL_SPEC['voice']}",
        f"--rate={REEL_SPEC['voice_rate']}",
        f"--pitch={REEL_SPEC['voice_pitch']}",
        f"--text={REEL_SPEC['spoken']}",
        f"--write-media={raw_voice}"
    ], check=True)
    
    # 2. Warm acoustic EQ: soft highs, warm gentle mids, light compression (intimate mic proximity)
    subprocess.run([
        "ffmpeg", "-y", "-i", str(raw_voice),
        "-af", "equalizer=f=120:t=q:w=1:g=2.5,equalizer=f=2800:t=q:w=1.2:g=1.5,acompressor=threshold=-18dB:ratio=2.2:attack=15:release=120",
        "-b:a", "192k", str(mastered_voice)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Probe duration
    dur_str = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(mastered_voice)
    ]).decode().strip()
    voice_dur = float(dur_str)
    total_dur = max(7.5, voice_dur + 0.8)
    REEL_SPEC["duration"] = round(total_dur, 2)
    log(f"Voice duration: {voice_dur:.2f}s | Total video duration set to: {REEL_SPEC['duration']}s")
    
    # 3. Mix with Snowfall acoustic piano at intimate low volume (0.22) with smooth fadeout
    bgm_file = AUDIO_DIR / "snowfall.mp3"
    filter_complex = (
        f"[0:a]aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={REEL_SPEC['duration']},volume=1.25[vce];"
        f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.22,"
        f"afade=t=in:st=0:d=0.5,afade=t=out:st={REEL_SPEC['duration']-1.2}:d=1.2[bgm];"
        "[vce][bgm]amix=inputs=2:duration=first:normalize=0[aout]"
    )
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(mastered_voice),
        "-ss", "00:00:15", "-t", str(REEL_SPEC["duration"]), "-i", str(bgm_file),
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-t", str(REEL_SPEC["duration"]),
        "-c:a", "mp3", "-b:a", "192k",
        str(mixed_audio)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    return mixed_audio

def step_2_footage():
    log("Step 2: Preparing vertical forest water stream clip...")
    source_clip = FOOTAGE_DIR / REEL_SPEC["footage_clip"]
    bg_video = TEMP_DIR / "assets" / "bg_video.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-ss", "00:00:02", "-t", str(REEL_SPEC["duration"]), "-i", str(source_clip),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-an",
        str(bg_video)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return source_clip

def step_3_render():
    log("Step 3: Building composition with organic typography & subtle vignette...")
    dur = REEL_SPEC["duration"]
    # Line 1 shows from 0.2s to 3.4s, Line 2 from 3.7s to dur-0.4s
    html_code = f"""<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>{REEL_SPEC['title']}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Playfair+Display:ital,wght@1,500;1,600&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
    <style>
      * {{ box-sizing: border-box; margin: 0; padding: 0; }}
      body, html {{ width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
      .video-bg {{ position: absolute; top: 0; left: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 1; }}
      .cinematic-vignette {{
        position: absolute; top: 0; left: 0; width: 1080px; height: 1920px;
        background: radial-gradient(circle at center, rgba(0,0,0,0.15) 0%, rgba(0,0,0,0.55) 100%),
                    linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0.05) 45%, rgba(0,0,0,0.60) 100%);
        z-index: 2;
      }}
      .attribution {{
        position: absolute; bottom: 220px; left: 0; width: 100%;
        text-align: center;
        font-family: 'Inter', -apple-system, sans-serif;
        font-size: 20px;
        font-weight: 600;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: rgba(255, 255, 255, 0.85);
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.9);
        z-index: 10;
      }}
      .text-stage {{
        position: absolute; top: 38%; left: 90px; right: 90px;
        transform: translateY(-50%);
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        text-align: center; z-index: 10;
      }}
      .quote-line {{
        position: absolute; width: 100%;
        font-family: 'Playfair Display', Georgia, serif;
        font-style: italic;
        font-size: 60px;
        font-weight: 500;
        line-height: 1.38;
        letter-spacing: -0.01em;
        color: #FFFFFF;
        text-shadow: 0 4px 35px rgba(0, 0, 0, 0.95), 0 2px 12px rgba(0, 0, 0, 0.9);
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

      // Line 1: 0.25s -> 3.30s
      tl.fromTo("#line1", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power2.out" }}, 0.25);
      tl.to("#line1", {{ opacity: 0, y: -8, duration: 0.35, ease: "power2.in" }}, 3.30);

      // Line 2: 3.65s -> {dur - 0.4}s
      tl.fromTo("#line2", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power2.out" }}, 3.65);
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
        shell=True,
        check=True
    )

    final_video = TEMP_DIR / "final_reel_030.mp4"
    log("Encoding faststart 1080x1920 MP4 with audio mux...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(raw_render),
        "-i", str(TEMP_DIR / "assets" / "audio.mp3"),
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

def step_4_archive(final_video, thumbnail, source_clip):
    log("Step 4: Archiving output into reels/reel-030-invisible-finish-line/...")
    target_dir = REELS_DIR / "reel-030-invisible-finish-line"
    target_dir.mkdir(parents=True, exist_ok=True)

    archived_video = target_dir / "video.mp4"
    archived_thumb = target_dir / "thumbnail.jpg"
    archived_audio = target_dir / "audio.mp3"
    archived_script = target_dir / "script.txt"
    archived_caption = target_dir / "caption.txt"
    meta_json = target_dir / "meta.json"

    shutil.copy(str(final_video), str(archived_video))
    shutil.copy(str(thumbnail), str(archived_thumb))
    shutil.copy(str(TEMP_DIR / "assets" / "audio.mp3"), str(archived_audio))

    with open(archived_script, "w") as f:
        f.write(REEL_SPEC["spoken"] + "\n")

    with open(archived_caption, "w") as f:
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
        "scheduledDate": REEL_SPEC["scheduledDate"],
        "voice": REEL_SPEC["voice"],
        "footage": source_clip.name,
        "spoken": REEL_SPEC["spoken"],
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    with open(meta_json, "w") as f:
        json.dump(meta, f, indent=2)

    log(f"[SUCCESS] Reel 030 v2 produced at {archived_video}")
    return archived_video

if __name__ == "__main__":
    step_1_audio()
    source_clip = step_2_footage()
    final_video, thumbnail = step_3_render()
    step_4_archive(final_video, thumbnail, source_clip)
