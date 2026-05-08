# 第17回：エラー処理とリトライ

## 今回のゴール

- スクレイピングで起きやすいエラーの種類がわかる
- `try/except` を使ってエラーに対処できる
- 失敗したリクエストを自動でリトライできる
- `tenacity` ライブラリを使ってリトライ処理を実装できる

## 所要時間：90分

---

## 導入：失敗しても諦めないプログラムを作る

スクレイピングのプログラムを動かしていると、予期せずエラーが起きることがあります。

例えば、100件のURLからデータを収集しようとしている最中に、ネットワークが一時的に切れたとします。エラー処理がなければ、プログラムはその時点で止まってしまい、残り99件の処理が行われません。

これは、宅配便のドライバーが1軒目の配達で「不在」だったからといって、その日の全配達を諦めてしまうようなものです。当然ながら、経験豊富なドライバーは「不在なら後でまた来る」「長時間待っても不在なら持ち帰る」というルールを持っています。

プログラムも同じで、エラーが起きたとき「どう対処するか」をあらかじめ決めておくことが重要です。

**エラー処理があると、次のようなことができます。**

- 一時的なエラーなら、しばらく待ってからもう一度試す
- 存在しないページならスキップして次に進む
- 重大なエラーならログに記録して通知する

今回は、このような「頑丈なスクレイピングプログラム」の作り方を学びます。

---

## ハンズオン：エラーを意図的に起こしてみよう

まず、エラーが起きたときにプログラムがどう動くかを確認しましょう。

以下のコードをファイルに保存して実行してください。

```python
import requests

# 存在しないURLにアクセスしてみる
url = "https://httpbin.org/status/404"
response = requests.get(url)
print(response.status_code)
```

このコードは404ステータスのレスポンスを返しますが、Pythonはエラーを出しません。では次に `raise_for_status()` を追加してみます。

```python
import requests

url = "https://httpbin.org/status/404"
response = requests.get(url)
response.raise_for_status()   # ← 追加
print("成功しました")
```

今度は `HTTPError` が発生してプログラムが止まります。`raise_for_status()` は、4xx・5xx のステータスコードを受け取ったときに自動でエラーを発生させるメソッドです。

次のセクションで、このエラーを「どうキャッチして対処するか」を学びます。

---

## 解説

### よくあるエラーの種類

スクレイピングで遭遇しやすいエラーをまとめます。

| エラー                                | 意味               | 主な原因                    | 対処法               |
| ------------------------------------- | ------------------ | --------------------------- | -------------------- |
| `requests.exceptions.Timeout`         | 時間切れ           | サーバーの応答が遅い        | 待ってリトライ       |
| `requests.exceptions.ConnectionError` | 接続失敗           | ネットワーク切断・DNSエラー | 待ってリトライ       |
| `requests.exceptions.HTTPError` (404) | ページが存在しない | URLが間違い・削除済み       | スキップ             |
| `requests.exceptions.HTTPError` (429) | アクセス過多       | リクエストが多すぎる        | 長めに待ってリトライ |
| `requests.exceptions.HTTPError` (500) | サーバーエラー     | サーバー側の不具合          | 待ってリトライ       |

### try/except でエラーをキャッチする

Pythonでは、エラーが起きても処理を続けるために `try/except` 構文を使います。

```python
try:
    # エラーが起きるかもしれない処理
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    print("成功")
except requests.exceptions.Timeout:
    # タイムアウトのときの処理
    print("タイムアウトしました")
except requests.exceptions.ConnectionError:
    # 接続エラーのときの処理
    print("接続できませんでした")
except requests.exceptions.HTTPError as e:
    # HTTPエラー（404や500など）のときの処理
    print(f"HTTPエラー: {e}")
```

`except` は複数書けます。エラーの種類に応じて、異なる対処ができます。

#### 404 と 500 を区別して処理する

```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code
    if status_code == 404:
        print(f"ページが存在しません: {url}")
        # スキップして次の処理へ
    elif status_code == 429:
        print("アクセス制限がかかっています。しばらく待ちます")
    elif status_code >= 500:
        print(f"サーバーエラー ({status_code})。リトライします")
```

### 手動でリトライを実装する

エラーが起きたとき、一定回数まで自動でやり直す処理を自分で書くと次のようになります。

