from pytube import YouTube
from flask import Flask, request, send_file, jsonify
import pytube
from flask.helpers import send_from_directory
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

@app.route('/dlv', methods=['GET', 'POST'])
@cross_origin()
def code():
    if request.method == "POST":
        json = request.get_json()
        link = json['ytlink']
        yt = YouTube(link)
        ytrl = yt.streams.get_highest_resolution().url
        ytimg= yt.thumbnail_url
        yttl= yt.title
        return jsonify(videolink = ytrl, thumbnail= ytimg, title= yttl)
    return print("done")


@app.route('/text')
@cross_origin()
def textal():
    return {
        'status':"online",}

@app.route('/')
@cross_origin()
def serve():
    return {"message": "this is a startup page"}

