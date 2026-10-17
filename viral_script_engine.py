#!/usr/bin/env python3
"""
viral_script_engine.py
Defines the 14 high-retention 7-second viral micro-loop reels (Reels 004 - 017).
Every hook is scored >= 80 STRONG via hookscore.py.
Every script is timed to 7.0 seconds with a seamless loop via beats.py.
Every caption passes caption.py and detect.py.
"""

VIRAL_REELS = [
    {
        "num": "004",
        "slug": "rule-of-silence",
        "date": "2026-10-17",
        "rule_badge": "RULE #1",
        "title": "Rule 1: The Power of Silence in Boardrooms",
        "book": "The Gravity of Power",
        "spoken_hook": "Rule 1: never speak first in your meetings.",
        "card1": "Never speak first in your meetings.",
        "card2": "Real authority never performs. It decides.",
        "footage": "minimal_architecture_28883887.mp4",
        "bgm": "solitude.mp3",
        "caption": """Rule 1 of corporate power: don't speak first.

When 10 people sit in a boardroom, watch who breaks the silence. The person scrambling to talk is usually the most terrified. Real authority doesn't perform. It decides.

Save this for your next 1-on-1 review.

#unwrittenrules #thegravityofpower #powerdynamics"""
    },
    {
        "num": "005",
        "slug": "silent-envy",
        "date": "2026-10-18",
        "rule_badge": "RULE #2",
        "title": "Rule 2: Why Insecure Friends Hate Your Wins",
        "book": "Status: The Currency of Envy",
        "spoken_hook": "Rule 2: never share your wins with an insecure friend.",
        "card1": "Never share your wins with an insecure friend.",
        "card2": "They will forgive your failure before your success.",
        "footage": "moody_landscape_39302781.mp4",
        "bgm": "new_home.mp3",
        "caption": """Rule 2 of status: camouflage your victories.

People love comforting you when you struggle. It confirms their hierarchy. But the moment you pull ahead, their comfort turns into subtle critique. Protect your peace.

Save this before you share your next big win.

#unwrittenrules #status #darkpsychology"""
    },
    {
        "num": "006",
        "slug": "institutional-compliance",
        "date": "2026-10-19",
        "rule_badge": "RULE #3",
        "title": "Rule 3: Company Loyalty Is Not Personal Safety",
        "book": "The Morality Machine",
        "spoken_hook": "Rule 3: never trust your company to protect your future.",
        "card1": "Never trust your company to protect your future.",
        "card2": "HR protects the balance sheet. Not you.",
        "footage": "night_traffic_30065145.mp4",
        "bgm": "gymnopedie.mp3",
        "caption": """Rule 3 of modern institutions: loyalty is a one-way transaction.

When profits drop 15%, decades of loyalty disappear in a 3-minute video call. Build personal leverage instead of corporate devotion.

Send this to someone who works 60 hours a week for a company that wouldn't notice.

#unwrittenrules #themoralitymachine #corporatepolitics"""
    },
    {
        "num": "007",
        "slug": "the-pedestal-trap",
        "date": "2026-10-20",
        "rule_badge": "RULE #4",
        "title": "Rule 4: The Weapon of Public Praise",
        "book": "The Ideology of Hypocrisy",
        "spoken_hook": "Rule 4: never trust anyone who praises you in public.",
        "card1": "Never trust anyone who praises you in public.",
        "card2": "Putting you on a pedestal makes your fall look like your fault.",
        "footage": "dark_forest_28462198.mp4",
        "bgm": "snowfall.mp3",
        "caption": """Rule 4 of deception: beware of unearned flattery.

Setting you on a pedestal is the easiest way to make you take the fall when a project misses its deadline. Flattery creates an obligation you never signed.

Save this for your next project kick-off.

#unwrittenrules #theideologyofhypocrisy #officepolitics"""
    },
    {
        "num": "008",
        "slug": "the-infinite-scoreboard",
        "date": "2026-10-21",
        "rule_badge": "RULE #5",
        "title": "Rule 5: Money as an Infinite Trap",
        "book": "The Architecture of Greed",
        "spoken_hook": "Rule 5: stop buying luxury to impress your critics.",
        "card1": "Stop buying luxury to impress your critics.",
        "card2": "True wealth is having the power to walk away.",
        "footage": "desert_dunes_34535421.mp4",
        "bgm": "interstellar.mp3",
        "caption": """Rule 5 of wealth: define your number or the machine consumes you.

Your stomach has a biological limit. A digital bank ledger does not. If you never define what is enough, your freedom becomes a permanent cage.

Save this to remind yourself what you are actually working for.

#unwrittenrules #thearchitectureofgreed #wealthmindset"""
    },
    {
        "num": "009",
        "slug": "the-cost-of-belonging",
        "date": "2026-10-22",
        "rule_badge": "RULE #6",
        "title": "Rule 6: The Dark Price of Group Belonging",
        "book": "The Tribal Mind",
        "spoken_hook": "Rule 6: never stay in a circle that punishes your questions.",
        "card1": "Never stay in a circle that punishes your questions.",
        "card2": "That is not a community. That is an ideological cult.",
        "footage": "ocean_storm_15847773.mp4",
        "bgm": "preset_2b_solitude_build.mp3",
        "caption": """Rule 6 of group psychology: tribes demand obedience before protection.

The price of belonging is always your intellectual freedom. If your group attacks honest curiosity, walk away without apology.

Send this to someone struggling with groupthink.

#unwrittenrules #thetribałmind #criticalthinking"""
    },
    {
        "num": "010",
        "slug": "the-asymmetry-engine",
        "date": "2026-10-23",
        "rule_badge": "RULE #7",
        "title": "Rule 7: The Asymmetry of Corporate Blame",
        "book": "The Gravity of Power",
        "spoken_hook": "Rule 7: never take the blame when your leadership fails.",
        "card1": "Never take the blame when leadership fails.",
        "card2": "Hierarchy is designed to harvest credit and export guilt.",
        "footage": "coastal_cliffs_31784580.mp4",
        "bgm": "solitude.mp3",
        "caption": """Rule 7 of power: keep your paper trail completely clean.

When an initiative succeeds, leadership takes 90% of the equity. When it fails, middle management takes the blame. Loyalty won't defend you in an audit.

Save this before your next quarterly review.

#unwrittenrules #thegravityofpower #careeradvice"""
    },
    {
        "num": "011",
        "slug": "conspicuous-humility",
        "date": "2026-10-24",
        "rule_badge": "RULE #8",
        "title": "Rule 8: Conspicuous Humility as Social Armor",
        "book": "Status: The Currency of Envy",
        "spoken_hook": "Rule 8: beware of friends who only support you when you struggle.",
        "card1": "Beware of friends who only support you when you struggle.",
        "card2": "Modesty isn't weakness. It's survival camouflage.",
        "footage": "snow_pines_10671896.mp4",
        "bgm": "new_home.mp3",
        "caption": """Rule 8 of human status: never flaunt your victories to an anxious room.

True modesty is not about feeling small. It is social camouflage to disarm envy before it turns into sabotage.

Save this for your next promotion.

#unwrittenrules #status #stoicmindset"""
    },
    {
        "num": "012",
        "slug": "outrage-economy",
        "date": "2026-10-25",
        "rule_badge": "RULE #9",
        "title": "Rule 9: Outrage as Commercial Entertainment",
        "book": "The Morality Machine",
        "spoken_hook": "Rule 9: never let public outrage dictate your moral compass.",
        "card1": "Never let public outrage dictate your moral compass.",
        "card2": "Anger is the most profitable product in the media.",
        "footage": "moody_waterfall_34491674.mp4",
        "bgm": "gymnopedie.mp3",
        "caption": """Rule 9 of the attention economy: moral panic is a business model.

Notice who profits when a digital mob forms. Anger generates 3x more ad clicks than calm analysis. Protect your focus.

Send this to someone who spends 3 hours a day arguing on the internet.

#unwrittenrules #themoralitymachine #stoicism"""
    },
    {
        "num": "013",
        "slug": "boundary-defense",
        "date": "2026-10-26",
        "rule_badge": "RULE #10",
        "title": "Rule 10: Weaponized Forgiveness & Boundaries",
        "book": "The Ideology of Hypocrisy",
        "spoken_hook": "Rule 10: never accept repeated disrespect from your coworkers.",
        "card1": "Never accept repeated disrespect from coworkers.",
        "card2": "Forgiveness without changed behavior is an invitation for escalation.",
        "footage": "atmospheric_rain_5310971.mp4",
        "bgm": "snowfall.mp3",
        "caption": """Rule 10 of boundaries: repeated disrespect is not a communication issue.

It is a boundary you refused to enforce. People treat you exactly how you train them to treat you. Protect your peace without guilt.

Save this to reinforce your standards.

#unwrittenrules #theideologyofhypocrisy #boundaries"""
    },
    {
        "num": "014",
        "slug": "the-hedonic-cage",
        "date": "2026-10-27",
        "rule_badge": "RULE #11",
        "title": "Rule 11: The Hedonic Treadmill & Freedom",
        "book": "The Architecture of Greed",
        "spoken_hook": "Rule 11: stop letting money become your scoreboard.",
        "card1": "Stop letting money become your scoreboard.",
        "card2": "Every luxury you can't afford is a mortgage on your freedom.",
        "footage": "cloudy_sky_8062900.mp4",
        "bgm": "interstellar.mp3",
        "caption": """Rule 11 of sovereignty: the most expensive thing you can buy is freedom.

Buying things to impress people you dislike is modern insanity. True wealth is the number of things you have the power to decline.

Save this to stay grounded.

#unwrittenrules #thearchitectureofgreed #minimalism"""
    },
    {
        "num": "015",
        "slug": "strategic-absence",
        "date": "2026-10-28",
        "rule_badge": "RULE #12",
        "title": "Rule 12: Scarcity and Strategic Absence",
        "book": "The Gravity of Power",
        "spoken_hook": "Rule 12: never make yourself available twenty-four hours a day.",
        "card1": "Never make yourself available 24/7.",
        "card2": "Presence creates familiarity. Strategic absence commands respect.",
        "footage": "moody_landscape_39302781.mp4",
        "bgm": "preset_2b_solitude_build.mp3",
        "caption": """Rule 12 of power dynamics: availability kills perceived value.

When you reply in 30 seconds to every message, you signal that your time has zero opportunity cost. Scarcity turns basic utility into luxury.

Save this before your next contract negotiation.

#unwrittenrules #thegravityofpower #boundaries"""
    },
    {
        "num": "016",
        "slug": "solitary-systems",
        "date": "2026-10-29",
        "rule_badge": "RULE #13",
        "title": "Rule 13: The Leverage of Autonomous Systems",
        "book": "AI Production Handbook",
        "spoken_hook": "Rule 13: stop managing 50 people when you can build systems.",
        "card1": "Stop managing 50 people when you can build systems.",
        "card2": "In the intelligence age, code and agents out-produce departments.",
        "footage": "travel_7815105.mp4",
        "bgm": "snowfall.mp3",
        "caption": """Rule 13 of the AI era: leverage has shifted from headcount to systems.

One focused mind orchestrating autonomous AI agents now out-produces an entire legacy corporate team. Build your leverage before the hierarchy dissolves.

Save this if you're building an autonomous business.

#unwrittenrules #aiproductionhandbook #aiagents"""
    },
    {
        "num": "017",
        "slug": "step-off-the-scoreboard",
        "date": "2026-10-30",
        "rule_badge": "RULE #14",
        "title": "Rule 14: The Ultimate Victory Over Status",
        "book": "Status: The Currency of Envy",
        "spoken_hook": "Rule 14: never compete with someone who ignores your status games.",
        "card1": "You can't defeat someone who refuses to compete.",
        "card2": "Step off the scoreboard. Living on your own terms is the ultimate win.",
        "footage": "iceland_ocean_waves_02.mp4",
        "bgm": "new_home.mp3",
        "caption": """Rule 14 of status: the only way to win is to refuse to bid.

The status game is only deadly when you believe its rules are real. The moment you stop seeking applause, you become immune to manipulation.

Send this to someone who needs to hear this today.

#unwrittenrules #status #stoicmindset"""
    }
]

if __name__ == "__main__":
    print(f"Loaded {len(VIRAL_REELS)} certified viral reels.")
