from flask import jsonify, abort
from youtube.YouTube import YouTube
from flask.helpers import send_file
import io
from model.playlist import Playlist


class Service:
    yt_instance = YouTube()

    def download_file(self, id: str | None):
        try:
            if id is None:
                raise ValueError(
                    "Parâmetro 'link' não fornecido na string de consulta."
                )

            yt_bytes = self.yt_instance.download(id=id)

            # Criando um objeto BytesIO para servir o arquivo
            yt_file = io.BytesIO(yt_bytes)
            yt_file.seek(0)

            return send_file(
                yt_file,
                download_name=f"{self.yt_instance.title}.mp4",
                as_attachment=True,
            )
        except Exception as e:
            print(e)
            abort(400)

    def search(self, query: str | None):
        try:
            if query is None:
                raise ValueError(
                    "Parâmetro 'query' não fornecido na string de consulta."
                )

            search_results = self.yt_instance.search(query=query)

            results_dict_list = [result.__dict__ for result in search_results]

            return jsonify({"results": results_dict_list})
        except Exception as e:
            print(e)
            abort(400)

    def playlist(self, link: str):
        try:
            if link is None:
                raise ValueError(
                    "Parâmetro 'link' não fornecido na string de consulta."
                )

            musics = YouTube().get_videos(link)

            results_dict_list = [result.__dict__ for result in musics]

            return jsonify(**{"id": 0, "link": link, "musics": results_dict_list})
        except Exception as e:
            raise e
            return jsonify({"error": "Erro durante a manipulação da playlist"}), 400
