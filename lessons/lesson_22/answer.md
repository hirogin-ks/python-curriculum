# 第22回：アンチスクレイピング対策【解答・解説】

この解答は、問題に対する一例です。動作すれば、別の書き方でも正解です。

---

## 📝 問題1の解答：ヘッダーなしとありを比較する

```python
import requests

url = "https://httpbin.org/headers"

# ① ヘッダーなし
response_plain = requests.get(url)
print("ヘッダーなし User-Agent:")
print(response_plain.json()["headers"].get("User-Agent"))

# ② ヘッダーあり
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
response_with_headers = requests.get(url, headers=headers)
print("ヘッダーあり User-Agent:")
print(response_with_headers.json()["headers"].get("User-Agent"))

# 全ヘッダーを確認する
print("\n送信された全ヘッダー:")
for key, value in response_with_headers.json()["headers"].items():
    print(f"  {key}: {value}")
```

実行結果：

```
ヘッダーなし User-Agent:
python-requests/2.31.0

ヘッダーあり User-Agent:
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...

送信された全ヘッダー:
  Accept: text/html,application/xhtml+xml,...
  Accept-Language: ja,en-US;q=0.9,en;q=0.8
  Host: httpbin.org
  User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...
```

### なぜこう書くの？

```python
# headers 辞書を requests.get に渡すだけで自由にヘッダーを設定できる
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
requests.get(url, headers=headers)

# httpbin.org/headers は受け取ったヘッダーをそのまま JSON で返してくれる
# → 自分のリクエストがどう見えているかを確認するのに便利
response.json()["headers"]["User-Agent"]
```

**ポイント: `python-requests/x.x.x` → ブラウザの User-Agent に変えるだけで通過できるサイトが多い！**

---

## 📝 問題2の解答：ランダム待機付きのスクレイパーを作る

```python
import time
import random
import requests

USER_AGENTS = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.1 Safari/605.1.15"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
]

urls = [
    "https://httpbin.org/get",
    "https://httpbin.org/user-agent",
    "https://httpbin.org/headers",
    "https://httpbin.org/get",
    "https://httpbin.org/user-agent",
]

with requests.Session() as session:
    for i, url in enumerate(urls, start=1):
        # リクエストのたびに User-Agent をランダムに更新する
        session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "ja,en-US;q=0.9",
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        })

        wait = random.uniform(1.0, 3.0)
        time.sleep(wait)

        response = session.get(url, timeout=10)
        print(f"[{i}/{len(urls)}] {url} → {response.status_code} (待機: {wait:.1f}秒)")
```

実行結果の例：

```
[1/5] https://httpbin.org/get → 200 (待機: 2.1秒)
[2/5] https://httpbin.org/user-agent → 200 (待機: 1.4秒)
[3/5] https://httpbin.org/headers → 200 (待機: 2.8秒)
[4/5] https://httpbin.org/get → 200 (待機: 1.1秒)
[5/5] https://httpbin.org/user-agent → 200 (待機: 2.5秒)
```

### なぜこう書くの？

```python
# session.headers.update() はリクエストのたびに呼べる
# → 毎回異なる User-Agent を使えるので、同じ UA の連続を避けられる
session.headers.update({"User-Agent": random.choice(USER_AGENTS)})

# random.uniform(1.0, 3.0) は 1.0〜3.0 の小数をランダムに返す
# → 毎回同じ間隔でなく、人間っぽいランダムな間隔になる
wait = random.uniform(1.0, 3.0)
time.sleep(wait)

# enumerate(urls, start=1) でインデックスを 1 始まりにする
for i, url in enumerate(urls, start=1):
    print(f"[{i}/{len(urls)}]")
```

**ポイント: 待機時間を毎回ランダムにすることで、一定間隔のボットより自然なアクセスに見える！**

---

## 📝 問題3の解答：robots.txt チェック付きのスクレイパーを作る

```python
import requests
from urllib.robotparser import RobotFileParser

BASE_URL = "https://quotes.toscrape.com"
CRAWLER_NAME = "MyCrawler"

# robots.txt を読み込む
rp = RobotFileParser()
rp.set_url(f"{BASE_URL}/robots.txt")
rp.read()

paths = [
    "/login",
    "/page/1/",
    "/admin/",
    "/",
    "/tag/love/",
]

with requests.Session() as session:
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    })

    for path in paths:
        url = BASE_URL + path
        if rp.can_fetch(CRAWLER_NAME, url):
            response = session.get(url, timeout=10)
            print(f"{path} → アクセス許可 (ステータス: {response.status_code})")
        else:
            print(f"{path} → アクセス禁止（スキップ）")
```

実行結果の例：

```
/login → アクセス許可 (ステータス: 200)
/page/1/ → アクセス許可 (ステータス: 200)
/admin/ → アクセス禁止（スキップ）
/ → アクセス許可 (ステータス: 200)
/tag/love/ → アクセス許可 (ステータス: 200)
```

### なぜこう書くの？

```python
from urllib.robotparser import RobotFileParser

rp = RobotFileParser()
rp.set_url("https://example.com/robots.txt")  # robots.txt の URL を設定
rp.read()                                      # 取得して解析する

# can_fetch(クローラー名, アクセスしたいURL) で True/False が返る
# クローラー名に "*" を使うと全 User-agent ルールで確認できる
rp.can_fetch("MyCrawler", "https://example.com/admin/")  # False なら禁止
```

**ポイント: `urllib.robotparser` は標準ライブラリなのでインストール不要！**

---

## 📝 問題4の解答：礼儀正しいスクレイパークラスを作る

