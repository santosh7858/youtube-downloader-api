from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "✅ YouTube Downloader API is Live!"

@app.route('/get_links')
def get_links():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing URL'}), 400

    cookie_path = os.path.join(os.path.dirname(__file__), 'youtube_cookies.txt')

    ydl_opts = {
        'quiet': True,
        'cookiefile': cookie_path,
        'skip_download': True,
        'forcejson': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            for f in info.get('formats', []):
                if not f.get('url'):
                    continue
                # ✅ Only include formats with audio
                if f.get('acodec') == 'none':
                    continue

                resolution = f.get('format_note') or f.get('resolution') or f.get('height')
                if isinstance(resolution, int):
                    resolution = f"{resolution}p"

                formats.append({
                    'format_id': f.get('format_id'),
                    'ext': f.get('ext'),
                    'resolution': resolution,
                    'filesize': f.get('filesize'),
                    'url': f.get('url')
                })

            return jsonify({
                'title': info.get('title'),
                'url': info.get('webpage_url'),
                'formats': formats
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
