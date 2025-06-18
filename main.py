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

            # Mapping of desired resolutions
            desired_resolutions = {
                'mp3': 'audio_only',
                '144p': ['144p', 'tiny'],
                '240p': ['240p'],
                '360p': ['360p'],
                '480p': ['480p'],
                '720p': ['720p', 'hd720'],
                '1080p': ['1080p', 'hd1080'],
                '1440p': ['1440p', 'hd1440'],
                '2160p': ['2160p', 'hd2160'],
            }

            for f in info.get('formats', []):
                if not f.get('url'):
                    continue

                # Audio-only (MP3)
                if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                    formats.append({
                        'format': 'mp3',
                        'ext': f.get('ext'),
                        'filesize_mb': round(f.get('filesize', 0) / 1024 / 1024, 2) if f.get('filesize') else None,
                        'url': f['url']
                    })
                    continue

                # MP4 or 3GP with audio and desired resolution
                if f.get('acodec') != 'none' and f.get('vcodec') != 'none':
                    note = f.get('format_note') or f.get('height') or ""
                    for res, keywords in desired_resolutions.items():
                        if res == 'mp3':
                            continue
                        if any(str(note).lower().find(k) != -1 for k in keywords):
                            formats.append({
                                'format': res,
                                'ext': f.get('ext'),
                                'filesize_mb': round(f.get('filesize', 0) / 1024 / 1024, 2) if f.get('filesize') else None,
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
