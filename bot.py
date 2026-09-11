import os

import httpx
from dotenv import load_dotenv


load_dotenv()

DISCORD_WEBHOOK_URL = (
    os.getenv("DISCORD_WEBHOOK_URL") or ""
).strip()

def send_announcement(announcement: dict) -> None:
    if not DISCORD_WEBHOOK_URL:
        raise RuntimeError("找不到 DISCORD_WEBHOOK_URL")

    tags = announcement.get("tags", [])
    tags_text = ", ".join(tags) if tags else "無"

    translated_title = announcement.get(
        "translated_title",
        announcement["title"],
    )

    translated_excerpt = announcement.get(
        "translated_excerpt",
        "目前沒有公告摘要。",
    )

    payload = {
        "username": "Roblox DevForum 官方公告",
        "embeds": [
            {
                "title": translated_title[:256],
                "url": announcement["url"],
                "description": translated_excerpt[:3500],
                "color": 5793266,
                "fields": [
                    {
                        "name": "英文標題",
                        "value": announcement["title"][:1024],
                        "inline": False,
                    },
                    {
                        "name": "標籤",
                        "value": tags_text[:1024],
                        "inline": True,
                    },
                    {
                        "name": "瀏覽次數",
                        "value": str(announcement["views"]),
                        "inline": True,
                    },
                ],
                "footer": {
                    "text": (
                        "機器翻譯｜來源："
                        "Roblox Developer Forum"
                    )
                },
                "timestamp": announcement["created_at"],
            }
        ],
    }

    response = httpx.post(
        DISCORD_WEBHOOK_URL,
        json=payload,
        timeout=15,
    )
    response.raise_for_status()

    print(f"已發送 Discord 通知：{translated_title}")


if __name__ == "__main__":
    print("請透過 main.py 執行通知流程")