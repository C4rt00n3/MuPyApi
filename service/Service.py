from flask import Flask, jsonify, request, abort
from YouTube.YouTube import YouTube
from flask.helpers import send_file
import io
from service.Database import Database


class Service:
    yt_instance = YouTube()
    database = Database()

    def download_file(self, link: str | None):
        try:
            if link is None:
                raise ValueError(
                    "Parâmetro 'link' não fornecido na string de consulta."
                )

            yt_bytes = self.yt_instance.download(url=link)

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

    def playlist(self, link):
        try:
            if link is None:
                raise ValueError(
                    "Parâmetro 'link' não fornecido na string de consulta."
                )

            find_first = self.database.find_first(link)

            if find_first is None:
                playlist = self.database.create_playlist(link)
                search_results = self.yt_instance.playlist(url=link)
                for element in search_results:
                    self.database.create_music(
                        element.title,
                        element.thumb,
                        element.author,
                        element.url,
                        playlist,
                    )
                find_first = self.database.find_first(link)
                return jsonify(find_first)

            return jsonify(find_first)
        except Exception as e:
            print(e)
            return jsonify({"error": "Erro durante a manipulação da playlist"}), 400

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
