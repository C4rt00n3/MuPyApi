import os
import psycopg2
from dotenv import load_dotenv
from model.Playlist import Playlist
from model.Muisc import Music


class Database:
    def __init__(self) -> None:
        load_dotenv()
        self.conn = psycopg2.connect(
            host=os.environ["HOST"],
            port=os.environ["PORT"],
            dbname=os.environ["DBNAME"],
            user=os.environ["USER"],
            password=os.environ["PASSWORD"],
        )
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        try:
            create_sql = """
                CREATE TABLE IF NOT EXISTS playlist (
                    id SERIAL PRIMARY KEY,
                    link TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS music (
                    id SERIAL PRIMARY KEY,
                    title TEXT,
                    thumb TEXT,
                    author TEXT,
                    url TEXT
                );

                CREATE TABLE IF NOT EXISTS playlist_music_relation (
                    playlist_id INT REFERENCES playlist(id) ON DELETE CASCADE,
                    music_id INT REFERENCES music(id) ON DELETE CASCADE,
                    PRIMARY KEY (playlist_id, music_id)
                );
            """
            self.execute(create_sql)
            print("=" * 20 + "Feito com sucesso!" + "=" * 20)
        except Exception as error:
            print(error)

    def execute(self, sql, parameters=None):
        try:
            self.cur.execute(sql, parameters)
            self.conn.commit()
        except Exception as error:
            print(error)
            raise  # Re-raise a exceção para notificar o chamador

    def create_playlist(self, link: str):
        try:
            # Verifica se a playlist já existe
            existing_playlist = self.find_first(link)

            if existing_playlist:
                return existing_playlist  # Retorna o ID da playlist existente

            # Insere a nova playlist
            sql = "INSERT INTO playlist (link) VALUES (%s) RETURNING id;"
            self.cur.execute(sql, (link,))
            self.conn.commit()

            return self.find_first(link)
        except Exception as error:
            print(error)

    def find_first(self, link: str):
        try:
            sql = """
                SELECT p.id AS playlist_id, p.link AS playlist_link,
                    m.id AS music_id, m.title, m.thumb, m.author, m.url
                FROM playlist p
                LEFT JOIN playlist_music_relation pmr ON p.id = pmr.playlist_id
                LEFT JOIN music m ON pmr.music_id = m.id
                WHERE p.link = %s
            """
            self.execute(sql, (link,))
            playlist_data = self.cur.fetchall()

            if not playlist_data:
                return None

            playlist_info = Playlist(playlist_data[0][0], playlist_data[0][1], [])

            for row in playlist_data:
                if row[2]:  # Se há dados de música
                    id = row[2]
                    title = row[3]
                    thumb = row[4]
                    url = row[6]
                    author = row[5]
                    music_info = Music(id, title, thumb, url, author)
                    playlist_info.musics.append(music_info)

            return playlist_info

        except Exception as error:
            raise error
        finally:
            # Não é necessário chamar __init__ aqui, pois a conexão já foi estabelecida no __init__
            pass

    def close_connection(self):
        if self.conn:
            self.conn.close()

    def __del__(self):
        # Certifique-se de fechar a conexão quando o objeto é destruído
        self.close_connection()

    def create_music(
        self, title: str, thumb: str, author: str, url: str, playlist_id: int
    ):
        try:
            # Insere a nova música
            sql_music = "INSERT INTO music (title, thumb, author, url) VALUES (%s, %s, %s, %s) RETURNING id;"
            self.cur.execute(sql_music, (title, thumb, author, url))
            music_id = self.cur.fetchone()[0]

            # Associa a música à playlist
            sql_relation = "INSERT INTO playlist_music_relation (playlist_id, music_id) VALUES (%s, %s);"
            self.cur.execute(sql_relation, (playlist_id, music_id))

            self.conn.commit()

            return music_id
        except Exception as error:
            print(error)
