import requests
from loguru import logger


def fetch_urls(urls: list[str]) -> None:
    logger.info("スクレイピング開始")

    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            logger.success(f"成功 ({response.status_code}): {url}")
        except requests.exceptions.HTTPError as exc:
            logger.error(f"HTTPエラー ({response.status_code}): {url} → {exc}")
        except requests.exceptions.RequestException as exc:
            logger.error(f"リクエストエラー: {url} → {exc}")

    logger.info("スクレイピング完了")
