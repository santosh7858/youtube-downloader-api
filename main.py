 from flask import Flask, request, jsonify
from pytube import YouTube
import re
import os

app = Flask(__name__)

def download_video(url, resolution):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution=resolution).first()
        if stream:
            stream.download(output_path="downloads")
            return True, None
        else:
            return False, "Video with the specified resolution not found."
    except Exception as e:
        return False, str(e)

def get_video_info(url):
    try:
        yt = YouTube(url)
        video_info = {
            "title": yt.title,
            "author": yt.author,
            "length": yt.length,
            "views": yt.views,
            "description": yt.description,
            "publish_date": str(yt.publish_date),
            "available_resolutions": [stream.resolution for stream in yt.streams.filter(progressive=True, file_extension='mp4')]
        }
        return video_info, None
    except Exception as e:
        return None, str(e)

def is_valid_youtube_url(url):
    pattern = r"^(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+(&\S*)?$"
    return re.match(pattern, url) is not None

@app.route('/')
def index():
    return "✅ YouTube Downloader API is Live!"

@app.route('/video_info', methods=['POST'])
def video_info():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "Missing 'url' parameter in request body."}), 400

    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL."}), 400

    video_info, error_message = get_video_info(url)
    
    if video_info:
        return jsonify(video_info), 200
    else:
        return jsonify({"error": error_message}), 500

@app.route('/download/<resolution>', methods=['POST'])
def download_by_resolution(resolution):
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "Missing 'url' parameter in request body."}), 400

    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL."}), 400

    success, error_message = download_video(url, resolution)
    
    if success:
        return jsonify({"message": f"✅ Video downloaded successfully in {resolution}."}), 200
    else:
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
