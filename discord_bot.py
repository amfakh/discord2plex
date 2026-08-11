import os
import re
import sys
import asyncio
import discord
from dotenv import load_dotenv

from streamable_scraper import download_streamable

load_dotenv()

# ==========================================
# --- CONFIGURATION (VIA .env) ---
# ==========================================
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "/media/Plex/DiscordVideos")

if not BOT_TOKEN:
    print("Error: DISCORD_BOT_TOKEN is not configured in .env file")
    sys.exit(1)

# Ensure download directory exists
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Set up Gateway Intents
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content & attachments

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print("=" * 40)
    print(f"🤖 Discord Bot is ONLINE as: {client.user}")
    print(f"📁 Target Download Folder: {DOWNLOAD_DIR}")
    if CHANNEL_ID:
        print(f"📢 Listening to Channel ID: {CHANNEL_ID}")
    else:
        print("📢 Listening to ALL channels where bot is present")
    print("=" * 40)


@client.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return

    # If CHANNEL_ID is specified, ignore messages from other channels
    if CHANNEL_ID and str(message.channel.id) != str(CHANNEL_ID):
        return

    print(f"\n[DEBUG] Received a message from {message.author} in channel {message.channel.id}")
    print(f"        Has attachments: {bool(message.attachments)}, Content length: {len(message.content)}")

    # 1. Check for Direct Video Attachments
    if message.attachments:
        msg_timestamp = message.created_at.timestamp()

        for attachment in message.attachments:
            filename = attachment.filename

            if filename.lower().endswith((".mp4", ".mkv", ".webm", ".mov", ".avi")):
                filepath = os.path.join(DOWNLOAD_DIR, filename)

                if os.path.exists(filepath):
                    print(f"[-] File already exists, skipping: {filename}")
                    continue

                print(f"[+] Real-time new episode detected! Downloading: {filename}...")
                try:
                    await attachment.save(filepath)
                    os.utime(filepath, (msg_timestamp, msg_timestamp))
                    print(f"[v] Successfully saved new episode: {filename}")
                    print(f"    [~] File metadata timestamp updated to Discord post date")
                except Exception as e:
                    print(f"[X] Failed to save {filename}: {e}")

    # 2. Check for Streamable Links (in content or embeds)
    content = message.content or ""
    streamable_links = re.findall(r"https?://(?:www\.)?streamable\.com/[a-zA-Z0-9]+", content)

    if message.embeds:
        for embed in message.embeds:
            if embed.url and "streamable.com/" in embed.url:
                streamable_links.append(embed.url)

    streamable_links = list(dict.fromkeys(streamable_links))
    if streamable_links:
        msg_timestamp = message.created_at.timestamp()
        for s_link in streamable_links:
            print(f"[+] Real-time Streamable link detected! Downloading: {s_link}...")
            download_streamable(s_link, DOWNLOAD_DIR, message_timestamp=msg_timestamp)


def main():
    print("Starting Discord Bot listener...")
    client.run(BOT_TOKEN)


if __name__ == "__main__":
    main()
