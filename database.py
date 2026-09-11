import os
from datetime import datetime, timezone

import psycopg
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = (
    os.getenv("DATABASE_URL") or ""
).strip()

#取得資料庫連線
def get_connection() -> psycopg.Connection:
    if not DATABASE_URL:
        raise RuntimeError("找不到 DATABASE_URL")

    return psycopg.connect(DATABASE_URL)

#初始化資料庫，建立必要的資料表
def initialize_database() -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS
                sent_announcements (
                    topic_id BIGINT PRIMARY KEY,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    sent_at TIMESTAMPTZ NOT NULL
                )
                """
            )

#檢查公告是否已經發送過
def is_announcement_sent(topic_id: int) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM sent_announcements
                WHERE topic_id = %s
                """,
                (topic_id,),
            )

            result = cursor.fetchone()

    return result is not None

#將公告標記為已發送
def mark_announcement_as_sent(
    announcement: dict,
) -> None:
    sent_at = datetime.now(timezone.utc)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sent_announcements (
                    topic_id,
                    title,
                    url,
                    sent_at
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (topic_id) DO NOTHING
                """,
                (
                    announcement["id"],
                    announcement["title"],
                    announcement["url"],
                    sent_at,
                ),
            )