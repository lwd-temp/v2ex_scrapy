import sqlite3
from typing import List, Type, Union
from tutorial_scrapy import utils

from tutorial_scrapy.items import (
    CommentItem,
    MemberItem,
    TopicItem,
    TopicSupplementItem,
)


class DB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Connect to SQLite database
        self.conn = sqlite3.connect("v2ex.sqlite")
        self.cursor = self.conn.cursor()

        self.create_tables()
        self.a = {
            TopicItem: self.topic_exist,
            CommentItem: self.comment_exist,
            MemberItem: self.member_exist,
        }

    def close(self):
        self.conn.close()

    def create_tables(self):
        # Create topics table
        with open("./db.sql") as f:
            self.cursor.executescript(f.read())

    def exist(
        self, type_: Union[Type[TopicItem], Type[CommentItem], Type[MemberItem]], q
    ) -> bool:
        return self.a[type_](q)

    def get_max_topic_id(self) -> int:
        result = self.cursor.execute("SELECT max(id) FROM topic").fetchone()[0]
        if result == None:
            return 1
        return int(result)

    def topic_exist(self, q) -> bool:
        # Check if topic exists in the database based on unique identifier (id_)
        query = "SELECT id FROM topic WHERE id = ?"
        self.cursor.execute(query, (q,))
        result = self.cursor.fetchone()

        return result is not None

    def comment_exist(self, q) -> bool:
        # Check if comment exists in the database based on unique identifier (id_)
        query = "SELECT id FROM comment WHERE id = ?"
        self.cursor.execute(query, (q,))
        result = self.cursor.fetchone()

        return result is not None

    def member_exist(self, q) -> bool:
        # Check if member exists in the database based on unique identifier (username)
        query = "SELECT username FROM member WHERE username = ?"
        self.cursor.execute(query, (q,))
        result = self.cursor.fetchone()

        return result is not None

    def save_topics(self, topics: List[TopicItem]) -> None:
        # Insert the topic data into the table
        self.cursor.executemany(
            """INSERT or IGNORE INTO topic (id, author, create_at, title, content, node, clicks, tag, votes)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    topic.id_,
                    topic.author,
                    topic.create_at,
                    topic.title,
                    topic.content,
                    topic.node,
                    topic.clicks,
                    utils.json_to_str(topic.tag),
                    topic.votes,
                )
                for topic in topics
            ],
        )
        self.conn.commit()

    def save_topic_supplements(self, i: List[TopicSupplementItem]) -> None:
        # Insert the topic data into the table
        self.cursor.executemany(
            """INSERT or IGNORE INTO topic_supplement (topic_id, content, create_at)
                              VALUES (?, ?, ?)""",
            ([(x.topic_id, x.content, x.create_at) for x in i]),
        )
        self.conn.commit()

    def save_comments(self, comments: List[CommentItem]) -> None:
        # Insert the comment data into the table
        self.cursor.executemany(
            """INSERT or IGNORE INTO comment (id, topic_id, commenter, content, create_at, thank_count)
                              VALUES (?, ?, ?, ?, ?, ?)""",
            [
                (
                    comment.id_,
                    comment.topic_id,
                    comment.commenter,
                    comment.content,
                    comment.create_at,
                    comment.thank_count,
                )
                for comment in comments
            ],
        )
        self.conn.commit()

    def save_members(self, members: List[MemberItem]) -> None:
        self.cursor.executemany(
            """INSERT or IGNORE INTO member (username, avatar_url, create_at, social_link, no)
                              VALUES (?, ?, ?, ?, ?)""",
            [
                (
                    member.username,
                    member.avatar_url,
                    member.create_at,
                    utils.json_to_str(member.social_link),
                    member.no,
                )
                for member in members
            ],
        )
        self.conn.commit()
