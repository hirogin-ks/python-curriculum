# 第19回：認証とセッション

## 今回のゴール

- HTTP のセッションと Cookie の仕組みがわかる
- `requests.Session` を使ってログイン状態を維持できる
- CSRF トークンを取得してログインフォームを送信できる
- ログイン後のページからデータを取得できる

## 所要時間：90分

---

## 導入：ログインが必要なページをスクレイピングする

これまで学んできたスクレイピングは、誰でも見られる公開ページへのアクセスでした。しかし、実際のWebサービスには「ログインしないと見られないページ」が数多くあります。

例えば、自分のSNSの投稿一覧や、ECサイトの注文履歴、社内システムのデータなどがそれに当たります。

ここで疑問が生まれます。「ブラウザでログインするときは、なぜ次のページに移動してもログイン状態が続くのか？」

HTTPというプロトコルはもともと、各リクエストが独立しており「前のやり取りを覚えない」という設計になっています。これを「ステートレス」と呼びます。

そこで登場するのが **Cookie** と **セッション** という仕組みです。

```text
ブラウザ              Webサーバー
   │                      │
   │── ログインリクエスト ──▶│
   │                      │
   │◀── Cookie を発行 ─────│
   │                      │
   │── 次のページを要求 ───▶│
   │   （Cookie を一緒に送る）
   │                      │
   │◀── ログイン済みとして  │
   │    ページを返す ────────│
```

ログインに成功すると、サーバーはブラウザに「この人は認証済み」という印（セッションCookie）を渡します。以降のリクエストでブラウザが自動的にこのCookieを送ることで、ログイン状態が維持されます。

`requests` ライブラリの `Session` を使えば、この Cookie の管理を自動化できます。

---

## ハンズオン：Session を使ってみよう

まず、`Session` なしと `Session` ありの違いを確認しましょう。

```python
import requests

# Session なし（通常のリクエスト）
r1 = requests.get("https://httpbin.org/cookies/set/mykey/myvalue")
r2 = requests.get("https://httpbin.org/cookies")
print("Session なし:", r2.json())  # cookies が空

# Session あり
session = requests.Session()
session.get("https://httpbin.org/cookies/set/mykey/myvalue")
r3 = session.get("https://httpbin.org/cookies")
print("Session あり:", r3.json())  # cookies が保持されている
```

`Session` を使うと、1回目のリクエストで受け取った Cookie が2回目以降も自動的に送られることが確認できます。

---

## 解説

### Cookie とセッションの仕組み

Cookie とはサーバーがブラウザ（クライアント）に保存させる小さなデータです。次回以降のリクエストで自動的に送られるため、「前回のやり取りの続き」として扱うことができます。

セッションとは、ログインから始まり一連の操作が終わるまでの「まとまり」です。サーバー側でセッションIDを発行し、クライアントはそのIDをCookieで持ち歩くことでログイン状態が維持されます。

### requests.Session の基本

```python
import requests

session = requests.Session()

# 以降のリクエストが同じセッションで管理される
session.get("https://example.com/page1")
session.get("https://example.com/page2")

# セッションを明示的に閉じる（with 構文でも可）
session.close()
```

`with` 構文を使うと、ブロックを抜けた時点でセッションが自動的に閉じられます。

```python
with requests.Session() as session:
    session.get("https://example.com/page1")
    session.get("https://example.com/page2")
# ここで session.close() が自動的に呼ばれる
```

### ログイン処理の基本パターン

多くのWebサービスはフォームログインを採用しています。基本的な流れは次の通りです。

```python
with requests.Session() as session:
    # 1. ログインページを GET してフォームの情報を確認する
    login_page = session.get("https://example.com/login")

    # 2. POST でログイン情報を送信する
    login_data = {
        "username": "your_username",
        "password": "your_password",
    }
    session.post("https://example.com/login", data=login_data)

    # 3. ログイン後のページにアクセスする
    mypage = session.get("https://example.com/mypage")
    print(mypage.text)
```

### CSRF トークンとは

現代のWebサービスの多くは、フォームに **CSRF（Cross-Site Request Forgery）トークン** というランダムな文字列を埋め込んでいます。

