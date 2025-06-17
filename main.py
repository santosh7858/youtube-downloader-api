from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download_video():
    video_url = request.args.get('url')

    if not video_url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'format': 'best',
        'cookiefile': 'youtube_cookies.json'  # optional if you added cookies
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
