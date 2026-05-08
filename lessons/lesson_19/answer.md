# 第19回：認証とセッション【解答・解説】

この解答は、問題に対する一例です。動作すれば、別の書き方でも正解です。

---

## 📝 問題1の解答：Session の Cookie 管理を確認する

```python
import requests

# Session あり
session = requests.Session()
session.get("https://httpbin.org/cookies/set?name=hello&value=world")
response = session.get("https://httpbin.org/cookies")
print("Session あり:", response.json())
print("保持されている Cookie:", session.cookies.get_dict())

# Session なし（比較用）
requests.get("https://httpbin.org/cookies/set?name=hello&value=world")
response2 = requests.get("https://httpbin.org/cookies")
print("Session なし:", response2.json())
```

実行結果：

```
Session あり: {'cookies': {'name': 'hello', 'value': 'world'}}
保持されている Cookie: {'name': 'hello', 'value': 'world'}
Session なし: {'cookies': {}}
```

### なぜこう書くの？

```python
# requests.Session() はリクエスト間で状態を保持するオブジェクト
# → 1回目のレスポンスで受け取った Cookie を
#   2回目以降のリクエストに自動で付与する

session = requests.Session()

# 1回目: サーバーが Cookie を発行する
session.get("https://httpbin.org/cookies/set?name=hello&value=world")

# 2回目: session が自動的に Cookie を送る
response = session.get("https://httpbin.org/cookies")
# → サーバーが「このCookieを持っているリクエストだ」と認識できる

# Session なしだと1回ごとに独立したリクエストになる
# → Cookie が引き継がれないので空のまま
```

**ポイント: `requests.Session()` を使うと Cookie が自動的に引き継がれる！**

---

## 📝 問題2の解答：quotes.toscrape.com にログインする

```python
import requests
from bs4 import BeautifulSoup

LOGIN_URL = "https://quotes.toscrape.com/login"

with requests.Session() as session:
    # 1. ログインページを GET して CSRF トークンを取得する
    login_page = session.get(LOGIN_URL)
    soup = BeautifulSoup(login_page.text, "html.parser")
    csrf_token = soup.find("input", {"name": "csrf_token"})["value"]
    print(f"CSRF トークン: {csrf_token}")

    # 2. ログイン情報と CSRF トークンを POST する
    login_data = {
        "csrf_token": csrf_token,
        "username": "testuser",
        "password": "testpass",
    }
    session.post(LOGIN_URL, data=login_data)

    # 3. ログイン成功を確認する
    top_page = session.get("https://quotes.toscrape.com/")
    soup = BeautifulSoup(top_page.text, "html.parser")

    if "Logout" in top_page.text:
        print("ログイン成功！")
    else:
        print("ログインに失敗しました")

    # 4. ログイン後のページから名言を3件取得する
    quotes = soup.select(".quote")[:3]
    for quote in quotes:
        text = quote.select_one(".text").get_text()
        author = quote.select_one(".author").get_text()
        print(f"「{text}」 - {author}")
```

実行結果：

```
CSRF トークン: abc123xyz...（毎回変わる）
ログイン成功！
「"The world as we have created it is a process of our thinking..."」 - Albert Einstein
「"It is our choices, Harry, that show what we truly are..."」 - J.K. Rowling
「"There are only two ways to live your life..."」 - Albert Einstein
```

### なぜこう書くの？（ログイン処理の流れ）

```
1. GET /login
   → サーバーが CSRF トークンを HTML に埋め込んで返す
   → soup.find("input", {"name": "csrf_token"})["value"] で取り出す

2. POST /login（csrf_token + username + password を送る）
   → サーバーがCookieを発行してログイン状態にする

3. GET /（session が Cookie を自動送信）
   → サーバーがログイン済みとして応答する
```

```python
# CSRF トークンの取り出し方
# <input type="hidden" name="csrf_token" value="abc123"> を探す
csrf_token = soup.find("input", {"name": "csrf_token"})["value"]
#              ↑ input タグで    ↑ name 属性が csrf_token のもの  ↑ value 属性を取得
```

**ポイント: 必ず GET してからトークンを取り出し、POST に含める！**

---

## 📝 問題3の解答：ログイン後に複数ページを取得する

```python
import requests
from bs4 import BeautifulSoup

LOGIN_URL = "https://quotes.toscrape.com/login"
PAGE_URLS = [
    "https://quotes.toscrape.com/",
    "https://quotes.toscrape.com/page/2/",
]

with requests.Session() as session:
    # ログイン処理
    login_page = session.get(LOGIN_URL)
    soup = BeautifulSoup(login_page.text, "html.parser")
    csrf_token = soup.find("input", {"name": "csrf_token"})["value"]

    session.post(LOGIN_URL, data={
        "csrf_token": csrf_token,
        "username": "testuser",
        "password": "testpass",
    })

    # 複数ページから名言を取得する
    all_authors = []

    for url in PAGE_URLS:
        page = session.get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        quotes = soup.select(".quote")
        # ページ番号を抽出（ルート URL の場合は '1'）
        page_num = url.split('/page/')[-1].rstrip('/') if '/page/' in url else '1'
        print(f"ページ ({page_num}): {len(quotes)}件")

        for quote in quotes:
            author = quote.select_one(".author").get_text()
            all_authors.append(author)

    # 著者名の重複を除いてソート
    unique_authors = sorted(set(all_authors))
    print(f"\n著者一覧: {unique_authors}")
```

