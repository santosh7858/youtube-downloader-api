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

    # Desired resolutions
    resolutions_order = [
        "144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"
    ]
    desired_formats = {
        "mp3": None,
        "144p": None,
        "240p": None,
        "360p": None,
        "480p": None,
        "720p": None,
        "1080p": None,
        "1440p": None,
        "2160p": None,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])

            for f in formats:
                if not f.get('url'):
                    continue

                # ✅ MP3: audio-only (e.g. m4a, webm with no video)
                if f.get('vcodec') == 'none' and f.get('acodec') != 'none' and f.get('ext') in ['m4a', 'webm']:
                    if not desired_formats["mp3"]:
                        desired_formats["mp3"] = {
                            "format": "MP3",
                            "ext": "mp3",
                            "bitrate": f.get('abr', 'N/A'),
                            "filesize_MB": round((f.get('filesize', 0) or 0) / 1_048_576, 2),
                            "url": f['url']
                        }
                    continue

                # ✅ MP4 video+audio
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    height = f.get('height')
                    if not height:
                        continue

                    label = f"{height}p"
                    if label in desired_formats and not desired_formats[label]:
                        desired_formats[label] = {
                            "format": label,
                            "ext": f.get('ext'),
                            "filesize_MB": round((f.get('filesize', 0) or 0) / 1_048_576, 2),
                            "url": f['url']
                        }

            # Final output list with only matched formats
            output_formats = [v for k, v in desired_formats.items() if v]

            return jsonify({
                "title": info.get("title"),
                "url": info.get("webpage_url"),
                "formats": output_formats
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
