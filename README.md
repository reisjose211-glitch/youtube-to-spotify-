# YouTube to MP3 (for Spotify Local Files)

A small web app for your iPhone: paste a YouTube link, get an MP3 with title,
artist and cover art, and save it into the **Spotify** folder in the Files app
so it shows up under Spotify's Local Files.

Only download audio you have the right to (your own uploads, Creative Commons,
public domain, or with the owner's permission).

## Option A: iPhone only (no computer)

This uses the free **a-Shell** app from the App Store, which can run the
converter (`ytmp3.py`) directly on the phone.

### One-time setup

1. Install **a-Shell** from the App Store and open it.
2. Type these, pressing return after each:
   ```
   pip install yt-dlp
   curl -L -o ~/Documents/ytmp3.py https://raw.githubusercontent.com/reisjose211-glitch/youtube-to-spotify-/claude/admiring-hypatia-2kr8tr/ytmp3.py
   pickFolder
   ```
3. `pickFolder` opens the Files picker: choose **On My iPhone > Spotify** and tap Open.
4. Type `bookmark spotify` so a-Shell remembers the folder.
5. In Spotify's settings turn on **Show audio files from this device**.

### Each time

1. Copy the YouTube link.
2. Open a-Shell and type:
   ```
   jump spotify
   python ~/Documents/ytmp3.py
   ```
   It picks the link up from the clipboard (or asks you to paste it) and saves
   the MP3 into the Spotify folder. Find it in Spotify under
   **Your Library > Local Files**.

### Optional: one-tap Home Screen button

In the **Shortcuts** app make a new shortcut with two actions:

1. **Get Clipboard**
2. a-Shell's **Execute Command**, with these two lines (insert the Clipboard
   variable where shown):
   ```
   jump spotify
   python ~/Documents/ytmp3.py [Clipboard]
   ```

Then use Share > **Add to Home Screen**. Copy a link, tap the icon, done.

## Option B: run a server on a computer

## How it works

An iPhone web page cannot convert video by itself, so the conversion runs on a
small server (`app.py`, using `yt-dlp` and `ffmpeg`). Your iPhone opens the page
in Safari, and the finished MP3 is handed to the iOS share sheet / Files.

## 1. Run the server

**Windows:** install Python from https://www.python.org/downloads/ (tick
"Add python.exe to PATH"), then double-click **start.bat**. The first run sets
itself up, then shows the address to open on your iPhone. If Windows Firewall
asks, allow access on **Private networks**.

**Mac / Linux:**

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```

ffmpeg is bundled, so there is nothing else to install.

Or with Docker (ffmpeg included):

```bash
docker build -t yt2mp3 . && docker run -p 8000:8000 yt2mp3
```

The `Dockerfile` also works on hosts such as Render, Railway or Fly.io if you
want it reachable away from home. Note that YouTube often blocks cloud server
addresses, so running it at home is the most reliable.

## 2. Open it on your iPhone

1. The server window shows an address such as `http://192.168.1.20:8000`.
2. Open that address in Safari on the iPhone (same Wi-Fi as the computer).
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
