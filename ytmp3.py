"""On-iPhone YouTube -> MP3, for the free a-Shell app. No computer needed.

Usage inside a-Shell:   python ytmp3.py [link]
With no link it uses the clipboard, or asks you to paste one.
The MP3 is saved in the current folder (jump to your Spotify folder first).
"""
import os
import subprocess
import sys

try:
    from yt_dlp import YoutubeDL
except ImportError:
    sys.exit("First run:  pip install yt-dlp")

HOSTS = ("youtube.com/", "youtu.be/")


def clipboard():
    try:
        return subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:
        return ""


def get_link():
    link = sys.argv[1].strip() if len(sys.argv) > 1 else clipboard()
    if not any(h in link for h in HOSTS):
        link = input("Paste the YouTube link: ").strip()
    if not any(h in link for h in HOSTS):
        sys.exit("That is not a YouTube link.")
    return link


def download(link, as_mp3):
    options = {
        "outtmpl": "%(title)s.%(ext)s",
        "noplaylist": True,
        "restrictfilenames": False,
        "format": "bestaudio/best" if as_mp3 else "bestaudio[ext=m4a]/bestaudio",
    }
    if as_mp3:
        options["postprocessors"] = [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"},
            {"key": "FFmpegMetadata"},
        ]
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(link, download=True)
    return info.get("title", "audio")


def main():
    link = get_link()
    print("Saving into:", os.getcwd())
    try:
        title = download(link, as_mp3=True)
        print("\nDone:", title + ".mp3")
    except Exception as exc:
        # MP3 conversion needs ffmpeg; if that step fails, keep the original audio.
        print("\nMP3 conversion failed (%s).\nSaving the original audio instead..." % exc)
        title = download(link, as_mp3=False)
        print("\nDone (not converted to MP3):", title)


if __name__ == "__main__":
    main()
