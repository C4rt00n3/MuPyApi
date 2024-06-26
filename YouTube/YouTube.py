import os
import io
import requests
import logging
from PIL import Image
from model.music import Music
from dotenv import load_dotenv
from pytube import YouTube as YT
from mutagen.mp4 import MP4, MP4Cover
from cachetools import cached, LRUCache



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

    @cached(cache=LRUCache(maxsize=100))
    def search(self, query: str) -> list[Result]:
        """
        Realiza uma busca por vídeos no YouTube com base em uma query.

        Args:
            query (str): O termo de busca.

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
                "type": "video",
                "videoCategoryId": "10",  # ID da categoria de música
            }
            response = requests.get(base_url, params=params)
            results = response.json()

            if "items" in results:
                videos = []
                for item in results.get("items", []):
                    if "id" in item and "videoId" in item["id"]:
                        video_title = item.get("snippet", {}).get("title")
                        video_thumb = (
                            item.get("snippet", {})
                            .get("thumbnails", {})
                            .get("high", {})
                            .get("url")
                        )
                        video_url = item["id"]["videoId"]
                        video_author = item.get("snippet", {}).get("channelTitle")
                        video = Result(
                            video_title, video_thumb, video_url, video_author
                        )
                        videos.append(video)
                    else:
                        logging.warning(f"Skipping non-video item: {item}")
                return videos
            else:
                logging.error(f"No 'items' key in API response: {results}")
                return []
        except requests.RequestException as e:
            logging.error(f"Request to YouTube API failed: {e}")
            return []
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return []
    
    @cached(cache=LRUCache(maxsize=100))
    def get_videos(self, playlist_id: str) -> list[Music]:
        """
        Obtém os vídeos de uma playlist do YouTube.

        Args:
            playlist_id (str): O ID da playlist no YouTube.

        Returns:
            List[Music]: Uma lista de vídeos da playlist.
        """
        try:
            base_url = "https://www.googleapis.com/youtube/v3/playlistItems"
            params = {
                "part": "snippet",
                "maxResults": 25,
                "playlistId": playlist_id,
                "key": self.api_key,
            }
            response = requests.get(base_url, params=params)
            results = response.json()

            videos = []
            for item in results.get("items", []):
                video_title = item["snippet"]["title"]
                video_thumb = item["snippet"]["thumbnails"].get("high", {}).get("url")
                video_url = item.get("snippet").get("resourceId").get("videoId")
                video_author = item["snippet"]["videoOwnerChannelTitle"]
                music = Music(video_title, video_thumb, video_url, video_author)
                videos.append(music)

            return videos
        except Exception as e:
            logging.error(f"Error while downloading the video: {e}")
            return None

    @cached(cache=LRUCache(maxsize=100))
    def get_playlist(self, query: str) -> list[Result]:
        """
        Obtém playlists do YouTube com base em uma query.

        Args:
            query (str): O termo de busca.

        Returns:
            List[Result]: Uma lista de playlists encontradas.
        """
        try:
            base_url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "maxResults": 25,
                "key": self.api_key,
                "type": "playlist",
                "q": query,
            }
            response = requests.get(base_url, params=params)
            results = response.json()

            if "items" in results:
                videos = []
                for item in results.get("items", []):
                    if "id" in item and "playlistId" in item["id"]:
                        video_title = item.get("snippet", {}).get("title")
                        video_thumb = (
                            item.get("snippet", {})
                            .get("thumbnails", {})
                            .get("high", {})
                            .get("url")
                        )
                        video_url = item["id"]["playlistId"]
                        video_author = item.get("snippet", {}).get("channelTitle")
                        video = Result(
                            video_title, video_thumb, video_url, video_author
                        )
                        videos.append(video)
                    else:
                        logging.warning(f"Skipping non-video item: {item}")
                return videos
            else:
                logging.error(f"No 'items' key in API response: {results}")
                return []
        except requests.RequestException as e:
            logging.error(f"Request to YouTube API failed: {e}")
            return []
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return []

    @cached(cache=LRUCache(maxsize=100))
    def stream(self, id: str) -> str:
        """
        Retorna a URL de streaming de áudio de um vídeo do YouTube.

        Args:
            id (str): O ID do vídeo no YouTube.

        Returns:
            str: A URL de streaming do áudio.
        """
        yt = YT(f"https://music.youtube.com/watch?v={id}")
        audio = yt.streams.filter(only_audio=True).first()
        return audio.url