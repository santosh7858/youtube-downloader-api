from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
from yt_dlp.utils import cookies
import os
import json

app = Flask(__name__)

# Convert JSON to Netscape format (if needed)
def ensure_netscape_cookie_format(json_cookie_path, netscape_cookie_path):
    try:
        with open(json_cookie_path, 'r') as f:
            json_cookies = json.load(f)
        with open(netscape_cookie_path, 'w') as f:
            f.write(cookies.json2netscape(json_cookies))
        return True
    except Exception as e:
        print(f"Cookie conversion error: {e}")
        return False

@app.route('/download', methods=['GET'])
def download_video():
    video_url = request.args.get('url')

    if not video_url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    # Convert cookie if necessary
    cookie_json_path = 'youtube_cookies.json'
    cookie_txt_path = 'youtube_cookies.txt'

    if os.path.exists(cookie_json_path):
        ensure_netscape_cookie_format(cookie_json_path, cookie_txt_path)

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'format': 'best',
        'cookiefile': cookie_txt_path  # Must be in Netscape format
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            formats = info_dict.get("formats", [])
            video_urls = [
                {
                    "format_id": f["format_id"],
                    "quality": f.get("quality_label", f.get("format")),
                    "url": f["url"]
                }
                for f in formats if f.get("url")
            ]
            return jsonify({
                "title": info_dict.get("title"),
                "thumbnail": info_dict.get("thumbnail"),
                "formats": video_urls
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return "YouTube Downloader API is running."

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
