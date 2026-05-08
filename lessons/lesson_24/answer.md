# 第24回：卒業制作 - 求人情報収集システム【解答・解説】

以下の解答はあくまでも一例です。同じ動作をするコードであれば、別の書き方でも正解です。自分のコードと見比べながら、設計の違いを確認してみてください。

---

## 📝 問題1 の解答

```python
import requests
from bs4 import BeautifulSoup

url = "https://realpython.github.io/fake-jobs/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

cards = soup.find_all("div", class_="card")
jobs = []

for card in cards:
    title = card.find("p", class_="title").text.strip()
    company = card.find("p", class_="subtitle").text.strip()
    location = card.find("p", class_="location").get_text(strip=True)
    date = card.find("time")["datetime"]

    jobs.append({
        "title": title,
        "company": company,
        "location": location,
        "date": date,
    })

for i, job in enumerate(jobs, start=1):
    print(f"[{i}] {job['title']}")
    print(f"    会社：{job['company']}")
    print(f"    場所：{job['location']}")
    print(f"    日付：{job['date']}")
    print()

print(f"合計 {len(jobs)} 件取得しました")
```

**実行結果（先頭2件）:**

```
[1] Senior Python Developer
    会社：Payne, Roberts and Davis
    場所：Stewartbury, AA
    日付：2021-04-08

[2] Energy engineer
    会社：Vasquez-Davidson
    場所：Christopherville, AA
    日付：2021-04-08

...

合計 100 件取得しました
```

### なぜこう書くの？

`card.find("p", class_="location")` で取得した `<p>` タグには SVG アイコンが含まれているため `.text` だとうまく取れない場合があります。`.get_text(strip=True)` を使うと、タグ内のテキストをすべて連結してから前後の空白を除去してくれます。

`card.find("time")["datetime"]` は `<time datetime="2021-04-08">` の属性値を取り出しています。`["属性名"]` で要素の属性にアクセスできます。

---

## 📝 問題2 の解答

```python
import csv
import os
import requests
from bs4 import BeautifulSoup

url = "https://realpython.github.io/fake-jobs/"
output_path = "output/jobs.csv"

def fetch_jobs(url: str) -> list[dict]:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.find_all("div", class_="card")

    jobs = []
    for card in cards:
        jobs.append({
            "title": card.find("p", class_="title").text.strip(),
            "company": card.find("p", class_="subtitle").text.strip(),
            "location": card.find("p", class_="location").get_text(strip=True),
            "date": card.find("time")["datetime"],
        })
    return jobs


def save_to_csv(jobs: list[dict], filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "company", "location", "date"])
        writer.writeheader()
        writer.writerows(jobs)

    print(f"{len(jobs)}件を {filepath} に保存しました")


jobs = fetch_jobs(url)
save_to_csv(jobs, output_path)
```

### なぜこう書くの？

`os.makedirs(os.path.dirname(filepath), exist_ok=True)` は `output/` フォルダがなければ作り、すでにあればエラーを出さずスキップします。`csv.DictWriter` は辞書のリストをそのまま CSV に書き出せる便利なクラスです。

`newline=""` を指定しないと Windows で改行が2重になるため、必ず指定します。

---

## 📝 問題3 の解答

```python
import csv
import os
import requests
from bs4 import BeautifulSoup
from loguru import logger

url = "https://realpython.github.io/fake-jobs/"
output_path = "output/jobs.csv"
log_path = "output/scraper.log"

os.makedirs("output", exist_ok=True)
logger.add(
    log_path,
    level="INFO",
    rotation="1 MB",
    retention="7 days",
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)


def fetch_jobs(url: str) -> list[dict]:
    logger.info(f"スクレイピング開始: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTPエラー: {e}")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"リクエストエラー: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.find_all("div", class_="card")

    jobs = []
    for card in cards:
        jobs.append({
            "title": card.find("p", class_="title").text.strip(),
            "company": card.find("p", class_="subtitle").text.strip(),
            "location": card.find("p", class_="location").get_text(strip=True),
            "date": card.find("time")["datetime"],
        })

    logger.success(f"{len(jobs)}件 取得完了")
    return jobs


def save_to_csv(jobs: list[dict], filepath: str) -> None:
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "company", "location", "date"])
        writer.writeheader()
        writer.writerows(jobs)
    logger.success(f"{filepath} に保存完了")


jobs = fetch_jobs(url)
if jobs:
    save_to_csv(jobs, output_path)
```

