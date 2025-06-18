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
        'noplaylist': True,
        'forcejson': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            formats_list = []
            for f in info.get('formats', []):
                if not f.get('url'):
                    continue
                if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                    # MP3 / audio only
                    tag = "MP3"
                elif f.get('acodec') == 'none':
                    continue  # skip video-only
                else:
                    height = f.get('height')
                    if height:
                        tag = f"{height}p"
                    else:
                        tag = f.get('format_note') or "Unknown"

                filesize = f.get('filesize') or 0
                size_mb = round(filesize / 1048576, 2) if filesize else None

                formats_list.append({
                    'format_id': f.get('format_id'),
                    'ext': f.get('ext'),
                    'tag': tag,
                    'resolution': f.get('format_note') or f"{f.get('height')}p",
                    'filesize_mb': size_mb,
                    'url': f.get('url'),
                })

            return jsonify({
                'title': info.get('title'),
                'url': info.get('webpage_url'),
                'formats': formats_list
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
