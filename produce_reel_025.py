#!/usr/bin/env python3
"""
produce_reel_025.py - Autonomous Socials Reel Producer for @unwrittenrules.b3
Produces Reel 025: 'The Illusion of Effort'
Book: 'AI Production Handbook'
Dynamic 2-Shot Viral Montage (Crossfade at 3.4s)
"""

import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path

WORKSPACE = Path("/Users/bidya/Documents/side hustle/socials")
FOOTAGE_DIR = WORKSPACE / "assets" / "footage"
USED_DIR = FOOTAGE_DIR / "used"
AUDIO_DIR = WORKSPACE / "assets" / "audio"
REELS_DIR = WORKSPACE / "reels"
TEMP_DIR = WORKSPACE / "temp_render_025"
CLEANUP_TRASH = Path(os.path.expanduser("~/.Trash/socials_temp_cleanup"))

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

REEL_SPEC = {
    "num": "025",
    "id": "reel-025",
    "slug": "illusion-of-effort",
    "title": "The Illusion of Effort",
    "book": "AI Production Handbook",
    "theme": "Automated Systems & The Devaluation of Manual Effort",
    "duration": 7.00,
    "spoken": "In an automated world, effort is no longer a virtue. It is an engineering failure.",
    "line1": "in an automated world, effort is no longer a virtue.",
    "line2": "it is an engineering failure.",
    "shot1_scenario": "Tired exhausted office worker grinding at desk late at night",
    "shot1_file": "tired_office_computer_night_12893568.mp4",
    "shot2_scenario": "Gleaming dark server room racks with pulsing data lights",
    "shot2_file": "server_room_lights_dark_7986749.mp4",
    "bgm_track": "solitude.mp3",
    "bgm_ss": "00:00:00",
    "bgm_volume": 0.18,
    "caption": """The hardest pill to swallow in the modern workplace:

We were trained to believe that sweat equals value. We were taught that exhaustion is proof of dedication.

In the intelligence age, that entire mental model is obsolete.

When an autonomous system can execute complex workflows without fatigue, hesitation, or human error, manual effort isn't rewarded. It is diagnosed as an architectural inefficiency.

The most vulnerable professionals in any organization are never the ones who lack effort. They are the ones whose value depends solely on routine labor.

Real leverage is no longer about how hard you can push. It is about whether you own the systems that do the pushing for you.

Save this before you spend your next 8 hours doing what a system could execute in seconds.

Deconstruct autonomous systems and modern leverage in 'AI Production Handbook'.

#aiproductionhandbook #unwrittenrules #leverage #systems #futureofwork #stoicmindset #humanbehavior #aiagents #reels #shorts #productivity"""
}


def log(msg):
    print(f"[*] {msg}")


def step_1_check_footage():
    log("Step 1: Locating 2-shot footage clips...")
    clip1 = FOOTAGE_DIR / REEL_SPEC["shot1_file"]
    clip2 = FOOTAGE_DIR / REEL_SPEC["shot2_file"]
    
    if not clip1.exists():
        fresh = [p for p in FOOTAGE_DIR.glob("*.mp4") if "used" not in str(p)]
        clip1 = fresh[0]
    if not clip2.exists():
        fresh = [p for p in FOOTAGE_DIR.glob("*.mp4") if str(p) != str(clip1) and "used" not in str(p)]
        clip2 = fresh[0]
        
    log(f"Shot 1 Clip: {clip1.name} (Tension/Human Grind)")
    log(f"Shot 2 Clip: {clip2.name} (System/Automated Infrastructure)")
    return clip1, clip2


