#!/usr/bin/env python3
"""
produce_viral_reel_026.py - High-Retention Multi-Scene Viral Reel Engine
Produces Reel 026: 'The Competence Trap'
Book: 'The Gravity of Power' (Corporate Thrones & The Performance Punishment)
Visual: 2-Shot Dynamic Human Narrative (Crossfade at 3.3s)
Shot 1: Businessman in dramatic shadow (The Corporate Grind)
Shot 2: Dramatic dark chess board (The Asymmetric Strategy)
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
TEMP_DIR = WORKSPACE / "temp_viral_026"
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
    "num": "026",
    "id": "reel-026",
    "slug": "competence-trap",
    "title": "The Competence Trap",
    "book": "The Gravity of Power",
    "chapter": "Chapter 10: Corporate Thrones",
    "theme": "The Performance Punishment & Asymmetric Leverage",
    "duration": 7.00,
    "scheduledDate": "2026-10-30",
    "spoken": "Extreme competence is never rewarded with freedom. It is only rewarded with more work.",
    "line1": "extreme competence<br>is never rewarded with freedom.",
    "line2": "it is only rewarded<br>with more work.",
    "shot1_file": "businessman_dark_shadow_13801293.mp4",
    "shot2_file": "chess_game_dramatic_dark_33688494.mp4",
    "bgm_track": "solitude.mp3",
    "bgm_ss": "00:00:00",
    "bgm_volume": 0.20,
    "caption": """The unspoken rule of corporate efficiency:

When you are exceptionally competent, management does not think: "Let us reward them with autonomy and rest."

Management thinks: "Let us give them the fire drill, the difficult client, and the workload of the person we just laid off."

Slacking colleagues receive grace, smaller quotas, and gentle check-ins. Top performers receive higher targets, uncompensated emergencies, and the silent expectation to carry the team.

Because competence is not treated as a virtue. In a corporate hierarchy, competence is treated as an exploitable resource.

The moment you realize that working harder only buys you a bigger shovel, you stop sprinting on someone else's treadmill.

Save this before you volunteer for your next weekend project.

Deconstruct asymmetric leverage and corporate power dynamics in 'The Gravity of Power'.

#thegravityofpower #unwrittenrules #corporatepolitics #burnout #stoicism #careeradvice #powerdynamics #reels #shorts #productivity"""
}


def log(msg):
    print(f"[*] {msg}")


def step_1_check_footage():
    log("Step 1: Checking multi-shot dramatic footage...")
    clip1 = FOOTAGE_DIR / REEL_SPEC["shot1_file"]
    clip2 = FOOTAGE_DIR / REEL_SPEC["shot2_file"]
    
    if not clip1.exists():
        fresh = [p for p in FOOTAGE_DIR.glob("*.mp4") if "used" not in str(p)]
        clip1 = fresh[0]
    if not clip2.exists():
        fresh = [p for p in FOOTAGE_DIR.glob("*.mp4") if str(p) != str(clip1) and "used" not in str(p)]
        clip2 = fresh[0]
        
    log(f"Shot 1 Clip: {clip1.name} (Tension/Executive Shadow)")
    log(f"Shot 2 Clip: {clip2.name} (Strategy/Chess Maneuver)")
    return clip1, clip2