```python
import time
import random
import logging
import requests
from urllib.robotparser import RobotFileParser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

USER_AGENTS = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.1 Safari/605.1.15"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
]

class PoliteScraper:
    CRAWLER_NAME = "PoliteScraper"

    def __init__(self):
        self.session = requests.Session()
        self.rp = RobotFileParser()
        self._crawl_delay = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def setup_robots(self, base_url):
        """robots.txt を読み込んで Crawl-delay を取得する"""
        robots_url = base_url.rstrip("/") + "/robots.txt"
        self.rp.set_url(robots_url)
        self.rp.read()
        self._crawl_delay = self.rp.crawl_delay(self.CRAWLER_NAME)
        if self._crawl_delay is not None:
            logging.info(f"Crawl-delay: {self._crawl_delay}秒")
        else:
            logging.info("Crawl-delay の指定なし。1〜3秒の待機を使用します")

    def _wait(self):
        """Crawl-delay または ランダム待機を行う"""
        if self._crawl_delay is not None:
            wait = self._crawl_delay
        else:
            wait = random.uniform(1.0, 3.0)
        time.sleep(wait)

    def _update_headers(self):
        """リクエストで使用する User-Agent を更新して返す"""
        user_agent = random.choice(USER_AGENTS)
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept-Language": "ja,en-US;q=0.9",
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        })
        return user_agent

    def fetch(self, url):
        """robots.txt チェック → 待機 → リクエスト"""
        self._wait()
        user_agent = self._update_headers()
        
        # robots.txt チェック（実際に送信する User-Agent で判定）
        if not self.rp.can_fetch(user_agent, url):
            logging.warning(f"robots.txt により禁止: {url}")
            return None

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            logging.info(f"成功 {response.status_code}: {url}")
            return response
        except requests.exceptions.RequestException as e:
            logging.error(f"エラー: {url} → {e}")
            return None

    def run(self, urls):
        """URLリストを処理して成功・スキップ件数を返す"""
        success, skipped = 0, 0
        for url in urls:
            result = self.fetch(url)
            if result is not None:
                success += 1
            else:
                skipped += 1
        logging.info(f"完了 → 成功: {success}件 / スキップ: {skipped}件")
        return success, skipped


# 使い方
urls = [
    "https://quotes.toscrape.com/",
    "https://quotes.toscrape.com/page/2/",
    "https://quotes.toscrape.com/admin/",   # 禁止されている場合はスキップ
    "https://quotes.toscrape.com/tag/love/",
]

with PoliteScraper() as scraper:
    scraper.setup_robots("https://quotes.toscrape.com")
    scraper.run(urls)
```

実行結果の例：

```
2025-01-01 12:00:00 [INFO] Crawl-delay の指定なし。1〜3秒の待機を使用します
2025-01-01 12:00:02 [INFO] 成功 200: https://quotes.toscrape.com/
2025-01-01 12:00:04 [INFO] 成功 200: https://quotes.toscrape.com/page/2/
2025-01-01 12:00:04 [WARNING] robots.txt により禁止: https://quotes.toscrape.com/admin/
2025-01-01 12:00:07 [INFO] 成功 200: https://quotes.toscrape.com/tag/love/
2025-01-01 12:00:07 [INFO] 完了 → 成功: 3件 / スキップ: 1件
```

### なぜこう書くの？

```python
# Crawl-delay の取得
# rp.crawl_delay(クローラー名) で robots.txt に指定された値を取得
# → None の場合は指定なしなのでデフォルト値を使う
self._crawl_delay = self.rp.crawl_delay(self.CRAWLER_NAME)

def _wait(self):
    if self._crawl_delay:
        wait = self._crawl_delay     # robots.txt の指示に従う
    else:
        wait = random.uniform(1.0, 3.0)  # なければランダム
    time.sleep(wait)

# fetch の中で3ステップを順番に実行する
# 1. robots.txt で可否確認（禁止なら None を返して終了）
# 2. 礼儀正しく待機
# 3. ヘッダーを更新してリクエスト
```

---

## 💡 今回のポイントまとめ

### 礼儀正しいスクレイピングのチェックリスト

```
□ robots.txt を確認した
□ 利用規約を確認した
□ User-Agent をブラウザのものに設定した
□ リクエストの間に待機時間を入れた
□ 収集したデータを適切な目的にのみ使用する
```

### ヘッダー設定の基本

```python
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "ja,en-US;q=0.9",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
})
```

### robots.txt チェックの基本

```python
from urllib.robotparser import RobotFileParser

rp = RobotFileParser()
rp.set_url("https://example.com/robots.txt")
rp.read()

if rp.can_fetch("*", url):
    # アクセスしてよい
else:
    # スキップする
```

### 待機時間のパターン

```python
import time, random

# 一定時間待つ
time.sleep(2)

# ランダムに待つ（推奨）
time.sleep(random.uniform(1.0, 3.0))

# robots.txt の Crawl-delay に従う
delay = rp.crawl_delay("*")
time.sleep(delay if delay else random.uniform(1.0, 3.0))
```

---

## 🔍 もっと知りたい人向け

### 検索キーワード

- `Python fake-useragent ライブラリ` - User-Agent を自動で収集・ランダム使用するライブラリ
- `Python Playwright` - Selenium より新しいブラウザ自動化ライブラリ
- `Python requests-cache` - レスポンスをキャッシュして同じURLへの再リクエストを減らす
- `スクレイピング 法律 日本` - 不正競争防止法・著作権法との関係

---

**次回は「総合演習⑤」です！**
