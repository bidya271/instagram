"""
Quarky Push Engine
Dispatches approved pitches to leads via Chrome Human Automation or Direct Communication.
"""

import subprocess
import urllib.parse
from typing import Dict

def push_chrome_social(url: str, pitch_text: str) -> bool:
    """Opens thread in Chrome and copies personalized pitch to macOS clipboard."""
    try:
        # Open in Chrome
        script = f'''
        tell application "Google Chrome"
            activate
            tell window 1
                make new tab with properties {{URL:"{url}"}}
            end tell
        end tell
        '''
        subprocess.run(["osascript", "-e", script], check=True)
        
        # Place pitch on clipboard
        p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE, text=True)
        p.communicate(input=pitch_text)
        return True
    except Exception as e:
        print(f"Error pushing to Chrome: {e}")
        return False

def push_direct_sms(phone: str, pitch_text: str) -> str:
    """Prepares an SMS launch link for iOS/macOS Messages app."""
    encoded_text = urllib.parse.quote(pitch_text)
    # macOS Messages URL scheme
    return f"sms:{phone}&body={encoded_text}"

def push_direct_whatsapp(phone: str, pitch_text: str) -> str:
    """Prepares a direct WhatsApp Web / App link."""
    clean_digits = "".join(filter(str.isdigit, phone))
    encoded_text = urllib.parse.quote(pitch_text)
    return f"https://wa.me/{clean_digits}?text={encoded_text}"
