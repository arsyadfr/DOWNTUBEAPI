import os
import uuid
import shutil
import re
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(BASE_DIR, "tmp")
os.makedirs(TMP_DIR, exist_ok=True)


# =========================
# HEALTH CHECK
# =========================
@app.route("/text", methods=["GET"])
def text():
    return jsonify({"status": "online"})


# =========================
# FETCH INFO + THUMBNAIL
# =========================
@app.route("/dlv", methods=["POST"])
def dlv():
    try:
        data = request.get_json()
        url = data.get("ytlink")

        if not url:
            return jsonify({"error": "ytlink required"}), 400

        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "uploader": info.get("uploader"),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# DOWNLOAD VIDEO
# =========================
@app.route("/download", methods=["POST"])
def download():
    try:
        data = request.get_json()
        url = data.get("ytlink")

        if not url:
            return jsonify({"error": "ytlink required"}), 400

        uid = str(uuid.uuid4())
        outtmpl = os.path.join(TMP_DIR, f"{uid}.%(ext)s")

        ydl_opts = {
            "outtmpl": outtmpl,
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "quiet": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        final_file = None
        for f in os.listdir(TMP_DIR):
            if f.startswith(uid):
                final_file = os.path.join(TMP_DIR, f)
                break

        if not final_file:
            return jsonify({"error": "file not found"}), 500

        # sanitize filename
        title = info.get("title", "video")
        safe_title = re.sub(r'[^\w\s.-]', '', title)

        return send_file(
            final_file,
            as_attachment=True,
            download_name=f"{safe_title}.mp4"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# CLEANUP
# =========================
@app.route("/cleanup", methods=["POST"])
def cleanup():
    try:
        shutil.rmtree(TMP_DIR)
        os.makedirs(TMP_DIR, exist_ok=True)
        return jsonify({"status": "cleaned"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
