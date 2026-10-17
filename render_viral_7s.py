#!/usr/bin/env python3
"""
render_viral_7s.py
7-Second High-Retention Viral Reel Engine:
1. Exactly 7.00 seconds duration for maximum Instagram/TikTok algorithmic loop completion (130%+ APV).
2. Transitioning video frames (2 multi-clip HD video shots crossfaded at 3.4s).
3. 1080x1920 crisp vertical HD footage from Pexels (ocean drone, rain night street, mist lake, calm water).
4. Balanced voice & narration: voice normalized to -14 LUFS broadcast standard, sitting 18-20 dB above ambient BGM.
5. Minimalist, organic, centered editorial typography (Cormorant Garamond / Playfair Display serif, no cards/boxes).
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path

WORKSPACE = Path("/Users/bidya/Documents/side hustle/socials")
FOOTAGE_DIR = WORKSPACE / "assets" / "footage"
AUDIO_DIR = WORKSPACE / "assets" / "audio"
REELS_DIR = WORKSPACE / "reels"
TEMP_DIR = WORKSPACE / "temp_viral_7s"

REELS_7S = {
    "004": {
        "num": "004",
        "slug": "quiet-power",
        "title": "The Loudest in the Room",
        "book": "The Gravity of Power",
        "shot1": FOOTAGE_DIR / "used" / "walking_rain_night_street_39611009.mp4",
        "shot1_ss": "00:00:02",
        "shot2": FOOTAGE_DIR / "calm_water_13692140.mp4",
        "shot2_ss": "00:00:01",
        "bgm": AUDIO_DIR / "snowfall.mp3",
        "bgm_ss": "00:00:20",
        "bgm_volume": 0.08,
        "voice": "en-US-AvaMultilingualNeural",
        "voice_rate": "+8%",
        "script": "The loudest in the room is never the most powerful. Real authority decides in silence.",
        "line1": "the loudest in the room<br>is never the most powerful.",
        "line2": "real authority never performs.<br>it decides in silence.",
        "caption": """The loudest person in the room is usually the most terrified.

When you constantly feel the urge to explain yourself, interrupt, or prove how smart you are, you aren’t demonstrating authority. You’re advertising anxiety.

Real power doesn’t scramble for validation. It watches, evaluates, and decides in silence.

The moment you stop reacting to everything thrown at you, you realize most battles win themselves while the other person is still talking.

Save this for the next time you're tempted to speak when you should be observing.

#thegravityofpower #quietpower #stoicmindset #psychologyfacts #humanbehavior #silenceispower #reels"""
    },
    "005": {
        "num": "005",
        "slug": "silent-envy",
        "title": "Camouflage Your Victories",
        "book": "Status: The Currency of Envy",
        "shot1": FOOTAGE_DIR / "ocean_drone_waves_36621255.mp4",
        "shot1_ss": "00:00:02",
        "shot2": FOOTAGE_DIR / "used" / "dark_lake_mist_solitude_35199993.mp4",
        "shot2_ss": "00:00:01",
        "bgm": AUDIO_DIR / "solitude.mp3",
        "bgm_ss": "00:00:00",
        "bgm_volume": 0.09,
        "voice": "en-US-AvaMultilingualNeural",
        "voice_rate": "+8%",
        "script": "Notice who gets quiet when you win. Protect your peace. Celebrate in silence.",
        "line1": "notice who gets quiet<br>the moment you succeed.",
        "line2": "protect your peace.<br>celebrate where no one can throw stones.",
        "caption": """People love comforting you when you struggle. It confirms their hierarchy.

The hardest truth to accept is that not everyone clapping for you is happy you’re winning. Some people only root for you as long as you don't do better than them.

The moment you pull ahead, their empathy turns into subtle critique, distant silence, or unsolicited warnings.

Modesty isn't just a virtue. It’s social camouflage.

Keep your moves quiet. Keep your circle small. Celebrate where no one can throw stones.

Save this before you share your next big win.

#status #currencyofenvy #darkpsychology #protectyourpeace #humanbehavior #mindsetmatters #reels"""
    }
}

