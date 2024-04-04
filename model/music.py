class Music:
    def __init__(self, title: str, thumb: str, url: str, author: str):
        self.title = title
        self.thumb = thumb
        self.url = url
        self.author = author

    def __str__(self) -> str:
        content = f"    url: {self.url},\n    thumb: {self.thumb}\n    title: {self.title}\n author: {self.author}"
        return "{\n" + content + "\n},"

    def to_dict(self):
        return {
            "title": self.title,
            "thumb": self.thumb,
            "url": self.url,
            "author": self.author,
        }
