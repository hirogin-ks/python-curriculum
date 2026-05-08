# 第20回：総合演習④ - ログイン必須サイトからデータ収集【解答・解説】

この解答は、問題に対する一例です。動作すれば、別の書き方でも正解です。

---

## 📝 問題1の解答：基本的なスクレイパークラスを作る

```python
import requests
from bs4 import BeautifulSoup

class AuthScraper:
    BASE_URL = "https://quotes.toscrape.com"
    LOGIN_URL = f"{BASE_URL}/login"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0"
        })

    def login(self, username, password):
        """ログイン処理。成功なら True、失敗なら False を返す"""
        # CSRF トークンを取得
        login_page = self.session.get(self.LOGIN_URL, timeout=10)
        soup = BeautifulSoup(login_page.text, "html.parser")
        csrf_token = soup.find("input", {"name": "csrf_token"})["value"]

        # ログイン POST
        self.session.post(self.LOGIN_URL, data={
            "csrf_token": csrf_token,
            "username": username,
            "password": password,
        }, timeout=10)

        # ログイン成功を確認
        top_page = self.session.get(self.BASE_URL, timeout=10)
        if "Logout" in top_page.text:
            print("ログイン成功")
            return True
        else:
            print("ログイン失敗")
            return False

    def get_quotes(self):
        """トップページから名言を取得する"""
        html = self.session.get(self.BASE_URL, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        quotes = []
        for q in soup.select(".quote"):
            quotes.append({
                "text": q.select_one(".text").get_text(strip=True),
                "author": q.select_one(".author").get_text(strip=True),
            })
        return quotes


# 使い方
scraper = AuthScraper()
success = scraper.login("testuser", "testpass")
if success:
    quotes = scraper.get_quotes()
    for q in quotes:
        print(f"「{q['text']}」 - {q['author']}")
scraper.session.close()
```

### なぜこう書くの？

```python
class AuthScraper:
    BASE_URL = "https://quotes.toscrape.com"  # クラス変数：インスタンスで共有
    LOGIN_URL = f"{BASE_URL}/login"

    def __init__(self):
        # self.session = ... → インスタンス変数：各インスタンスが持つ状態
        self.session = requests.Session()

    def login(self, username, password):
        # self. でインスタンス変数にアクセスできる
        login_page = self.session.get(self.LOGIN_URL)
        #            ↑ どのメソッドからも同じ session にアクセス可能
```

**ポイント: `self` を通じてインスタンス変数（セッションなど）をメソッド間で共有できる！**

---

## 📝 問題2の解答：with 構文に対応させる

```python
import requests
from bs4 import BeautifulSoup

class AuthScraper:
    BASE_URL = "https://quotes.toscrape.com"
    LOGIN_URL = f"{BASE_URL}/login"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})

    def __enter__(self):
        return self  # with ブロックの変数に self を渡す

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()  # ブロックを抜けると自動で呼ばれる
        print("セッションを閉じました")

    def login(self, username, password):
        login_page = self.session.get(self.LOGIN_URL, timeout=10)
        soup = BeautifulSoup(login_page.text, "html.parser")
        csrf_token = soup.find("input", {"name": "csrf_token"})["value"]
        self.session.post(self.LOGIN_URL, data={
            "csrf_token": csrf_token,
            "username": username,
            "password": password,
        }, timeout=10)
        top_page = self.session.get(self.BASE_URL, timeout=10)
        return "Logout" in top_page.text

    def get_quotes(self):
        html = self.session.get(self.BASE_URL, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        quotes = []
        for q in soup.select(".quote"):
            quotes.append({
                "text": q.select_one(".text").get_text(strip=True),
                "author": q.select_one(".author").get_text(strip=True),
            })
        return quotes


# with 構文で使う
with AuthScraper() as scraper:
    scraper.login("testuser", "testpass")
    quotes = scraper.get_quotes()
    print(f"{len(quotes)}件取得しました")

# with を抜けた後、セッションが閉じられたことが確認できた
print("セッションが正常に閉じられました")
```

実行結果：

```
10件取得しました
セッションを閉じました
セッションが正常に閉じられました
```

### なぜこう書くの？

```python
# __enter__ と __exit__ を定義すると with 構文が使えるようになる

def __enter__(self):
    return self
# with AuthScraper() as scraper: の「scraper」に self が入る
# → scraper.login(...) と呼べる

def __exit__(self, exc_type, exc_val, exc_tb):
    self.session.close()
# with ブロックを抜けると（正常終了でも例外でも）必ず呼ばれる
# → リソースの解放漏れを防げる
```

### with 構文の動き

```
with AuthScraper() as scraper:
    ↑ ここで __enter__ が呼ばれる

    scraper.login(...)
    quotes = scraper.get_quotes()

← ここで __exit__ が呼ばれる（session.close() が実行される）
```

**ポイント: `__enter__` と `__exit__` を実装すると `with` 構文でリソースを安全に管理できる！**

---

## 📝 問題3の解答：複数ページ取得とエラー処理を追加する

