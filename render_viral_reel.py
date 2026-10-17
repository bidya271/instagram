#!/usr/bin/env python3
"""
render_viral_reel.py
High-retention 7-second viral reel renderer for Reels 004 through 017.
- 1080x1920, 60fps, exactly 7.00 seconds (420 frames)
- Frosted dark glass container with mobile-first bold typography
- High-contrast Rule Badge (#FFD700) and power word highlights
- GSAP Ken Burns camera push (+7% scale)
- Christopher Neural voiceover + mastered atmospheric BGM
"""

import os
import sys
import json
import time
import shutil
import argparse
import subprocess
from pathlib import Path

from viral_script_engine import VIRAL_REELS

WORKSPACE = Path("/Users/bidya/Documents/side hustle/socials")
FOOTAGE_DIR = WORKSPACE / "assets" / "footage"
USED_DIR = FOOTAGE_DIR / "used"
AUDIO_DIR = WORKSPACE / "assets" / "audio"
REELS_DIR = WORKSPACE / "reels"
TEMP_DIR = WORKSPACE / "temp_viral_batch"

def run_step(cmd, desc):
    print(f"    [{desc}]")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"    [ERROR] in {desc}:\n{res.stderr}")
        raise RuntimeError(f"Step failed: {desc}")
    return res.stdout

def get_dur(f):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(f)
    ])
    return float(out.strip())

