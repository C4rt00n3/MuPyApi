import os
import io
import requests
import logging
from mutagen.mp4 import MP4, MP4Cover
from PIL import Image
from model.music import Music
from typing import List
from dotenv import load_dotenv
from pytube import YouTube as YT

class Result:
    """
    Representa um resultado de pesquisa do YouTube.
    """

    def __init__(self, title: str, thumb: str, url: str, author: str):
        self.title = title
        self.thumb = thumb
        self.url = url
        self.author = author

    def __str__(self) -> str:
        """
        Retorna uma representação em string do resultado.
        """
        content = (
            f"    url: {self.url},\n    thumb: {self.thumb}\n    title: {self.title}"
        )
        return "{\n" + content + "\n},"

class YouTube:
    """
    Classe para interação com a API do YouTube.
    """

    def __init__(self) -> None:
        """
        Inicializa a classe, carregando a chave de API do arquivo .env.
        """
        load_dotenv()
        self.api_key = os.getenv("API_KEY")

    def download(self, id: str) -> bytes:
        """
        Realiza o download de um vídeo do YouTube e retorna o conteúdo do arquivo de áudio.

        Args:
            id (str): O ID do vídeo do YouTube.

        Returns:
            bytes: O conteúdo do arquivo de áudio.
        """
        path = ""
        try:
            yt = YT(f"https://music.youtube.com/watch?v={id}")
            video = yt.streams.filter(only_audio=True).first()
            result = Result(yt.title, yt.thumbnail_url, yt.video_id, yt.author)
            path = video.download("cache")

            response = requests.get(result.thumb)
            image = Image.open(io.BytesIO(response.content))
            byte_arr = io.BytesIO()
            image.save(byte_arr, format="JPEG")
            mp4_cover = MP4Cover(byte_arr.getvalue(), imageformat=MP4Cover.FORMAT_JPEG)
            
            mp4 = MP4(path)
            mp4["covr"] = [mp4_cover]
            mp4["\xa9ART"] = result.author
            mp4["\xa9alb"] = f"thumbnail_url = {result.thumb}, url = {id}"
            mp4["\xa9nam"] = result.title
            mp4["\xa9des"] = id
            mp4.save()

            with open(path, "rb") as audio_file:
                audio_content = audio_file.read()

            return audio_content
        except Exception as e:
            logging.error(f"Error while downloading the video: {e}")
            return None
        finally:
            if path != "":
                os.remove(path)

    def search(self, query: str) -> List[Result]:
        """
        Realiza uma busca no YouTube com base em uma consulta e retorna os resultados.

        Args:
            query (str): A consulta de busca.

        Returns:
            List[Result]: Uma lista de resultados da busca.
        """
        try:
            base_url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "maxResults": 25,
                "key": self.api_key,
                "q": query,
            }
            response = requests.get(base_url, params=params)
            results = response.json()

            videos: List[Result] = []
            for item in results.get("items", []):
                if "id" in item and "videoId" in item["id"]:
                    video_title = item["snippet"]["title"]
                    video_thumb = item["snippet"]["thumbnails"].get("high", {}).get("url")
                    video_url = item["id"]["videoId"]
                    video_author = item["snippet"]["channelTitle"]
                    video = Result(video_title, video_thumb, video_url, video_author)
                    videos.append(video)
                else:
                    logging.warning(f"Skipping non-video item: {item}")
            return videos
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return []

    # Métodos adicionais...

