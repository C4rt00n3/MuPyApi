import io
import re
import os
import requests
import logging
from PIL import Image
import yt_dlp as youtube_dl
from model.music import Music
from dotenv import load_dotenv
from typing import List, Any, Dict
from cachetools import cached, LRUCache
from youtube_dl.utils import DownloadError
from mutagen.id3 import ID3, TIT2, APIC, TPE1, TALB


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
    """
    Classe para interação com a API do YouTube.

    Attributes:
        api_key (str): A chave de API do YouTube.
    """

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
            }
        ],
        'outtmpl': '%(id)s.%(ext)s',
        "postprocessor_args": ["-ar", "16000"],
        "prefer_ffmpeg": True,
        "keepvideo": False,  # Não mantém o vídeo baixado
        "ignoreerrors": True,  # Para ignorar erros durante a extração
    }

    def __init__(self) -> None:
        """
        Inicializa a classe YouTube e carrega a chave de API do YouTube do ambiente.
        """
        load_dotenv()
        self.api_key = os.getenv("API_KEY")

    def set_content(self, music: Result) -> None:
        """
        Define o título, imagem de thumbnail, URL e autor de um vídeo.

        Args:
            music (Result): O objeto Result contendo informações sobre o vídeo.
        """
        self.title = music.title
        self.thumb = music.thumb
        self.url = music.url
        self.author = music.author

    def extract_metadata_and_add_to_mp3(
        self, metadata: Dict[str, Any], 
    ):
        try:
            mp3_filename = metadata.get("path")
            thumbnail_url = metadata.get("thumb")
            channel_name = metadata.get("channel")
            video_id = metadata.get("id")
            video_title = metadata.get("title")

            response = requests.get(thumbnail_url)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content))

            # Save the image to a byte array
            byte_arr = io.BytesIO()
            image.save(byte_arr, format="JPEG")
            image_data = byte_arr.getvalue()

            # Lê os metadados existentes
            tags = ID3(mp3_filename)
            # Adicione titulo ao arquivo
            tags.add(TIT2(encoding=3, text=video_title))
            # Adiciona a imagem como arte de álbum
            tags.add(
                APIC(
                    encoding=3, mime="image/jpeg", type=3, desc="Cover", data=image_data
                )
            )
            # Adicona nome do artista
            tags.add(TPE1(encoding=3, text=channel_name))
            # Adiciona nome do album
            tags.add(
                TALB(
                    encoding=3,
                    text=f"thumbnail_url = {thumbnail_url}, url = {video_id}",
                )
            )

            # Salva as alterações
            tags.save()
            return mp3_filename
        except (requests.exceptions.RequestException, IOError) as e:
            raise RuntimeError(f"Failed to extract metadata and add to MP3: {e}")

    @cached(cache=LRUCache(maxsize=15))
    def download(self, video_id: str) -> bytes:
        try:
            with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(
                    f"https://www.youtube.com/watch?v={video_id}",
                    download=True,
                )
                metadata = {
                    "title": str(info["title"]),
                    "thumb": info["thumbnails"][-1]["url"],
                    "id": video_id,
                    "channel": info["uploader"],
                    "path": f"{video_id}.mp3"
                }

                mp3_path = self.extract_metadata_and_add_to_mp3(metadata)

                with open(mp3_path, "rb") as content:
                    mp3_content = content.read()

                os.remove(mp3_path)

                return mp3_content
        except DownloadError as e:
            raise RuntimeError(f"Failed to download audio: {e}")

    @cached(cache=LRUCache(maxsize=100))
    def search(self, query: str) -> List[Result]:
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
    def get_videos(self, playlist_id: str) -> List[Music]:
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

    @cached(cache=LRUCache(maxsize=15))
    def get_playlist(self, query: str) -> List[Result]:
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
