#!/usr/bin/env python3
"""
batch_produce_next_3.py - Produces Reels 021, 022, 023 via Creator-Critic Pipeline
Channel: @unwrittenrules.b3
"""

import sys
import json
import shutil
import subprocess
from pathlib import Path

WORKSPACE = Path("/Users/bidya/Documents/side hustle/socials")
REELS_DIR = WORKSPACE / "reels"
TEMP_DIR = WORKSPACE / "temp_next_3"
ARTIFACTS_DIR = Path("/Users/bidya/.gemini/antigravity/brain/0856c0d7-0199-4618-9b57-0caca9390c2c")

sys.path.insert(0, str(WORKSPACE))
from creator_critic_pipeline import CreatorAgent, CriticAgent, ProductionEngine

REELS_SPECS = [
    {
        "num": "021",
        "slug": "bigger-shovel",
        "title": "The Performance Punishment",
        "book": "The Gravity of Power",
        "theme": "Strategic Incompetence & Institutional Extraction",
        "spoken": "If you are good at digging holes, they just give you a bigger shovel.",
        "line1": "if you are good at digging holes,",
        "line2": "they just give you a bigger shovel.",
        "shot1_scenario": "Tired exhausted office worker staring at screens in dark corporate office late at night",
        "shot1_query": "tired man office computer night",
        "shot2_scenario": "Corporate executive silhouette walking through luxury modern architectural hallway",
        "shot2_query": "businessman walking luxury dark",
        "bgm_track": "solitude.mp3",
        "bgm_ss": "00:00:00",
        "bgm_volume": 0.18,
        "caption": """The unspoken rule of corporate efficiency:

Extreme competence is never rewarded with freedom. It is rewarded with more work.

If you prove that you can dig holes faster than anyone else in the room, management doesn't promote you out of the ditch. They hand you a bigger shovel.

True leverage isn't advertising infinite capacity. True leverage is knowing what to withhold.

Save this before you volunteer for your next assignment.

#thegravityofpower #powerdynamics #corporatepsychology #humanbehavior #stoicmindset #unwrittenrules #reels #shorts""",
        "hashtags": "#thegravityofpower #powerdynamics #corporatepsychology #humanbehavior #stoicmindset #unwrittenrules #reels #shorts"
    },
    {
        "num": "022",
        "slug": "false-cheerleader",
        "title": "The Hierarchy of Empathy",
        "book": "Status: The Currency of Envy",
        "theme": "Peer Competition & Covert Jealousy",
        "spoken": "Some people only support you, as long as you fail to compete.",
        "line1": "some people only support you,",
        "line2": "as long as you fail to compete.",
        "shot1_scenario": "Polite formal corporate handshake between two figures in sharp silhouettes",
        "shot1_query": "handshake business meeting shadow",
        "shot2_scenario": "Intense close-up of cold calculating eyes watching from shadowy vehicle interior",
        "shot2_query": "dramatic eyes shadow man",
        "bgm_track": "snowfall.mp3",
        "bgm_ss": "00:00:20",
        "bgm_volume": 0.16,
        "caption": """People love being empathetic when you struggle. It confirms their hierarchy.

The hardest truth of human nature is that not everyone clapping for you wants you to win. Some people only root for your recovery so long as you remain below them.

The moment your momentum threatens their status, their support turns into subtle critique, silence, or unsolicited caution.

Keep your wins quiet. Celebrate in silence.

Save this before you announce your next goal.

#currencyofenvy #status #darkpsychology #humanbehavior #protectyourpeace #stoicmindset #reels #shorts""",
        "hashtags": "#currencyofenvy #status #darkpsychology #humanbehavior #protectyourpeace #stoicmindset #reels #shorts"
    },
    {
        "num": "023",
        "slug": "selling-time",
        "title": "The Golden Handcuffs",
        "book": "The Architecture of Greed",
        "theme": "Wealth as Scoreboard & Cognitive Traps",
        "spoken": "The price of selling your time, is forgetting what it was worth.",
        "line1": "the price of selling your time,",
        "line2": "is forgetting what it was worth.",
        "shot1_scenario": "Close-up of luxury gold wristwatch ticking in cinematic dark lighting",
        "shot1_query": "luxury watch dark close up",
        "shot2_scenario": "Solitary silhouette walking slowly alone on a rain-slicked city bridge at twilight",
        "shot2_query": "lone man walking city night rain",
        "bgm_track": "solitude.mp3",
        "bgm_ss": "00:00:44",
        "bgm_volume": 0.18,
        "caption": """The ultimate irony of financial ambition:

You exchange your irreplaceable hours for currency, telling yourself you will buy your freedom back later.

By the time the account is full, your tastes have inflated, your energy has depreciated, and the habits of obedience have hardened into your personality.

The price of selling your time isn't just exhaustion. It is forgetting that time was the only wealth you ever had.

Save this as a reminder of what you are actually trading.

#thearchitectureofgreed #moneypsychology #humanbehavior #freedommindset #stoicism #unwrittenrules #reels #shorts""",
        "hashtags": "#thearchitectureofgreed #moneypsychology #humanbehavior #freedommindset #stoicism #unwrittenrules #reels #shorts"
    }
]

