#!/usr/bin/env python3
"""
Meta Threads API Client for TrackSub & FeelsRight Growth
Implements official Meta Graph API endpoints:
- /me: Profile lookup
- /threads_search: Real-time public keyword search
- /{user_id}/threads: Container creation (supports reply_to_id)
- /{user_id}/threads_publish: Two-step post publication
"""

import os
import sys
import time
import json
import logging
import urllib.request
import urllib.parse
from typing import List, Dict, Optional

logger = logging.getLogger("ThreadsClient")
BASE_URL = "https://graph.threads.net/v1.0"

class ThreadsClient:
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token or os.environ.get("THREADS_ACCESS_TOKEN", "").strip()
        self.user_id = None
        self.username = None

    def _api_request(self, endpoint: str, method: str = "GET", params: Optional[Dict] = None, data: Optional[Dict] = None) -> Optional[Dict]:
        """Makes an authenticated request to the Meta Threads Graph API."""
        if not self.access_token:
            logger.warning("No THREADS_ACCESS_TOKEN found.")
            return None

        url = f"{BASE_URL}/{endpoint.lstrip('/')}"
        query_params = params.copy() if params else {}
        query_params["access_token"] = self.access_token

        encoded_query = urllib.parse.urlencode(query_params)
        full_url = f"{url}?{encoded_query}"

        encoded_data = None
        if data:
            data_with_token = data.copy()
            data_with_token["access_token"] = self.access_token
            encoded_data = urllib.parse.urlencode(data_with_token).encode("utf-8")

        req = urllib.request.Request(full_url if method == "GET" else url, data=encoded_data, method=method)
        req.add_header("User-Agent", "AutonomousSocialAgent/1.0")

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            logger.error(f"Threads API Error [{e.code}] on {endpoint}: {error_body}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error on Threads request: {e}")
            return None

    def get_profile(self) -> Optional[Dict]:
        """Fetches the authenticated user profile and stores user_id."""
        res = self._api_request("me", params={"fields": "id,username,threads_profile_picture_url"})
        if res and "id" in res:
            self.user_id = res["id"]
            self.username = res.get("username")
            logger.info(f"Authenticated with Threads as @{self.username} (ID: {self.user_id})")
            return res
        return None

    def search_posts(self, query: str) -> List[Dict]:
        """Searches public Threads posts by keyword using the official /threads_search endpoint."""
        logger.info(f"Searching Threads for query: '{query}'")
        res = self._api_request("threads_search", params={"q": query})
        if res and "data" in res:
            return res["data"]
        return []

    def reply_to_thread(self, reply_to_post_id: str, text: str) -> Optional[str]:
        """
        Executes the official Meta 2-step publish flow:
        Step 1: Create a container targeting `reply_to_post_id`
        Step 2: Publish the container
        """
        if not self.user_id:
            profile = self.get_profile()
            if not profile:
                logger.error("Cannot reply: User ID could not be resolved.")
                return None

        # Step 1: Create container
        container_payload = {
            "media_type": "TEXT",
            "text": text,
            "reply_to_id": reply_to_post_id
        }
        logger.info(f"Creating Threads reply container for post {reply_to_post_id}...")
        step1_res = self._api_request(f"{self.user_id}/threads", method="POST", data=container_payload)
        
        if not step1_res or "id" not in step1_res:
            logger.error("Failed to create Threads reply container.")
            return None

        container_id = step1_res["id"]
        logger.info(f"Container created with ID: {container_id}. Publishing...")

        # Small delay to ensure Meta container ingestion is ready
        time.sleep(3)

        # Step 2: Publish container
        publish_payload = {
            "creation_id": container_id
        }
        step2_res = self._api_request(f"{self.user_id}/threads_publish", method="POST", data=publish_payload)
        
        if step2_res and "id" in step2_res:
            published_id = step2_res["id"]
            logger.info(f"🎉 Successfully published reply to Threads! (ID: {published_id})")
            return published_id

        logger.error("Failed to publish Threads container.")
        return None

def test_threads_integration():
    """Diagnostic check for Threads API configuration."""
    print("=" * 60)
    print("THREADS API DIAGNOSTIC")
    print("=" * 60)
    client = ThreadsClient()
    if not client.access_token:
        print("❌ Status: THREADS_ACCESS_TOKEN is not set.")
        print("👉 Add your token to .env or run: export THREADS_ACCESS_TOKEN='...'")
        return

    print("Connecting to Meta Graph API...")
    profile = client.get_profile()
    if profile:
        print(f"✅ Success! Connected as @{profile.get('username')} (ID: {profile.get('id')})")
    else:
        print("❌ Could not connect to Threads. Check token permissions.")

if __name__ == "__main__":
    test_threads_integration()