def step_2_audio():
    log("Step 2: Synthesizing & mastering dual-phrase studio audio...")
    assets_dir = TEMP_DIR / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    raw_p1 = assets_dir / "raw_part1.mp3"
    raw_p2 = assets_dir / "raw_part2.mp3"
    audio_master = assets_dir / "audio.mp3"
    
    p1_text = REEL_SPEC["line1"]
    p2_text = REEL_SPEC["line2"]
    
    # 1. Edge TTS for both phrases
    log(f"Synthesizing Phrase 1: '{p1_text}'...")
    subprocess.run([
        str(WORKSPACE / ".venv" / "bin" / "edge-tts"),
        "--voice=en-US-ChristopherNeural",
        "--pitch=-5Hz",
        "--rate=+2%",
        f"--text={p1_text}",
        f"--write-media={raw_p1}"
    ], check=True)

    log(f"Synthesizing Phrase 2: '{p2_text}'...")
    subprocess.run([
        str(WORKSPACE / ".venv" / "bin" / "edge-tts"),
        "--voice=en-US-ChristopherNeural",
        "--pitch=-5Hz",
        "--rate=+2%",
        f"--text={p2_text}",
        f"--write-media={raw_p2}"
    ], check=True)

    def get_d(f):
        return float(subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(f)
        ]).strip())

    d1 = get_d(raw_p1)
    d2 = get_d(raw_p2)
    log(f"Phrase 1 duration: {d1:.2f}s | Phrase 2 duration: {d2:.2f}s")

    # 2. Dual-phrase studio mastering chain with dramatic pause at 3.45s (cut point)
    bgm_file = AUDIO_DIR / REEL_SPEC["bgm_track"]
    log(f"Mixing dual-phrase audio over BGM '{bgm_file.name}' with crossfade sync...")

    filter_complex = (
        "[0:a]adelay=180|180,volume=1.0[v1];"
        "[1:a]adelay=3500|3500,volume=1.0[v2];"
        "[v1][v2]amix=inputs=2:duration=longest:normalize=0[vce_raw];"
        "[vce_raw]aresample=48000,aformat=channel_layouts=stereo,"
        "equalizer=f=120:width_type=o:width=1.0:g=3.5,"
        "equalizer=f=400:width_type=o:width=1.0:g=-2.5,"
        "equalizer=f=3200:width_type=o:width=1.2:g=2.8,"
        "loudnorm=I=-14.0:TP=-1.5:LRA=7[vce];"
        f"[2:a]aresample=48000,aformat=channel_layouts=stereo,volume={REEL_SPEC['bgm_volume']},"
        "afade=t=in:st=0:d=0.2,afade=t=out:st=6.0:d=1.0[bgm];"
        "[vce][bgm]amix=inputs=2:duration=first:normalize=0[aout]"
    )

    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(raw_p1),
        "-i", str(raw_p2),
        "-ss", REEL_SPEC["bgm_ss"], "-t", "7.00", "-i", str(bgm_file),
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-t", "7.00",
        "-c:a", "mp3", "-b:a", "192k",
        str(audio_master)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    return raw_p1, raw_p2, audio_master


def step_3_prepare_montage(clip1, clip2):
    log("Step 3: Assembling 2-scene multi-shot montage (crossfade at 3.4s)...")
    bg_video = TEMP_DIR / "assets" / "bg_video.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-ss", "00:00:00.5", "-t", "3.6", "-i", str(clip1),
        "-ss", "00:00:01", "-t", "3.7", "-i", str(clip2),
        "-filter_complex",
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,settb=AVTB[v0];"
        "[1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,settb=AVTB[v1];"
        "[v0][v1]xfade=transition=fade:duration=0.3:offset=3.4[outv]",
        "-map", "[outv]",
        "-t", "7.00",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p", "-an",
        str(bg_video)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return bg_video


