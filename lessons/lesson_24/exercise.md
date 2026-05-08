# 第24回：卒業制作 - 求人情報収集システム

## 今回のゴール

- これまで学んだ全スキルを1つのプロジェクトに統合できる
- 実用的なスクレイピングシステムを設計・実装できる
- 複数ファイルに処理を分けてコードを整理できる
- CSV・SQLite にデータを保存できる
- ログ出力とエラーハンドリングを組み込める

## 所要時間：120分

---

## 導入：卒業制作へようこそ

就職活動中にエクセルで求人情報を手動でコピーしている人を想像してください。毎日サイトを開いて、会社名・職種・勤務地を1件ずつコピーしていくと、100件で数時間かかります。

スクレイピングを使えば、このような作業を数秒で自動化できます。

今回作るシステムはこの図のような構成です：

```text
[求人サイト] → scraper.py（取得・HTML解析）
                     ↓
              main.py（全体制御・ログ）
                     ↓
         ┌───────────┴──────────┐
     jobs.csv               jobs.db
   （いつでも開ける）    （重複なし・検索可能）
```

これまでのレッスンで学んだすべての技術を使います。

| 使用する技術 | 対応レッスン |
|-------------|------------|
| requests / BeautifulSoup | 第1〜5回 |
| CSV / JSON 保存 | 第8〜9回 |
| SQLite 保存 | 第10〜11回 |
| クラス設計 | 第20回 |
| エラーハンドリング・リトライ | 第17回 |
| ログ出力 | 第23回 |
| 定期実行 | 第21回 |
| アンチスクレイピング対策 | 第22回 |

---

## ハンズオン：対象サイトを確認しよう

今回のターゲットは `https://realpython.github.io/fake-jobs/` です。ブラウザで開いて「検証」で HTML 構造を確認してください。

求人カードは以下の構造になっています。

```html
<div class="card">
  <div class="card-content">
    <div class="media">
      <div class="media-content">
        <p class="title is-5">Senior Python Developer</p>
        <p class="subtitle is-6 company">Payne, Roberts and Davis</p>
      </div>
    </div>
    <div class="content">
      <p class="location">
        <svg ...></svg>
        Stewartbury, AA
      </p>
      <p class="is-small has-text-grey">
        <time datetime="2021-04-08">2021-04-08</time>
      </p>
    </div>
  </div>
</div>
```

まずカード1件だけを取り出して確認します。

```python
import requests
from bs4 import BeautifulSoup

url = "https://realpython.github.io/fake-jobs/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# カードを1件だけ取り出す
card = soup.find("div", class_="card")
print(card.find("p", class_="title").text.strip())
print(card.find("p", class_="subtitle").text.strip())
print(card.find("p", class_="location").get_text(strip=True))
```

期待する出力：

```
Senior Python Developer
Payne, Roberts and Davis
Stewartbury, AA
```

---

## 解説

### プロジェクト構成

大きなプロジェクトでは処理をファイルに分けて管理します。役割の分離が重要です。

```text
lesson_24/
├── main.py         # エントリーポイント。全体の流れを制御する
├── scraper.py      # 取得・HTML解析処理。ネットワークに関わる処理を集める
├── database.py     # DB保存処理。データの永続化に関わる処理を集める
└── output/
    ├── jobs.csv    # CSV出力ファイル
    ├── jobs.db     # SQLite データベース
    └── scraper.log # ログファイル
```

**なぜファイルを分けるのか？**

- `scraper.py` だけをテストできる
- DB を変えても `main.py` を修正しなくてよい
- チームで作業を分担できる

### BeautifulSoup での複数要素取得

```python
# 全カードを取得する（find_all はリストを返す）
cards = soup.find_all("div", class_="card")

jobs = []
for card in cards:
    title = card.find("p", class_="title").text.strip()
    company = card.find("p", class_="subtitle").text.strip()
    # location には SVG アイコンが含まれるので get_text() で取り出す
    location = card.find("p", class_="location").get_text(strip=True)
    date = card.find("time")["datetime"]  # 属性値は ["属性名"] で取得

    jobs.append({
        "title": title,
        "company": company,
        "location": location,
        "date": date,
    })
```

