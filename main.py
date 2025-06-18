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

    desired_resolutions = {
        'mp3': 'MP3',
        '144p': ['144p', 'tiny'],       # covers 3GP too
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
            formats = []

            for f in info.get('formats', []):
                if not f.get('url') or f.get('acodec') == 'none':
                    continue

                height = f.get('height')
                format_note = f.get('format_note', '').lower()
                ext = f.get('ext')
                abr = f.get('abr')

                # Match MP3 or audio-only
                if ext == 'm4a' and abr:
                    formats.append({
                        'format': 'MP3',
                        'ext': 'mp3',
                        'bitrate': f'{abr} kbps',
                        'filesize_MB': round((f.get('filesize', 0) or 0) / 1_048_576, 2),
                        'url': f['url']
                    })
                    continue

                # Match video + audio for specific resolutions
                for res_key, values in desired_resolutions.items():
                    if res_key == 'mp3':
                        continue
                    if (str(height) + 'p' in values or format_note in values):
                        formats.append({
                            'format': res_key,
                            'ext': ext,
                            'filesize_MB': round((f.get('filesize', 0) or 0) / 1_048_576, 2),
                            'url': f['url']
                        })
                        break

            return jsonify({
                'title': info.get('title'),
                'url': info.get('webpage_url'),
                'formats': formats
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
