import json

files = {
    "YouTube (Unwrittenrules.B3)": "/Users/bidya/.gemini/antigravity/brain/aaa18ecf-eb8b-4c91-aa47-1a4559b81395/.system_generated/steps/586/output.txt",
    "Instagram (unwrittenrules.b3)": "/Users/bidya/.gemini/antigravity/brain/aaa18ecf-eb8b-4c91-aa47-1a4559b81395/.system_generated/steps/588/output.txt",
    "TikTok (unwrittenrules.b3)": "/Users/bidya/.gemini/antigravity/brain/aaa18ecf-eb8b-4c91-aa47-1a4559b81395/.system_generated/steps/590/output.txt"
}

for name, filepath in files.items():
    print("\n" + "=" * 55)
    print("CHANNEL: %s" % name)
    print("=" * 55)
    with open(filepath, "r") as f:
        line = f.readline().strip()
        data = json.loads(line)
    
    edges = data.get("edges", [])
    print("Total Posts returned: %d" % len(edges))
    
    posts = []
    for edge in edges:
        node = edge.get("node", {})
        status = node.get("status")
        metrics_dict = {}
        for m in node.get("metrics") or []:
            metrics_dict[m.get("type")] = m.get("value")
        
        sent_date = (node.get("sentAt") or node.get("dueAt") or node.get("createdAt") or "Unknown")[:10]
        posts.append({
            "status": status,
            "sentAt": sent_date,
            "text": (node.get("text") or "").replace("\n", " "),
            "views": metrics_dict.get("views", 0),
            "reach": metrics_dict.get("reach", 0),
            "impressions": metrics_dict.get("impressions", 0),
            "reactions": metrics_dict.get("reactions", 0),
            "likes": metrics_dict.get("likes", metrics_dict.get("reactions", 0)),
            "comments": metrics_dict.get("comments", 0),
            "shares": metrics_dict.get("shares", 0),
            "engRate": metrics_dict.get("engagementRate", 0),
            "avgWatchSec": metrics_dict.get("averageTimeWatched", 0),
            "metrics": metrics_dict
        })
    
    sent_posts = [p for p in posts if p["status"] == "sent"]
    draft_posts = [p for p in posts if p["status"] == "draft"]
    error_posts = [p for p in posts if p["status"] == "error"]
    print("Breakdown: %d sent, %d draft, %d error" % (len(sent_posts), len(draft_posts), len(error_posts)))
    
    if sent_posts:
        print("\n--- TOP SENT POSTS BY TRACTION ---")
        for p in sorted(sent_posts, key=lambda x: max(x["views"], x["reach"], x["impressions"], x["likes"]), reverse=True)[:5]:
            print("[%s] Views: %s | Reach: %s | Likes: %s | Comments: %s | Shares: %s | EngRate: %s%%" % 
                  (p['sentAt'], p['views'], p['reach'], p['likes'], p['comments'], p['shares'], p['engRate']))
            print("   Content: %s..." % p['text'][:120])
            print("   Metrics details: %s\n" % p['metrics'])
    else:
        print("No sent posts currently recorded on this channel in Buffer.")
