import csv
from importlib import util
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from loguru import logger


def load_database():
    path = Path(__file__).with_name("01_database.py")
    spec = util.spec_from_file_location("lesson_24_database", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("module load failed: 01_database.py")

    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JobScraper:
    def __init__(self, url: str, output_dir: str = "output"):
        self.url = url
        self.output_dir = Path(output_dir)
        self.csv_path = self.output_dir / "jobs.csv"
        self.db_path = self.output_dir / "jobs.db"

    def fetch(self) -> list[dict]:
        response = requests.get(self.url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        jobs: list[dict] = []

        for card in soup.select(".card-content"):
            title = card.select_one(".title").get_text(strip=True)
            company = card.select_one(".company").get_text(strip=True)
            location = card.select_one(".location").get_text(strip=True)
            jobs.append({"title": title, "company": company, "location": location})

        return jobs

    def save_csv(self, jobs: list[dict]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with self.csv_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "company", "location"])
            writer.writeheader()
            writer.writerows(jobs)

    def save_db(self, jobs: list[dict]) -> tuple[int, int]:
        database = load_database()
        return database.save_jobs_to_db(jobs, self.db_path)

    def run(self) -> None:
        logger.info("スクレイピング開始")
        jobs = self.fetch()
        logger.success(f"{len(jobs)}件 取得完了")
        self.save_csv(jobs)
        logger.success(f"{self.csv_path} に保存完了")
        inserted, skipped = self.save_db(jobs)
        logger.success(f"DB: 新規 {inserted}件 / スキップ {skipped}件")
