from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
import os
import json

app = Flask(__name__)

# ✅ Convert JSON cookies to Netscape format
def convert_json_to_netscape(json_path, txt_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            cookies = json.load(f)

        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write('# Netscape HTTP Cookie File\n')
            for cookie in cookies:
                domain = cookie.get('domain', '')
                flag = 'TRUE' if domain.startswith('.') else 'FALSE'
                path = cookie.get('path', '/')
                secure = 'TRUE' if cookie.get('secure', False) else 'FALSE'
                expiry = int(cookie.get('expires', 9999999999))
                name = cookie.get('name', '')
                value = cookie.get('value', '')
                f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n")
        return True
    except Exception as e:
        print("Cookie conversion error:", e)
        return False

@app.route('/download', methods=['GET'])
def download_video():
    video_url = request.args.get('url')

    if not video_url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    # Paths
    cookie_json_path = 'youtube_cookies.json'
    cookie_txt_path = 'youtube_cookies.txt'

    # Convert cookies if json file exists
    if os.path.exists(cookie_json_path):
        convert_json_to_netscape(cookie_json_path, cookie_txt_path)

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'format': 'best',
        'cookiefile': cookie_txt_path  # ✅ this must be Netscape format
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            formats = info_dict.get("formats", [])
            video_urls = [
                {
                    "format_id": f.get("format_id"),
                    "quality": f.get("quality_label", f.get("format")),
                    "url": f.get("url")
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
