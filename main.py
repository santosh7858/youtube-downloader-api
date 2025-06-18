from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/')
def index():
    return '✅ YouTube Downloader API is Live!'

@app.route('/get_links', methods=['GET'])
def get_links():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter is missing'}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'cookiefile': 'youtube_cookies.txt',
            'format': 'bestvideo+bestaudio/best',
            'forcejson': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [])
            result = []

            for fmt in formats:
                if fmt.get('url') and fmt.get('ext') in ['mp4', 'webm', 'm4a', 'mp3']:
                    result.append({
                        'format_id': fmt.get('format_id'),
                        'extension': fmt.get('ext'),
                        'resolution': fmt.get('resolution') or f"{fmt.get('height')}p",
                        'url': fmt.get('url'),
                        'filesize': fmt.get('filesize') or 'N/A'
                    })

            return jsonify({
                'title': info_dict.get('title'),
                'thumbnail': info_dict.get('thumbnail'),
                'formats': result
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))  # For Render deployment
    app.run(host='0.0.0.0', port=port)
