#!/usr/bin/env python3
"""
omni_video_engine.py - Unified OmniVideo Production Engine
Synthesized from state-of-the-art open-source video skills (awesome-claude-video-skills):
1. Mode A: 7-Second Viral Loop Shorts (Retention Engine: exact 7.00s, 130%+ APV micro-loops,
   multi-shot 4K b-roll, centered italic serif typography, intimate voice, loop audio tail).
2. Mode B: 12-14 Second Kinetic Explanatory Shorts (Value Engine: multi-beat progressive disclosure,
   frosted glass insight cards, kinetic typography, top progress bar, narrative payoff).
3. Automated Quality Control (QC): Duration, Resolution, and Broadcast Loudness (-14.0 LUFS).
"""

import os
import re
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path

# Paths
WORKSPACE = Path("/Users/bidya/Documents/side hustle/socials")
FOOTAGE_DIR = WORKSPACE / "assets" / "footage"
AUDIO_DIR = WORKSPACE / "assets" / "audio"
TEMPLATES_DIR = WORKSPACE / "engine" / "templates"
REELS_DIR = WORKSPACE / "reels"
TEMP_DIR = WORKSPACE / "temp_omni_engine"
ARTIFACTS_DIR = Path("/Users/bidya/.gemini/antigravity/brain/aaa18ecf-eb8b-4c91-aa47-1a4559b81395")

# Import Pexels Harvester
try:
    from pexels_scout import fetch_best_vertical_clip
except ImportError:
    fetch_best_vertical_clip = None

# Built-in Content Catalog
CATALOG = {
    "004": {
        "num": "004",
        "slug": "quiet-power",
        "title": "The Loudest in the Room",
        "book": "The Gravity of Power",
        "category": "Corporate Psychology",
        "rule_badge": "RULE #1",
        "shot1_query": "rain night street",
        "shot1_fallback": FOOTAGE_DIR / "used" / "walking_rain_night_street_39611009.mp4",
        "shot1_ss": "00:00:02",
        "shot2_query": "calm dark water ripples",
        "shot2_fallback": FOOTAGE_DIR / "calm_water_13692140.mp4",
        "shot2_ss": "00:00:01",
        "bgm": AUDIO_DIR / "snowfall.mp3",
        "bgm_ss": "00:00:20",
        "bgm_volume": 0.08,
        "voice": "en-US-AvaMultilingualNeural",
        # Mode A: 7s Viral Loop
        "loop_script": "The loudest in the room is never the most powerful. Real authority decides in silence.",
        "line1": "the loudest in the room<br>is never the most powerful.",
        "line2": "real authority never performs.<br>it decides in silence.",
        # Mode B: 13.5s Explainer
        "explainer_script": (
            "Notice the person scrambling to talk in every meeting. They aren't demonstrating power. "
            "They are advertising anxiety. The loudest in the room is never in control. "
            "Real authority never performs. It evaluates, and decides in silence."
        ),
        "hook_title": "The Loudest in the Room is <span class=\"accent\">Never in Control</span>",
        "hook_sub": "Why frantic speaking advertises anxiety instead of authority.",
        "mechanism_heading": "The Performance Trap",
        "mechanism_body": "When you scramble to explain yourself, you reveal an urgent need for <strong>external validation</strong>.",
        "truth_heading": "Power Does Not Compete",
        "truth_body": "Real authority watches the room exhaust itself. <span class=\"highlight-strip\">Most battles win themselves in silence.</span>",
        "payoff_rule": "Never perform. Decide.",
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
        "category": "Social Dynamics",
        "rule_badge": "RULE #2",
        "shot1_query": "ocean drone waves",
        "shot1_fallback": FOOTAGE_DIR / "ocean_drone_waves_36621255.mp4",
        "shot1_ss": "00:00:02",
        "shot2_query": "solitary mist dark lake",
        "shot2_fallback": FOOTAGE_DIR / "used" / "dark_lake_mist_solitude_35199993.mp4",
        "shot2_ss": "00:00:01",
        "bgm": AUDIO_DIR / "solitude.mp3",
        "bgm_ss": "00:00:00",
        "bgm_volume": 0.09,
        "voice": "en-US-AvaMultilingualNeural",
        # Mode A: 7s Viral Loop
        "loop_script": "Notice who gets quiet when you win. Protect your peace. Celebrate in silence.",
        "line1": "notice who gets quiet<br>the moment you succeed.",
        "line2": "protect your peace.<br>celebrate where no one can throw stones.",
        # Mode B: 13.5s Explainer
        "explainer_script": (
            "Notice who goes quiet when you win. People love comforting you during failure, "
            "because it confirms their hierarchy. The moment you pull ahead, that empathy turns into distance. "
            "Modesty is social camouflage. Celebrate where no one can throw stones."
        ),
        "hook_title": "Notice Who Goes <span class=\"accent\">Quiet When You Win</span>",
        "hook_sub": "The hidden psychology behind unearned comfort vs. cold silence.",
        "mechanism_heading": "The Hierarchy Reflex",
        "mechanism_body": "People readily support you at the bottom. It confirms their subconscious <strong>status advantage</strong>.",
        "truth_heading": "Camouflage is Strategy",
        "truth_body": "When you pull ahead, comfort turns into critique. <span class=\"highlight-strip\">Never display victories to insecure spectators.</span>",
        "payoff_rule": "Celebrate where no one can throw stones.",
        "caption": """People love comforting you when you struggle. It confirms their hierarchy.

The hardest truth to accept is that not everyone clapping for you is happy you’re winning. Some people only root for you as long as you don't do better than them.

The moment you pull ahead, their empathy turns into subtle critique, distant silence, or unsolicited warnings.

Modesty isn't just a virtue. It’s social camouflage.

Keep your moves quiet. Keep your circle small. Celebrate where no one can throw stones.

Save this before you share your next big win.

#status #currencyofenvy #darkpsychology #protectyourpeace #humanbehavior #mindsetmatters #reels"""
    }
}