### CSV への保存

```python
import csv
import os

def save_to_csv(jobs: list[dict], filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)  # フォルダがなければ作る

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "company", "location", "date"])
        writer.writeheader()
        writer.writerows(jobs)
```

### SQLite への保存と重複チェック

```python
import sqlite3

def init_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            date TEXT,
            UNIQUE(title, company)  -- タイトルと会社の組み合わせで重複を禁止する
        )
    """)
    conn.commit()
    return conn

def insert_job(conn: sqlite3.Connection, job: dict) -> bool:
    """INSERT OR IGNORE で重複があればスキップし、挿入されたか bool で返す"""
    cursor = conn.execute(
        "INSERT OR IGNORE INTO jobs (title, company, location, date) VALUES (?, ?, ?, ?)",
        (job["title"], job["company"], job["location"], job["date"]),
    )
    conn.commit()
    return cursor.rowcount > 0  # 挿入されたら True、スキップなら False
```

---

## 練習問題

### 問題1：全求人データを取得して表示する

`https://realpython.github.io/fake-jobs/` から全求人を取得し、以下の形式で表示してください。

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
```

何件取得できたかも最後に表示してください。

**考え方:**

```
1. requests.get でページを取得する
2. soup.find_all("div", class_="card") で全カードを取得する
3. for ループで各カードから title, company, location, date を取り出す
4. enumerate でインデックスを付けて表示する
```

---

### 問題2：取得した求人データを CSV に保存する

問題1で取得したデータを `output/jobs.csv` に保存してください。

- ヘッダー行に `title, company, location, date` を付ける
- 保存後に「XX件を output/jobs.csv に保存しました」と表示する
- `output/` フォルダがなければ自動で作成する

**考え方:**

```
1. os.makedirs("output", exist_ok=True) でフォルダを作る
2. csv.DictWriter で辞書のリストをCSVに書き出す
3. fieldnames にヘッダーのリストを渡す
4. writeheader() を忘れずに呼ぶ
```

---

### 問題3：エラーハンドリングと loguru ログを追加する

問題2のコードに以下を追加してください。

```
追加する処理:
- loguru でコンソールとファイル（output/scraper.log）にログを出力する
- 取得開始・完了・保存完了をログに記録する
- requests の例外を try/except でキャッチしてログに記録する
- ステータスコードが 200 以外のときはログにエラーを出力して処理を中断する
```

期待するログ出力：

```
2025-01-01 12:00:00 | INFO | スクレイピング開始: https://realpython.github.io/fake-jobs/
2025-01-01 12:00:01 | SUCCESS | 100件 取得完了
2025-01-01 12:00:01 | SUCCESS | output/jobs.csv に保存完了
```

**考え方:**

```
1. logger.add("output/scraper.log", ...) でファイル出力を追加する
2. requests.get を try/except で囲む
3. response.raise_for_status() で HTTP エラーを検知する
4. 成功なら logger.success、エラーなら logger.error を使う
```

---

### 問題4：全機能を統合した JobScraper クラスを作る

以下の設計で `scraper.py` と `main.py` を実装してください。

#### scraper.py

```python
class JobScraper:
    def __init__(self, url: str, output_dir: str = "output"):
        # URL、出力先ディレクトリ、CSV/DBのパスを設定する

    def fetch(self) -> list[dict]:
        # ページを取得して求人リストを返す

    def save_csv(self, jobs: list[dict]) -> None:
        # jobs.csv に保存する

    def save_db(self, jobs: list[dict]) -> tuple[int, int]:
        # jobs.db に保存し、(新規件数, スキップ件数) を返す

    def run(self) -> None:
        # fetch → save_csv → save_db の順に実行する
```

#### main.py

```python
from scraper import JobScraper

if __name__ == "__main__":
    scraper = JobScraper("https://realpython.github.io/fake-jobs/")
    scraper.run()
