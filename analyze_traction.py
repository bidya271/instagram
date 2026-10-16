import json

with open("/Users/bidya/.gemini/antigravity/brain/aaa18ecf-eb8b-4c91-aa47-1a4559b81395/.system_generated/steps/568/output.txt", "r") as f:
    line = f.readline().strip()
    data = json.loads(line)

posts = []
for edge in data.get("edges", []):
    node = edge.get("node", {})
    if node.get("status") == "sent":
        metrics_dict = {}
        for m in node.get("metrics") or []:
            metrics_dict[m.get("type")] = m.get("value")
        
        sent_date = (node.get("sentAt") or "Unknown")[:10]
        posts.append({
            "id": node.get("id"),
            "sentAt": sent_date,
            "text": node.get("text", "").replace("\n", " "),
            "views": metrics_dict.get("views", 0),
            "reach": metrics_dict.get("reach", 0),
            "reactions": metrics_dict.get("reactions", 0),
            "shares": metrics_dict.get("shares", 0),
            "comments": metrics_dict.get("comments", 0),
            "engRate": metrics_dict.get("engagementRate", 0),
            "avgWatchSec": metrics_dict.get("averageTimeWatched", 0),
            "totalWatchMin": metrics_dict.get("totalTimeWatched", 0)
        })

print("Total Sent Posts Analyzed: %d\n" % len(posts))

print("=== TOP 10 POSTS BY VIEWS & REACH ===")
for p in sorted(posts, key=lambda x: x["views"], reverse=True)[:10]:
    print("[%s] Views: %s | Reach: %s | Likes: %s | AvgWatch: %ss | EngRate: %s%%" % 
          (p['sentAt'], p['views'], p['reach'], p['reactions'], p['avgWatchSec'], p['engRate']))
    print("   Content: %s...\n" % p['text'][:130])

print("\n=== TOP POSTS BY ENGAGEMENT & SHARES ===")
for p in sorted(posts, key=lambda x: (x["reactions"] + x["shares"] * 2), reverse=True)[:8]:
    print("[%s] Likes: %s | Shares: %s | Views: %s | EngRate: %s%%" % 
          (p['sentAt'], p['reactions'], p['shares'], p['views'], p['engRate']))
    print("   Content: %s...\n" % p['text'][:130])

print("\n=== TOP POSTS BY RETENTION (AVG WATCH TIME) ===")
for p in sorted(posts, key=lambda x: x["avgWatchSec"], reverse=True)[:8]:
    print("[%s] AvgWatch: %ss | TotalWatch: %smin | Views: %s" % 
          (p['sentAt'], p['avgWatchSec'], p['totalWatchMin'], p['views']))
    print("   Content: %s...\n" % p['text'][:130])
