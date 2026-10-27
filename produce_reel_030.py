#!/usr/bin/env python3
"""
produce_reel_030.py - Autonomous Socials Reel Producer for @unwrittenrules.b3
Produces Reel 030: 'The Invisible Finish Line'
Theme: The Rat Race Illusion & Stoic Sovereignty
Book: 'The Architecture of Greed'
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
TEMP_DIR = WORKSPACE / "temp_render_030"
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
    "num": "030",
    "id": "reel-030",
    "slug": "invisible-finish-line",
    "title": "The Invisible Finish Line",
    "book": "The Architecture of Greed",
    "chapter": "Chapter 8: The Endless Treadmill",
    "theme": "The Rat Race Illusion & Inner Peace",
    "duration": 7.00,
    "scheduledDate": "2026-11-03",
    "spoken": "The hardest truth about the rat race is that there is no finish line. The goalposts were designed to move the moment you cross them.",
    "line1": "the hardest truth about the rat race, is that there is no finish line.",
    "line2": "the goalposts were designed to move, the moment you cross them.",
    "preferred_clip": "calm_sunset_ocean_32539931.mp4",
    "bgm_track": "snowfall.mp3",
    "bgm_ss": "00:00:15",
    "bgm_volume": 0.22,
    "caption": """The unspoken illusion of modern ambition:

We were conditioned to believe that life is a structured race with a definitive finish line. If you just sacrifice your twenties, endure the 60-hour workweeks, and hit the next arbitrary milestone, you will finally arrive at peace.

Here is the truth no corporate ladder ever tells you: there is no finish line.

The system was engineered so that every achievement simply qualifies you for higher anxiety, bigger targets, and a heavier set of invisible chains. The goalposts do not stay still—they move the exact second your foot crosses the line.

The only real leverage in an infinite rat race is having the courage to step off the track.

Peace is not a prize waiting at the end of exhaustion. It is a decision you make today.

Save this before you spend another year sprinting toward a mirage.

Deconstruct the psychology of infinite scoreboards and artificial scarcity in 'The Architecture of Greed'.

#thearchitectureofgreed #unwrittenrules #ratrace #innerpeace #stoicmindset #burnout #peaceofmind #sovereignty #reels #shorts #motivation"""
}

def log(msg):
    print(f"[*] {msg}")

def step_1_check_footage():
    log("Step 1: Checking footage in assets/footage/...")
    preferred_clip = FOOTAGE_DIR / REEL_SPEC["preferred_clip"]
    if not preferred_clip.exists():
        fresh_clips = [p for p in FOOTAGE_DIR.glob("*.mp4") if "used" not in str(p)]
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
    
    log("Generating Christopher Neural speech...")
    subprocess.run([
        str(WORKSPACE / ".venv" / "bin" / "edge-tts"),
        "--voice=en-US-ChristopherNeural",
        "--pitch=-3Hz",
        "--rate=+5%",
        f"--text={REEL_SPEC['spoken']}",
        f"--write-media={raw_voice}"
    ], check=True)
    
    log("Applying studio mastering chain...")
    subprocess.run([
        "ffmpeg", "-y", "-i", str(raw_voice),
        "-af", "equalizer=f=130:t=q:w=1:g=3.5,equalizer=f=400:t=q:w=1.5:g=-2.5,equalizer=f=3500:t=q:w=1:g=2.5,acompressor=threshold=-18dB:ratio=3:attack=5:release=50",
        "-b:a", "192k", str(mastered_voice)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    bgm_file = AUDIO_DIR / REEL_SPEC["bgm_track"]
    log(f"Mixing with {REEL_SPEC['bgm_track']}...")
    filter_complex = (
        "[0:a]aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur=7.0,volume=1.20[vce];"
        f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={REEL_SPEC['bgm_volume']},"
        "afade=t=in:st=0:d=0.3,afade=t=out:st=5.8:d=1.2[bgm];"
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
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-an",
        str(bg_video)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return bg_video

def step_4_render_reel(audio_file):
    log("Step 4: Building Hyperframes composition and rendering...")
    html_code = f"""<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>{REEL_SPEC['title']}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Playfair+Display:ital,wght@1,500;1,600&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
    <style>
      * {{ box-sizing: border-box; margin: 0; padding: 0; }}
      body, html {{ width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
      .video-bg {{ position: absolute; top: 0; left: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 1; }}
      .cinematic-vignette {{
        position: absolute; top: 0; left: 0; width: 1080px; height: 1920px;
        background: radial-gradient(circle at center, rgba(0,0,0,0.18) 0%, rgba(0,0,0,0.60) 100%),
                    linear-gradient(180deg, rgba(0,0,0,0.40) 0%, rgba(0,0,0,0.10) 40%, rgba(0,0,0,0.65) 100%);
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

      // Line 1: 0.15s -> 3.35s
      tl.fromTo("#line1", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.40, ease: "power2.out" }}, 0.15);
      tl.to("#line1", {{ opacity: 0, y: -10, duration: 0.30, ease: "power2.in" }}, 3.35);

      // Line 2: 3.55s -> 6.65s
      tl.fromTo("#line2", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.40, ease: "power2.out" }}, 3.55);
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

    final_video = TEMP_DIR / "final_reel_030.mp4"
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

def step_5_archive_output(final_video, thumbnail, source_clip):
    log("Step 5: Archiving output into reels/reel-030-invisible-finish-line/...")
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
        "footage": source_clip.name,
        "bgm_track": REEL_SPEC["bgm_track"],
        "spoken": REEL_SPEC["spoken"],
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    with open(meta_json, "w") as f:
        json.dump(meta, f, indent=2)

    # Move source clip to used
    used_dest = USED_DIR / source_clip.name
    shutil.move(str(source_clip), str(used_dest))
    log(f"Moved source clip to {used_dest.name}")

    return target_dir, archived_video, meta

if __name__ == "__main__":
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    source_clip = step_1_check_footage()
    _, _, mixed_audio = step_2_audio()
    step_3_prepare_background_video(source_clip)
    final_video, thumbnail = step_4_render_reel(mixed_audio)
    target_dir, archived_video, meta = step_5_archive_output(final_video, thumbnail, source_clip)
    log(f"[SUCCESS] Reel 030 produced at {archived_video}")
