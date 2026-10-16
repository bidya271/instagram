#!/usr/bin/env python3
"""
Human-Like Chrome Social Automator for Reddit & Threads (macOS Native)
Operates through your live Google Chrome browser profile:
- No developer consoles or API keys required
- Uses your existing logged-in sessions (Reddit, Threads, etc.)
- Human-like pacing, typing, and tab navigation via macOS Apple Events
"""

import os
import sys
import time
import random
import subprocess
from typing import Optional

CHROME_APP = "Google Chrome"

def run_applescript(script: str) -> str:
    """Executes an AppleScript command targeting Google Chrome."""
    process = subprocess.Popen(["osascript", "-e", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"AppleScript error: {stderr.strip()}")
    return stdout.strip()

def open_url_in_chrome(url: str, new_tab: bool = True):
    """Opens a target discussion thread in your existing Google Chrome window."""
    if new_tab:
        script = f'''
        tell application "{CHROME_APP}"
            activate
            tell window 1
                make new tab with properties {{URL:"{url}"}}
            end tell
        end tell
        '''
    else:
        script = f'''
        tell application "{CHROME_APP}"
            activate
            set URL of active tab of window 1 to "{url}"
        end tell
        '''
    run_applescript(script)

def simulate_human_reading(min_seconds: float = 3.0, max_seconds: float = 6.0):
    """Simulates realistic human reading and pause time."""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def focus_and_paste_text(text: str):
    """Copies the text to clipboard and simulates keyboard paste to avoid bot typing flags."""
    # Place text on macOS clipboard
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE, text=True)
    p.communicate(input=text)
    
    # Simulate Cmd+V via System Events
    script = '''
    tell application "System Events"
        keystroke "v" using command down
    end tell
    '''
    run_applescript(script)

def run_scout_and_open(app_name: str, target_url: str, comment_text: str):
    """
    1. Opens target thread in real Chrome window
    2. Copies pre-written founder comment to clipboard
    3. Prompts user to review and submit with 1 click
    """
    print("=" * 60)
    print(f"🤖 CHROME COPILOT: Launching for {app_name.upper()}")
    print("=" * 60)
    print(f"Opening discussion in Chrome: {target_url}")
    open_url_in_chrome(target_url)
    
    # Set clipboard to comment
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE, text=True)
    p.communicate(input=comment_text)

    print("\n📋 Drafted Founder Reply (already copied to your clipboard!):")
    print("-" * 60)
    print(comment_text)
    print("-" * 60)
    print("\n👉 Chrome is now open at the thread.")
    print("Simply click the comment box and hit Cmd+V (Paste) to review & post!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Human Chrome Social Automation")
    parser.add_argument("--app", choices=["tracksub", "feelsright"], default="tracksub")
    args = parser.parse_args()

    if args.app == "tracksub":
        url = "https://www.reddit.com/r/ProductivityApps/comments/example"
        comment = (
            "I dealt with the exact same frustration myself. "
            "I built TrackSub (https://tracksub.app) to solve this without connecting bank credentials. "
            "You can drop in a screenshot of your subscriptions or bank statement and the AI parses it automatically, "
            "plus it gives you 3-day renewal alerts and 1-click cancel links. It's free up to 5 subscriptions, and $1/mo for unlimited."
        )
        run_scout_and_open("TrackSub", url, comment)
    else:
        url = "https://www.reddit.com/r/LongDistance/comments/example"
        comment = (
            "Staying close without constant texting or interrogation is something my partner and I struggled with too. "
            "We built FeelsRight (https://feelsright.me) for this: a quiet 30-second daily check-in where your partner sees your "
            "emotional 'shape' rather than raw numbers or pressure. No streaks, no trivia, 100% free on iOS."
        )
        run_scout_and_open("FeelsRight", url, comment)