### なぜこう書くの？

`Response.raise_for_status()` は 4xx・5xx のステータスコードで `HTTPError` を発生させます。これを `except requests.exceptions.HTTPError` でキャッチすることで、HTTP エラーと接続エラーを分けて処理できます。

`if jobs:` でフェッチに失敗して空リストが返ってきたときは CSV 保存をスキップします。

---

## 📝 問題4 の解答

```python
# scraper.py
import csv
import os
import sqlite3

import requests
from bs4 import BeautifulSoup
from loguru import logger


class JobScraper:
    def __init__(self, url: str, output_dir: str = "output"):
        self.url = url
        self.output_dir = output_dir
        self.csv_path = os.path.join(output_dir, "jobs.csv")
        self.db_path = os.path.join(output_dir, "jobs.db")
        self.log_path = os.path.join(output_dir, "scraper.log")

        os.makedirs(output_dir, exist_ok=True)
        logger.add(
            self.log_path,
            level="INFO",
            rotation="1 MB",
            retention="7 days",
            encoding="utf-8",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        )

    def fetch(self) -> list[dict]:
        logger.info(f"スクレイピング開始: {self.url}")

        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTPエラー: {e}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"リクエストエラー: {e}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.find_all("div", class_="card")

        jobs = []
        for card in cards:
            jobs.append({
                "title": card.find("p", class_="title").text.strip(),
                "company": card.find("p", class_="subtitle").text.strip(),
                "location": card.find("p", class_="location").get_text(strip=True),
                "date": card.find("time")["datetime"],
            })

        logger.success(f"{len(jobs)}件 取得完了")
        return jobs

    def save_csv(self, jobs: list[dict]) -> None:
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=["title", "company", "location", "date"]
            )
            writer.writeheader()
            writer.writerows(jobs)
        logger.success(f"{self.csv_path} に保存完了")

    def save_db(self, jobs: list[dict]) -> tuple[int, int]:
        new_count = 0
        skip_count = 0
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT,
                    date TEXT,
                    UNIQUE(title, company)
                )
            """)
            for job in jobs:
                cursor = conn.execute(
                    "INSERT OR IGNORE INTO jobs (title, company, location, date) VALUES (?, ?, ?, ?)",
                    (job["title"], job["company"], job["location"], job["date"]),
                )
                if cursor.rowcount > 0:
                    new_count += 1
                else:
                    skip_count += 1
        return new_count, skip_count

    def run(self) -> None:
        jobs = self.fetch()
        if not jobs:
            logger.warning("取得データが0件のため処理を中断します")
            return

        self.save_csv(jobs)

        new_count, skip_count = self.save_db(jobs)
        if new_count > 0:
            logger.success(f"DB: 新規 {new_count}件 / スキップ {skip_count}件")
        else:
            logger.info(f"DB: 新規 {new_count}件 / スキップ {skip_count}件")
```

```python
# main.py
from scraper import JobScraper

if __name__ == "__main__":
    scraper = JobScraper("https://realpython.github.io/fake-jobs/")
    scraper.run()
```

**1回目の実行結果:**

```
2025-01-01 12:00:00 | INFO    | スクレイピング開始: https://realpython.github.io/fake-jobs/
2025-01-01 12:00:01 | SUCCESS | 100件 取得完了
2025-01-01 12:00:01 | SUCCESS | output/jobs.csv に保存完了
2025-01-01 12:00:01 | SUCCESS | DB: 新規 100件 / スキップ 0件
```

