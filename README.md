# Discord2Plex

Automation tool to scrape and download videos from a Discord channel directly to your local/server media directory for Plex, Jellyfin, or local storage.

## Features
- Auto-downloads `.mp4`, `.mkv`, `.webm`, `.mov`, `.avi` files from Discord channel history.
- Prevents duplicate downloads automatically.
- Smart anti-spam delay between downloads (30–60s) to avoid Discord rate-limits or bans.
- Includes `MAX_VIDEOS` test mode for quick verification.

---

## Setup Instructions

### 1. Requirements
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended package manager)

### 2. Configuration (`.env`)
Create a `.env` file in the root folder with the following variables:

```env
DISCORD_TOKEN="YOUR_DISCORD_TOKEN_HERE"
DISCORD_CHANNEL_ID="YOUR_CHANNEL_ID_HERE"
DOWNLOAD_DIR="/path/to/your/Plex/DiscordVideos"

# Optional: Set to 1 for quick test, or 0 (or omit) for full download
MAX_VIDEOS=0
```

---

## How to Get Your Discord Token

> Warning: Never share your Discord token with anyone. It gives full access to your account.

1. Open Discord in your Web Browser (Chrome, Brave, Firefox, etc.) and log in.
2. Press `F12` or `Cmd + Option + I` (Mac) to open Developer Tools.
3. Switch to the **Console** tab.
4. Paste the snippet below and press **Enter**:

```javascript
window.webpackChunkdiscord_app.push([[Symbol()],{},e=>{
  for(let m of Object.values(e.c)){
    let x = m?.exports?.default || m?.exports;
    if(x?.getToken && typeof x.getToken === 'function'){
      let t = x.getToken();
      if(typeof t === 'string' && t.length > 30){
        console.log("%cTOKEN DISCORD KAMU:", "color: lime; font-size: 20px; font-weight: bold;", t);
      }
    }
  }
}]);
```
5. Copy the generated token string into your `.env` file.

---

## Running the Scraper

Run using `uv`:
```bash
uv run discord_scraper.py
```
