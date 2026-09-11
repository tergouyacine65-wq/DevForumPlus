import os

import httpx
from dotenv import load_dotenv


load_dotenv()

DEEPL_API_KEY = (
    os.getenv("DEEPL_API_KEY") or ""
).strip()

DEEPL_API_URL = (
    os.getenv(
        "DEEPL_API_URL",
        "https://api-free.deepl.com/v2/translate",
    )
    or ""
).strip()


def translate_text(
    text: str,
    target_language: str = "ZH-HANT",
) -> str:
    if not text.strip():
        return ""

    if not DEEPL_API_KEY:
        raise RuntimeError("找不到 DEEPL_API_KEY")

    response = httpx.post(
        DEEPL_API_URL,
        headers={
            "Authorization": (
                f"DeepL-Auth-Key {DEEPL_API_KEY}"
            ),
            "Content-Type": "application/json",
        },
        json={
            "text": [text],
            "source_lang": "EN",
            "target_lang": target_language,
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()
    translations = data.get("translations", [])

    if not translations:
        raise RuntimeError("DeepL 沒有回傳翻譯結果")

    return translations[0]["text"]


if __name__ == "__main__":
    original = "Roblox Studio is receiving a new update."
    translated = translate_text(original)

    print(f"原文：{original}")
    print(f"翻譯：{translated}")