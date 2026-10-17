#!/usr/bin/env python3
"""
render_natural_reel.py
Dynamic, realistic, aesthetic Instagram Reel renderer with audible, mastered trending BGM.
- 1080x1920 Full-Bleed 4K/HD Authentic Video (zero artificial UI cards/borders)
- Frameless editorial typography with soft film drop-shadow
- Mastered trending ambient audio (Snowfall, Solitude) with explicit hook offsets, stereo normalization, and loudnorm (-14 LUFS)
- Warm, relatable human voiceover (AndrewMultilingualNeural)
- Ultra-high retention dynamic pacing
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
TEMP_DIR = WORKSPACE / "temp_natural_reels"

def get_dur(file_path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)
    ])
    return float(out.strip())

REELS_DATA = {
    "004": {
        "num": "004",
        "slug": "quiet-power",
        "title": "The Loudest in the Room",
        "book": "The Gravity of Power",
        "footage": FOOTAGE_DIR / "walking_rain_night_street_39611009.mp4",
        "bgm": AUDIO_DIR / "snowfall.mp3",
        "bgm_ss": "00:00:20",       # Jump right to the famous Snowfall synth drop
        "bgm_volume": 0.09,         # Calibrated ambient bed (-34 dB, 19 dB below speech)
        "voice": "en-US-AndrewMultilingualNeural",
        "voice_rate": "+0%",
        "script": "The most dangerous person in the room is never the one shouting. Insecurity is loud. It needs an audience. But true power is quiet. It watches, listens, and decides without ever needing to perform.",
        "line1": "The most dangerous person in the room is never the one shouting.",
        "line2": "Insecurity is loud. True power is quiet.\nIt never needs an audience to know its worth.",
        "video_ss": "00:00:02",
        "caption": """The loudest person in the room is usually the most terrified.

When you constantly feel the urge to explain yourself, interrupt, or prove how smart you are, you aren’t demonstrating authority. You’re advertising anxiety.

Real power doesn’t perform. It doesn’t scramble for validation. It watches, evaluates, and decides in silence.

The moment you stop reacting to everything thrown at you, you realize most battles win themselves while the other person is still talking.

Save this for the next time you're tempted to speak when you should be observing.

#thegravityofpower #quietpower #stoicmindset #psychologyfacts #humanbehavior #silenceispower #reels"""
    },
    "005": {
        "num": "005",
        "slug": "silent-envy",
        "title": "Camouflage Your Victories",
        "book": "Status: The Currency of Envy",
        "footage": FOOTAGE_DIR / "dark_lake_mist_solitude_35199993.mp4",
        "bgm": AUDIO_DIR / "solitude.mp3",
        "bgm_ss": "00:00:00",       # Immediate orchestral piano and synth
        "bgm_volume": 0.10,         # Calibrated ambient bed (-35 dB, 20 dB below speech)
        "voice": "en-US-AndrewMultilingualNeural",
        "voice_rate": "+0%",
        "script": "Notice how people love giving you advice when you're struggling, but grow strangely quiet the moment you succeed? Learn to celebrate your wins in silence. Protect your peace from rooms that only loved you when you were small.",
        "line1": "Notice how people love giving advice when you struggle, but grow silent the moment you succeed?",
        "line2": "Learn to celebrate your wins in silence.\nProtect your peace from rooms that only loved you when you were small.",
        "video_ss": "00:00:01",
        "caption": """People love comforting you when you're down. It confirms their hierarchy.

The hardest pill to swallow is that not everyone clapping for you is happy you’re winning. Some people only root for you as long as you don't do better than them.

The moment you pull ahead, their empathy turns into subtle critique, distant silence, or unsolicited warnings.

Modesty isn't just a virtue. It’s social camouflage.

Keep your moves quiet. Keep your circle small. Celebrate where no one can throw stones.

Save this before you share your next big win.

#status #currencyofenvy #darkpsychology #protectyourpeace #humanbehavior #mindsetmatters #reels"""
    }
}

