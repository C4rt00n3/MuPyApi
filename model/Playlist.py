from model.music import Music
from typing import List

class Playlist:
    def __init__(self, id: int, link, musics: List[Music]):
        self.id = id
        self.link = link
        self.musics = musics

    def __str__(self):
        return f"Playlist(id={self.id}, link={self.link}, musics={self.musics})"

    def to_dict(self):
        return {
            "id": self.id,
            "link": self.link,
            "musics": [music.to_dict() for music in self.musics],
        }