```python
import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class AuthScraper:
    BASE_URL = "https://quotes.toscrape.com"
    LOGIN_URL = f"{BASE_URL}/login"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def login(self, username, password):
        login_page = self.session.get(self.LOGIN_URL, timeout=10)
        soup = BeautifulSoup(login_page.text, "html.parser")
        csrf_token = soup.find("input", {"name": "csrf_token"})["value"]
        self.session.post(self.LOGIN_URL, data={
            "csrf_token": csrf_token,
            "username": username,
            "password": password,
        }, timeout=10)
        top_page = self.session.get(self.BASE_URL, timeout=10)
        return "Logout" in top_page.text

    def _parse_quotes(self, html):
        """名言データをパースして辞書のリストを返す"""
        soup = BeautifulSoup(html, "html.parser")
        quotes = []
        for q in soup.select(".quote"):
            quotes.append({
                "text": q.select_one(".text").get_text(strip=True),
                "author": q.select_one(".author").get_text(strip=True),
                "tags": [t.get_text() for t in q.select(".tag")],
            })
        return quotes

    def get_all_quotes(self, max_pages=3):
        """複数ページから名言を取得して DataFrame で返す"""
        all_quotes = []
        success_pages = 0

        for page in range(1, max_pages + 1):
            url = f"{self.BASE_URL}/page/{page}/"
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                quotes = self._parse_quotes(response.text)
                all_quotes.extend(quotes)
                success_pages += 1
                logging.info(f"ページ {page}: {len(quotes)}件取得")
            except Exception as e:
                logging.error(f"ページ {page} の取得に失敗: {e}")
                # エラーでもスキップして次へ進む

        logging.info(f"合計 {success_pages}ページ / {len(all_quotes)}件取得しました")
        return pd.DataFrame(all_quotes)


# 使い方
with AuthScraper() as scraper:
    scraper.login("testuser", "testpass")
    df = scraper.get_all_quotes(max_pages=3)
    print(df[["text", "author"]].head())
```

実行結果の例：

```
2025-01-01 12:00:01 [INFO] ページ 1: 10件取得
2025-01-01 12:00:02 [INFO] ページ 2: 10件取得
2025-01-01 12:00:03 [INFO] ページ 3: 10件取得
2025-01-01 12:00:03 [INFO] 合計 3ページ / 30件取得しました
                                                text            author
0  "The world as we have created it is a process...  Albert Einstein
1  "It is our choices, Harry, that show what we ...     J.K. Rowling
...
```

### なぜこう書くの？

```python
# ページ取得を try/except で囲む
# → エラーが起きても continue して次のページへ進む
for page in range(1, max_pages + 1):
    try:
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        quotes = self._parse_quotes(response.text)
        all_quotes.extend(quotes)
    except Exception as e:
        logging.error(f"ページ {page} の取得に失敗: {e}")
        # ここで continue は不要（ループが次に進む）

# pd.DataFrame(リスト) で辞書のリストを表形式に変換
df = pd.DataFrame(all_quotes)
# → text, author, tags 列が作られる
```

**ポイント: エラーをスキップして最後まで完走させることが大規模スクレイピングの基本！**

---

## 📝 問題4の解答：並列処理でページ取得を高速化する

```python
import time
import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class AuthScraper:
    BASE_URL = "https://quotes.toscrape.com"
    LOGIN_URL = f"{BASE_URL}/login"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def login(self, username, password):
        login_page = self.session.get(self.LOGIN_URL, timeout=10)
        soup = BeautifulSoup(login_page.text, "html.parser")
        csrf_token = soup.find("input", {"name": "csrf_token"})["value"]
        self.session.post(self.LOGIN_URL, data={
            "csrf_token": csrf_token,
            "username": username,
            "password": password,
        }, timeout=10)
        top_page = self.session.get(self.BASE_URL, timeout=10)
        return "Logout" in top_page.text

    def _parse_quotes(self, html):
        soup = BeautifulSoup(html, "html.parser")
        quotes = []
        for q in soup.select(".quote"):
            quotes.append({
                "text": q.select_one(".text").get_text(strip=True),
                "author": q.select_one(".author").get_text(strip=True),
                "tags": [t.get_text() for t in q.select(".tag")],
            })
        return quotes

    def _fetch_and_parse(self, args):
        """1ページ分の取得とパースをまとめたメソッド
        
        複数スレッドから安全にアクセスするため、
        Session を共有せず Cookie を明示的に渡す
        """
        url, cookies = args
        try:
            # ThreadPoolExecutor で実行するため、新しい Session を作成
            session = requests.Session()
            session.headers.update({"User-Agent": "Mozilla/5.0"})
            response = session.get(url, cookies=cookies, timeout=10)
            response.raise_for_status()
            quotes = self._parse_quotes(response.text)
            logging.info(f"{url.split('/')[-2]}: {len(quotes)}件取得")
            session.close()
            return quotes
        except Exception as e:
            logging.error(f"取得失敗: {url} → {e}")
            return []  # 失敗したら空リストを返す

    def get_all_quotes_parallel(self, max_pages=5, max_workers=3):
        """並列処理でページを取得する"""
        # ログイン後の Cookie を取得
        cookies = self.session.cookies.copy()
        
        # URL と Cookie のペアを作成
        urls = [f"{self.BASE_URL}/page/{i}/" for i in range(1, max_pages + 1)]
        args_list = [(url, cookies) for url in urls]

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            pages_results = list(executor.map(self._fetch_and_parse, args_list))

        # 各ページの結果（リストのリスト）をフラットにまとめる
        all_quotes = [q for page in pages_results for q in page]
        logging.info(f"合計 {len(all_quotes)}件取得しました")
        return pd.DataFrame(all_quotes)

    def get_all_quotes_serial(self, max_pages=5):
        """直列処理でページを取得する（比較用）"""
        all_quotes = []
        for page in range(1, max_pages + 1):
            url = f"{self.BASE_URL}/page/{page}/"
            quotes = self._fetch_and_parse((url, self.session.cookies.copy()))
            all_quotes.extend(quotes)
        return pd.DataFrame(all_quotes)


# 実行時間の比較
with AuthScraper() as scraper:
    scraper.login("testuser", "testpass")

    # 直列
    start = time.time()
    df_serial = scraper.get_all_quotes_serial(max_pages=5)
    serial_time = time.time() - start
    print(f"直列: {serial_time:.1f}秒")

    # 並列
    start = time.time()
    df_parallel = scraper.get_all_quotes_parallel(max_pages=5, max_workers=3)
    parallel_time = time.time() - start
    print(f"並列: {parallel_time:.1f}秒")

    print(f"\n取得件数: {len(df_parallel)}件")
```

