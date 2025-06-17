from flask import Flask, request, jsonify
from flask_cors import CORS
from pytube import YouTube
import re
import os
import logging

from http.cookiejar import MozillaCookieJar
import requests

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

COOKIE_FILE = "https://raw.githubusercontent.com/santosh7858/youtube-downloader-api/refs/heads/main/youtube_cookies.json"  # Path to your cookie file

def load_cookies_from_file():
    try:
        cookie_jar = MozillaCookieJar()
        cookie_jar.load(COOKIE_FILE, ignore_discard=True, ignore_expires=True)
        session = requests.Session()
        session.cookies.update(cookie_jar)
        return session
    except Exception as e:
        logging.error("Failed to load cookies: %s", str(e))
        return None

def is_valid_youtube_url(url):
    pattern = r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$"
    return re.match(pattern, url)

def get_video_info(url):
    try:
        session = load_cookies_from_file()
        yt = YouTube(url, use_oauth=False, allow_oauth_cache=True, proxies=None, request=session)
        resolutions = sorted(list(set(
            stream.resolution for stream in yt.streams.filter(progressive=True, file_extension='mp4') if stream.resolution
        )))
        return {
            "title": yt.title,
            "author": yt.author,
            "length": yt.length,
            "views": yt.views,
            "description": yt.description,
            "publish_date": str(yt.publish_date),
            "available_resolutions": resolutions
        }, None
    except Exception as e:
        logging.error("Video info error: %s", str(e))
        return None, str(e)

def download_video(url, resolution):
    try:
        session = load_cookies_from_file()
        yt = YouTube(url, use_oauth=False, allow_oauth_cache=True, proxies=None, request=session)
        stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution=resolution).first()
        if stream:
            return {"download_url": stream.url}, None
        else:
            return None, "Video with the specified resolution not found."
    except Exception as e:
        logging.error("Download error: %s", str(e))
        return None, str(e)

@app.route('/')
def index():
    return "✅ YouTube Downloader API is Live!"

@app.route('/video_info', methods=['POST'])
def video_info():
    try:
        data = request.get_json(force=True)
        url = data.get('url')
    except:
        return jsonify({"error": "Invalid JSON"}), 400

    if not url:
        return jsonify({"error": "Missing 'url' parameter in request body."}), 400
    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL."}), 400

    info, error = get_video_info(url)
    if error:
        return jsonify({"error": error}), 500
    return jsonify(info), 200

@app.route('/download/<resolution>', methods=['POST'])
def download_by_resolution(resolution):
    try:
        data = request.get_json(force=True)
        url = data.get('url')
    except:
        return jsonify({"error": "Invalid JSON"}), 400

    if not url:
        return jsonify({"error": "Missing 'url' parameter in request body."}), 400
    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL."}), 400

    result, error = download_video(url, resolution)
    if error:
        return jsonify({"error": error}), 500
    return jsonify(result), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
