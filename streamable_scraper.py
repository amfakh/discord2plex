import os
import re
import yt_dlp


try:
    from rename_episodes import parse_episode_info
except ImportError:
    parse_episode_info = None

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
            info = ydl.extract_info(url, download=False)
            filename = ydl.prepare_filename(info)
            basename = os.path.basename(filename)

            if parse_episode_info:
                parsed = parse_episode_info(basename)
                if parsed:
                    ep_num, v_suffix, ext = parsed
                    basename = f"{ep_num:03d}{v_suffix}{ext}"
                    filename = os.path.join(folder, basename)
            
            if os.path.exists(filename):
                print(f"[-] Streamable file already exists, skipping: {basename}")
                return False

            ydl.params['outtmpl']['default'] = filename
            ydl.download([url])

        print(f"[v] Successfully downloaded Streamable: {url} as {basename}")
        return True
    except Exception as e:
        print(f"[X] Failed to download Streamable {url}: {e}")
        return False
