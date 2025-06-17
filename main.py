import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from pytube import YouTube
import re

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yt_downloader")

def is_valid_youtube_url(url):
    pattern = r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$"
    return re.match(pattern, url)

@app.route('/')
def home():
    logger.info("Root accessed")
    return "YouTube Downloader API is running."

@app.route('/video_info', methods=['POST'])
def video_info():
    logger.info("/video_info called")
    try:
        data = request.get_json(force=True)
        logger.info(f"Payload: {data}")
        url = data.get('url')
    except Exception as e:
        logger.error("Failed to parse JSON", exc_info=True)
        return jsonify({"error": "Invalid JSON"}), 400

    if not url:
        logger.warning("URL missing")
        return jsonify({"error": "Missing URL"}), 400
    if not is_valid_youtube_url(url):
        logger.warning("Invalid URL", url)
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        yt = YouTube(url)
        logger.info(f"Fetched video: {yt.title}")
        resolutions = list({st.resolution for st in yt.streams.filter(progressive=True, file_extension='mp4')})
        return jsonify({
            "title": yt.title,
            "author": yt.author,
            "length": yt.length,
            "views": yt.views,
            "resolutions": resolutions
        }), 200

    except Exception as e:
        logger.error("Error in video_info", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/download/<resolution>', methods=['POST'])
def download_video(resolution):
    logger.info(f"/download/{resolution} called")
    try:
        data = request.get_json(force=True)
        logger.info(f"Payload: {data}")
        url = data.get('url')
    except Exception as e:
        logger.error("Failed to parse JSON", exc_info=True)
        return jsonify({"error": "Invalid JSON"}), 400

    if not url:
        logger.warning("URL missing")
        return jsonify({"error": "Missing URL"}), 400
    if not is_valid_youtube_url(url):
        logger.warning("Invalid URL", url)
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution=resolution).first()
        if stream:
            logger.info("Got stream, returning direct URL")
            return jsonify({"download_url": stream.url}), 200
        else:
            logger.warning("No stream for resolution", resolution)
            return jsonify({"error": f"No video found with resolution {resolution}"}), 404

    except Exception as e:
        logger.error("Error in download", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
