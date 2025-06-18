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
                # Must have audio and URL
                if not f.get('url') or f.get('acodec') == 'none':
                    continue

                ext = f.get('ext')
                resolution = f.get('format_note') or f.get('resolution') or f.get('height')
                if isinstance(resolution, int):
                    resolution = f"{resolution}p"

                formats.append({
                    'format_id': f.get('format_id'),
                    'ext': ext,
                    'resolution': resolution,
                    'filesize': f.get('filesize'),
                    'url': f.get('url'),
                    'audio_codec': f.get('acodec'),
                    'video_codec': f.get('vcodec'),
                })

            # Filter for only expected formats
            desired_formats = []
            resolutions_to_include = ['144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p']
            video_exts = ['mp4', '3gp']
            audio_exts = ['mp3', 'm4a', 'webm', 'opus']

            for fmt in formats:
                ext = fmt['ext']
                res = str(fmt.get('resolution'))

                # MP3/audio-only
                if ext in audio_exts and fmt.get('video_codec') == 'none':
                    desired_formats.append({**fmt, 'type': 'audio'})

                # MP4/3GP video+audio with specified resolutions
                elif ext in video_exts and res in resolutions_to_include:
                    desired_formats.append({**fmt, 'type': 'video'})

            return jsonify({
                'title': info.get('title'),
                'url': info.get('webpage_url'),
                'formats': desired_formats
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
