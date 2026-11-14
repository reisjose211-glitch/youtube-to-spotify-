# YouTube to MP3 (for Spotify Local Files)

A small web app for your iPhone: paste a YouTube link, get an MP3 with title,
artist and cover art, and save it into the **Spotify** folder in the Files app
so it shows up under Spotify's Local Files.

Only download audio you have the right to (your own uploads, Creative Commons,
public domain, or with the owner's permission).

## How it works

An iPhone web page cannot convert video by itself, so the conversion runs on a
small server (`app.py`, using `yt-dlp` and `ffmpeg`). Your iPhone opens the page
in Safari, and the finished MP3 is handed to the iOS share sheet / Files.

## 1. Run the server

On a Mac or PC on the same Wi-Fi as your iPhone (needs Python 3.10+ and ffmpeg):

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt      # Windows: .venv\Scripts\pip
.venv/bin/python app.py
```

Install ffmpeg with `brew install ffmpeg` (Mac) or `winget install ffmpeg` (Windows).

Or with Docker (ffmpeg included):

```bash
docker build -t yt2mp3 . && docker run -p 8000:8000 yt2mp3
```

The `Dockerfile` also works on hosts such as Render, Railway or Fly.io if you
want it reachable away from home. Note that YouTube often blocks cloud server
addresses, so running it at home is the most reliable.

## 2. Open it on your iPhone

1. Find your computer's local address (Mac: System Settings › Wi-Fi › Details;
   Windows: `ipconfig`), for example `192.168.1.20`.
2. In Safari on the iPhone open `http://192.168.1.20:8000`.
3. Tap Share › **Add to Home Screen** to get an app icon.

## 3. Save straight into the Spotify folder

One-time setup so every download lands in the Spotify folder with no extra taps:

1. iPhone **Settings › Apps › Safari › Downloads › Other…**
2. Choose **On My iPhone › Spotify** and tap Done.
3. In **Spotify › Settings › Apps and devices (or Local Files)**, turn on
   **Show audio files from this device**.

Then in the app: paste the link, tap **Convert**, and tap **Download MP3**.
The song appears in Spotify under **Your Library › Local Files**.

If you open the app over HTTPS (for example when hosted), a **Save to Files**
button opens the share sheet instead; pick **Save to Files › On My iPhone ›
Spotify**.

## Settings

Environment variables: `PORT` (default 8000), `MP3_BITRATE` (default 192),
`MAX_SECONDS` (longest video allowed, default 3 hours).

If conversions start failing, YouTube has probably changed something; update
with `.venv/bin/pip install -U yt-dlp`.
