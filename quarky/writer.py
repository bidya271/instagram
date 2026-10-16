"""
Quarky Sales Pitch Generator
Generates high-converting, human 1-to-1 B2C sales pitches tailored to the lead's channel & context.
"""

from typing import Dict

def generate_pitch(lead: Dict, config: Dict) -> str:
    """Generates an authentic, objection-proof sales pitch for the lead."""
    app_key = lead.get("target_app", "tracksub")
    source = lead.get("source", "contact_list")
    context = lead.get("context_snippet", "")
    name = lead.get("name", "").strip()
    first_name = name.split()[0] if name else ""

    if app_key == "tracksub":
        if source == "contact_list":
            greeting = f"Hey {first_name}," if first_name else "Hey,"
            return (
                f"{greeting} quick question—are you still paying for recurring subscriptions you barely use?\n\n"
                f"We just dropped an AI feature on TrackSub (https://tracksub.app): you upload a screenshot of your bank statement "
                f"or Apple subscriptions, and it instantly maps every renewal date and provides 1-click cancel links. "
                f"No bank logins or passwords needed. Free to track up to 5 apps, take a look if you want to kill some subscription waste!"
            )
        else: # social/reddit/threads
            return (
                f"I dealt with the exact same headache with forgotten renewals.\n\n"
                f"I built TrackSub (https://tracksub.app) to fix this without linking bank credentials. "
                f"You just take a screenshot of your statement or subscriptions page and our AI parses the renewal dates & costs automatically. "
                f"It gives 3-day alerts before charges hit and 1-click cancel guides so you don't get trapped. Free on iOS and Web!"
            )

    else: # feelsright
        if source == "contact_list":
            greeting = f"Hey {first_name}," if first_name else "Hey,"
            return (
                f"{greeting} wanted to share something we built for keeping close relationships strong:\n\n"
                f"It's called FeelsRight (https://feelsright.me) on iOS. It's a 30-second daily check-in that quietly shows your partner or best friend "
                f"how you're holding up without raw scores, pressure, or streaks. Voice notes stay on your device, completely free with no ads. "
                f"Check it out with your person if you want an easy way to stay connected!"
            )
        else:
            return (
                f"Staying genuinely close without constant texting or 'how was your day' interrogations is tough.\n\n"
                f"My partner and I built FeelsRight (https://feelsright.me) for this: a quiet 30-second daily emotional check-in where your partner sees "
                f"your emotional 'shape' instead of numbers or pressure. No streaks, no trivia, 100% free on iOS, and voice notes never leave your phone."
            )
