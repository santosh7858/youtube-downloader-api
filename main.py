from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '✅ YouTube Downloader API is Live!'

@app.route('/get_links', methods=['GET'])
def get_links():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        # yt-dlp options
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'cookies': 'youtube_cookies.txt',  # local cookie file
            'forcejson': True,
            'extract_flat': False,
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            formats = []
            for fmt in info.get('formats', []):
                formats.append({
                    'format_id': fmt.get('format_id'),
                    'ext': fmt.get('ext'),
                    'resolution': fmt.get('resolution') or f"{fmt.get('height')}p",
                    'filesize': fmt.get('filesize'),
                    'url': fmt.get('url')
                })

            return jsonify({
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "formats": formats
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # for Render
    app.run(host='0.0.0.0', port=port)
