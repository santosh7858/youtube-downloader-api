from flask import Flask, request, jsonify
from pytube import YouTube

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ YouTube Downloader API is Running"

@app.route('/get_links', methods=['GET'])
def get_links():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing YouTube URL'}), 400

    try:
        yt = YouTube(url)

        video_streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
        audio_streams = yt.streams.filter(only_audio=True).order_by('abr').desc()

        video_list = []
        for stream in video_streams:
            video_list.append({
                'resolution': stream.resolution,
                'mime_type': stream.mime_type,
                'filesize_MB': round(stream.filesize / 1024 / 1024, 2) if stream.filesize else None,
                'url': stream.url
            })

        audio_list = []
        for stream in audio_streams:
            audio_list.append({
                'bitrate': stream.abr,
                'mime_type': stream.mime_type,
                'filesize_MB': round(stream.filesize / 1024 / 1024, 2) if stream.filesize else None,
                'url': stream.url
            })

        return jsonify({
            'title': yt.title,
            'thumbnail': yt.thumbnail_url,
            'videos': video_list,
            'audios': audio_list
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
