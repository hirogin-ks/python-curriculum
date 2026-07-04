from bs4 import BeautifulSoup


def parse_price(text: str) -> int | float:
    cleaned = (
        text.replace("¥", "")
        .replace("$", "")
        .replace("円", "")
        .replace(",", "")
        .strip()
    )

    if not cleaned:
        raise ValueError(f"変換できない価格文字列です: '{text}'")

    try:
        return float(cleaned) if "." in cleaned else int(cleaned)
    except ValueError as exc:
        raise ValueError(f"変換できない価格文字列です: '{text}'") from exc


def parse_quote(html: str) -> dict | None:
    soup = BeautifulSoup(html, "html.parser")
    text_tag = soup.find(class_="text")
    author_tag = soup.find(class_="author")

    if text_tag is None or author_tag is None:
        return None

    return {
        "text": text_tag.get_text(strip=True),
        "author": author_tag.get_text(strip=True),
    }
