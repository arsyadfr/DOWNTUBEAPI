from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
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
# PREVIEW VIDEO
# =========================
@app.route("/dlv", methods=["POST"])
def dlv():
    data = request.get_json(silent=True)
    if not data or "ytlink" not in data:
        return jsonify({"error": "ytlink missing"}), 400

    try:
        url = data["ytlink"].split("&")[0]

        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "format": "best"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        return jsonify({
            "videolink": info["url"],
            "thumbnail": info.get("thumbnail"),
            "title": info.get("title")
        })

    except Exception as e:
        print("DLV ERROR:", e)
        return jsonify({"error": "yt-dlp failed"}), 500

# =========================
# DOWNLOAD VIDEO (STREAM)
# =========================
@app.route("/download", methods=["POST"])
def download():
    data = request.get_json(silent=True)
    if not data or "ytlink" not in data:
        return jsonify({"error": "ytlink missing"}), 400

    try:
        url = data["ytlink"].split("&")[0]

        ydl_opts = {
            "quiet": True,
            "format": "best"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        video_url = info["url"]
        title = info.get("title", "video")

        r = requests.get(video_url, stream=True)

        return Response(
            r.iter_content(chunk_size=1024 * 1024),
            headers={
                "Content-Disposition": f'attachment; filename="{title}.mp4"',
                "Content-Type": "video/mp4"
            }
        )

    except Exception as e:
        print("DOWNLOAD ERROR:", e)
        return jsonify({"error": "download failed"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
