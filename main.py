from flask import Flask, request, jsonify
from pytube import YouTube
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '✅ YouTube Downloader API is Running'

@app.route('/get_links', methods=['GET'])
def get_links():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    try:
        yt = YouTube(url)
        title = yt.title
        thumbnail = yt.thumbnail_url

        video_streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
        audio_streams = yt.streams.filter(only_audio=True).order_by('abr').desc()

        videos = []
        for stream in video_streams:
            videos.append({
                "resolution": stream.resolution,
                "mime_type": stream.mime_type,
                "filesize_MB": round(stream.filesize / 1024 / 1024, 2),
                "url": stream.url
            })

        audios = []
        for stream in audio_streams:
            abr = stream.abr if stream.abr else "unknown"
            audios.append({
                "bitrate": abr,
                "mime_type": stream.mime_type,
                "filesize_MB": round(stream.filesize / 1024 / 1024, 2),
                "url": stream.url
            })

        return jsonify({
            "title": title,
            "thumbnail": thumbnail,
            "videos": videos,
            "audios": audios
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Port binding from environment (Render compatible)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # fallback to 10000 if PORT not set
    app.run(host='0.0.0.0', port=port)
