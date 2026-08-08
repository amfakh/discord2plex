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

# Time parameters (in seconds)
DOWNLOAD_DELAY_MIN=30
DOWNLOAD_DELAY_MAX=60
PAGE_DELAY=10
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

## Available Scripts & Usage

### 1. Direct Attachments Scraper (`discord_scraper.py`)
Scrapes channel history and downloads direct `.mp4`, `.mkv`, `.mov`, etc. file attachments.
```bash
uv run discord_scraper.py
```

### 2. Streamable Links Scraper (`streamable_scraper.py`)
Scrapes channel history for `https://streamable.com/...` links and downloads them via `yt-dlp`.
```bash
uv run streamable_scraper.py
```

### 3. Real-Time Bot for New Episodes (`discord_bot.py`)
Official Discord Bot listener for 100% legal, real-time downloads of new episodes auto-forwarded to your channel with zero risk of account ban.

**Additional `.env` Configuration:**
```env
DISCORD_BOT_TOKEN="YOUR_OFFICIAL_DISCORD_BOT_TOKEN"
```

**Run the Real-Time Bot:**
```bash
uv run discord_bot.py
```
