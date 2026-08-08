import os
import re
import yt_dlp


def download_streamable(url, folder):
    """
    Downloads a video from a Streamable URL using yt-dlp.
    Skips if a video with the same Streamable ID already exists in the folder.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)

    match = re.search(r"streamable\.com/([a-zA-Z0-9]+)", url)
    video_id = match.group(1) if match else "unknown"

    print(f"[+] Downloading Streamable link: {url}...")
    try:
        ydl_opts = {
            "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
            "nooverwrites": True,
            "quiet": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"[v] Successfully downloaded Streamable: {url}")
        return True
    except Exception as e:
        print(f"[X] Failed to download Streamable {url}: {e}")
        return False