def step_2_audio():
    log("Step 2: Synthesizing & mastering Christopher Neural studio audio...")
    assets_dir = TEMP_DIR / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    raw_voice = assets_dir / "raw_voice.mp3"
    mastered_voice = assets_dir / "mastered_voice.mp3"
    mixed_audio = assets_dir / "audio.mp3"
    
    # 1. Edge TTS
    log("Generating Christopher Neural speech (-5Hz, +4%)...")
    subprocess.run([
        str(WORKSPACE / ".venv" / "bin" / "edge-tts"),
        "--voice=en-US-ChristopherNeural",
        "--pitch=-5Hz",
        "--rate=+4%",
        f"--text={REEL_SPEC['spoken']}",
        f"--write-media={raw_voice}"
    ], check=True)
    
    # 2. Studio Mastering Chain from REEL_PRODUCTION_STANDARD.md
    log("Applying studio mastering chain: 130Hz bass boost, 400Hz notch scoop, 3500Hz razor clarity, optical compression...")
    subprocess.run([
        "ffmpeg", "-y", "-i", str(raw_voice),
        "-af", "equalizer=f=130:t=q:w=1:g=3.5,equalizer=f=400:t=q:w=1.5:g=-2.5,equalizer=f=3500:t=q:w=1:g=2.5,acompressor=threshold=-18dB:ratio=3:attack=5:release=50",
        "-b:a", "192k", str(mastered_voice)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 3. Audio Mixing with Preset 2A (Solitude Intro)
    bgm_file = AUDIO_DIR / REEL_SPEC["bgm_track"]
    log(f"Mixing voice with {REEL_SPEC['bgm_track']} (Preset 2A)...")
    filter_complex = (
        "[0:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.20[vce];"
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


def step_3_prepare_montage(clip1, clip2):
    log("Step 3: Assembling 2-scene multi-shot montage (crossfade at 3.3s)...")
    bg_video = TEMP_DIR / "assets" / "bg_video.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-ss", "00:00:01", "-t", "3.5", "-i", str(clip1),
        "-ss", "00:00:00.5", "-t", "3.9", "-i", str(clip2),
        "-filter_complex",
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,settb=AVTB[v0];"
        "[1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,settb=AVTB[v1];"
        "[v0][v1]xfade=transition=fade:duration=0.3:offset=3.3[outv]",
        "-map", "[outv]",
        "-t", "7.00",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p", "-an",
        str(bg_video)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return bg_video


def step_4_render_hyperframes(audio_file):
    log("Step 4: Rendering dynamic 2-scene Hyperframes composition...")
    with open(TEMP_DIR / "package.json", "w") as f:
        json.dump({"name": "reel-026-v2", "version": "1.0.0", "private": True}, f)

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
        background: radial-gradient(circle at 50% 38%, transparent 20%, rgba(0,0,0,0.50) 100%),
                    linear-gradient(to bottom, rgba(0,0,0,0.40) 0%, transparent 25%, transparent 70%, rgba(0,0,0,0.75) 100%);
        pointer-events: none; z-index: 2;
      }}
      /* Bottom Attribution Signature: @unwrittenrules.b3 • Current Book Title */
      .attribution {{
        position: absolute; bottom: 220px; width: 100%; text-align: center;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 24px; font-weight: 600; letter-spacing: 0.14em;
        text-transform: uppercase; color: rgba(255, 255, 255, 0.75);
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

      // Line 1: 0.15s -> 2.85s (Scene 1: Businessman in Shadows)
      tl.fromTo("#line1", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power2.out" }}, 0.15);
      tl.to("#line1", {{ opacity: 0, y: -10, duration: 0.35, ease: "power2.in" }}, 2.80);

      // Line 2: 3.25s -> 6.65s (Scene 2: Chessboard Cut at 3.3s)
      tl.fromTo("#line2", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power2.out" }}, 3.25);
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

    final_video = TEMP_DIR / "final_reel_026.mp4"
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


def step_5_archive(final_video, thumbnail, raw_voice, mastered_voice, mixed_audio, clip1, clip2):
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
        "shot1": clip1.name,
        "shot2": clip2.name,
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
        trash_dest = CLEANUP_TRASH / f"temp_viral_026_{int(time.time())}"
        shutil.move(str(TEMP_DIR), str(trash_dest))
        log(f"Moved temp render dir to {trash_dest}")


if __name__ == "__main__":
    log("Starting Production of 2-Scene Viral Reel 026 ('The Competence Trap')...")
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    clip1, clip2 = step_1_check_footage()
    raw_v, mast_v, mix_a = step_2_audio()
    bg_video = step_3_prepare_montage(clip1, clip2)
    final_video, thumbnail = step_4_render_hyperframes(mix_a)
    target_dir, archived_video, meta = step_5_archive(final_video, thumbnail, raw_v, mast_v, mix_a, clip1, clip2)
    public_url = step_6_github_upload(archived_video)
    step_7_move_footage_and_cleanup(clip1, clip2)
    
    log("[SUCCESS] Million-View Caliber Reel 026 Production & GitHub Media Vault Sync Complete!")