def render_reel(item):
    reel_id = f"reel-{item['num']}"
    slug = item['slug']
    target_dir = REELS_DIR / f"{reel_id}-{slug}"
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=======================================================")
    print(f"[*] RENDERING 7-SECOND VIRAL REEL: {reel_id} ({item['rule_badge']})")
    print(f"[*] Theme: {item['title']} | Book: {item['book']}")
    print(f"=======================================================")

    work_dir = TEMP_DIR / reel_id
    assets_dir = work_dir / "assets"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    assets_dir.mkdir(parents=True, exist_ok=True)

    # 1. Voiceover TTS
    tts_bin = WORKSPACE / ".venv" / "bin" / "edge-tts"
    if not tts_bin.exists():
        tts_bin = "edge-tts"

    card1_clean = item['card1'].replace('"', '\\"')
    card2_clean = item['card2'].replace('"', '\\"')
    run_step(f"\"{tts_bin}\" --voice en-US-ChristopherNeural --rate=+12% --text \"{card1_clean}\" --write-media \"{work_dir}/b1.mp3\"", "TTS Card 1")
    run_step(f"\"{tts_bin}\" --voice en-US-ChristopherNeural --rate=+12% --text \"{card2_clean}\" --write-media \"{work_dir}/b2.mp3\"", "TTS Card 2")

    d_b1 = get_dur(work_dir / "b1.mp3")
    d_b2 = get_dur(work_dir / "b2.mp3")

    # Timing calculations to fit within 7.0 seconds
    t_start = 0.25
    silence_gap = max(0.15, 3.5 - (t_start + d_b1))
    run_step(f"ffmpeg -y -f lavfi -i anullsrc=r=24000:cl=mono -t {t_start:.2f} \"{work_dir}/s_start.mp3\"", "Start Silence")
    run_step(f"ffmpeg -y -f lavfi -i anullsrc=r=24000:cl=mono -t {silence_gap:.2f} \"{work_dir}/s_gap.mp3\"", "Gap Silence")

    concat_txt = work_dir / "concat.txt"
    with open(concat_txt, "w") as f:
        f.write("file 's_start.mp3'\nfile 'b1.mp3'\nfile 's_gap.mp3'\nfile 'b2.mp3'\n")

    run_step(f"ffmpeg -y -f concat -safe 0 -i \"{concat_txt}\" -c copy \"{work_dir}/voice_raw.mp3\"", "Concat Voice")

    # Master voice with compressor and EQ
    master_filter = "equalizer=f=120:t=q:w=1:g=3.0,equalizer=f=3200:t=q:w=1:g=2.5,acompressor=threshold=-16dB:ratio=3.5:attack=5:release=50"
    run_step(f"ffmpeg -y -i \"{work_dir}/voice_raw.mp3\" -af \"{master_filter}\" -t 7.0 \"{work_dir}/voice_master.mp3\"", "Master Voice")

    # Mix with BGM (strictly 7.0s duration)
    bgm_path = AUDIO_DIR / item['bgm']
    filter_complex = "[0:a]volume=1.20[v];[1:a]volume=0.20,atrim=0:7.0,afade=t=out:st=6.6:d=0.4[m];[v][m]amix=inputs=2:duration=first:dropout_transition=0"
    run_step(f"ffmpeg -y -i \"{work_dir}/voice_master.mp3\" -i \"{bgm_path}\" -filter_complex \"{filter_complex}\" -t 7.0 -b:a 256k \"{assets_dir}/audio.mp3\"", "Mix Voice & BGM")

    # 2. Background Video (7.0s)
    footage_file = FOOTAGE_DIR / item['footage']
    if not footage_file.exists():
        footage_file = USED_DIR / item['footage']
    
    foot_dur = get_dur(footage_file)
    if foot_dur < 7.0:
        pts_mult = round(7.0 / foot_dur + 0.05, 2)
        v_filter = f"setpts={pts_mult}*PTS"
    else:
        v_filter = "null"

    run_step(f"ffmpeg -y -i \"{footage_file}\" -filter:v \"{v_filter}\" -c:v libx264 -preset ultrafast -r 60 -pix_fmt yuv420p -an -t 7.0 \"{assets_dir}/bg_video.mp4\"", "Prepare 7s Footage")

    # 3. Create Hyperframes config
    with open(work_dir / "package.json", "w") as f:
        json.dump({"name": reel_id, "version": "1.0.0", "private": True}, f)

    with open(work_dir / "hyperframes.json", "w") as f:
        json.dump({
            "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
            "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
            "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
            "media": {"autoProxy": True}
        }, f, indent=2)

    # 4. Generate High-Impact HTML with Frosted Glass & Gold Badge
    html_code = f"""<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800;900&family=Inter:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap" rel="stylesheet">
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
        position: absolute; inset: -40px; width: 1160px; height: 2000px; object-fit: cover; z-index: 1;
        filter: brightness(0.85) contrast(1.1);
      }}
      .vignette-overlay {{
        position: absolute; inset: 0;
        background: radial-gradient(circle at center, rgba(0,0,0,0.15) 20%, rgba(0,0,0,0.75) 100%),
                    linear-gradient(to bottom, rgba(0,0,0,0.4) 0%, transparent 35%, transparent 65%, rgba(0,0,0,0.7) 100%);
        pointer-events: none; z-index: 2;
      }}
      
      /* Central Frosted Glass Card */
      .card-wrapper {{
        position: absolute; top: 680px; left: 80px; right: 80px;
        background: rgba(10, 12, 18, 0.78);
        backdrop-filter: blur(32px);
        -webkit-backdrop-filter: blur(32px);
        border: 1.5px solid rgba(255, 255, 255, 0.16);
        border-radius: 40px;
        padding: 56px 48px;
        box-shadow: 0 30px 80px rgba(0, 0, 0, 0.9), inset 0 1px 0 rgba(255, 255, 255, 0.25);
        display: flex; flex-direction: column; align-items: center; text-align: center;
        z-index: 10;
      }}

      /* High-Voltage Rule Badge */
      .badge-pill {{
        display: inline-flex; align-items: center; justify-content: center;
        background: rgba(255, 215, 0, 0.12);
        border: 1.5px solid rgba(255, 215, 0, 0.55);
        border-radius: 100px;
        padding: 10px 28px;
        font-family: 'Cinzel', 'Inter', sans-serif;
        font-size: 26px;
        font-weight: 800;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: #FFD700;
        text-shadow: 0 0 25px rgba(255, 215, 0, 0.5);
        margin-bottom: 36px;
      }}

      /* Main Dynamic Text Area */
      .content-viewport {{
        position: relative; width: 100%; min-height: 200px;
        display: flex; align-items: center; justify-content: center;
      }}
      .card-text {{
        position: absolute; width: 100%;
        font-family: 'Inter', -apple-system, sans-serif;
        font-size: 50px; font-weight: 700; line-height: 1.35; letter-spacing: -0.01em;
        color: #FFFFFF;
        text-shadow: 0 4px 20px rgba(0,0,0,0.8);
        opacity: 0;
      }}
      .highlight {{
        color: #FFD700;
        text-shadow: 0 0 30px rgba(255, 215, 0, 0.6);
      }}

      /* Footer Signature */
      .card-footer {{
        margin-top: 40px;
        font-family: 'Inter', sans-serif;
        font-size: 22px; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase;
        color: rgba(255, 255, 255, 0.55);
        display: flex; align-items: center; gap: 8px;
      }}
      .footer-dot {{ color: #FFD700; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="7.0" data-width="1080" data-height="1920">
      <video id="bgVideo" src="assets/bg_video.mp4" class="clip video-bg" data-start="0" data-duration="7.0" autoplay muted loop playsinline></video>
      <div class="vignette-overlay"></div>

      <div class="card-wrapper" id="cardWrapper">
        <div class="badge-pill" id="badgePill">{item['rule_badge']}</div>
        
        <div class="content-viewport">
          <div class="card-text" id="textCard1">{item['card1']}</div>
          <div class="card-text" id="textCard2">{item['card2']}</div>
        </div>

        <div class="card-footer" id="cardFooter">
          <span>@unwrittenrules.b3</span>
          <span class="footer-dot">•</span>
          <span>{item['book']}</span>
        </div>
      </div>

      <audio id="masterAudio" src="assets/audio.mp3" class="clip" data-start="0" data-duration="7.0"></audio>
    </div>

    <script>
      const tl = gsap.timeline({{ paused: true }});

      // Ken Burns subtle camera push
      tl.to("#bgVideo", {{ scale: 1.07, duration: 7.0, ease: "none" }}, 0);

      // Card 1: 0.0s to 3.4s
      tl.fromTo("#textCard1", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }}, 0.1);
      tl.to("#textCard1", {{ opacity: 0, y: -15, duration: 0.35, ease: "power2.in" }}, 3.2);

      // Card 2: 3.5s to 7.0s
      tl.fromTo("#textCard2", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }}, 3.5);

      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>"""

    with open(work_dir / "index.html", "w") as f:
        f.write(html_code)

    # 5. Render with Hyperframes
    run_step(f"cd \"{work_dir}\" && npx hyperframes render . --output raw_render.mp4", "Hyperframes Render (7.0s)")

    # 6. Optimize Faststart MP4
    final_video = target_dir / "video.mp4"
    run_step(f"ffmpeg -y -i \"{work_dir}/raw_render.mp4\" -t 7.0 -c:v libx264 -crf 19 -preset slow -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 192k \"{final_video}\"", "Faststart Encode")

    # 7. Extract Thumbnail & Save Metadata
    shutil.copy(assets_dir / "audio.mp3", target_dir / "audio.mp3")
    run_step(f"ffmpeg -y -ss 00:00:02 -i \"{final_video}\" -vframes 1 \"{target_dir}/thumbnail.jpg\"", "Extract Thumbnail")

    meta = {
        "id": reel_id,
        "slug": slug,
        "title": item['title'],
        "book": item['book'],
        "rule_badge": item['rule_badge'],
        "duration": 7.0,
        "date": item['date'],
        "caption": item['caption'],
        "hook": item['spoken_hook']
    }
    with open(target_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    with open(target_dir / "script.txt", "w") as f:
        f.write(f"TITLE: {item['title']}\nBOOK: {item['book']}\nBADGE: {item['rule_badge']}\n\nCARD 1: {item['card1']}\nCARD 2: {item['card2']}\n")

    print(f"[SUCCESS] {reel_id} rendered to {final_video} (7.00s)")
    return final_video

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num", type=str, default="004", help="Reel number (e.g. 004)")
    parser.add_argument("--all", action="store_true", help="Render all 14 reels")
    args = parser.parse_args()

    if args.all:
        for r in VIRAL_REELS:
            render_reel(r)
    else:
        matched = [r for r in VIRAL_REELS if r["num"] == args.num]
        if matched:
            render_reel(matched[0])
        else:
            print(f"[!] Reel {args.num} not found in VIRAL_REELS")
