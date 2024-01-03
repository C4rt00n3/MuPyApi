from pytube import YouTube as YT
from pytube import Search
from pytube import Playlist
import os
import requests
import logging
from mutagen.mp4 import MP4, MP4Cover
from PIL import Image
import io


class Result:
    def __init__(self, title: str, thumb: str, url: str, author: str):
        self.title = title
        self.thumb = thumb
        self.url = url
        self.author = author

    def __str__(self) -> str:
        content = (
            f"    url: {self.url},\n    thumb: {self.thumb}\n    title: {self.title}"
        )
        return "{\n" + content + "\n},"


class YouTube:
    def setContent(self, music: Result):
        self.title = music.title
        self.thumb = music.thumb
        self.url = music.url
        self.author = music.author

    def download(self, url: str):
        try:
            yt = YT(url)
            video = yt.streams.filter(only_audio=True).first()
            self.setContent(Result(yt.title, yt.thumbnail_url, url, yt.author))
            downloaded_file = video.download("cache")

            path = f"./cache/{yt.title}.mp4"

            response = requests.get(yt.thumbnail_url)

            # Abrindo a imagem usando a biblioteca PIL
            image = Image.open(io.BytesIO(response.content))

            # Convertendo a imagem para o formato .jpg
            byte_arr = io.BytesIO()
            image.save(byte_arr, format="JPEG")

            # Criando um objeto MP4Cover com a imagem
            mp4_cover = MP4Cover(byte_arr.getvalue(), imageformat=MP4Cover.FORMAT_JPEG)

            # Adicionando a imagem ao arquivo .mp4
            mp4 = MP4(path)
            mp4["covr"] = [mp4_cover]

            # Adicionando metatag de artista
            mp4["\xa9ART"] = yt.author
            mp4["\xa9alb"] = yt.thumbnail_url
            mp4["\xa9nam"] = yt.title
            # Salvando as alterações
            mp4.save()

            with open(path, "rb") as audio_file:
                audio_content = audio_file.read()

            return audio_content
        except Exception as e:
            logging.error(f"Error while downloading the video: {e}")
            return None

    def search(self, query: str) -> list[Result] | None:
        results: list[Result] = []
        try:
            search_results = Search(query).results
            for result in search_results:
                results.append(
                    Result(
                        result.title,
                        result.thumbnail_url,
                        result.watch_url,
                        result.author,
                    )
                )

            return results

        except Exception as e:
            print(f"Erro ao realizar a pesquisa: {e}")

    def playlist(self, url: str) -> list[Result] | None:
        playlist = Playlist(url)
        results: list[Result] = []

        try:
            for result in playlist.videos:
                if (
                    result.author != ""
                    and result.title != ""
                    and result.watch_url != ""
                    and result.thumbnail_url != ""
                ):
                    results.append(
                        Result(
                            result.title,
                            result.thumbnail_url,
                            result.watch_url,
                            result.author,
                        )
                    )

            return results
        except Exception as e:
            print(f"Erro ao realizar a pesquisa: {e}")
