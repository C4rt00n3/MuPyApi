class Music:
    def __init__(self, id: int, title: str, thumb: str, url: str, author: str):
        self.id = id
        self.title = title
        self.thumb = thumb
        self.url = url
        self.author = author

    def __str__(self) -> str:
        content = f"    url: {self.url},\n    thumb: {self.thumb}\n    title: {self.title}\n author: {self.author}"
        return "{\n" + content + "\n},"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "thumb": self.thumb,
            "url": self.url,
            "author": self.author,
        }