def produce_all():
    results = []
    critic = CriticAgent(pass_threshold=8.5)

    for item in REELS_SPECS:
        reel_id = f"reel-{item['num']}"
        print(f"\n=======================================================")
        print(f"[*] INITIATING PRODUCTION: {reel_id} - {item['title']}")
        print(f"[*] Book: {item['book']} | Theme: {item['theme']}")
        print(f"=======================================================")

        creator = CreatorAgent(book_title=item['book'], rule_theme=item['theme'])
        proposal = creator.draft_proposal(
            reel_num=item['num'],
            slug=item['slug'],
            title=item['title'],
            script_data=item
        )

        review = critic.evaluate(proposal)
        print("=== CRITIC EVALUATION ===")
        print(json.dumps(review, indent=2))

        if review["verdict"] != "APPROVED":
            print(f"[!] Critic REJECTED {reel_id}: {review['issues']}")
            continue

        work_dir = TEMP_DIR / reel_id
        engine = ProductionEngine(work_dir)

        # 1. Scout Footage
        clip1, clip2 = engine.prepare_stock_footage(proposal)

        # 2. Synthesize & Master Audio
        audio = engine.synthesize_audio(proposal)

        # 3. Multi-Shot Montage
        bg_video = engine.build_video_montage(clip1, clip2)

        # 4. Render 7s Master Video
        final_video, thumbnail = engine.render_composition(proposal, audio)

        # 5. Mark Footage Used
        engine.mark_footage_used(clip1, clip2)

        # 6. Archive to reels/
        target_dir = REELS_DIR / f"{reel_id}-{item['slug']}"
        target_dir.mkdir(parents=True, exist_ok=True)
        archived_video = target_dir / "video.mp4"
        archived_thumb = target_dir / "thumbnail.jpg"
        
        shutil.copy(str(final_video), str(archived_video))
        shutil.copy(str(thumbnail), str(archived_thumb))

        with open(target_dir / "script.txt", "w") as f:
            f.write(proposal["script"] + "\n")

        with open(target_dir / "caption.txt", "w") as f:
            f.write(proposal["caption"] + "\n")

        meta = {
            "id": reel_id,
            "num": item["num"],
            "slug": item["slug"],
            "title": item["title"],
            "book": item["book"],
            "theme": item["theme"],
            "duration": 7.00,
            "script": proposal["script"],
            "bgm": proposal["bgm_track"],
            "shot1": clip1.name,
            "shot2": clip2.name,
            "critic_score": review["average_score"],
            "caption": proposal["caption"]
        }
        with open(target_dir / "meta.json", "w") as f:
            json.dump(meta, f, indent=2)

        # 7. Extract inspection frames for chat preview
        f1_path = ARTIFACTS_DIR / f"{reel_id}_shot1.jpg"
        f2_path = ARTIFACTS_DIR / f"{reel_id}_shot2.jpg"
        
        import subprocess
        subprocess.run(["ffmpeg", "-y", "-ss", "00:00:01.8", "-i", str(archived_video), "-vframes", "1", str(f1_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["ffmpeg", "-y", "-ss", "00:00:05.2", "-i", str(archived_video), "-vframes", "1", str(f2_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        results.append({
            "reel_id": reel_id,
            "title": item["title"],
            "book": item["book"],
            "video_path": str(archived_video),
            "thumb_path": str(archived_thumb),
            "shot1_frame": str(f1_path),
            "shot2_frame": str(f2_path),
            "critic_score": review["average_score"],
            "script": item["spoken"],
            "caption": item["caption"],
            "shot1": clip1.name,
            "shot2": clip2.name,
            "bgm": item["bgm_track"]
        })

    with open(TEMP_DIR / "production_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\n[SUCCESS] Batch production complete for all 3 reels!")

if __name__ == "__main__":
    produce_all()