```python
import time
import requests

def fetch_with_retry(url, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except (requests.exceptions.Timeout,
                requests.exceptions.ConnectionError) as e:
            if attempt < max_retries:
                wait = 2 ** attempt  # 2秒、4秒、8秒…と増える
                print(f"失敗 ({attempt}回目)。{wait}秒後にリトライします")
                time.sleep(wait)
            else:
                print(f"{max_retries}回失敗しました。処理を中止します: {e}")
                return None
```

この「待ち時間を徐々に増やす」方法を **指数バックオフ（Exponential Backoff）** と呼びます。1回失敗するたびに待ち時間を2倍にすることで、サーバーに負荷をかけすぎずにリトライできます。

```text
1回目失敗 → 2秒待つ
2回目失敗 → 4秒待つ
3回目失敗 → 8秒待つ
→ だんだん長く待つ（サーバーに優しい）
```

### tenacity でリトライを簡単に書く

手動でリトライ処理を書くのは手間がかかります。`tenacity` ライブラリを使うと、デコレータ1つで同じことが実現できます。

```python
from tenacity import retry, stop_after_attempt, wait_exponential
import requests

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def fetch(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text
```

`@retry` はデコレータと呼ばれる仕組みで、関数の前に付けるだけでリトライ機能が追加されます。

| オプション                    | 意味                             |
| ----------------------------- | -------------------------------- |
| `stop_after_attempt(3)`       | 最大3回まで試す                  |
| `wait_exponential()`          | 指数バックオフで待機時間を増やす |
| `multiplier=1, min=1, max=10` | 1秒から始めて最大10秒まで増やす  |

