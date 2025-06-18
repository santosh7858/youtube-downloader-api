from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '✅ YouTube Downloader API is Live!'

@app.route('/get_links', methods=['GET'])
def get_links():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestvideo+bestaudio/best',
            'extract_flat': False,
        }

        links = {'mp4': [], 'mp3': []}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            # MP4 download links
            for f in info.get("formats", []):
                if f.get("ext") == "mp4" and f.get("url"):
                    res = f.get("format_note") or f.get("height", "unknown")
                    links['mp4'].append({
                        'resolution': res,
                        'filesize': f.get("filesize"),
                        'url': f["url"]
                    })

                # MP3 or audio formats
                if f.get("ext") in ["m4a", "mp3", "webm"] and f.get("acodec") != "none":
                    links['mp3'].append({
                        'abr': f.get("abr", "unknown"),
                        'filesize': f.get("filesize"),
                        'url': f["url"]
                    })

        return jsonify({
            'title': info.get('title'),
            'thumbnail': info.get('thumbnail'),
            'duration': info.get('duration'),
            'links': links
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