def render_natural_reel(item):
    reel_id = f"reel-{item['num']}"
    slug = item['slug']
    target_dir = REELS_DIR / f"{reel_id}-{slug}"
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=======================================================")
    print(f"[*] RENDERING DYNAMIC NATURAL REEL: {reel_id} - {item['title']}")
    print(f"[*] Book: {item['book']} | Music: {item['bgm'].name} (offset {item['bgm_ss']}, vol {item['bgm_volume']})")
    print(f"=======================================================")

    work_dir = TEMP_DIR / reel_id
    assets_dir = work_dir / "assets"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    assets_dir.mkdir(parents=True, exist_ok=True)

    # 1. Generate Voiceover via Edge-TTS
    print("    [1/6] Generating warm relatable voiceover...")
    voice_file = assets_dir / "voice.mp3"
    subprocess.run([
        ".venv/bin/edge-tts",
        f"--voice={item['voice']}",
        f"--rate={item['voice_rate']}",
        f"--text={item['script']}",
        f"--write-media={voice_file}"
    ], check=True)

    voice_dur = get_dur(voice_file)
    # Add 1.8s musical tail after the speech finishes for emotional resonance
    dur = round(voice_dur + 1.8, 1)
    print(f"    [+] Voice duration: {voice_dur:.2f}s | Total Reel Duration: {dur:.1f}s")

    # 2. Master Audio: Vocal Clarity EQ + Voice Loudnorm (-14 LUFS) + Ambient BGM Bed
    print("    [2/6] Mixing voice with calibrated ambient music (voice @ -14 LUFS, music @ -34 dB)...")
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
        f"afade=t=in:st=0:d=0.3,afade=t=out:st={dur-1.8}:d=1.8[bgm];"
        f"[vce][bgm]amix=inputs=2:duration=longest:normalize=0[aout]",
        "-map", "[aout]",
        "-t", str(dur),
        "-c:a", "mp3", "-b:a", "192k",
        str(audio_file)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 3. Prepare Background Video (Full-bleed 1080x1920)
    print("    [3/6] Preparing full-bleed 1080x1920 video clip...")
    subprocess.run([
        "ffmpeg", "-y",
        "-ss", item['video_ss'],
        "-t", str(dur),
        "-i", str(item['footage']),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-an",
        str(assets_dir / "bg_video.mp4")
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 4. Generate Hyperframes Composition with Pure Frameless Typography
    print("    [4/6] Creating Hyperframes composition (ZERO cards/borders)...")
    with open(work_dir / "package.json", "w") as f:
        json.dump({"name": reel_id, "version": "1.0.0", "private": True}, f)

    with open(work_dir / "hyperframes.json", "w") as f:
        json.dump({
            "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
            "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
            "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
            "media": {"autoProxy": True}
        }, f, indent=2)

    # Compute text transitions dynamically based on speech midpoint
    midpoint = round(voice_dur * 0.45, 1)
    l1_start = 0.2
    l1_end = midpoint + 0.3
    l2_start = midpoint + 0.6
    l1_text = item['line1'].replace("\n", "<br>")
    l2_text = item['line2'].replace("\n", "<br>")

    html_code = f"""<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap" rel="stylesheet">
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
      /* Ultra-subtle filmic contrast gradient for seamless text legibility */
      .cinematic-vignette {{
        position: absolute; inset: 0;
        background: radial-gradient(circle at 50% 38%, transparent 28%, rgba(0,0,0,0.42) 100%),
                    linear-gradient(to bottom, rgba(0,0,0,0.32) 0%, transparent 22%, transparent 75%, rgba(0,0,0,0.6) 100%);
        pointer-events: none; z-index: 2;
      }}
      
      /* Frameless Editorial Typography - Organic Placement in Upper-Middle */
      .text-stage {{
        position: absolute; top: 38%; left: 90px; right: 90px;
        transform: translateY(-50%);
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        text-align: center;
        z-index: 10;
      }}
      .quote-line {{
        position: absolute; width: 100%;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 52px;
        font-weight: 700;
        line-height: 1.40;
        letter-spacing: -0.02em;
        color: #FFFFFF;
        text-shadow: 0 4px 22px rgba(0,0,0,0.92), 0 2px 6px rgba(0,0,0,1);
        opacity: 0;
      }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920">
      <video id="bgVideo" src="assets/bg_video.mp4" class="clip video-bg" data-start="0" data-duration="{dur}" autoplay muted loop playsinline></video>
      <div class="cinematic-vignette"></div>

      <div class="text-stage">
        <div class="quote-line" id="line1">{l1_text}</div>
        <div class="quote-line" id="line2">{l2_text}</div>
      </div>

      <audio id="masterAudio" src="assets/audio.mp3" class="clip" data-start="0" data-duration="{dur}"></audio>
    </div>

    <script>
      const tl = gsap.timeline({{ paused: true }});

      // Line 1 transition
      tl.fromTo("#line1", {{ opacity: 0, y: 15 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power2.out" }}, {l1_start});
      tl.to("#line1", {{ opacity: 0, y: -10, duration: 0.4, ease: "power2.in" }}, {l1_end - 0.4});

      // Line 2 transition
      tl.fromTo("#line2", {{ opacity: 0, y: 15 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power2.out" }}, {l2_start});

      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>"""

    with open(work_dir / "index.html", "w") as f:
        f.write(html_code)

    # 5. Render with Hyperframes
    print("    [5/6] Executing Hyperframes rendering engine...")
    subprocess.run(f"cd \"{work_dir}\" && npx hyperframes render . --output raw_render.mp4", shell=True, check=True)

    # 6. Encode Faststart MP4 and Extract Artifacts
    print("    [6/6] Finalizing web-optimized MP4 & metadata...")
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

    # Extract thumbnail
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
        "bgm": item['bgm'].name,
        "bgm_ss": item['bgm_ss']
    }
    with open(target_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    with open(target_dir / "caption.txt", "w") as f:
        f.write(item['caption'])

    print(f"[SUCCESS] {reel_id} rendered to {final_video} ({dur}s)")
    return final_video

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num", type=str, default="004", help="Reel number (004, 005)")
    parser.add_argument("--all", action="store_true", help="Render all natural reels")
    args = parser.parse_args()

    if args.all:
        for num in ["004", "005"]:
            render_natural_reel(REELS_DATA[num])
    else:
        if args.num in REELS_DATA:
            render_natural_reel(REELS_DATA[args.num])
        else:
            print(f"[!] Unknown reel {args.num}")