```

実行結果の例：

```
2025-01-01 12:00:00 | INFO | スクレイピング開始
2025-01-01 12:00:01 | SUCCESS | 100件 取得完了
2025-01-01 12:00:01 | SUCCESS | output/jobs.csv に保存完了
2025-01-01 12:00:01 | SUCCESS | DB: 新規 100件 / スキップ 0件
```

2回目の実行では重複がスキップされることを確認してください。

```
2025-01-01 12:01:00 | INFO | スクレイピング開始
2025-01-01 12:01:01 | SUCCESS | 100件 取得完了
2025-01-01 12:01:01 | SUCCESS | output/jobs.csv に保存完了
2025-01-01 12:01:01 | INFO | DB: 新規 0件 / スキップ 100件
```

**考え方:**

```
1. __init__ で self.url, self.output_dir, csv_path, db_path を設定する
2. fetch は requests.get → BeautifulSoup → find_all → リスト返却
3. save_db は os.makedirs → sqlite3.connect → CREATE TABLE IF NOT EXISTS
4. INSERT OR IGNORE で重複をスキップ → rowcount で新規/スキップを数える
5. run は fetch → save_csv → save_db を順に呼ぶ
```

---

## 検索キーワード

| 知りたいこと | 検索キーワード |
|-------------|---------------|
| 複数要素の取得 | `BeautifulSoup find_all 使い方` |
| CSV 辞書書き込み | `Python csv DictWriter 使い方` |
| SQLite UNIQUE 制約 | `SQLite UNIQUE INSERT OR IGNORE` |
| フォルダを自動作成 | `Python os.makedirs exist_ok` |
| タグの属性値取得 | `BeautifulSoup 属性 取得` |

---

## 困ったときは

### 「取得件数が少ない / 多い」

`find_all("div", class_="card")` ではなく `soup.find_all("div", class_="card-content")` など別の要素を取得してしまっている可能性があります。ブラウザの検証ツールで正しいセレクターを確認してください。

### 「location に余分な文字が入る」

SVG アイコンのテキストが混入しています。`get_text(strip=True)` を使うか、`p.find("svg").decompose()` で SVG を除去してから `.text.strip()` を使ってください。

### 「CSV を開くと文字化けする」

Windows の Excel ではエンコードの問題があります。`encoding="utf-8-sig"` を指定するか、Excel の「データ」→「テキストファイル」から取り込んでみてください。

### 「SQLite のデータを確認したい」

VS Code の `SQLite Viewer` 拡張機能か、ターミナルで `python -c "import sqlite3; [print(r) for r in sqlite3.connect('output/jobs.db').execute('SELECT * FROM jobs LIMIT 5')]"` で確認できます。

---

## 確認事項

- [ ] 全求人（100件）を取得できた
- [ ] `output/jobs.csv` にデータが保存された
- [ ] `output/scraper.log` にログが出力された
- [ ] 2回実行したときに DB の重複がスキップされた
- [ ] クラスに処理をまとめて `main.py` から1行で実行できた

---

## おめでとうございます！🎉

このコースで身につけたスキル：

| スキル | 内容 |
|-------|------|
| Python 基礎 | 変数・ループ・関数・クラス |
| HTTP 通信 | requests、ステータスコード、セッション |
| HTML 解析 | BeautifulSoup、CSS セレクター |
| データ保存 | CSV・JSON・SQLite |
| エラー処理 | try/except・tenacity によるリトライ |
| 並列処理 | ThreadPoolExecutor |
| 認証 | Cookie・セッション・CSRF トークン |
| 自動化 | schedule による定期実行 |
| マナー | robots.txt 遵守・適切な待機 |
| 品質管理 | loguru・pytest |

**次のステップ：**

1. **自分のプロジェクトを作る** — 欲しいデータを集めるシステムを設計してみましょう
2. **Scrapy を学ぶ** — 大規模クローリング向けのフレームワーク（`Python Scrapy チュートリアル`）
3. **API 開発** — 集めたデータを FastAPI で公開する（`Python FastAPI 入門`）
4. **データ分析** — pandas・matplotlib でデータを可視化する（`Python pandas データ分析`）
