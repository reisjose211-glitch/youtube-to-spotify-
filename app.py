"""YouTube -> MP3 converter with a phone-friendly web page.

Run:  python app.py   then open http://<this-computer's-ip>:8000 on your iPhone.
"""
import os
import re
import shutil
import tempfile
import threading
import time
import uuid
from urllib.parse import urlparse

from flask import Flask, abort, jsonify, request, send_file, send_from_directory
from yt_dlp import YoutubeDL

APP_DIR = os.path.dirname(os.path.abspath(__file__))
WORK_DIR = os.path.join(tempfile.gettempdir(), "yt2mp3")
MAX_SECONDS = int(os.environ.get("MAX_SECONDS", 3 * 60 * 60))  # longest video allowed
KEEP_SECONDS = 30 * 60  # converted files are deleted after this long
BITRATE = os.environ.get("MP3_BITRATE", "192")
ALLOWED_HOSTS = {
    "youtube.com", "www.youtube.com", "m.youtube.com",
    "music.youtube.com", "youtu.be",
}

app = Flask(__name__, static_folder=None)
jobs = {}  # id -> {status, progress, title, filename, path, error, created}
jobs_lock = threading.Lock()


def is_youtube_url(url):
    try:
        parts = urlparse(url)
    except ValueError:
        return False
    return parts.scheme in ("http", "https") and (parts.hostname or "").lower() in ALLOWED_HOSTS


def safe_filename(title):
    name = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "", title).strip(" .")
    return (name[:120] or "audio") + ".mp3"


def cleanup_old_jobs():
    cutoff = time.time() - KEEP_SECONDS
    with jobs_lock:
        expired = [jid for jid, job in jobs.items() if job["created"] < cutoff]
        for jid in expired:
            del jobs[jid]
    for jid in expired:
        shutil.rmtree(os.path.join(WORK_DIR, jid), ignore_errors=True)


def convert(job_id, url):
    job = jobs[job_id]
    out_dir = os.path.join(WORK_DIR, job_id)
    os.makedirs(out_dir, exist_ok=True)

    def on_progress(d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            if total:
                job["progress"] = round(d.get("downloaded_bytes", 0) / total * 90)
        elif d["status"] == "finished":
            job["status"] = "converting"
            job["progress"] = 92

    def check_length(info, *, incomplete):
        if info.get("is_live"):
            return "Live streams can't be converted."
        if (info.get("duration") or 0) > MAX_SECONDS:
            return "That video is too long."
        return None

    options = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(out_dir, "audio.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "writethumbnail": True,
        "match_filter": check_length,
        "progress_hooks": [on_progress],
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": BITRATE},
            {"key": "FFmpegMetadata"},   # title / artist tags so Spotify shows them
            {"key": "EmbedThumbnail"},   # cover art
        ],
    }
    try:
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
        path = os.path.join(out_dir, "audio.mp3")
        if not os.path.exists(path):
            raise RuntimeError("The video was skipped (too long, or a live stream).")
        title = info.get("title") or "audio"
        job.update(status="done", progress=100, title=title,
                   filename=safe_filename(title), path=path)
    except Exception as exc:  # report every failure to the page
        message = re.sub(r"\x1b\[[0-9;]*m", "", str(exc)).replace("ERROR: ", "")
        message = message.split("; please report this issue")[0]
        job.update(status="error", error=message[:300])
        shutil.rmtree(out_dir, ignore_errors=True)


@app.get("/")
def index():
    return send_from_directory(os.path.join(APP_DIR, "static"), "index.html")


@app.get("/static/<path:name>")
def static_files(name):
    return send_from_directory(os.path.join(APP_DIR, "static"), name)


@app.post("/api/convert")
def start_convert():
    url = ((request.get_json(silent=True) or {}).get("url") or "").strip()
    if not is_youtube_url(url):
        return jsonify(error="Please paste a YouTube link."), 400
    cleanup_old_jobs()
    job_id = uuid.uuid4().hex
    with jobs_lock:
        jobs[job_id] = {"status": "downloading", "progress": 0, "created": time.time()}
    threading.Thread(target=convert, args=(job_id, url), daemon=True).start()
    return jsonify(id=job_id)


@app.get("/api/status/<job_id>")
def status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify(error="That conversion has expired. Try again."), 404
    return jsonify({k: job.get(k) for k in ("status", "progress", "title", "filename", "error")})


@app.get("/api/file/<job_id>")
def download(job_id):
    job = jobs.get(job_id)
    if not job or job["status"] != "done":
        abort(404)
    return send_file(job["path"], mimetype="audio/mpeg",
                     as_attachment=True, download_name=job["filename"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), threaded=True)
