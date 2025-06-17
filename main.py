from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL

app = Flask(__name__)

@app.route('/')
def home():
    return "YouTube API is running."

@app.route('/download')
def download():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "URL parameter is missing"}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'format': 'best',
            'dump_single_json': True
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = info.get("formats", [])
            results = [
                {
                    "quality": f.get("format_note"),
                    "url": f.get("url")
                }
                for f in formats if "video" in f.get("mime_type", "")
            ]
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
