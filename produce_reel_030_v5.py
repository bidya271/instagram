#!/usr/bin/env python3
"""
produce_reel_030_v5.py - Natural Comma Pacing Producer
- Line 1: "You're not tired from working hard."
- Breath pause: 0.70s
- Line 2: "You're tired of running a race, you never wanted to win." (Single continuous clause with natural comma intonation)
- Audio: en-GB-RyanNeural at -18%, intimate acoustic EQ + Snowfall ambient piano
- Video: Forest water stream (1080x1920)
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
AUDIO_DIR = WORKSPACE / "assets" / "audio"
REELS_DIR = WORKSPACE / "reels"
TEMP_DIR = WORKSPACE / "temp_render_030_v5"

REEL_SPEC = {
    "num": "030",
    "id": "reel-030",
    "slug": "not-tired-of-working-hard",
    "title": "You're Running a Race You Never Wanted to Win",
    "book": "The Architecture of Greed",
    "chapter": "Chapter 8: The Endless Treadmill",
    "theme": "Exhaustion, Self-Sovereignty & The Rat Race Trap",
    "voice": "en-GB-RyanNeural",
    "footage_clip": "forest_water_stream_39528850.mp4",
    "caption": """The real reason you feel so exhausted:

It isn’t the 40-hour or 60-hour workweek. It isn’t the back-to-back meetings or the unfinished to-do list.

You are not exhausted from working hard.

You are exhausted from running a race you never actually wanted to win.

You’re sprinting for titles you don’t respect, competing against people you don’t care about, and sacrificing your peace for milestones that move the second you cross them.

The moment you realize the finish line is a mirage, you give yourself permission to step off the track.

Save this before you spend another week running someone else's race.

Protect your peace.

Deconstruct the psychology of artificial competition in 'The Architecture of Greed'.

#thearchitectureofgreed #unwrittenrules #burnout #innerpeace #ratrace #stoicmindset #peaceofmind #mentalhealth #selfworth #reels #shorts #motivation"""
}

def log(msg):
    print(f"[*] {msg}")

def step_1_human_audio():
    log("Step 1: Generating two natural sentences with natural comma prosody...")
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    assets_dir = TEMP_DIR / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    tts_bin = str(WORKSPACE / ".venv" / "bin" / "edge-tts")
    
    # Sentence 1: "You're not tired from working hard."
    p1 = assets_dir / "p1.mp3"
    subprocess.run([
        tts_bin, f"--voice={REEL_SPEC['voice']}", "--rate=-15%", "--pitch=-1Hz",
        "--text=You're not tired from working hard.", f"--write-media={p1}"
    ], check=True)
    
    # Sentence 2: One single continuous natural sentence with a comma
    p2 = assets_dir / "p2.mp3"
    subprocess.run([
        tts_bin, f"--voice={REEL_SPEC['voice']}", "--rate=-18%", "--pitch=-1Hz",
        "--text=You're tired of running a race, you never wanted to win.", f"--write-media={p2}"
    ], check=True)
    
    # Stitch Sentence 1 and Sentence 2 with a natural 0.70s breath pause
    stitched_voice = assets_dir / "stitched_voice.mp3"
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(p1),
        "-i", str(p2),
        "-filter_complex",
        "[0:a]aresample=48000,aformat=channel_layouts=stereo[a0];"
        "[1:a]aresample=48000,aformat=channel_layouts=stereo[a1];"
        "aevalsrc=0:d=0.70:s=48000:c=stereo[sil];"
        "[a0][sil][a1]concat=n=3:v=0:a=1[stitched];"
        "[stitched]equalizer=f=110:t=q:w=1.2:g=3.0,equalizer=f=450:t=q:w=1.0:g=-1.5,equalizer=f=3000:t=q:w=1.2:g=1.2,acompressor=threshold=-16dB:ratio=2.2:attack=20:release=150[voice_out]",
        "-map", "[voice_out]",
        "-c:a", "mp3", "-b:a", "192k",
        str(stitched_voice)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    dur_str = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(stitched_voice)
    ]).decode().strip()
    voice_dur = float(dur_str)
    total_dur = round(max(9.0, voice_dur + 0.8), 2)
    REEL_SPEC["duration"] = total_dur
    log(f"Stitched natural voice duration: {voice_dur:.2f}s | Reel total duration: {total_dur}s")
    
    # Mix with acoustic piano (snowfall.mp3)
    mixed_audio = assets_dir / "audio.mp3"
    bgm_file = AUDIO_DIR / "snowfall.mp3"
    filter_complex = (
        f"[0:a]aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={total_dur},volume=1.28[vce];"
        f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.20,"
        f"afade=t=in:st=0:d=0.7,afade=t=out:st={total_dur-1.3}:d=1.3[bgm];"
        "[vce][bgm]amix=inputs=2:duration=first:normalize=0[aout]"
    )
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(stitched_voice),
        "-ss", "00:00:15", "-t", str(total_dur), "-i", str(bgm_file),
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-t", str(total_dur),
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
        "-ss", "00:00:01", "-t", str(REEL_SPEC["duration"]), "-i", str(source_clip),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-an",
        str(bg_video)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return source_clip

def step_3_render():
    log("Step 3: Building Hyperframes composition with natural typographic cadence...")
    dur = REEL_SPEC["duration"]
    # P1 runs ~0.15s to 3.35s. Sentence 2 runs 4.05s to 8.65s.
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
        background: radial-gradient(circle at center, rgba(0,0,0,0.12) 0%, rgba(0,0,0,0.52) 100%),
                    linear-gradient(180deg, rgba(0,0,0,0.32) 0%, rgba(0,0,0,0.05) 45%, rgba(0,0,0,0.58) 100%);
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
        font-size: 58px;
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
        <div class="quote-line" id="line1">you're not tired from working hard.</div>
        <div class="quote-line" id="line2">you're tired of running a race,<br/>you never wanted to win.</div>
      </div>

      <div class="attribution">@unwrittenrules.b3 • {REEL_SPEC['book']}</div>

      <audio id="masterAudio" src="assets/audio.mp3" class="clip" data-start="0" data-duration="{dur}"></audio>
    </div>

    <script>
      const tl = gsap.timeline({{ paused: true }});

      // Line 1: 0.25s -> 3.55s
      tl.fromTo("#line1", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.50, ease: "power2.out" }}, 0.25);
      tl.to("#line1", {{ opacity: 0, y: -8, duration: 0.35, ease: "power2.in" }}, 3.55);

      // Line 2: 4.05s -> {dur - 0.4}s
      tl.fromTo("#line2", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.55, ease: "power2.out" }}, 4.05);
      tl.to("#line2", {{ opacity: 0, duration: 0.40, ease: "power2.in" }}, {dur - 0.4});

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

    spoken_text = "You're not tired from working hard. You're tired of running a race, you never wanted to win."
    with open(archived_script, "w") as f:
        f.write(spoken_text + "\n")

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
        "voice": REEL_SPEC["voice"],
        "footage": source_clip.name,
        "spoken": spoken_text,
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    with open(meta_json, "w") as f:
        json.dump(meta, f, indent=2)

    log(f"[SUCCESS] Reel 030 v5 produced at {archived_video}")
    return archived_video

if __name__ == "__main__":
    step_1_human_audio()
    source_clip = step_2_footage()
    final_video, thumbnail = step_3_render()
    step_4_archive(final_video, thumbnail, source_clip)
