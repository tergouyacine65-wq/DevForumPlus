from bot import send_announcement
from scraper import (
    get_announcement_excerpt,
    get_latest_announcements,
)
from database import (
    initialize_database,
    is_announcement_sent,
    mark_announcement_as_sent,
)
from translator import translate_text


def prepare_announcement(announcement: dict) -> dict:
    print(f"正在取得正文：{announcement['title']}")
    excerpt = get_announcement_excerpt(announcement)

    print("正在翻譯標題……")
    translated_title = translate_text(
        announcement["title"]
    )

    print("正在翻譯摘要……")
    translated_excerpt = translate_text(excerpt)

    return {
        **announcement,
        "excerpt": excerpt,
        "translated_title": translated_title,
        "translated_excerpt": translated_excerpt,
    }


def main() -> None:
    initialize_database()

    announcements = get_latest_announcements(limit=5)

    if not announcements:
        print("目前找不到公告")
        return

    new_announcement_count = 0

    # 由最舊到最新發送，保持閱讀順序
    for announcement in reversed(announcements):
        if is_announcement_sent(announcement["id"]):
            print(f"已發送過，跳過：{announcement['title']}")
            continue

        prepared_announcement = prepare_announcement(
            announcement
        )

        send_announcement(prepared_announcement)

        mark_announcement_as_sent(
            prepared_announcement
        )

        new_announcement_count += 1

    if new_announcement_count == 0:
        print("沒有需要發送的新公告")
    else:
        print(
            f"本次共發送 "
            f"{new_announcement_count} 篇新公告"
        )


if __name__ == "__main__":
    main()