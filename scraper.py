from datetime import datetime #用來格式化時間日期
from bs4 import BeautifulSoup #用來解析HTML

import httpx #用來發送HTTP請求

#設定網址，會直接連接兩行
DEVFORUM_URL = (
    "https://devforum.roblox.com"
    "/c/updates/announcements/36/l/latest.json"
)

#設定請求標頭，告訴網站管理者請求來源是誰
HEADERS = {
    "User-Agent": "RobloxDevForumNotifier/0.1"
}

#取得最新五篇公告，回傳一個字典列表
def get_latest_announcements(limit: int = 5) -> list[dict]:

    #發送HTTP GET請求
    response = httpx.get(
        DEVFORUM_URL,
        headers=HEADERS,
        timeout=15, #最多等15秒
        follow_redirects=True, #自動跟隨重新導向
    )
    response.raise_for_status() #檢查HTTP狀態碼

    data = response.json() #json轉python字典
    topics = data["topic_list"]["topics"]

    announcements = []

    for topic in topics:

        #排除分類介紹等置頂內容
        if topic.get("pinned"):
            continue

        announcements.append(
            {
                "id": topic["id"],
                "title": topic["title"],
                "slug": topic["slug"], #網址可讀名稱
                "url": (
                    f"https://devforum.roblox.com/t/"
                    f"{topic['slug']}/{topic['id']}"
                ),
                "created_at": topic["created_at"],
                "views": topic.get("views", 0),
                "reply_count": topic.get("reply_count", 0),
                "tags": topic.get("tags", []),
            }
        )

    #按時間排序，最新到最舊
    announcements.sort(
        key=lambda item: item["created_at"],
        reverse=True,
    )

    return announcements[:limit]

def normalize_heading(text: str) -> str:
    return text.strip().lower().rstrip(":")


def find_key_takeaways_block(
    soup: BeautifulSoup,
):
    accepted_headings = {
        "key takeaway",
        "key takeaways",
    }

    for blockquote in soup.find_all("blockquote"):
        headings = blockquote.find_all(
            [
                "strong",
                "b",
                "h1",
                "h2",
                "h3",
                "h4",
                "p",
            ]
        )

        for heading in headings:
            heading_text = normalize_heading(
                heading.get_text(" ", strip=True)
            )

            if heading_text in accepted_headings:
                return blockquote

    return None


def remove_key_takeaways_heading(
    soup: BeautifulSoup,
) -> None:
    accepted_headings = {
        "key takeaway",
        "key takeaways",
    }

    for heading in soup.find_all(
        [
            "strong",
            "b",
            "h1",
            "h2",
            "h3",
            "h4",
            "p",
        ]
    ):
        heading_text = normalize_heading(
            heading.get_text(" ", strip=True)
        )

        if heading_text not in accepted_headings:
            continue

        parent = heading.parent

        # 常見結構是 <p><strong>Key Takeaways</strong></p>
        if (
            parent is not None
            and parent.name == "p"
            and parent.get_text(" ", strip=True)
            == heading.get_text(" ", strip=True)
        ):
            parent.decompose()
        else:
            heading.decompose()

        return

#取得公告正文摘要
def get_announcement_excerpt(
    announcement: dict,
    max_characters: int = 800,
) -> str:
    topic_url = (
        f"https://devforum.roblox.com/t/"
        f"{announcement['id']}.json"
    )

    response = httpx.get(
        topic_url,
        headers=HEADERS,
        timeout=15,
        follow_redirects=True,
    )
    response.raise_for_status()

    data = response.json()
    posts = data["post_stream"]["posts"]

    if not posts:
        return "這篇公告目前沒有可讀取的內容。"

    first_post_html = posts[0]["cooked"]
    soup = BeautifulSoup(first_post_html, "html.parser")

    key_takeaways_block = find_key_takeaways_block(soup)

    if key_takeaways_block is None:
        return "這篇公告沒有提供重點摘要。"

    # 重新解析一份副本，避免修改原始 soup
    block_copy = BeautifulSoup(
        str(key_takeaways_block),
        "html.parser",
    )

    remove_key_takeaways_heading(block_copy)

    for element in block_copy(
        ["script", "style", "pre", "code", "img"]
    ):
        element.decompose()

    text = block_copy.get_text(
        separator=" ",
        strip=True,
    )
    text = " ".join(text.split())

    if len(text) <= max_characters:
        return text

    return text[:max_characters].rstrip() + "…"

#時間格式
def format_time(timestamp: str) -> str:
    parsed_time = datetime.fromisoformat(
        timestamp.replace("Z", "+00:00")
    )
    return parsed_time.strftime("%Y-%m-%d %H:%M UTC")


if __name__ == "__main__":
    topics = get_latest_announcements(limit=1)

    for topic in topics:
        excerpt = get_announcement_excerpt(topic)

        print(f"標題：{topic['title']}")
        print(f"網址：{topic['url']}")
        print("\n正文摘要：")
        print(excerpt)