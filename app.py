import asyncio
from flask_cors import CORS
from flask import Flask, request
from service import Service
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app)
service = Service()
semaphore = asyncio.Semaphore(100)  # Limita o número de requisições concorrentes a 100


async def processar_rota_coro(coroutine, *args, **kwargs):
    async with semaphore:
        return await coroutine(*args, **kwargs)


@app.route("/download", methods=["GET", "POST"])
async def download_req():
    link = request.args.get("link")
    return await processar_rota_coro(service.download_file, link)


@app.route("/search", methods=["GET"])
async def search_req():
    query = request.args.get("query")
    return await processar_rota_coro(service.search, query)


@app.route("/playlist", methods=["GET"])
async def playlist_req():
    link = request.args.get("link")
    return await processar_rota_coro(service.playlist, link)


@app.route("/getPlaylist", methods=["GET"])
async def get_playlist():
    query = request.args.get("query")
    return await processar_rota_coro(service.get_playlist, query)


@app.route("/stream", methods=["GET"])
async def stream_req():
    link = request.args.get("link")
    return await processar_rota_coro(service.stream, link)


@app.route("/", methods=["GET"])
def home():
    return "<h1>Sound Py</h1>"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
