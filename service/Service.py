import io
from flask import jsonify, abort
from YouTube.YouTube import YouTube
from flask.helpers import send_file
from typing import Union

class Service:
    """
    Classe que fornece serviços relacionados ao YouTube, como download de vídeos, busca e listagem de playlists.
    """

    def __init__(self):
        self.yt_instance = YouTube()

    def download_file(self, id: Union[str, None]):
        """
        Faz o download de um vídeo do YouTube e retorna o arquivo para download.

        Args:
            id (Union[str, None]): O ID do vídeo do YouTube a ser baixado.

        Returns:
            O arquivo de vídeo para download.
        """
        try:
            if id is None:
                raise ValueError(
                    "Parâmetro 'id' não fornecido na string de consulta."
                )

            yt_bytes = self.yt_instance.download(id=id)

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

    def search(self, query: str):
        """
        Realiza uma busca no YouTube com base em uma consulta e retorna os resultados.

        Args:
            query (str): A consulta de busca.

        Returns:
            Os resultados da busca em formato JSON.
        """
        try:
            if not query:
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
        """
        Retorna a lista de músicas de uma playlist do YouTube.

        Args:
            link (str): O link da playlist do YouTube.

        Returns:
            As músicas da playlist em formato JSON.
        """
        try:
            if not link:
                raise ValueError(
                    "Parâmetro 'link' não fornecido na string de consulta."
                )

            musics = self.yt_instance.get_videos(link)

            results_dict_list = [result.__dict__ for result in musics]

            return jsonify(**{"id": 0, "link": link, "musics": results_dict_list})
        except Exception as e:
            print(e)
            abort(400)

    def get_playlist(self, query: str):
        """
        Retorna a lista de playlists do YouTube com base em uma consulta.

        Args:
            query (str): A consulta de busca.

        Returns:
            As playlists encontradas em formato JSON.
        """
        try:
            if not query:
                raise ValueError(
                    "Parâmetro 'query' não fornecido na string de consulta."
                )

            search_results = self.yt_instance.get_playlist(query=query)

            results_dict_list = [result.__dict__ for result in search_results]

            return jsonify(results_dict_list)
        except Exception as e:
            print(e)
            abort(400)

    def stream(self, link: str):
        """
        Retorna as informações de streaming de um vídeo do YouTube.

        Args:
            link (str): O link do vídeo do YouTube.

        Returns:
            As informações de streaming em formato JSON.
        """
        try:
            if not link:
                raise ValueError(
                    "Parâmetro 'link' não fornecido na string de consulta."
                )

            search_results = self.yt_instance.stream(id=link)

            return jsonify({"result": search_results})
        except Exception as e:
            print(e)
            abort(400)