これは「このリクエストは本物のフォームから送られた」ことを確認するためのセキュリティ対策です。ログインフォームを POST するときは、このトークンもあわせて送らないとサーバーに弾かれます。

```html
<!-- ログインページのHTMLに埋め込まれている例 -->
<form method="post" action="/login">
  <input type="hidden" name="csrf_token" value="abc123xyz" />
  <input type="text" name="username" />
  <input type="password" name="password" />
</form>
```

BeautifulSoup でこのトークンを取り出します。

```python
from bs4 import BeautifulSoup

login_page = session.get("https://example.com/login")
soup = BeautifulSoup(login_page.text, "html.parser")

# hidden フィールドから csrf_token を取得
csrf_token = soup.find("input", {"name": "csrf_token"})["value"]
```

### quotes.toscrape.com へのログイン

練習用サイト `quotes.toscrape.com` にはログイン機能があります。ログインするとページにユーザー名が表示されるなど、ログインと未ログインで見える内容が変わります。

```
URL: https://quotes.toscrape.com/login
ユーザー名: 任意の文字列（例: testuser）
パスワード: 任意の文字列（例: testpass）
```

このサイトでは CSRF トークンを取得してからログインする必要があります。

```python
import requests
from bs4 import BeautifulSoup

with requests.Session() as session:
    # 1. ログインページを GET して CSRF トークンを取得する
    login_url = "https://quotes.toscrape.com/login"
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.text, "html.parser")
    csrf_token = soup.find("input", {"name": "csrf_token"})["value"]

    # 2. ログイン情報と CSRF トークンを POST する
    login_data = {
        "csrf_token": csrf_token,
        "username": "testuser",
        "password": "testpass",
    }
    session.post(login_url, data=login_data)

    # 3. ログイン後のページを取得する
    top_page = session.get("https://quotes.toscrape.com/")
    soup = BeautifulSoup(top_page.text, "html.parser")

    # ログイン成功の確認（ナビゲーションに "Logout" が表示されるか）
    logout_link = soup.find("a", string="Logout")
    if logout_link:
        print("ログイン成功！")
    else:
        print("ログインに失敗しました")
```

### ログイン成功の確認方法

ログインに成功したかどうかは、以下の方法で確認できます。

#### 方法1：リダイレクト先のURLを確認する

ログイン成功後にホームページにリダイレクトされるサービスが多いです。

```python
response = session.post(login_url, data=login_data)
print(response.url)  # リダイレクト後のURLが表示される
```

#### 方法2：ページ内のテキストを確認する

ログイン後のページにユーザー名や「ログアウト」リンクが表示されるか確認します。

```python
top_page = session.get("https://quotes.toscrape.com/")
if "Logout" in top_page.text:
    print("ログイン成功")
```

#### 方法3：セッション Cookie を確認する

```python
print(session.cookies.get_dict())
# {'session': 'eyJ1c2Vy...'} のようなCookieが表示されればログイン済み
```

### セッションにヘッダーを設定する

`Session` に共通のヘッダーを設定すると、以降のすべてのリクエストに自動的に付与されます。

```python
with requests.Session() as session:
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
    })
    # 以降のリクエスト全てに User-Agent が付く
    session.get("https://example.com/page1")
    session.get("https://example.com/page2")
```

User-Agent はブラウザの種類を示す情報で、設定することでブラウザからのアクセスに見せることができます。

---

## 練習問題

### 問題1：Session の Cookie 管理を確認する

`python/lesson19/01_session_cookie_check.py` に回答を書いてください。

以下のコードを完成させて、`Session` が Cookie を自動管理していることを確認してください。

```python
import requests

session = requests.Session()

# Step 1: Cookie を設定するエンドポイントにアクセス
session.get("https://httpbin.org/cookies/set?name=hello&value=world")

# Step 2: 現在の Cookie を確認するエンドポイントにアクセス
response = session.get("https://httpbin.org/cookies")
print(response.json())
```

期待する出力：

```python
{'cookies': {'name': 'hello', 'value': 'world'}}
```

さらに、`session` を使わず通常の `requests.get` で同じことを試み、Cookie が保持されないことを確認してください。

**考え方:**

