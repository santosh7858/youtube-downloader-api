from flask import Flask, request, jsonify
from flask_cors import CORS
from pytube import YouTube
import re

app = Flask(__name__)
CORS(app)

def is_valid_youtube_url(url):
    pattern = r"^(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+(&\S*)?$"
    return re.match(pattern, url) is not None

@app.route('/')
def home():
    return "YouTube Downloader API is running."

@app.route('/video_info', methods=['POST'])
def video_info():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "Missing URL"}), 400

    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        yt = YouTube(url)
        resolutions = list(set([stream.resolution for stream in yt.streams.filter(progressive=True, file_extension='mp4') if stream.resolution]))

        video_info = {
            "title": yt.title,
            "author": yt.author,
            "length": yt.length,
            "views": yt.views,
            "description": yt.description,
            "publish_date": str(yt.publish_date),
            "resolutions": resolutions
        }
        return jsonify(video_info), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<resolution>', methods=['POST'])
def download_video(resolution):
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "Missing URL"}), 400

    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution=resolution).first()

        if stream:
            return jsonify({"download_url": stream.url}), 200
        else:
            return jsonify({"error": f"No video found with resolution {resolution}"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
