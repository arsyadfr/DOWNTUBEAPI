from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from pytube import YouTube
import requests

app = Flask(__name__)
CORS(app)

# =========================
# HEALTH CHECK
# =========================
@app.route("/text", methods=["GET"])
def text():
    return {"status": "online"}

# =========================
# PREVIEW VIDEO (thumbnail, title, direct url)
# =========================
@app.route("/dlv", methods=["POST"])
def dlv():
    data = request.get_json(silent=True)

    if not data or "ytlink" not in data:
        return jsonify({"error": "ytlink missing"}), 400

    try:
        yt = YouTube(data["ytlink"])
        stream = yt.streams.get_highest_resolution()

        return jsonify({
            "videolink": stream.url,
            "thumbnail": yt.thumbnail_url,
            "title": yt.title
        })

    except Exception as e:
        print("DLV ERROR:", e)
        return jsonify({"error": "failed to fetch video"}), 500

# =========================
# DOWNLOAD VIDEO (stream proxy)
# =========================
@app.route("/download", methods=["POST"])
def download():
    data = request.get_json(silent=True)

    if not data or "ytlink" not in data:
        return jsonify({"error": "ytlink missing"}), 400

    try:
        yt = YouTube(data["ytlink"])
        stream = yt.streams.get_highest_resolution()

        r = requests.get(stream.url, stream=True)

        return Response(
            r.iter_content(chunk_size=1024 * 1024),
            headers={
                "Content-Disposition": f'attachment; filename="{yt.title}.mp4"',
                "Content-Type": "video/mp4"
            }
        )

    except Exception as e:
        print("DOWNLOAD ERROR:", e)
        return jsonify({"error": "download failed"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
