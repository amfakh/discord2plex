import os
import random
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# --- CONFIGURATION (VIA .env) ---
# ==========================================
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "/media/Plex/DiscordVideos")
# If MAX_VIDEOS > 0, the script will stop after downloading that number of videos (useful for testing)
MAX_VIDEOS = int(os.getenv("MAX_VIDEOS", 0))

# Time parameters (in seconds)
DOWNLOAD_DELAY_MIN = float(os.getenv("DOWNLOAD_DELAY_MIN", 30))
DOWNLOAD_DELAY_MAX = float(os.getenv("DOWNLOAD_DELAY_MAX", 60))
PAGE_DELAY = float(os.getenv("PAGE_DELAY", 10))

if not TOKEN or not CHANNEL_ID:
    print("Error: DISCORD_TOKEN or DISCORD_CHANNEL_ID is not configured in .env file")
    sys.exit(1)
# ==========================================

headers = {"Authorization": TOKEN}


def get_messages(channel_id, before=None):
    # Fetch 100 messages at a time
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=100"
    if before:
        url += f"&before={before}"  # To paginate backwards in history

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching messages: Status {response.status_code} - {response.text}")
        return None


def download_video(url, filename, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

    filepath = os.path.join(folder, filename)

    # Skip if file has already been downloaded
    if os.path.exists(filepath):
        print(f"[-] File already exists, skipping: {filename}")
        return True

    print(f"[+] Downloading: {filename}...")
    try:
        # Use stream=True to conserve RAM during large video file downloads
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(filepath, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"[v] Successfully saved: {filename}")
        return True
    except Exception as e:
        print(f"[X] Failed to download {filename}: {e}")
        return False


def main():
    print("Starting channel history scraping...")
    last_message_id = None
    messages_processed = 0
    videos_downloaded = 0

    while True:
        messages = get_messages(CHANNEL_ID, before=last_message_id)

        # Stop if no more messages are retrieved
        if not messages:
            print("Reached the beginning of channel history.")
            break

        print(f"Checking history page ({len(messages)} messages)...")

        for msg in messages:
            messages_processed += 1
            if "attachments" in msg and len(msg["attachments"]) > 0:
                for att in msg["attachments"]:
                    filename = att.get("filename", "")

                    # Detect video files based on popular extensions
                    if filename.lower().endswith((".mp4", ".mkv", ".webm", ".mov", ".avi")):
                        url = att.get("url")
                        if url:
                            success = download_video(url, filename, DOWNLOAD_DIR)
                            if success:
                                videos_downloaded += 1
                                if MAX_VIDEOS > 0 and videos_downloaded >= MAX_VIDEOS:
                                    print(
                                        f"\n[!] Successfully downloaded {MAX_VIDEOS} video(s) (MAX_VIDEOS limit reached). Stopping test."
                                    )
                                    break
                                # Random delay between downloads to prevent rate limits / spam detection
                                delay = random.uniform(DOWNLOAD_DELAY_MIN, DOWNLOAD_DELAY_MAX)
                                print(f"   (Waiting {delay:.1f} seconds to avoid spam detection...)")
                                time.sleep(delay)
                if MAX_VIDEOS > 0 and videos_downloaded >= MAX_VIDEOS:
                    break
        if MAX_VIDEOS > 0 and videos_downloaded >= MAX_VIDEOS:
            break

        # Get ID of the oldest message in this batch to paginate backwards
        last_message_id = messages[-1]["id"]

        # Delay between fetching history pages
        time.sleep(PAGE_DELAY)

    print("\n" + "=" * 40)
    print("PROCESS COMPLETED!")
    print(f"Total messages checked: {messages_processed}")
    print(f"Total videos downloaded: {videos_downloaded}")
    print("=" * 40)


if __name__ == "__main__":
    main()
