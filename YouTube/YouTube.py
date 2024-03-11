from pytube import YouTube as YT
import os
import requests
import logging
from mutagen.mp4 import MP4, MP4Cover
from PIL import Image
from model.music import Music
import io
from dotenv import load_dotenv

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
    def __init__(self) -> None:
        load_dotenv()

        self.api_key = os.environ["API_KEY"]

    def setContent(self, music: Result):
        self.title = music.title
        self.thumb = music.thumb
        self.url = music.url
        self.author = music.author

    def download(self, id: str):
        path = ""
        try:
            yt = YT(f"https://music.youtube.com/watch?v={id}")
            video = yt.streams.filter(only_audio=True).first()
            self.setContent(
                Result(
                    yt.title,
                    yt.thumbnail_url,
                    yt.video_id,
                    yt.author,
                )
            )
            downloaded_file = video.download("cache")
            path = downloaded_file

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
            mp4["\xa9alb"] = f"thumbnail_url = {yt.thumbnail_url}, url = {id}"
            mp4["\xa9nam"] = yt.title
            mp4["\xa9des"] = id
            # Salvando as alterações
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

    def search(self, query: str) -> list[Result]:
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

            if "items" in results:
                videos: list[Result] = []
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

    def get_videos(self, playlist_id: str) -> list[Music]:
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

            videos: list[Music] = []
            for item in results["items"]:
                video_title = item["snippet"]["title"]
                video_thumb = item["snippet"]["thumbnails"].get("high", {}).get("url")
                video_url = item.get("snippet").get("resourceId").get("videoId")
                video_author = item["snippet"]["videoOwnerChannelTitle"]
                music = Music(
                    video_title,
                    video_thumb,
                    video_url,
                    video_author,
                )
                videos.append(music)

            return videos
        except Exception as e:
            logging.error(f"Error while downloading the video: {e}")
            return None

    def get_playlist(self, query: str) -> list[Result]:
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
                videos: list[Result] = []
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
        
    def stream(self, id: str): 
        yt = YT(f"https://music.youtube.com/watch?v={id}")
        audio = yt.streams.filter(only_audio=True).first()
        return audio.url