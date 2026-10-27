"""
pusher.py — Execution bridge: opens Chrome + copies pitch to clipboard
macOS: uses osascript + pbcopy
Linux: uses xdg-open + xclip (fallback)
Windows: uses subprocess start + pyperclip
"""
import subprocess, sys, platform, shutil
from quarky import db

def _copy_to_clipboard(text: str) -> bool:
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["pbcopy"], input=text.encode(), check=True)
            return True
        elif system == "Linux":
            if shutil.which("xclip"):
                subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), check=True)
                return True
            elif shutil.which("xsel"):
                subprocess.run(["xsel", "--clipboard", "--input"], input=text.encode(), check=True)
                return True
        elif system == "Windows":
            subprocess.run(["clip"], input=text.encode(), check=True)
            return True
    except Exception as e:
        print(f"  [pusher] Clipboard error: {e}")
    return False

def _open_url_in_chrome(url: str) -> bool:
    system = platform.system()
    try:
        if system == "Darwin":
            script = f'''
tell application "Google Chrome"
    activate
    open location "{url}"
end tell
'''
            subprocess.run(["osascript", "-e", script], check=True)
            return True
        elif system == "Linux":
            for browser in ["google-chrome", "chromium-browser", "chromium", "firefox"]:
                if shutil.which(browser):
                    subprocess.Popen([browser, url])
                    return True
            subprocess.Popen(["xdg-open", url])
            return True
        elif system == "Windows":
            subprocess.Popen(["start", "chrome", url], shell=True)
            return True
    except Exception as e:
        print(f"  [pusher] Browser open error: {e}")
    return False

def push_outbox_item(outbox_id: int, custom_pitch: str = None) -> dict:
    """
    Opens the lead URL in Chrome and copies pitch to clipboard.
    Accepts optional custom_pitch if the user edited it in the UI.
    Returns {"success": bool, "message": str}
    """
    db.init_db()
    with db._conn() as c:
        if custom_pitch:
            c.execute("UPDATE outbox SET pitch_text=? WHERE outbox_id=?", (custom_pitch, outbox_id))
        row = c.execute(
            "SELECT o.*, l.identifier, l.source FROM outbox o JOIN leads l ON o.lead_id=l.lead_id WHERE o.outbox_id=?",
            (outbox_id,)
        ).fetchone()

    if not row:
        return {"success": False, "message": "Outbox item not found"}

    row = dict(row)
    url = row.get("identifier", "")
    pitch = custom_pitch if custom_pitch else row.get("pitch_text", "")

    clipboard_ok = _copy_to_clipboard(pitch)
    browser_ok = _open_url_in_chrome(url)

    if clipboard_ok and browser_ok:
        db.update_outbox_status(outbox_id, "sent")
        db.update_lead_status(row["lead_id"], "pushed")
        db.log_activity(row["lead_id"], "pushed", f"outbox_id={outbox_id}")
        return {"success": True, "message": f"Opened in browser. Pitch copied to clipboard — just paste (Cmd+V / Ctrl+V)."}
    elif clipboard_ok:
        return {"success": True, "message": f"Pitch copied to clipboard. Open manually: {url}"}
    else:
        return {"success": False, "message": f"Could not open browser or clipboard. URL: {url}"}

def reject_outbox_item(outbox_id: int) -> dict:
    db.init_db()
    with db._conn() as c:
        row = c.execute("SELECT lead_id FROM outbox WHERE outbox_id=?", (outbox_id,)).fetchone()
    if row:
        db.update_outbox_status(outbox_id, "rejected")
        db.log_activity(row["lead_id"], "rejected", f"outbox_id={outbox_id}")
    return {"success": True, "message": "Rejected and archived."}
