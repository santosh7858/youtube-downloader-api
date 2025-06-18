from flask import Flask, request, jsonify
import yt_dlp
import os
import requests

app = Flask(__name__)

COOKIE_URL = "https://raw.githubusercontent.com/santosh7858/youtube-downloader-api/main/youtube_cookies.txt"
COOKIE_FILE = "youtube_cookies.txt"

def download_cookie_file():
    try:
        response = requests.get(COOKIE_URL)
        if response.status_code == 200:
            with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("✅ youtube_cookies.txt downloaded successfully.")
        else:
            print("❌ Failed to download youtube_cookies.txt.")
    except Exception as e:
        print(f"❌ Exception while downloading cookie file: {e}")

@app.route('/')
def home():
    return "✅ YouTube Downloader API is Live!"

@app.route('/get_links')
def get_links():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    ydl_opts = {
        'quiet': True,
        'nocheckcertificate': True,
        'cookiefile': COOKIE_FILE,
        'skip_download': True,
        'force_generic_extractor': False,
        'extract_flat': False,
        'format': 'bestaudio/best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = info.get('formats', [])
            results = []

            for f in formats:
                if f.get('url') and f.get('ext') in ['mp4', 'm4a', 'mp3', 'webm']:
                    results.append({
                        'format_id': f.get('format_id'),
                        'ext': f.get('ext'),
                        'resolution': f.get('format_note') or f.get('height'),
                        'audio_only': f.get('vcodec') == 'none',
                        'video_url': f.get('url')
                    })

            return jsonify({
                'title': info.get('title'),
                'id': info.get('id'),
                'formats': results
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    download_cookie_file()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