実行結果の例：

```
ページ (1): 10件
ページ (2): 10件

著者一覧: ['Albert Einstein', 'Alexandre Dumas fils', 'Allen Saunders', ...]
```

### なぜこう書くの？

```python
# ログイン後のリクエストも同じ session を使うことが重要
# session は Cookie を保持しているので、ページを移動してもログイン状態が続く

for url in PAGE_URLS:
    page = session.get(url)  # session を使ってアクセス
    # → Cookie が自動送信 → ログイン済みとして応答が返る

# set() で重複を除く
# sorted() でアルファベット順に並べる
unique_authors = sorted(set(all_authors))
```

### セッションを使った複数ページ取得のパターン

```
session を作成
    ↓
ログイン処理（1回だけ）
    ↓
session.get でページ1 → データ取得
    ↓
session.get でページ2 → データ取得  ← ログイン状態が維持される
    ↓
...
```

---

## 📝 問題4の解答：セッションにヘッダーを設定してログインする

```python
import time
import requests
from bs4 import BeautifulSoup

LOGIN_URL = "https://quotes.toscrape.com/login"

with requests.Session() as session:
    # User-Agent ヘッダーを設定する
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    })

    # 1. ログインページを GET
    login_page = session.get(LOGIN_URL)
    time.sleep(1)

    soup = BeautifulSoup(login_page.text, "html.parser")
    csrf_token = soup.find("input", {"name": "csrf_token"})["value"]

    # 2. ログイン POST
    session.post(LOGIN_URL, data={
        "csrf_token": csrf_token,
        "username": "testuser",
        "password": "testpass",
    })
    time.sleep(1)

    # 3. ログイン後のページを取得
    top_page = session.get("https://quotes.toscrape.com/")
    time.sleep(1)

    # 4. ログイン成功を確認
    if "Logout" in top_page.text:
        print("ログイン成功！")

    # 5. セッション Cookie を表示
    print("\nセッション Cookie:")
    for name, value in session.cookies.get_dict().items():
        # 長い値は省略して表示
        display_value = value[:30] + "..." if len(value) > 30 else value
        print(f"  {name}: {display_value}")
```

実行結果の例：

```
ログイン成功！

セッション Cookie:
  session: eyJ1c2VybmFtZSI6InRlc3R1c2VyIn0...
```

### なぜこう書くの？

```python
# session.headers.update() で設定したヘッダーは
# 以降の全リクエストに自動付与される
session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

# → session.get() も session.post() も全部このヘッダーで送られる

# session.cookies.get_dict() はセッションが保持しているCookieを辞書で返す
# ログイン後は "session" という名前のCookieが入っているはず
print(session.cookies.get_dict())
```

### User-Agent を設定する理由

```text
User-Agent なし:
  → "python-requests/2.x.x" として送られる
  → 一部のサイトはスクリプトからのアクセスをブロックする

User-Agent あり（ブラウザのもの）:
  → ブラウザからのアクセスと同じように見える
  → ブロックされにくくなる
```

---

## 💡 今回のポイントまとめ

### ログイン処理の基本パターン

```python
with requests.Session() as session:
    # 1. ログインページを GET して CSRF トークンを取得
    login_page = session.get(LOGIN_URL)
    soup = BeautifulSoup(login_page.text, "html.parser")
    csrf_token = soup.find("input", {"name": "csrf_token"})["value"]

    # 2. CSRF トークン + 認証情報を POST
    session.post(LOGIN_URL, data={
        "csrf_token": csrf_token,
        "username": "testuser",
        "password": "password123",
    })

    # 3. ログイン後のページを session.get で取得
    response = session.get("https://example.com/mypage")
```

### Session を使う場面

| 状況                                     | 使うもの             |
| ---------------------------------------- | -------------------- |
| ログイン不要な公開ページ                 | `requests.get()`     |
| ログイン後のページ                       | `requests.Session()` |
| 複数のリクエストで Cookie を引き継ぎたい | `requests.Session()` |

### よく使うメソッド

```python
session = requests.Session()

session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
session.get(url)                                # GET リクエスト
session.post(url, data={"username": "user", "password": "pass"})
session.cookies.get_dict()                      # 保持している Cookie を確認
session.close()                                 # セッションを閉じる（with なら不要）
```

---

## 🔍 もっと知りたい人向け

### 検索キーワード

- `Python requests Session 使い方` - Session のより詳しい使い方
- `Python requests ログイン 自動化` - ログイン処理の実例
- `HTTP Cookie 仕組み` - Cookie の詳しい仕組み
- `CSRF 対策 トークン` - CSRF トークンの仕組み

---

**次回は「JavaScriptレンダリングへの対応」です！**