実行結果の例：

```
直列: 6.4秒
並列: 2.3秒

取得件数: 50件
```

### なぜこう書くの？

```python
# _fetch_and_parse はURL1つ分の処理をまとめたメソッド
# → executor.map に渡すと並列実行される
def _fetch_and_parse(self, url):
    try:
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        quotes = []
        for q in soup.select(".quote"):
            quotes.append({
                "text": q.select_one(".text").get_text(strip=True),
                "author": q.select_one(".author").get_text(strip=True),
            })
        return quotes  # 成功したら名言リスト
    except Exception:
        return []       # 失敗したら空リスト

# executor.map(self._fetch_and_parse, urls) が
# → [ページ1の結果, ページ2の結果, ...] を返す
pages_results = list(executor.map(self._fetch_and_parse, urls))

# リストのリストをフラットにする内包表記
all_quotes = [q for page in pages_results for q in page]
# pages_results = [[q1, q2], [q3, q4], []]
# → all_quotes = [q1, q2, q3, q4]
```

### 内包表記の展開

```python
# [q for page in pages_results for q in page] は以下と同じ意味
all_quotes = []
for page in pages_results:
    for q in page:
        all_quotes.append(q)
```

---

## 💡 今回のポイントまとめ

### スクレイパークラスの基本構成

```python
class AuthScraper:
    BASE_URL = "https://quotes.toscrape.com"  # クラス変数（共通の設定）

    def __init__(self):
        self.session = requests.Session()  # インスタンス変数（状態）

    def __enter__(self):
        return self  # with 構文のサポート

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()  # リソースの解放

    def login(self, username, password):
        # ログインページから CSRF トークンを取得、ログインリクエストを送信
        login_page = self.session.get(f"{self.BASE_URL}/login")
        csrf_token = BeautifulSoup(login_page.text, "html.parser").find("input", {"name": "csrf_token"})["value"]
        self.session.post(f"{self.BASE_URL}/login", data={"csrf_token": csrf_token, "username": username, "password": password})

    def _fetch_page(self, url):
        # 内部処理（アンダースコアで示す）
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def get_data(self):
        # 外部向けの処理。トップページから名言を取得して返す
        soup = self._fetch_page(self.BASE_URL)
        return [{"text": q.select_one(".text").get_text(strip=True)} for q in soup.select(".quote")]
```

### 知識の組み合わせまとめ

| 回     | 技術                 | 今回の使い所                                |
| ------ | -------------------- | ------------------------------------------- |
| 第17回 | エラー処理・リトライ | `_fetch_and_parse` の try/except            |
| 第18回 | 並列処理             | `ThreadPoolExecutor` で複数ページを同時取得 |
| 第19回 | 認証・セッション     | `requests.Session` でログイン状態を維持     |
| 今回   | クラス設計           | 上記すべてをひとつのクラスにまとめる        |

### クラス変数とインスタンス変数の違い

```python
class AuthScraper:
    BASE_URL = "https://quotes.toscrape.com"  # クラス変数: 全インスタンスで共有

    def __init__(self):
        self.session = requests.Session()  # インスタンス変数: インスタンスごとに独立
```

---

## 🔍 もっと知りたい人向け

### 検索キーワード

- `Python クラス継承` - 共通処理を親クラスにまとめる方法
- `Python dataclass` - データ保持に特化したクラスの書き方
- `Python ABC 抽象クラス` - インターフェースを定義する方法
- `Python contextmanager` - `with` 構文をより簡単に実装する方法

---

**次回は「データの保存と整形」です！**
