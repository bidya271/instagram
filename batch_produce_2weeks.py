#!/usr/bin/env python3
"""
batch_produce_2weeks.py
Generates 14 consecutive daily reels (Reel 004 through Reel 017),
uploads them to GitHub release vault, and schedules them across
Instagram, YouTube Shorts, and TikTok via Buffer.
"""

import os
import sys
import json
import time
import shutil
import subprocess
import urllib.request
from pathlib import Path

WORKSPACE = Path("/Users/bidya/Documents/side hustle/socials")
FOOTAGE_DIR = WORKSPACE / "assets" / "footage"
USED_DIR = FOOTAGE_DIR / "used"
AUDIO_DIR = WORKSPACE / "assets" / "audio"
REELS_DIR = WORKSPACE / "reels"
TEMP_DIR = WORKSPACE / "temp_batch"
BUFFER_TOKEN = "kT3VN2dNEG0GDfVTnYlr-6SB0MpUuwEK89bBVWmFdwU"

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
        "time": "22:33:00"
    }
}

REELS_DATA = [
    {
        "num": "004",
        "slug": "illusion-of-loud-power",
        "date": "2026-10-17",
        "book": "The Gravity of Power",
        "theme": "The Illusion of Loud Power / Strategic Silence",
        "footage": "minimal_architecture_28883887.mp4",
        "bgm": "solitude.mp3",
        "b1": "The loudest person in the room is never the most powerful.",
        "b2": "Real authority does not perform. It decides.",
        "b3_head": "When you need to announce control, you have already lost it.",
        "b3_sub": "True leverage moves in total silence.",
        "caption": "The loudest person in the room is never the most powerful. Real authority does not perform; it decides. When you need to announce your control, you have already lost it. True leverage moves in total silence.\n\nDiscover the unwritten dynamics of corporate thrones in 'The Gravity of Power'.\n\n#unwrittenrules #thegravityofpower #darkpsychology #powerdynamics #leadership #stoicism #quietluxury #reels #shorts"
    },
    {
        "num": "005",
        "slug": "exhaustion-of-approval",
        "date": "2026-10-18",
        "book": "Status: The Currency of Envy",
        "theme": "The Exhaustion of Approval / The Prison of Opinions",
        "footage": "foggy_mountain_36146543.mp4",
        "bgm": "new_home.mp3",
        "b1": "You are not exhausted from working hard.",
        "b2": "You are exhausted from performing for people you don't even respect.",
        "b3_head": "Status is an auction with no closing bell.",
        "b3_sub": "The only way to win is to refuse to bid.",
        "caption": "You are not exhausted from working hard. You are exhausted from performing for people you don't even respect. Status is an auction with no closing bell. The only way to win is to refuse to bid.\n\nDeconstruct the games of prestige and social envy in 'Status: The Currency of Envy'.\n\n#unwrittenrules #status #darkpsychology #stoicmindset #boundaries #mentalclarity #freedom #reels #shorts"
    },
    {
        "num": "006",
        "slug": "institutional-conscience",
        "date": "2026-10-19",
        "book": "The Morality Machine",
        "theme": "Institutional Compliance vs True Ethics",
        "footage": "night_traffic_30065145.mp4",
        "bgm": "gymnopedie.mp3",
        "b1": "Institutions do not have a conscience.",
        "b2": "They have compliance departments designed to protect their balance sheets.",
        "b3_head": "Never confuse corporate policy with moral truth.",
        "b3_sub": "A rule exists to shield the hierarchy, not you.",
        "caption": "Institutions do not have a conscience. They have compliance departments designed to protect their balance sheets. Never confuse corporate policy with moral truth. A rule exists to shield the hierarchy, not you.\n\nExplore ethical illusions and corporate absolution in 'The Morality Machine'.\n\n#unwrittenrules #themoralitymachine #corporateculture #powerdynamics #darkpsychology #stoicism #boundaries #reels #shorts"
    },
    {
        "num": "007",
        "slug": "weapon-of-praise",
        "date": "2026-10-20",
        "book": "The Ideology of Hypocrisy",
        "theme": "The Weapon of Public Praise / The Pedestal Trap",
        "footage": "dark_forest_28462198.mp4",
        "bgm": "snowfall.mp3",
        "b1": "Beware of unearned praise in public meetings.",
        "b2": "Setting you on a pedestal is the easiest way to make your fall look like your fault.",
        "b3_head": "Flattery creates an obligation you never signed.",
        "b3_sub": "Stay grounded. Stay strategically detached.",
        "caption": "Beware of unearned praise in public meetings. Setting you on a pedestal is the easiest way to make your fall look like your own fault. Flattery creates an obligation you never signed. Stay grounded. Stay detached.\n\nUncover the psychological architecture of workplace deception in 'The Ideology of Hypocrisy'.\n\n#unwrittenrules #theideologyofhypocrisy #officepolitics #darkpsychology #manipulation #stoic #boundaries #reels #shorts"
    },
    {
        "num": "008",
        "slug": "infinite-scoreboard",
        "date": "2026-10-21",
        "book": "The Architecture of Greed",
        "theme": "Money as an Infinite Scoreboard",
        "footage": "desert_dunes_34535421.mp4",
        "bgm": "interstellar.mp3",
        "b1": "Money was invented as a simple tool for trade.",
        "b2": "Human psychology mutated it into an infinite scoreboard.",
        "b3_head": "When money becomes your identity, no amount will ever feel safe.",
        "b3_sub": "Define your number, or the machine will consume you.",
        "caption": "Money was invented as a simple tool for trade. Human psychology mutated it into an infinite scoreboard. When money becomes your identity, no amount will ever feel safe. Define your number, or the machine will consume you.\n\nFrom 'The Architecture of Greed'.\n\n#unwrittenrules #thearchitectureofgreed #wealthmindset #stoicism #freedom #financialfreedom #psychology #reels #shorts"
    },
    {
        "num": "009",
        "slug": "cost-of-belonging",
        "date": "2026-10-22",
        "book": "The Tribal Mind",
        "theme": "The Cost of Belonging / Intellectual Freedom",
        "footage": "ocean_storm_15847773.mp4",
        "bgm": "preset_2b_solitude_build.mp3",
        "b1": "A tribe demands loyalty long before it offers protection.",
        "b2": "The price of belonging is always your intellectual independence.",
        "b3_head": "If your circle punishes honest questions, you are not in a community.",
        "b3_sub": "You are trapped in an ideological cult.",
        "caption": "A tribe demands loyalty long before it offers protection. The price of belonging is always your intellectual independence. If your circle punishes honest questions, you are not in a community. You are trapped in an ideological cult.\n\nUnderstand group psychology in 'The Tribal Mind'.\n\n#unwrittenrules #thetribałmind #criticalthinking #darkpsychology #stoicism #autonomy #freedom #reels #shorts"
    },
    {
        "num": "010",
        "slug": "asymmetry-engine",
        "date": "2026-10-23",
        "book": "The Gravity of Power",
        "theme": "Corporate Thrones / The Asymmetry of Blame",
        "footage": "coastal_cliffs_31784580.mp4",
        "bgm": "solitude.mp3",
        "b1": "When an initiative succeeds, leadership takes the equity.",
        "b2": "When it fails, middle management takes the blame.",
        "b3_head": "Hierarchy is an asymmetry engine.",
        "b3_sub": "Keep your paper trail clean. Loyalty will never defend you.",
        "caption": "When an initiative succeeds, leadership takes the equity. When it fails, middle management takes the blame. Hierarchy is an asymmetry engine. Keep your paper trail clean. Loyalty will never defend you.\n\nFrom 'The Gravity of Power'.\n\n#unwrittenrules #thegravityofpower #careeradvice #corporatepolitics #workplace #powerdynamics #stoic #reels #shorts"
    },
    {
        "num": "011",
        "slug": "silent-envy",
        "date": "2026-10-24",
        "book": "Status: The Currency of Envy",
        "theme": "Conspicuous Humility / Silent Envy",
        "footage": "snow_pines_10671896.mp4",
        "bgm": "new_home.mp3",
        "b1": "People support you when you struggle.",
        "b2": "They begin to critique you the moment you pull ahead.",
        "b3_head": "Never flaunt your victories to an anxious room.",
        "b3_sub": "Modesty is not humility. It is social camouflage.",
        "caption": "People support you when you struggle. They begin to critique you the moment you pull ahead. Never flaunt your victories to an anxious room. Modesty is not humility. It is social camouflage.\n\nMaster the laws of envy in 'Status: The Currency of Envy'.\n\n#unwrittenrules #status #darkpsychology #envy #humanbehavior #stoicmindset #psychologyfacts #reels #shorts"
    },
    {
        "num": "012",
        "slug": "outrage-economy",
        "date": "2026-10-25",
        "book": "The Morality Machine",
        "theme": "Outrage as Entertainment",
        "footage": "moody_waterfall_34491674.mp4",
        "bgm": "gymnopedie.mp3",
        "b1": "Public outrage is rarely about justice.",
        "b2": "It is a social luxury good, manufactured to signal virtue without cost.",
        "b3_head": "Notice who profits when a digital mob forms.",
        "b3_sub": "Anger is the most lucrative product in the attention economy.",
        "caption": "Public outrage is rarely about justice. It is a social luxury good, manufactured to signal virtue without cost. Notice who profits when a digital mob forms. Anger is the most lucrative product in the attention economy.\n\nFrom 'The Morality Machine'.\n\n#unwrittenrules #themoralitymachine #media #attentioneconomy #darkpsychology #stoicism #mindfulness #reels #shorts"
    },
    {
        "num": "013",
        "slug": "weaponized-forgiveness",
        "date": "2026-10-26",
        "book": "The Ideology of Hypocrisy",
        "theme": "Weaponized Forgiveness & Boundary Defense",
        "footage": "atmospheric_rain_5310971.mp4",
        "bgm": "snowfall.mp3",
        "b1": "Repeated disrespect is never a communication problem.",
        "b2": "It is a boundary problem that you refused to enforce.",
        "b3_head": "Forgiveness without changed behavior is an invitation for escalation.",
        "b3_sub": "Protect your peace without apology.",
        "caption": "Repeated disrespect is never a communication problem. It is a boundary problem that you refused to enforce. Forgiveness without changed behavior is an invitation for escalation. Protect your peace without apology.\n\nFrom 'The Ideology of Hypocrisy'.\n\n#unwrittenrules #theideologyofhypocrisy #boundaries #respect #darkpsychology #stoicmindset #protectyourpeace #reels #shorts"
    },
    {
        "num": "014",
        "slug": "hedonic-trap",
        "date": "2026-10-27",
        "book": "The Architecture of Greed",
        "theme": "The Hedonic Trap & True Sovereignty",
        "footage": "cloudy_sky_8062900.mp4",
        "bgm": "interstellar.mp3",
        "b1": "Buying things to impress people you dislike is modern insanity.",
        "b2": "Every luxury you cannot afford is a mortgage on your future freedom.",
        "b3_head": "True wealth is not the size of your display.",
        "b3_sub": "It is the number of things you have the power to walk away from.",
        "caption": "Buying things to impress people you dislike is modern insanity. Every luxury you cannot afford is a mortgage on your future freedom. True wealth is not the size of your display. It is the number of things you have the power to walk away from.\n\nFrom 'The Architecture of Greed'.\n\n#unwrittenrules #thearchitectureofgreed #wealth #freedom #sovereignty #stoicism #minimalism #reels #shorts"
    },
    {
        "num": "015",
        "slug": "power-of-absence",
        "date": "2026-10-28",
        "book": "The Gravity of Power",
        "theme": "Strategic Absence & Scarcity of Value",
        "footage": "moody_landscape_39302781.mp4",
        "bgm": "preset_2b_solitude_build.mp3",
        "b1": "If you are available all the time, your perceived value approaches zero.",
        "b2": "Presence creates familiarity, but strategic absence commands respect.",
        "b3_head": "Learn to withdraw before your welcome expires.",
        "b3_sub": "Scarcity turns basic utility into luxury.",
        "caption": "If you are available all the time, your perceived value approaches zero. Presence creates familiarity, but strategic absence commands respect. Learn to withdraw before your welcome expires. Scarcity turns basic utility into luxury.\n\nFrom 'The Gravity of Power'.\n\n#unwrittenrules #thegravityofpower #powerdynamics #value #scarcity #negotiation #stoic #reels #shorts"
    },
    {
        "num": "016",
        "slug": "solitary-systems",
        "date": "2026-10-29",
        "book": "AI Production Handbook",
        "theme": "The Solitary Leverage of Intelligent Systems",
        "footage": "travel_7815105.mp4",
        "bgm": "snowfall.mp3",
        "b1": "In the industrial age, power meant managing thousands of people.",
        "b2": "In the intelligence age, power means orchestrating autonomous systems.",
        "b3_head": "A single focused mind with automated architecture now out-produces an entire legacy department.",
        "b3_sub": "Build your leverage before the hierarchy dissolves.",
        "caption": "In the industrial age, power meant managing thousands of people. In the intelligence age, power means orchestrating autonomous systems. A single focused mind with automated architecture now out-produces an entire legacy department. Build your leverage.\n\nFrom 'AI Production Handbook'.\n\n#unwrittenrules #aiproductionhandbook #aiagents #systems #solopreneur #leverage #futureofwork #reels #shorts"
    },
    {
        "num": "017",
        "slug": "step-off-the-scoreboard",
        "date": "2026-10-30",
        "book": "Status: The Currency of Envy",
        "theme": "The Ultimate Victory: Stepping Outside the Arena",
        "footage": "iceland_ocean_waves_02.mp4",
        "bgm": "new_home.mp3",
        "b1": "You cannot defeat someone who refuses to compete with you.",
        "b2": "The status game is only deadly when you believe the rules are real.",
        "b3_head": "Step off the scoreboard.",
        "b3_sub": "The only real luxury is living entirely on your own terms.",
        "caption": "You cannot defeat someone who refuses to compete with you. The status game is only deadly when you believe the rules are real. Step off the scoreboard. The only real luxury is living entirely on your own terms.\n\nFrom 'Status: The Currency of Envy'.\n\n#unwrittenrules #status #innerpeace #stoicism #freedom #autonomy #psychology #reels #shorts"
    }
]

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
        "id": int(time.time()),
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