def step_4_render_hyperframes(audio_file):
    log("Step 4: Rendering 2-scene Hyperframes composition...")
    with open(TEMP_DIR / "package.json", "w") as f:
        json.dump({"name": "reel-025", "version": "1.0.0", "private": True}, f)

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
        background: radial-gradient(circle at 50% 38%, transparent 20%, rgba(0,0,0,0.5) 100%),
                    linear-gradient(to bottom, rgba(0,0,0,0.35) 0%, transparent 25%, transparent 70%, rgba(0,0,0,0.7) 100%);
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

      // Line 1: 0.15s -> 3.20s (Scene 1: Human Grind)
      tl.fromTo("#line1", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power2.out" }}, 0.15);
      tl.to("#line1", {{ opacity: 0, y: -10, duration: 0.30, ease: "power2.in" }}, 3.10);

      // Line 2: 3.45s -> 6.65s (Scene 2: Automated Machine - locks to 3.4s scene cut)
      tl.fromTo("#line2", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power2.out" }}, 3.45);
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

    final_video = TEMP_DIR / "final_reel_025.mp4"
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


def step_5_archive(final_video, thumbnail, audio_master, clip1, clip2):
    target_dir = REELS_DIR / f"{REEL_SPEC['id']}-{REEL_SPEC['slug']}"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    archived_video = target_dir / "video.mp4"
    archived_thumb = target_dir / "thumbnail.jpg"
    archived_audio = target_dir / "audio.mp3"
    
    shutil.copy(str(final_video), str(archived_video))
    shutil.copy(str(thumbnail), str(archived_thumb))
    shutil.copy(str(audio_master), str(archived_audio))
    
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
        "theme": REEL_SPEC["theme"],
        "duration": REEL_SPEC["duration"],
        "mediaUrl": f"https://github.com/bidya271/instagram/releases/download/media-vault/reel_{REEL_SPEC['num']}.mp4",
        "script": REEL_SPEC["spoken"],
        "bgm": REEL_SPEC["bgm_track"],
        "voice": "en-US-ChristopherNeural",
        "shot1": clip1.name,
        "shot2": clip2.name,
        "caption": REEL_SPEC["caption"],
        "bufferPosts": {
            "instagram": "6adb261ae2b536ff313ff5eb",
            "youtube": "6adb2629bab742f874b9f2ab",
            "tiktok": "6adb262f2baa602d024243b5"
        },
        "scheduledDue": {
            "instagram": "2026-10-26T19:23:00.000Z",
            "youtube": "2026-10-24T17:05:00.000Z",
            "tiktok": "2026-10-24T06:44:00.000Z"
        },
        "status": "scheduled_in_buffer"
    }
    with open(target_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    log(f"Archived final 2-shot package into {target_dir}")
    return target_dir, archived_video, meta


def step_6_github_upload(archived_video):
    log("Step 6: Re-uploading to GitHub media-vault release (clobber)...")
    asset_name = f"reel_{REEL_SPEC['num']}.mp4"
    temp_upload = Path(f"/tmp/{asset_name}")
    shutil.copy(str(archived_video), str(temp_upload))
    cmd = f"gh release upload media-vault \"{temp_upload}\" --clobber -R bidya271/instagram"
    log(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)
    temp_upload.unlink(missing_ok=True)
    public_url = f"https://github.com/bidya271/instagram/releases/download/media-vault/{asset_name}"
    log(f"Permanent Media URL: {public_url}")
    return public_url


def step_7_move_footage_and_cleanup(clip1, clip2):
    log("Step 7: Moving both source clips to assets/footage/used/ and cleaning temp...")
    USED_DIR.mkdir(parents=True, exist_ok=True)
    for c in [clip1, clip2]:
        dest = USED_DIR / c.name
        if c.exists():
            shutil.move(str(c), str(dest))
            log(f"Moved {c.name} to {dest}")
    
    CLEANUP_TRASH.mkdir(parents=True, exist_ok=True)
    if TEMP_DIR.exists():
        trash_dest = CLEANUP_TRASH / f"temp_render_025_{int(time.time())}"
        shutil.move(str(TEMP_DIR), str(trash_dest))
        log(f"Moved temp render dir to {trash_dest}")


if __name__ == "__main__":
    log("Starting 2-Shot Reel 025 Production...")
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    clip1, clip2 = step_1_check_footage()
    _, _, audio_master = step_2_audio()
    bg_video = step_3_prepare_montage(clip1, clip2)
    final_video, thumbnail = step_4_render_hyperframes(audio_master)
    target_dir, archived_video, meta = step_5_archive(final_video, thumbnail, audio_master, clip1, clip2)
    public_url = step_6_github_upload(archived_video)
    step_7_move_footage_and_cleanup(clip1, clip2)
    
    log("[SUCCESS] 2-Shot Reel 025 Upgrade & GitHub Vault Sync Complete!")