def render_reel_7s(item):
    reel_id = f"reel-{item['num']}"
    slug = item['slug']
    target_dir = REELS_DIR / f"{reel_id}-{slug}"
    target_dir.mkdir(parents=True, exist_ok=True)
    dur = 7.0

    print(f"\n=======================================================")
    print(f"[*] PRODUCING 7-SECOND VIRAL REEL: {reel_id} - {item['title']}")
    print(f"[*] Visuals: Multi-shot HD Crossfade | Audio: {item['bgm'].name} + {item['voice']}")
    print(f"=======================================================")

    work_dir = TEMP_DIR / reel_id
    assets_dir = work_dir / "assets"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    assets_dir.mkdir(parents=True, exist_ok=True)

    # 1. Generate Voiceover
    print("    [1/6] Synthesizing intimate, human voiceover...")
    voice_file = assets_dir / "voice.mp3"
    subprocess.run([
        ".venv/bin/edge-tts",
        f"--voice={item['voice']}",
        f"--rate={item['voice_rate']}",
        f"--text={item['script']}",
        f"--write-media={voice_file}"
    ], check=True)

    v_dur = float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(voice_file)
    ]).strip())
    print(f"    [+] Voice duration: {v_dur:.2f}s (Loop cushion: {dur - v_dur:.2f}s)")

    # 2. Master Audio (Voice @ -14 LUFS broadcast, BGM @ -34 dB ambient bed)
    print("    [2/6] Mastering balanced audio track (voice dominant, ambient music)...")
    audio_file = assets_dir / "audio.mp3"
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(voice_file),
        "-ss", item["bgm_ss"],
        "-t", str(dur),
        "-i", str(item["bgm"]),
        "-filter_complex",
        f"[0:a]aresample=48000,aformat=channel_layouts=stereo,highpass=f=80,equalizer=f=3000:width_type=h:width=1500:g=3.0,loudnorm=I=-14:TP=-1.5:LRA=7[vce];"
        f"[1:a]aresample=48000,aformat=channel_layouts=stereo,equalizer=f=2500:width_type=h:width=2000:g=-4.0,volume={item['bgm_volume']},"
        f"afade=t=in:st=0:d=0.2,afade=t=out:st={dur-0.8}:d=0.8[bgm];"
        f"[vce][bgm]amix=inputs=2:duration=longest:normalize=0[aout]",
        "-map", "[aout]",
        "-t", str(dur),
        "-c:a", "mp3", "-b:a", "192k",
        str(audio_file)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 3. Assemble Multi-Shot Video (Crossfade at 3.4s)
    print("    [3/6] Generating transitioning HD video montage (Shot 1 -> Shot 2)...")
    bg_video = assets_dir / "bg_video.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-ss", item["shot1_ss"], "-t", "3.6", "-i", str(item["shot1"]),
        "-ss", item["shot2_ss"], "-t", "3.7", "-i", str(item["shot2"]),
        "-filter_complex",
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,settb=AVTB[v0];"
        "[1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,settb=AVTB[v1];"
        "[v0][v1]xfade=transition=fade:duration=0.3:offset=3.4[outv]",
        "-map", "[outv]",
        "-t", str(dur),
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-an",
        str(bg_video)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 4. Generate Hyperframes Composition with Centered Minimalist Typography
    print("    [4/6] Creating Hyperframes composition (delicate serif typography)...")
    with open(work_dir / "package.json", "w") as f:
        json.dump({"name": reel_id, "version": "1.0.0", "private": True}, f)

    with open(work_dir / "hyperframes.json", "w") as f:
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
      /* Subtle filmic vignette to ensure white serif text pops against water/rain */
      .cinematic-vignette {{
        position: absolute; inset: 0;
        background: radial-gradient(circle at 50% 48%, transparent 25%, rgba(0,0,0,0.38) 100%),
                    linear-gradient(to bottom, rgba(0,0,0,0.25) 0%, transparent 20%, transparent 80%, rgba(0,0,0,0.5) 100%);
        pointer-events: none; z-index: 2;
      }}
      
      /* Optical center stage matching viral reference */
      .text-stage {{
        position: absolute; top: 48%; left: 90px; right: 90px;
        transform: translateY(-50%);
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        text-align: center;
        z-index: 10;
      }}
      .quote-line {{
        position: absolute; width: 100%;
        font-family: 'Playfair Display', Georgia, serif;
        font-style: italic;
        font-size: 56px;
        font-weight: 500;
        line-height: 1.38;
        letter-spacing: -0.01em;
        color: #FFFFFF;
        text-shadow: 0 2px 14px rgba(0,0,0,0.95), 0 1px 4px rgba(0,0,0,0.9);
        opacity: 0;
      }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920">
      <video id="bgVideo" src="assets/bg_video.mp4" class="clip video-bg" data-start="0" data-duration="{dur}" autoplay muted loop playsinline></video>
      <div class="cinematic-vignette"></div>

      <div class="text-stage">
        <div class="quote-line" id="line1">{item['line1']}</div>
        <div class="quote-line" id="line2">{item['line2']}</div>
      </div>

      <audio id="masterAudio" src="assets/audio.mp3" class="clip" data-start="0" data-duration="{dur}"></audio>
    </div>

    <script>
      const tl = gsap.timeline({{ paused: true }});

      // Line 1: 0.15s -> 3.2s
      tl.fromTo("#line1", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }}, 0.15);
      tl.to("#line1", {{ opacity: 0, y: -8, duration: 0.35, ease: "power2.in" }}, 3.1);

      // Line 2: 3.5s -> 6.6s (transitions precisely with the video cut)
      tl.fromTo("#line2", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }}, 3.5);
      tl.to("#line2", {{ opacity: 0, duration: 0.3, ease: "power2.in" }}, 6.6);

      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>"""

    with open(work_dir / "index.html", "w") as f:
        f.write(html_code)

    # 5. Render with Hyperframes
    print("    [5/6] Rendering 7-second sequence via Hyperframes...")
    subprocess.run(f"cd \"{work_dir}\" && npx hyperframes render . --output raw_render.mp4", shell=True, check=True)

    # 6. Mux Master Audio & Encode Faststart MP4
    print("    [6/6] Finalizing 7-second MP4 with master audio muxing...")
    final_video = target_dir / "video.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(work_dir / "raw_render.mp4"),
        "-i", str(audio_file),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-t", str(dur),
        "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "192k",
        str(final_video)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Extract thumbnail at 2.0s
    subprocess.run([
        "ffmpeg", "-y",
        "-ss", "00:00:02",
        "-i", str(final_video),
        "-vframes", "1",
        str(target_dir / "thumbnail.jpg")
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    meta = {
        "id": reel_id,
        "slug": slug,
        "title": item['title'],
        "book": item['book'],
        "duration": dur,
        "caption": item['caption'],
        "script": item['script'],
        "shot1": str(item['shot1'].name),
        "shot2": str(item['shot2'].name),
        "bgm": str(item['bgm'].name),
        "voice": item['voice']
    }
    with open(target_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    with open(target_dir / "caption.txt", "w") as f:
        f.write(item['caption'])

    print(f"[SUCCESS] 7s Viral Reel {reel_id} rendered to {final_video}")
    return final_video

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num", type=str, default="004", help="Reel number (004, 005)")
    parser.add_argument("--all", action="store_true", help="Render all 7s viral reels")
    args = parser.parse_args()

    if args.all:
        for num in ["004", "005"]:
            render_reel_7s(REELS_7S[num])
    else:
        if args.num in REELS_7S:
            render_reel_7s(REELS_7S[args.num])
        else:
            print(f"[!] Unknown reel {args.num}")