**2回目の実行結果（重複スキップ）:**

```
2025-01-01 12:01:00 | INFO    | スクレイピング開始: https://realpython.github.io/fake-jobs/
2025-01-01 12:01:01 | SUCCESS | 100件 取得完了
2025-01-01 12:01:01 | SUCCESS | output/jobs.csv に保存完了
2025-01-01 12:01:01 | INFO    | DB: 新規 0件 / スキップ 100件
```

### なぜこう書くの？

**`UNIQUE(title, company)` について:**

CREATE TABLE に `UNIQUE` 制約を付けることで、タイトルと会社名の組み合わせが同一のレコードは2件目以降が自動的に拒否されます。`INSERT OR IGNORE` と組み合わせることで、エラーを発生させずに静かにスキップできます。

**`cursor.rowcount` について:**

`INSERT OR IGNORE` が実際に挿入に成功した場合は `rowcount` が `1`、スキップされた場合は `0` になります。これで新規件数とスキップ件数を数えられます。

**`if __name__ == "__main__":` について:**

`main.py` を直接実行したときだけ `scraper.run()` が動くようにしています。`import main` したときは実行されないため、他のファイルから `main.py` をインポートしても誤って実行されません。

---

## 💡 今回のポイントまとめ

### プロジェクト構成のパターン

```python
# scraper.py ─ 取得・解析のみ担当
class JobScraper:
    def fetch(self) -> list[dict]:
        # requests.get → BeautifulSoup → find_all → リスト返却
        pass

    def save_csv(self, jobs: list[dict]) -> None:
        # os.makedirs → csv.DictWriter → writeheader + writerows
        pass

    def save_db(self, jobs: list[dict]) -> tuple[int, int]:
        # sqlite3.connect → CREATE TABLE IF NOT EXISTS → INSERT OR IGNORE
        return (0, 0)

    def run(self) -> None:
        jobs = self.fetch()
        self.save_csv(jobs)
        self.save_db(jobs)

# main.py ─ 呼び出しのみ
if __name__ == "__main__":
    scraper = JobScraper("https://realpython.github.io/fake-jobs/")
    scraper.run()
```

### SQLite 重複チェックのパターン

```python
# テーブル作成時に UNIQUE 制約を付ける
conn.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key1 TEXT NOT NULL,
        key2 TEXT NOT NULL,
        data TEXT,
        UNIQUE(key1, key2)   -- この組み合わせは1件だけ許可
    )
""")

# INSERT OR IGNORE で重複をスキップ
cursor = conn.execute(
    "INSERT OR IGNORE INTO items (key1, key2, data) VALUES (?, ?, ?)",
    ("value1", "value2", "data")
)
is_new = cursor.rowcount > 0  # 挿入されたか確認
```

### loguru の基本パターン（まとめ）

```python
from loguru import logger

logger.add("app.log", level="INFO", rotation="1 MB", retention="7 days", encoding="utf-8")

logger.debug("詳細情報（開発時のみ）")
logger.info("進捗報告")
logger.success("成功")
logger.warning("軽い問題")
logger.error("エラー")
logger.exception("except ブロック内でスタックトレース付きエラー")
```

---

## 🔍 もっと知りたい人向け

| トピック | 検索キーワード |
|---------|---------------|
| 定期実行との組み合わせ | `Python schedule JobScraper` |
| Scrapy（大規模クローリング） | `Python Scrapy チュートリアル 日本語` |
| FastAPI でデータを公開する | `Python FastAPI SQLite API` |
| pandas でデータを分析する | `Python pandas CSV 分析 可視化` |
| Docker でスクレイパーを動かす | `Python scraper Docker 定期実行` |

---

**お疲れ様でした！全24回のカリキュラムを完走しました。ここで学んだスキルを活かして、自分だけのプロジェクトを作ってみましょう。🎉**
