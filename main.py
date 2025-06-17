import os
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
            'dump_single_json': True,
            'cookiefile': 'cookies.txt'
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

# 🔧 This tells Flask to run on the port Render provides
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
