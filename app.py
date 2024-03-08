from flask import Flask, request
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from service.service import Service

app = Flask(__name__)
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app)
service = Service()


def __init__() -> None:
    app.run(debug=True)


@app.route("/download", methods=["GET", "POST"])
def download_req():
    link = request.args.get("link")
    return service.download_file(link)


@app.route("/search", methods=["GET"])
def search_req():
    query = request.args.get("query")
    return service.search(query)


@app.route("/playlist", methods=["GET"])
def playlist_req():
    link = request.args.get("link")
    return service.playlist(link)


if __name__ == "__main__":
    __init__()