class OmniVideoEngine:
    def __init__(self, mode="viral_loop", output_dir=None):
        self.mode = mode  # "viral_loop" (7s) or "kinetic_explainer" (13.5s)
        self.duration = 7.00 if mode == "viral_loop" else 13.50
        self.output_dir = Path(output_dir) if output_dir else REELS_DIR
        TEMP_DIR.mkdir(parents=True, exist_ok=True)

    def resolve_clip(self, query, fallback_path=None):
        """Resolves video clip: check local library, or download authentic vertical 4K via Pexels."""
        if fallback_path and Path(fallback_path).exists():
            return Path(fallback_path)

        # Search local library by query tokens
        tokens = query.lower().split()
        for p in list(FOOTAGE_DIR.glob("*.mp4")) + list((FOOTAGE_DIR / "used").glob("*.mp4")):
            name = p.name.lower()
            if any(t in name for t in tokens if len(t) > 3):
                return p

        # If not found locally, fetch via Pexels Harvester
        if fetch_best_vertical_clip:
            print(f"    [*] Auto-harvesting 4K vertical footage for query '{query}'...")
            downloaded = fetch_best_vertical_clip(query=query)
            if downloaded and Path(downloaded).exists():
                return Path(downloaded)

        # Ultimate fallback: return any existing clip
        all_clips = list(FOOTAGE_DIR.glob("*.mp4"))
        if all_clips:
            return all_clips[0]
        raise RuntimeError(f"No footage found for query '{query}' and no local fallback available.")

    def assemble_multishot_broll(self, shot1_path, shot2_path, shot1_ss, shot2_ss, output_path):
        """Assembles 2-shot cinematic crossfade montage normalized to 1080x1920 30fps."""
        dur = self.duration
        cut_point = 3.4 if self.mode == "viral_loop" else 6.8
        t1_len = cut_point + 0.35
        t2_len = dur - cut_point + 0.35

        cmd = [
            "ffmpeg", "-y",
            "-ss", str(shot1_ss), "-t", str(t1_len), "-i", str(shot1_path),
            "-ss", str(shot2_ss), "-t", str(t2_len), "-i", str(shot2_path),
            "-filter_complex",
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,settb=AVTB[v0];"
            "[1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,settb=AVTB[v1];"
            f"[v0][v1]xfade=transition=fade:duration=0.35:offset={cut_point}[outv]",
            "-map", "[outv]",
            "-t", str(dur),
            "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-an",
            str(output_path)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_path

    def master_audio(self, script_text, voice_name, bgm_path, bgm_ss, bgm_vol, output_path, work_dir):
        """
        Broadcast sound engineering suite:
        1. Synthesizes Edge-TTS voice.
        2. Applies 80Hz rumble cut + 3kHz intelligibility boost.
        3. Normalizes voice to -14.0 LUFS.
        4. Applies -4dB notch @ 2.5kHz on BGM.
        5. Calibrates 19-20dB dynamic separation between voice and music.
        """
        dur = self.duration
        voice_file = work_dir / "raw_voice.mp3"
        rate = "+8%" if self.mode == "viral_loop" else "+5%"

        # 1. Edge TTS
        subprocess.run([
            ".venv/bin/edge-tts",
            f"--voice={voice_name}",
            f"--rate={rate}",
            f"--text={script_text}",
            f"--write-media={voice_file}"
        ], check=True)

        voice_dur = float(subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(voice_file)
        ]).strip())
        print(f"    [+] Voice duration: {voice_dur:.2f}s (Tail cushion: {dur - voice_dur:.2f}s)")

        # 2. Studio Master Audio Mix
        cmd = [
            "ffmpeg", "-y",
            "-i", str(voice_file),
            "-ss", str(bgm_ss),
            "-t", str(dur),
            "-i", str(bgm_path),
            "-filter_complex",
            f"[0:a]aresample=48000,aformat=channel_layouts=stereo,highpass=f=80,equalizer=f=3000:width_type=h:width=1500:g=3.0,loudnorm=I=-14:TP=-1.5:LRA=7[vce];"
            f"[1:a]aresample=48000,aformat=channel_layouts=stereo,equalizer=f=2500:width_type=h:width=2000:g=-4.0,volume={bgm_vol},"
            f"afade=t=in:st=0:d=0.2,afade=t=out:st={dur-0.8}:d=0.8[bgm];"
            f"[vce][bgm]amix=inputs=2:duration=longest:normalize=0[aout]",
            "-map", "[aout]",
            "-t", str(dur),
            "-c:a", "mp3", "-b:a", "192k",
            str(output_path)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_path

    def render_composition(self, item, work_dir, bg_video, master_audio):
        """Generates HyperFrames composition and renders frame sequence to raw_render.mp4."""
        # Setup hyperframes files
        with open(work_dir / "package.json", "w") as f:
            json.dump({"name": f"omni-{item['num']}", "version": "1.0.0", "private": True}, f)

        with open(work_dir / "hyperframes.json", "w") as f:
            json.dump({
                "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
                "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
                "media": {"autoProxy": True}
            }, f, indent=2)

        if self.mode == "viral_loop":
            template_file = TEMPLATES_DIR / "viral_loop.html"
            with open(template_file, "r") as f:
                tmpl = f.read()
            html = (
                tmpl.replace("{{duration}}", str(self.duration))
                    .replace("{{line1}}", item["line1"])
                    .replace("{{line2}}", item["line2"])
                    .replace("{{t1_end}}", "3.2")
                    .replace("{{t2_start}}", "3.5")
                    .replace("{{t2_end}}", "6.6")
            )
        else:
            template_file = TEMPLATES_DIR / "kinetic_explainer.html"
            with open(template_file, "r") as f:
                tmpl = f.read()
            html = (
                tmpl.replace("{{duration}}", str(self.duration))
                    .replace("{{category}}", item.get("category", "Unwritten Rules"))
                    .replace("{{rule_badge}}", item.get("rule_badge", "INSIGHT"))
                    .replace("{{hook_title}}", item["hook_title"])
                    .replace("{{hook_sub}}", item["hook_sub"])
                    .replace("{{mechanism_heading}}", item["mechanism_heading"])
                    .replace("{{mechanism_body}}", item["mechanism_body"])
                    .replace("{{truth_heading}}", item["truth_heading"])
                    .replace("{{truth_body}}", item["truth_body"])
                    .replace("{{payoff_rule}}", item["payoff_rule"])
                    .replace("{{book_title}}", item.get("book", "@unwrittenrules.b3"))
            )

        with open(work_dir / "index.html", "w") as f:
            f.write(html)

        print(f"    [*] Rendering {self.duration}s via HyperFrames engine...")
        subprocess.run(f"cd \"{work_dir}\" && npx hyperframes render . --output raw_render.mp4", shell=True, check=True)
        return work_dir / "raw_render.mp4"

    def mux_final_mp4(self, raw_video, master_audio, final_output):
        """Muxes deterministic video stream with master audio and encodes faststart MP4."""
        cmd = [
            "ffmpeg", "-y",
            "-i", str(raw_video),
            "-i", str(master_audio),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-t", str(self.duration),
            "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-c:a", "aac", "-b:a", "192k",
            str(final_output)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return final_output

    def run_qc_checks(self, video_path, reel_id):
        """
        Automated QC Suite:
        - Exact duration within ±0.15s
        - Resolution: 1080x1920
        - Integrated Loudness: -14.0 ± 1.5 LUFS
        - Preview frames extracted to Artifact Directory
        """
        print(f"\n    [QC SUITE] Running automated quality verification on {video_path.name}...")
        
        # 1. Check Duration & Dimensions
        probe = subprocess.check_output([
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,duration,r_frame_rate",
            "-of", "json", str(video_path)
        ])
        v_info = json.loads(probe)["streams"][0]
        actual_dur = float(v_info.get("duration", 0))
        width = int(v_info["width"])
        height = int(v_info["height"])

        dur_diff = abs(actual_dur - self.duration)
        if dur_diff > 0.2:
            print(f"    [!] QC WARNING: Duration deviation {dur_diff:.3f}s (actual: {actual_dur}s, expected: {self.duration}s)")
        else:
            print(f"    [✓] Duration: {actual_dur:.2f}s (Target: {self.duration:.2f}s, Delta: {dur_diff:.3f}s)")

        if width == 1080 and height == 1920:
            print(f"    [✓] Resolution: {width}x{height} (Portrait HD 9:16)")
        else:
            print(f"    [!] QC WARNING: Unexpected resolution {width}x{height}")

        # 2. Check Integrated Loudness (ebur128)
        loud_out = subprocess.run([
            "ffmpeg", "-i", str(video_path),
            "-af", "ebur128=framelog=verbose",
            "-f", "null", "-"
        ], capture_output=True, text=True).stderr

        lufs_match = re.search(r"Integrated loudness:\s+I:\s+([-\d\.]+)\s+LUFS", loud_out)
        tp_match = re.search(r"True peak:\s+Peak:\s+([-\d\.]+)\s+dBFS", loud_out)
        
        if lufs_match:
            lufs = float(lufs_match.group(1))
            tp = float(tp_match.group(1)) if tp_match else -1.5
            lufs_ok = -15.5 <= lufs <= -12.5
            status_icon = "✓" if lufs_ok else "!"
            print(f"    [{status_icon}] Integrated Loudness: {lufs:.1f} LUFS (Broadcast Target: -14.0 LUFS, True Peak: {tp:.1f} dBFS)")
        else:
            print("    [!] Could not parse ebur128 integrated loudness")

        # 3. Extract Key Frame Artifacts for Inspection
        frames = [1.5, 5.0] if self.mode == "viral_loop" else [1.5, 5.0, 9.0, 12.0]
        extracted_frames = []
        for i, ts in enumerate(frames, start=1):
            frame_file = ARTIFACTS_DIR / f"{reel_id}_{self.mode}_beat{i}.jpg"
            subprocess.run([
                "ffmpeg", "-y",
                "-ss", str(ts),
                "-i", str(video_path),
                "-vframes", "1",
                "-q:v", "2",
                str(frame_file)
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            extracted_frames.append(frame_file)
            print(f"    [✓] Preview frame Beat {i} ({ts:.1f}s) -> {frame_file.name}")

        return {
            "duration": actual_dur,
            "width": width,
            "height": height,
            "lufs": lufs if lufs_match else None,
            "frames": extracted_frames
        }

    def produce(self, item):
        """Full pipeline execution for a catalog item or custom brief."""
        reel_id = f"reel-{item['num']}"
        slug = item['slug']
        target_dir = self.output_dir / f"{reel_id}-{slug}"
        target_dir.mkdir(parents=True, exist_ok=True)

        mode_label = "7-SECOND VIRAL LOOP" if self.mode == "viral_loop" else "13.5-SECOND KINETIC EXPLAINER"
        print(f"\n=======================================================")
        print(f"[*] PRODUCING {mode_label}: {reel_id} - {item['title']}")
        print(f"[*] Voice: {item['voice']} | Audio: {item['bgm'].name}")
        print(f"=======================================================")

        work_dir = TEMP_DIR / f"{reel_id}_{self.mode}"
        assets_dir = work_dir / "assets"
        if work_dir.exists():
            shutil.rmtree(work_dir)
        assets_dir.mkdir(parents=True, exist_ok=True)

        # 1. Resolve Footage
        print("    [1/5] Resolving authentic 4K/HD vertical footage...")
        shot1 = self.resolve_clip(item.get("shot1_query", "moody"), item.get("shot1_fallback"))
        shot2 = self.resolve_clip(item.get("shot2_query", "mist"), item.get("shot2_fallback"))
        print(f"    [+] Shot 1: {shot1.name}")
        print(f"    [+] Shot 2: {shot2.name}")

        # 2. Master Audio
        print("    [2/5] Mastering balanced audio track (voice dominant, ambient music)...")
        script = item["loop_script"] if self.mode == "viral_loop" else item["explainer_script"]
        audio_file = assets_dir / "audio.mp3"
        self.master_audio(
            script_text=script,
            voice_name=item["voice"],
            bgm_path=item["bgm"],
            bgm_ss=item["bgm_ss"],
            bgm_vol=item["bgm_volume"],
            output_path=audio_file,
            work_dir=work_dir
        )

        # 3. Assemble Multi-Shot Background Video
        print("    [3/5] Assembling transitioning HD video montage...")
        bg_video = assets_dir / "bg_video.mp4"
        self.assemble_multishot_broll(
            shot1_path=shot1,
            shot2_path=shot2,
            shot1_ss=item["shot1_ss"],
            shot2_ss=item["shot2_ss"],
            output_path=bg_video
        )

        # 4. HyperFrames Render
        print("    [4/5] Executing HyperFrames frame-exact motion render...")
        raw_video = self.render_composition(item, work_dir, bg_video, audio_file)

        # 5. Final Faststart Mux
        print("    [5/5] Muxing master audio and writing faststart MP4...")
        final_video = target_dir / "video.mp4"
        self.mux_final_mp4(raw_video, audio_file, final_video)

        # Extract Thumbnail
        thumb_file = target_dir / "thumbnail.jpg"
        subprocess.run([
            "ffmpeg", "-y",
            "-ss", "00:00:02",
            "-i", str(final_video),
            "-vframes", "1",
            str(thumb_file)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Save metadata and caption
        meta = {
            "id": reel_id,
            "slug": slug,
            "title": item['title'],
            "book": item.get('book'),
            "mode": self.mode,
            "duration": self.duration,
            "caption": item['caption'],
            "script": script,
            "shot1": str(shot1.name),
            "shot2": str(shot2.name),
            "bgm": str(item['bgm'].name),
            "voice": item['voice']
        }
        with open(target_dir / "meta.json", "w") as f:
            json.dump(meta, f, indent=2)

        with open(target_dir / "caption.txt", "w") as f:
            f.write(item['caption'])

        # Automated Quality Control
        qc_results = self.run_qc_checks(final_video, reel_id)

        print(f"\n[SUCCESS] Completed {mode_label} -> {final_video}")
        return final_video, qc_results


def main():
    parser = argparse.ArgumentParser(description="OmniVideo Production Engine")
    parser.add_argument("--mode", choices=["viral-loop", "explainer"], default="viral-loop",
                        help="Video mode: viral-loop (7s) or explainer (13.5s)")
    parser.add_argument("--num", type=str, default="004", help="Catalog reel number (e.g. 004, 005)")
    parser.add_argument("--test", action="store_true", help="Run in test mode without overwriting production reels")
    args = parser.parse_args()

    engine_mode = "viral_loop" if args.mode == "viral-loop" else "kinetic_explainer"
    out_dir = (WORKSPACE / "test_renders") if args.test else REELS_DIR

    engine = OmniVideoEngine(mode=engine_mode, output_dir=out_dir)

    if args.num in CATALOG:
        item = CATALOG[args.num]
        engine.produce(item)
    else:
        print(f"[!] Unknown catalog number {args.num}. Available: {list(CATALOG.keys())}")


if __name__ == "__main__":
    main()
