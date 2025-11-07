# streamlit_yt_playlist_downloader.py
# Run with: streamlit run streamlit_yt_playlist_downloader.py

import os
import zipfile
import time
import random
from tqdm import tqdm
import yt_dlp
import streamlit as st

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="YouTube Playlist MP3 Downloader", layout="wide")
st.title("🎵 YouTube Playlist MP3 Downloader")

playlist_url = st.text_input("Paste the YouTube playlist URL here:")

cookies_file = st.file_uploader("Optional: Upload cookies.txt (for age-restricted/region-locked videos)", type="txt")

download_button = st.button("Download Playlist")

# ---------- Download Config ----------
BATCH_SIZE = 8
MIN_DELAY_BETWEEN_VIDEOS = 2
MAX_DELAY_BETWEEN_VIDEOS = 5
MIN_DELAY_BETWEEN_BATCHES = 8
MAX_DELAY_BETWEEN_BATCHES = 20
MAX_RETRIES = 3
OUTPUT_DIR = "mp3_downloads"

# ------------------------------------------------
def extract_playlist_info(url, cookies_path=None):
    opts = {'quiet': True}
    if cookies_path:
        opts['cookies'] = cookies_path
    for attempt in range(1, MAX_RETRIES+1):
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            if attempt < MAX_RETRIES:
                time.sleep(5 * attempt)
            else:
                raise RuntimeError(f"Could not fetch playlist info: {e}")

def download_video(video_entry, base_ydl_opts, st_container):
    video_id = video_entry.get('id')
    if not video_id:
        return False, "no-id"
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        with yt_dlp.YoutubeDL({**base_ydl_opts, 'quiet': True}) as ydl:
            vinfo = ydl.extract_info(video_url, download=False)
    except Exception:
        vinfo = {}
    title = vinfo.get('title') or video_entry.get('title') or video_id
    filesize = vinfo.get('filesize') or vinfo.get('filesize_approx') or 0

    progress_bar = st_container.progress(0)
    current_n = 0

    def progress_hook(d):
        nonlocal current_n
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes') or 0
            if filesize:
                progress_bar.progress(min(downloaded / filesize, 1.0))
        elif d['status'] == 'finished':
            progress_bar.progress(1.0)

    ydl_opts = dict(base_ydl_opts)
    ydl_opts['noplaylist'] = True
    ydl_opts['progress_hooks'] = [progress_hook]

    success = False
    error_msg = None
    for attempt in range(1, MAX_RETRIES+1):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            success = True
            break
        except Exception as e:
            error_msg = str(e)
            time.sleep(5 * attempt)
    return success, error_msg

# ---------- Main ----------
if download_button and playlist_url:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    cookies_path = None
    if cookies_file:
        cookies_path = "cookies.txt"
        with open(cookies_path, "wb") as f:
            f.write(cookies_file.getbuffer())

    st.info("🔍 Fetching playlist information...")
    try:
        info = extract_playlist_info(playlist_url, cookies_path)
    except Exception as e:
        st.error(f"❌ Failed to fetch playlist info: {e}")
        st.stop()

    entries = [e for e in (info.get('entries') or []) if isinstance(e, dict) and e.get('id')]
    if not entries:
        st.error("❌ No videos found in playlist or playlist is private/empty.")
        st.stop()

    playlist_title = info.get('title') or info.get('playlist_title') or "playlist"
    safe_playlist_title = "".join(c for c in playlist_title if c.isalnum() or c in " _-").strip() or "playlist"
    st.success(f"✅ Found {len(entries)} videos in playlist: {playlist_title}")

    base_ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(OUTPUT_DIR, '%(playlist_title)s/%(title)s.%(ext)s'),
        'ignoreerrors': True,
        'nooverwrites': True,
        'noplaylist': False,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }
    if cookies_path:
        base_ydl_opts['cookies'] = cookies_path

    all_success = []
    all_failed = []

    # Split into batches
    batches = [entries[i:i+BATCH_SIZE] for i in range(0, len(entries), BATCH_SIZE)]
    for b_index, batch in enumerate(batches, start=1):
        st.info(f"🔁 Starting batch {b_index}/{len(batches)}")
        for video in batch:
            with st.container() as video_container:
                ok, err = download_video(video, base_ydl_opts, video_container)
                vid_title = (video.get('title') or video.get('id'))[:60]
                if ok:
                    st.write(f"✔ {vid_title}")
                    all_success.append(video.get('id'))
                else:
                    st.write(f"✖ {vid_title} → {err}")
                    all_failed.append((video.get('id'), err))
            time.sleep(random.uniform(MIN_DELAY_BETWEEN_VIDEOS, MAX_DELAY_BETWEEN_VIDEOS))
        if b_index < len(batches):
            pause = random.uniform(MIN_DELAY_BETWEEN_BATCHES, MAX_DELAY_BETWEEN_BATCHES)
            st.info(f"🛑 Pausing {pause:.1f}s before next batch...")
            time.sleep(pause)

    # Create ZIP