#### 特定のエラーのときだけリトライする

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(
        (requests.exceptions.Timeout, requests.exceptions.ConnectionError)
    )
)
def fetch(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text
```

`retry_if_exception_type` を使うと、「タイムアウトと接続エラーのときだけリトライして、404はリトライしない」といった細かい制御ができます。404はリトライしても意味がないため、このような使い分けが重要です。

### エラーをログに記録する

本番のスクレイピングでは、どのURLでエラーが起きたかを記録しておくと後で確認できます。

```python
import logging

# ログの設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def fetch(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        logging.info(f"成功: {url}")
        return response.text
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTPエラー {e.response.status_code}: {url}")
        return None
    except Exception as e:
        logging.error(f"予期しないエラー: {url} → {e}")
        return None
```

実行するとコンソールに次のような形式で出力されます。

```
2025-01-01 12:00:01 [INFO] 成功: https://example.com/item/1
2025-01-01 12:00:02 [ERROR] HTTPエラー 404: https://example.com/item/2
```

---

## 練習問題

### 問題1：try/except でエラーをキャッチする

以下の関数に `try/except` を追加して、エラーが起きても処理が止まらないようにしてください。

```python
import requests

def fetch_page(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text

urls = [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
]

for url in urls:
    result = fetch_page(url)
    print(result)
```

期待する動作：

```
200: 成功
404: HTTPエラーのためスキップ
500: HTTPエラーのためスキップ
```

**考え方:**

```
1. fetch_page に try/except を追加する
2. 成功したら response.text を返す
3. HTTPError が起きたらステータスコードを表示して None を返す
4. 呼び出し側で None かどうかをチェックして表示を切り替える
```

---

### 問題2：手動でリトライを実装する

以下の条件を満たすリトライ付き関数を作成してください。

```
条件:
- 最大3回まで試す
- タイムアウトまたは接続エラーの場合のみリトライ
- リトライするたびに待機時間を2倍にする（初回：1秒）
- 3回失敗したら None を返す
- 404エラーはリトライせずにすぐ None を返す
```

**考え方:**

```
1. for attempt in range(1, 4) でループを回す
2. try/except でエラーをキャッチ
3. Timeout と ConnectionError → time.sleep(wait) してリトライ
4. HTTPError → status_code が 404 ならループを break してリターン
5. wait は attempt に応じて 1, 2, 4 と変化させる（2 ** (attempt - 1)）
```

---

### 問題3：tenacity を使ってリトライを実装する

問題2の関数を `tenacity` を使って書き直してください。

さらに、`retry_if_exception_type` を使い、404エラー（`HTTPError`）のときはリトライしないようにしてください。

**考え方:**

```
1. @retry デコレータをつける
2. stop=stop_after_attempt(3) で3回まで
3. wait=wait_exponential(multiplier=1, min=1, max=8) で待機
4. retry=retry_if_exception_type((Timeout, ConnectionError)) で対象を絞る
5. 関数の中で HTTPError をキャッチして None を返す
```

---

### 問題4：複数URLを処理してエラーログを記録する

下記のURLリストを順にフェッチし、成功・失敗を `logging` で記録するプログラムを作成してください。

```python
urls = [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/404",
    "https://httpbin.org/delay/2",      # 2秒かかるページ（timeout=1にするとタイムアウト）
    "https://httpbin.org/status/500",
]
```

期待するログの出力例：

```
[INFO] 成功: https://httpbin.org/status/200
[ERROR] HTTPエラー 404: https://httpbin.org/status/404
[WARNING] タイムアウト、リトライします (1/3): ...
[ERROR] 3回失敗: https://httpbin.org/delay/2
[ERROR] HTTPエラー 500: https://httpbin.org/status/500
```

**考え方:**

```
1. logging.basicConfig で出力形式を設定する
2. fetch 関数に tenacity のリトライと logging を組み合わせる
3. URLをforループで回す
```

---

## 検索キーワード

| 知りたいこと          | 検索キーワード                 |
| --------------------- | ------------------------------ |
| try/except の書き方   | `Python try except 使い方`     |
| requests のエラー一覧 | `requests exceptions 一覧`     |
| 指数バックオフとは    | `exponential backoff 仕組み`   |
| tenacity の使い方     | `tenacity Python retry 使い方` |
| logging の書き方      | `Python logging 使い方 初心者` |

---

## 困ったときは

### 「if/else でステータスコードをチェックしたらダメですか？」

初心者の方は `if response.status_code >= 400:` で条件分岐をしたくなりますが、Pythonでは `try/except` を使うことが標準です。理由は以下の通りです：

**if/else の問題：**
```python
# ❌ 200や404は処理できるが、ネットワークエラーには対応できない
response = requests.get(url)  # ← ここで接続失敗するとプログラムが止まる
if response.status_code == 404:
    print("ページなし")
```

**try/except の利点：**
```python
# ✅ ステータスコードもネットワークエラーも統一的に処理できる
try:
    response = requests.get(url)  # ← タイムアウトや接続エラーもキャッチできる
    response.raise_for_status()   # ← 404や500も自動でエラーになる
except requests.exceptions.Timeout:
    print("タイムアウト")
except requests.exceptions.HTTPError:
    print("HTTPエラー")
```

つまり、`try/except` は「ネットワークエラー」と「HTTPエラー」の両方に対応できるため、スクレイピングには必須です。

### 「どのエラーをキャッチすればいいかわからない」

まず `except Exception as e: print(e)` で全エラーをキャッチして、どんなエラーが出るか確認しましょう。その後で、出てきたエラーの種類に合わせて `except` の対象を絞ります。

### 「tenacity をインストールしたのにimportできない」

仮想環境が有効になっているか確認してください。`pip install tenacity` を実行したとき、プロンプトの先頭に `(.venv)` が表示されていた必要があります。表示されていなければ仮想環境を有効にしてから再インストールしてください。

### 「リトライしているのにすぐ止まる」

`retry_if_exception_type` で指定したエラーと、実際に発生しているエラーが一致していない可能性があります。`except Exception as e: print(type(e))` でエラーの型を確認してみてください。

### 「ログがコンソールに出ない」

`logging.basicConfig` はプログラムの一番最初に1回だけ呼び出す必要があります。また、デフォルトのレベルは `WARNING` なので、`INFO` を表示させるには `level=logging.INFO` を指定してください。

---

## 確認事項

- [ ] スクレイピングで起きやすいエラーの種類がわかった
- [ ] `try/except` を使ってエラーをキャッチできた
- [ ] 指数バックオフの仕組みがわかった
- [ ] 手動でリトライ処理を実装できた
- [ ] `tenacity` を使ってリトライを実装できた
- [ ] `logging` でエラーを記録できた

---

**次回は「並行処理」です。複数のリクエストを同時に送信して、スクレイピングを高速化する方法を学びます。**
