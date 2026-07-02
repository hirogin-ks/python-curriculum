# 第5回：HTTP通信の基礎

## 今回のゴール

- Webページを取得できる（requests）
- GETとPOSTの違いがわかる
- ヘッダーやパラメータを設定できる

---

## 5.1 導入：プログラムがWebサイトにアクセスする仕組み

普段、ブラウザでWebサイトを見るとき、裏側では「HTTP通信」という仕組みでサーバーとやり取りをしています。スクレイピングでは、ブラウザの代わりにPythonのプログラムがこのHTTP通信を行います。

この回では、Pythonからwebサイトにアクセスしてデータを取得する方法を学びます。

---

## 5.2 ハンズオン：Webページを取得してみよう

以下のコードをファイルに保存して実行してください。

```python
import requests

response = requests.get("https://httpbin.org/get")

print("ステータスコード:", response.status_code)
print("レスポンス本文:")
print(response.text)
```

実行すると、ステータスコード（200なら成功）と、サーバーからの応答が表示されます。

### ハンズオンが動かないとき

| 起こりうる現象         | 原因                               | 解決策（アドバイス）                                                |
| ---------------------- | ---------------------------------- | ------------------------------------------------------------------- |
| `ConnectionError`      | ネットワークが接続を拒否           | 大学のWi-Fiではなく、スマホのテザリングで試してみる                 |
| `SSLError`             | 安全な接続の確認に失敗             | `requests.get(url, verify=False)` を試す（※学習用の一時的な回避策） |
| 実行がずっと終わらない | 通信がどこかで詰まっている         | `requests.get(url, timeout=5)` のようにタイムアウトを設定する       |
| `ImportError`          | requestsがインストールされていない | 仮想環境（venv）を作り、`pip install requests` を再実行する         |

---

## 解説

### HTTP通信とは

HTTPとは「HyperText Transfer Protocol（ハイパーテキスト転送プロトコル）」の略で、ブラウザとWebサーバーがデータをやり取りするための約束事（プロトコル）です。URLの冒頭が `http://` なら HTTP、`https://` なら HTTPS（HTTPをTLSで保護したもの）を使って通信しています。

以下がブラウザとWebサイトの信号のやり取りの様子で、これがHTTP/HTTPSの基本的なやり取りです。

```
プログラム                Webサーバー
    │                         │
    │── リクエスト ─────────▶│  「このページください」
    │                         │
    │◀── レスポンス ────────│  「はい、どうぞ」
    │    （HTML等）           │
```

### requestsの基本

以下のコードを見て、各行が何をしているか説明してみましょう（答えは解答編に書いてあります）。わからない単語や書き方があったら、まず自分で調べてみましょう。

```python
import requests

response = requests.get("https://example.com")

print(response.status_code)
print(response.text)
```

### ステータスコード

覚えておくべきコードは以下の3種類です。
| コード | 意味 | 対処 |
|--------|------|------|
| 200 | 成功 | そのまま処理を続ける |
| 404 | ページが存在しない | URLを確認する |
| 500 | サーバー側のエラー | 時間を置いて再試行 |

### GETとPOST

HTTPには「メソッド」と呼ばれる通信の種類があります。主に使うのは以下の2つです。

| メソッド | 用途                         | 例                     |
| -------- | ---------------------------- | ---------------------- |
| GET      | サーバーからデータを取得する | 検索、ページ閲覧       |
| POST     | サーバーにデータを送信する   | ログイン、フォーム送信 |

ブラウザでURLを入力してページを表示するのはGETの典型例です。スクレイピングではほとんどGETを使います。

### パラメータの送信

URLに `?key=value` という形式でパラメータを付けることができます。

```python
params = {"name": "太郎", "age": 25}
response = requests.get("https://httpbin.org/get", params=params)
# https://httpbin.org/get?name=太郎&age=25 にアクセスしたのと同じ
```

### ヘッダーの設定

サーバーに追加情報を送ることができます。User-Agentを設定すると、どのブラウザからアクセスしているかを変えることができます。

> **補足：** 「偽装」と聞くと悪いことのように思えますが、ブラウザも内部でUser-Agentを送っており、これ自体は一般的な技術です。ただし、アクセス先のサイトの利用規約に従うことが前提です。

WindowsのChromeからのアクセスを偽装する例:

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
response = requests.get("https://httpbin.org/get", headers=headers)
```

MacのSafariからのアクセスを偽装する例:

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15"
}
response = requests.get("https://httpbin.org/get", headers=headers)
```

---

## 練習問題

### 5.3 問題1：Webページを取得

https://httpbin.org/get にアクセスして結果を表示してください。

```python
import requests

# ここを書く
```

**考え方:**

1. `requests.get(URL)` でアクセス
2. `response.status_code` でステータス確認
3. `response.text` で本文を表示

---

### 5.4 問題2：パラメータ付きリクエスト

検索パラメータを送ってみましょう。

```python
import requests

# name=太郎、age=25 というパラメータを送る
params = {"name": "太郎", "age": 25}
# ここを書く
```

**考え方:**

1. `requests.get()` の第2引数に `params=params` を指定
2. レスポンスの `.text` を表示
3. レスポンスの中の "args" 項目にパラメータが表示されることを確認

コードを実行して確認できれば正解です。

---

### 5.5 問題3：エラー処理付きで取得

存在しないページにアクセスしたときにエラーメッセージを出す関数を作ってください。

```python
import requests

def fetch_url(url):
    # ここを書く
    # 成功したら response.text を返す
    # 失敗したら None を返す
    pass

# テスト
result = fetch_url("https://httpbin.org/get")
print(result)

result = fetch_url("https://httpbin.org/status/404")
print(result)  # None
```

**考え方:**

1. try-exceptでエラーに備える
2. `response.status_code` が 200 か確認
3. 200なら `.text` を返す、そうでなければ None を返す

---

### 5.6 問題4：タイムアウトの設定

サーバーの応答が遅い場合に備えて、タイムアウトを設定してみましょう。

```python
import requests

# 5秒かかるURLに3秒のタイムアウトを設定
try:
    response = requests.get("https://httpbin.org/delay/5", timeout=3)
    # ここを書く
except requests.exceptions.Timeout:
    # ここを書く
```

**考え方:**

1. `timeout=3` で3秒のタイムアウトを設定
2. `try` ブロック内で `response.text` を表示
3. `except requests.exceptions.Timeout` でタイムアウトエラーをキャッチ
4. タイムアウト時は「タイムアウトしました」と表示

コードを実行して「タイムアウトしました」と表示されれば正解です。

---

## 検索キーワード

| 知りたいこと     | 検索キーワード               |
| ---------------- | ---------------------------- |
| requestsの使い方 | `Python requests 使い方`     |
| ステータスコード | `HTTP ステータスコード 一覧` |
| タイムアウト設定 | `Python requests timeout`    |
| ヘッダー設定     | `Python requests headers`    |

---

## 困ったときは

### 「ConnectionError と出る」

インターネット接続を確認してください。また、URLが間違っていないかも確認してください。

### 「文字化けする」

`response.encoding = "utf-8"` を設定してから `response.text` を参照してみてください。

```python
response = requests.get(url)
response.encoding = "utf-8"
print(response.text)
```

### 「403 Forbidden と出る」

サーバーがアクセスを拒否しています。User-Agentヘッダーを設定すると解決することがあります。

---

## 確認事項

- [ ] requests.get() でページを取得できた
- [ ] ステータスコードを確認できた
- [ ] パラメータを送れた
- [ ] タイムアウトを設定できた

---

**次回は「HTML解析入門」です。**