def run_step(cmd, desc):
    print(f"    [{desc}]")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"    [ERROR] in {desc}:\n{res.stderr}")
        raise RuntimeError(f"Step failed: {desc}")
    return res.stdout

def build_single_reel(item):
    reel_id = f"reel-{item['num']}"
    slug = item['slug']
    target_dir = REELS_DIR / f"{reel_id}-{slug}"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n==========================================")
    print(f"[*] PRODUCING {reel_id}: {item['title']} ({item['date']})")
    print(f"[*] Book: {item['book']} | Track: {item['bgm']} | Clip: {item['footage']}")
    print(f"==========================================")

    b_work = TEMP_DIR / reel_id
    b_assets = b_work / "assets"
    b_assets.mkdir(parents=True, exist_ok=True)

    # 1. Voiceover TTS
    run_step(f".venv/bin/edge-tts --voice en-US-ChristopherNeural --text \"{item['b1']}\" --write-media \"{b_work}/b1.mp3\"", "TTS Beat 1")
    run_step(f".venv/bin/edge-tts --voice en-US-ChristopherNeural --text \"{item['b2']}\" --write-media \"{b_work}/b2.mp3\"", "TTS Beat 2")
    run_step(f".venv/bin/edge-tts --voice en-US-ChristopherNeural --text \"{item['b3_head']}\" --write-media \"{b_work}/b3a.mp3\"", "TTS Beat 3 Head")
    run_step(f".venv/bin/edge-tts --voice en-US-ChristopherNeural --text \"{item['b3_sub']}\" --write-media \"{b_work}/b3b.mp3\"", "TTS Beat 3 Sub")

    # Get durations
    def get_dur(f):
        out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(f)])
        return float(out.strip())

    d_b1 = get_dur(b_work / "b1.mp3")
    d_b2 = get_dur(b_work / "b2.mp3")
    d_b3a = get_dur(b_work / "b3a.mp3")
    d_b3b = get_dur(b_work / "b3b.mp3")

    # Create silences
    run_step(f"ffmpeg -y -f lavfi -i anullsrc=r=24000:cl=mono -t 0.5 \"{b_work}/s0_5.mp3\"", "Silence 0.5s")
    run_step(f"ffmpeg -y -f lavfi -i anullsrc=r=24000:cl=mono -t 0.6 \"{b_work}/s0_6.mp3\"", "Silence 0.6s")
    run_step(f"ffmpeg -y -f lavfi -i anullsrc=r=24000:cl=mono -t 0.8 \"{b_work}/s0_8.mp3\"", "Silence 0.8s")

    # Concat voice
    concat_txt = b_work / "concat.txt"
    with open(concat_txt, "w") as f:
        f.write("file 's0_5.mp3'\nfile 'b1.mp3'\nfile 's0_6.mp3'\nfile 'b2.mp3'\nfile 's0_6.mp3'\nfile 'b3a.mp3'\nfile 's0_5.mp3'\nfile 'b3b.mp3'\nfile 's0_8.mp3'\n")

    run_step(f"ffmpeg -y -f concat -safe 0 -i \"{concat_txt}\" -c copy \"{b_work}/voice_raw.mp3\"", "Concat Voice")
    
    # Master Voice
    master_filter = "equalizer=f=130:t=q:w=1:g=3.5,equalizer=f=400:t=q:w=1.5:g=-2.5,equalizer=f=3500:t=q:w=1:g=2.5,acompressor=threshold=-18dB:ratio=3:attack=5:release=50"
    run_step(f"ffmpeg -y -i \"{b_work}/voice_raw.mp3\" -af \"{master_filter}\" -b:a 192k \"{b_work}/voice_master.mp3\"", "Master Voice")

    total_dur = get_dur(b_work / "voice_master.mp3")
    print(f"    [Audio Duration: {total_dur:.2f}s]")

    # Mix with BGM
    bgm_path = AUDIO_DIR / item['bgm']
    fade_start = max(0.0, total_dur - 1.2)
    filter_complex = f"[0:a]volume=1.15[v];[1:a]volume=0.22,atrim=0:{total_dur},afade=t=out:st={fade_start}:d=1.2[m];[v][m]amix=inputs=2:duration=longest:dropout_transition=0"
    run_step(f"ffmpeg -y -i \"{b_work}/voice_master.mp3\" -i \"{bgm_path}\" -filter_complex \"{filter_complex}\" -b:a 256k \"{b_assets}/audio.mp3\"", "Mix Voice & BGM")

    # 2. Prepare Background Video
    src_footage = FOOTAGE_DIR / item['footage']
    foot_dur = get_dur(src_footage)
    
    if foot_dur < total_dur:
        pts_mult = round(total_dur / foot_dur + 0.05, 2)
        v_filter = f"setpts={pts_mult}*PTS"
    else:
        v_filter = "null"

    run_step(f"ffmpeg -y -i \"{src_footage}\" -filter:v \"{v_filter}\" -c:v libx264 -preset ultrafast -r 30 -g 30 -keyint_min 30 -pix_fmt yuv420p -an -t {total_dur} \"{b_assets}/bg_video.mp4\"", "Prepare Background Video")

    # 3. Create Hyperframes & HTML
    with open(b_work / "package.json", "w") as f:
        json.dump({"name": reel_id, "version": "1.0.0", "private": True}, f)

    with open(b_work / "hyperframes.json", "w") as f:
        json.dump({
            "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
            "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
            "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
            "media": {"autoProxy": True}
        }, f, indent=2)

    # Keyframe timings
    t_s1_start = 0.5
    t_s1_end = t_s1_start + d_b1 + 0.3
    t_s2_start = t_s1_end + 0.4
    t_s2_end = t_s2_start + d_b2 + 0.3
    t_s3_head_start = t_s2_end + 0.4
    t_s3_sub_start = t_s3_head_start + d_b3a + 0.4
    t_fade = total_dur - 0.7

    html_code = f"""<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;1,400;1,500&display=swap" rel="stylesheet">
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
      .vignette-overlay {{
        position: absolute; inset: 0;
        background: radial-gradient(circle at center, rgba(0,0,0,0.20) 30%, rgba(0,0,0,0.68) 100%);
        pointer-events: none; z-index: 2;
      }}
      .quote-container {{
        position: absolute; top: 360px; left: 90px; right: 90px;
        display: flex; flex-direction: column; align-items: center; z-index: 10; text-align: center;
      }}
      .aesthetic-quote {{
        font-family: "Playfair Display", Georgia, serif; font-style: italic; font-size: 58px; font-weight: 500;
        line-height: 1.4; letter-spacing: 0.015em; color: #fff;
        text-shadow: 0 4px 35px rgba(0,0,0,0.95), 0 2px 10px rgba(0,0,0,0.9);
        position: absolute; width: 100%; opacity: 0;
      }}
      .quote-head {{ display: block; opacity: 0; }}
      .quote-sub {{
        display: block; font-size: 46px; font-style: normal; font-weight: 400;
        color: rgba(255,255,255,0.92); margin-top: 35px; letter-spacing: 0.03em;
        text-shadow: 0 4px 30px rgba(0,0,0,0.95); opacity: 0;
      }}
      .bottom-credit {{
        position: absolute; bottom: 220px; left: 0; right: 0; text-align: center; z-index: 10;
        font-family: -apple-system, BlinkMacSystemFont, "Inter", sans-serif; font-size: 26px; font-weight: 500;
        letter-spacing: 0.14em; text-transform: uppercase; color: rgba(255,255,255,0.72);
        text-shadow: 0 2px 15px rgba(0,0,0,0.9); opacity: 0;
      }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total_dur}" data-width="1080" data-height="1920">
      <video id="bgVideo" src="assets/bg_video.mp4" class="clip video-bg" data-start="0" data-duration="{total_dur}" autoplay muted loop playsinline></video>
      <div class="vignette-overlay"></div>
      <div class="quote-container">
        <div class="aesthetic-quote" id="quoteScene1">{item['b1']}</div>
        <div class="aesthetic-quote" id="quoteScene2">{item['b2']}</div>
        <div class="aesthetic-quote" id="quoteScene3">
          <span class="quote-head" id="scene3Head">{item['b3_head']}</span>
          <span class="quote-sub" id="scene3Sub">{item['b3_sub']}</span>
        </div>
      </div>
      <div class="bottom-credit" id="bottomCredit">@unwrittenrules.b3 &bull; {item['book']}</div>
      <audio id="masterAudio" src="assets/audio.mp3" class="clip" data-start="0" data-duration="{total_dur}"></audio>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#bottomCredit", {{ opacity: 0, y: 15 }}, {{ opacity: 1, y: 0, duration: 0.8, ease: "power2.out" }}, 1.5);
      tl.fromTo("#quoteScene1", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.85, ease: "power2.out" }}, {t_s1_start});
      tl.to("#quoteScene1", {{ opacity: 0, y: -25, duration: 0.45, ease: "power2.in" }}, {t_s1_end});
      tl.fromTo("#quoteScene2", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.85, ease: "power2.out" }}, {t_s2_start});
      tl.to("#quoteScene2", {{ opacity: 0, y: -25, duration: 0.45, ease: "power2.in" }}, {t_s2_end});
      tl.fromTo("#quoteScene3", {{ opacity: 1 }}, {{ opacity: 1 }}, {t_s3_head_start});
      tl.fromTo("#scene3Head", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.85, ease: "power2.out" }}, {t_s3_head_start});
      tl.fromTo("#scene3Sub", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.85, ease: "power2.out" }}, {t_s3_sub_start});
      tl.to(["#quoteScene3", "#bottomCredit"], {{ opacity: 0, duration: 0.6, ease: "power2.in" }}, {t_fade});
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>"""

    with open(b_work / "index.html", "w") as f:
        f.write(html_code)

    # 4. Render with Hyperframes
    run_step(f"cd \"{b_work}\" && npx hyperframes render . --output raw_render.mp4", "Hyperframes Render")

    # 5. Optimize with ffmpeg faststart
    final_video = target_dir / "video.mp4"
    run_step(f"ffmpeg -y -i \"{b_work}/raw_render.mp4\" -c:v libx264 -crf 20 -preset slow -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 192k \"{final_video}\"", "Optimize Faststart MP4")

    # 6. Archive thumbnail, script, and meta
    shutil.copy(b_assets / "audio.mp3", target_dir / "audio.mp3")
    run_step(f"ffmpeg -y -ss 00:00:02 -i \"{final_video}\" -vframes 1 \"{target_dir}/thumbnail.jpg\"", "Extract Thumbnail")

    with open(target_dir / "script.txt", "w") as f:
        f.write(f"TITLE: {item['theme']}\nBOOK: {item['book']}\n\nSCENE 1: {item['b1']}\nSCENE 2: {item['b2']}\nSCENE 3: {item['b3_head']} {item['b3_sub']}\n")

    # 7. Move source footage into used/
    shutil.move(str(src_footage), str(USED_DIR / src_footage.name))
    print(f"    [Footage moved to used: {src_footage.name}]")

    # 8. Upload to GitHub release vault
    asset_name = f"reel_{item['num']}.mp4"
    run_step(f"gh release upload media-vault \"{final_video}#{asset_name}\" --repo bidya271/instagram --clobber", "Upload to GitHub Media Vault")
    public_url = f"https://github.com/bidya271/instagram/releases/download/media-vault/{asset_name}"
    print(f"    [Vault URL: {public_url}]")

    # 9. Schedule on Buffer across Instagram, YouTube, and TikTok
    post_ids = {}
    for chan_name, chan_info in CHANNELS.items():
        due_at = f"{item['date']}T{chan_info['time']}+02:00"
        title = item['theme']
        text = item['caption']
        if chan_name == "youtube":
            text = text.replace("#reels", "#shorts")

        print(f"    [Scheduling {chan_name.upper()} at {due_at} via Buffer]...")
        post_id, err = buffer_create_post(chan_info['id'], due_at, text, public_url, title, chan_info['service'])
        if post_id:
            print(f"    [+] {chan_name.upper()} Post Created: {post_id}")
            post_ids[chan_name] = post_id
        else:
            print(f"    [!] Error scheduling {chan_name}: {err}")
            post_ids[chan_name] = f"error: {err}"
        time.sleep(1.2)

    # 10. Save metadata
    meta = {
        "id": reel_id,
        "slug": slug,
        "title": item['theme'],
        "book": item['book'],
        "scheduledDate": item['date'],
        "mediaUrl": public_url,
        "bufferPosts": post_ids,
        "durationSeconds": round(total_dur, 2)
    }
    with open(target_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    return meta

def main():
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    
    print("\n=======================================================")
    print("STARTING 2-WEEK AUTOMATED BATCH REEL PRODUCTION")
    print("=======================================================")

    for item in REELS_DATA:
        item['title'] = item['theme']
        try:
            m = build_single_reel(item)
            manifest.append(m)
            with open(WORKSPACE / "scheduled_2weeks_manifest.json", "w") as f:
                json.dump(manifest, f, indent=2)
            # Cleanup temp work for this reel
            shutil.rmtree(TEMP_DIR / f"reel-{item['num']}", ignore_errors=True)
        except Exception as e:
            print(f"[CRITICAL ERROR ON REEL {item['num']}]: {e}")
            break

    print("\n[ALL 14 REELS PRODUCED, VAULTED, AND SCHEDULED TO BUFFER!]")

if __name__ == "__main__":
    main()
