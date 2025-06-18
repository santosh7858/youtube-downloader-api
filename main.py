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
        'extract_flat': False,
    }

    format_map = {
        'mp3': 'MP3',
        '144p': ['144p', 'tiny'],
        '240p': ['240p'],
        '360p': ['360p'],
        '480p': ['480p'],
        '720p': ['720p', 'hd720'],
        '1080p': ['1080p', 'hd1080'],
        '1440p': ['1440p', 'hd1440'],
        '2160p': ['2160p', 'hd2160'],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            results = {
                'title': info.get('title'),
                'url': info.get('webpage_url'),
                'formats': {}
            }

            for tag, res_list in format_map.items():
                if isinstance(res_list, str):
                    res_list = [res_list]

                for fmt in info.get('formats', []):
                    if fmt.get('acodec') == 'none':
                        continue  # ignore formats without audio
                    if fmt.get('format_note') in res_list or str(fmt.get('height')) + 'p' in res_list:
                        filesize_mb = round((fmt.get('filesize', 0) or 0) / 1048576, 2)
                        results['formats'][tag] = {
                            'ext': fmt.get('ext'),
                            'resolution': fmt.get('format_note') or f"{fmt.get('height')}p",
                            'filesize_mb': filesize_mb,
                            'url': fmt.get('url')
                        }
                        break

            return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