```
1. session.get でCookieをセットするURLにアクセスする
2. session.get でCookieを確認するURLにアクセスする
3. session.cookies.get_dict() で保持されているCookieを表示する
4. requests.get（Sessionなし）でも同じことを試みて比較する
```

---

### 問題2：quotes.toscrape.com にログインする

`python/lesson19/02_quotes_login.py` に回答を書いてください。

以下の手順でログイン処理を実装してください。

```
手順:
1. https://quotes.toscrape.com/login を GET して CSRF トークンを取得する
2. CSRF トークン・ユーザー名・パスワードを POST してログインする
3. ログイン成功を確認する（ページに "Logout" が含まれるか）
4. ログイン後のページから名言を3件取得して表示する
```

**考え方:**

```
1. session.get でログインページを取得する
2. BeautifulSoup で input[name="csrf_token"] の value を取り出す
3. session.post にフォームデータを渡す
4. session.get でトップページを取得し .quote > .text を抽出する
```

---

### 問題3：ログイン後に複数ページを取得する

`python/lesson19/03_login_multiple_pages.py` に回答を書いてください。

問題2でログインした状態で、以下を実装してください。

```
- ページ1（/）とページ2（/page/2/）から名言を取得する
- 各ページの名言数を表示する
- 全名言の著者名をまとめてリストで表示する
```

期待する出力例：

```
ページ1: 10件
ページ2: 10件
著者一覧: ['Albert Einstein', 'J.K. Rowling', ...]
```

**考え方:**

```
1. ログイン処理は問題2と同じ
2. ログイン後に複数のURLを session.get で取得する
3. 各ページで著者名を取得してリストに追加していく
```

---

### 問題4：セッションにヘッダーを設定してログインする

`python/lesson19/04_session_headers_delay.py` に回答を書いてください。

問題2のログイン処理に以下を追加してください。

```
追加要件:
- session.headers に User-Agent を設定する
- リクエストのたびに time.sleep(1) で待機する
- ログイン後にセッション Cookie の内容を表示する
```

**考え方:**

```
1. session.headers.update({"User-Agent": "..."}) でヘッダーを設定
2. 各 session.get / session.post の後に time.sleep(1) を追加
3. session.cookies.get_dict() で Cookie を表示
```

---

## 検索キーワード

| 知りたいこと                   | 検索キーワード                            |
| ------------------------------ | ----------------------------------------- |
| Cookie の仕組み                | `HTTP Cookie 仕組み わかりやすく`         |
| CSRF トークンとは              | `CSRF トークン わかりやすく`              |
| requests.Session の使い方      | `Python requests Session 使い方`          |
| フォームのデータを取得する方法 | `BeautifulSoup フォーム input value 取得` |
| ログインの確認方法             | `requests ログイン 確認 Python`           |

---

## 困ったときは

### 「ログインしても次のページでログインが切れる」

`requests.get` を直接使っているかもしれません。ログイン後のすべてのリクエストを `session.get` / `session.post` で行ってください。`session` 変数を通じてアクセスすることで Cookie が維持されます。

### 「POST したら 403 エラーになる」

CSRF トークンが正しく取得・送信できていない可能性があります。ログインページのHTMLを表示して（`print(login_page.text)`）、`<input type="hidden">` の `name` 属性が何になっているか確認してください。サイトによって `csrf_token`・`_token`・`authenticity_token` など名前が異なります。

### 「フォームの name が分からない」

ブラウザの開発者ツール（F12）でログインフォームを右クリック → 「検証」を選ぶと、各フィールドの `name` 属性が確認できます。

### 「ログインできたか確認する方法がわからない」

`print(response.url)` でリダイレクト後のURLを確認するか、`print("Logout" in session.get(...).text)` でログアウトリンクの有無を確認するのが簡単です。

---

## 確認事項

- [ ] Cookie とセッションの仕組みがわかった
- [ ] `requests.Session` を使ってリクエストを送れた
- [ ] `Session` が Cookie を自動管理していることを確認できた
- [ ] CSRF トークンを取得してログインフォームに含められた
- [ ] ログイン後のページからデータを取得できた
- [ ] `session.headers` に共通ヘッダーを設定できた

---

**次回は「統合演習④」です。これまでの知識を組み合わせて、認証・エラー処理・データ保存を含む完全なスクレイピングシステムを構築します。**
