# 第18回：並列処理

## 今回のゴール

- 直列処理と並列処理の違いがわかる
- `ThreadPoolExecutor` を使ってスクレイピングを高速化できる
- 適切なスレッド数を設定できる
- 並列処理における注意点を理解できる

## 所要時間：90分

---

## 導入：待ち時間を無駄にしない

スクレイピングで100件のURLからデータを取得するとき、1件あたり3秒かかるとすると、直列処理では合計300秒（5分）かかります。

これは、コンビニのレジが1台しかなく、お客さんが1人ずつ順番に会計するようなものです。列が長くなるほど待ち時間も増えます。

では、レジを5台に増やしたらどうでしょうか。5人が同時に会計できるので、同じ100人でも待ち時間はおよそ5分の1になります。

プログラムの「並列処理」もこれと同じ考え方です。複数のURLに同時にアクセスすることで、ネットワークの待ち時間を有効活用し、全体の処理時間を大幅に短縮できます。

```text
直列処理:
URL1 → URL2 → URL3 → URL4 → URL5
  3秒    3秒    3秒    3秒    3秒  = 合計15秒

並列処理（5並列）:
URL1 ─┐
URL2 ─┤
URL3 ─┼→ 合計3秒！
URL4 ─┤
URL5 ─┘
```

ただし、並列数を増やしすぎるとサーバーに大きな負荷をかけてしまいます。この回では、効率とマナーを両立した並列処理の書き方を学びます。

---

## ハンズオン：直列と並列の速度を比べてみよう

以下のコードをファイルに保存して実行してください。`time` モジュールで処理時間を計測します。

```python
import time
import requests
from concurrent.futures import ThreadPoolExecutor

urls = [f"https://httpbin.org/delay/1"] * 5  # 1秒かかるエンドポイント

# 直列処理
start = time.time()
results_serial = []
for url in urls:
    response = requests.get(url, timeout=10)
    results_serial.append(response.status_code)
serial_time = time.time() - start
print(f"直列: {serial_time:.1f}秒")

# 並列処理
def fetch(url):
    response = requests.get(url, timeout=10)
    return response.status_code

start = time.time()
with ThreadPoolExecutor(max_workers=5) as executor:
    results_parallel = list(executor.map(fetch, urls))
parallel_time = time.time() - start
print(f"並列: {parallel_time:.1f}秒")
```

直列では5秒前後かかるのに対し、並列では1〜2秒で完了するはずです。この差が並列処理の効果です。

---

## 解説

### スレッドとは何か

**スレッド**とは、プログラムが処理を実行する「流れ」のことです。通常のプログラムはスレッドが1本しかなく、処理を1つずつ順番にこなします。

複数のスレッドを使うと、それぞれのスレッドが独立して処理を進められます。特にスクレイピングのような「ネットワークの応答を待つ時間が長い処理」では、スレッドを増やすことで待ち時間を並列に消化でき、大幅な高速化が期待できます。

### ThreadPoolExecutor の基本

Pythonの標準ライブラリに含まれる `concurrent.futures` モジュールの `ThreadPoolExecutor` を使うと、スレッドプールを簡単に扱えます。

```python
import requests
from concurrent.futures import ThreadPoolExecutor

def fetch(url):
    response = requests.get(url, timeout=10)
    return response.status_code

urls = ["https://example.com/1", "https://example.com/2", "https://example.com/3"]

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(fetch, urls))

print(results)  # [200, 200, 200]
```

`with` ブロックを抜けると、全スレッドの完了を自動で待ってから次の処理に進みます。

### executor.map と executor.submit の違い

`ThreadPoolExecutor` には主に2つの使い方があります。

#### executor.map：結果をまとめて受け取る

```python
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(fetch, urls))
# urls の順番通りに結果が返ってくる
```

#### executor.submit：1つずつ処理を渡す

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

futures = []
with ThreadPoolExecutor(max_workers=3) as executor:
    for url in urls:
        future = executor.submit(fetch, url)
        futures.append(future)

# 完了した順番に結果を取り出す
for future in as_completed(futures):
    result = future.result()
    print(result)
```

`as_completed` を使うと、**完了した順番に**結果を取り出せます。時間がかかるURLと速いURLが混在している場合に便利です。

### エラー処理と組み合わせる

並列処理中に1つのURLでエラーが起きても、他のURLへの処理を続けるには、前回学んだ `try/except` と組み合わせます。

```python
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return {"url": url, "status": "success", "text": response.text[:100]}
    except requests.exceptions.HTTPError as e:
        return {"url": url, "status": "error", "text": str(e)}
    except Exception as e:
        return {"url": url, "status": "error", "text": str(e)}

urls = [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/200",
]

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(fetch, urls))

for result in results:
    print(f"{result['status']}: {result['url']}")
```

`fetch` 関数の中でエラーをキャッチして、エラー情報を結果として返すのがポイントです。関数の外でエラーが発生すると、`executor.map` が例外を再送出して処理が中断します。

### tenacity と組み合わせる

前回学んだリトライ処理も、並列処理と組み合わせられます。

```python
from concurrent.futures import ThreadPoolExecutor
from tenacity import retry, stop_after_attempt, wait_exponential
import requests

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def fetch_with_retry(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text

urls = ["https://example.com"] * 10

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(fetch_with_retry, urls))
```

デコレータを付けた関数をそのまま `executor.map` に渡せます。

### 適切なスレッド数の決め方

`max_workers` の値は大きければ大きいほど速いわけではありません。

```text
max_workers が多すぎる
    → サーバーへの短時間の集中アクセス
    → 429 Too Many Requests（アクセス制限）が起きる
    → 最悪の場合、IP がブロックされる

max_workers が少なすぎる
    → 並列化の効果が薄い
    → 処理時間が長くなる
```

一般的な目安：

| 状況                   | 推奨 max_workers |
| ---------------------- | ---------------- |
| 一般的なWebサイト      | 3〜5             |
| API（レート制限あり）  | 1〜2             |
| 自分が管理するサーバー | 10〜20           |

また、スレッドを増やすほどローカルPCのCPUやメモリも消費します。スクレイピング用途では **3〜5 が現実的な上限** です。

### スレッドセーフに注意する

複数のスレッドが同じ変数を同時に書き込もうとすると、データが壊れることがあります（競合状態）。

```python
# ❌ 危険：複数スレッドが results に同時に append する可能性がある
results = []

def fetch_and_append(url):
    data = requests.get(url).text
    results.append(data)  # ← スレッドセーフではない（結果的に動くことも多いが推奨しない）
```

```python
# ✅ 安全：executor.map で結果をまとめて受け取る
import requests
from concurrent.futures import ThreadPoolExecutor

def fetch(url):
    return requests.get(url).text

urls = ["https://example.com/1", "https://example.com/2", "https://example.com/3"]

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(fetch, urls))
```

`executor.map` は結果をスレッドセーフにまとめてくれるので、こちらを使うのが安全です。

---

## 練習問題

### 問題1：直列と並列の実行時間を比較する

`python/lesson18/01_compare_serial_parallel.py` に回答を書いてください。

以下の条件でプログラムを作成し、直列処理と並列処理の実行時間を計測してください。

```
条件:
- URLリスト: ["https://httpbin.org/delay/1"] * 8
  （8件すべて同じURL。1秒かかるエンドポイント）
- 直列処理: for ループで1件ずつ処理
- 並列処理: ThreadPoolExecutor(max_workers=4) を使用
- 実行時間を time.time() で計測して表示
```

期待する出力例：

```
直列: 8.3秒
並列: 2.1秒
```

**考え方:**

```
1. time.time() で開始時刻を記録する
2. 処理が終わったら time.time() で終了時刻を記録する
3. 終了時刻 - 開始時刻 = 経過時間
4. 直列と並列でそれぞれ計測して比較する
```

---

### 問題2：エラーが混在するURLを並列処理する

`python/lesson18/02_parallel_error_handling.py` に回答を書いてください。

以下のURLリストを並列で処理し、成功・失敗を区別して表示してください。

```python
urls = [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/500",
    "https://httpbin.org/status/200",
]
```

期待する出力例：

```
✅ 成功: https://httpbin.org/status/200
❌ 失敗 (404): https://httpbin.org/status/404
✅ 成功: https://httpbin.org/status/200
❌ 失敗 (500): https://httpbin.org/status/500
✅ 成功: https://httpbin.org/status/200
```

**考え方:**

```
1. fetch 関数の中で try/except を使う
2. 成功したら {"url": url, "ok": True} を返す
3. HTTPError なら {"url": url, "ok": False, "code": status_code} を返す
4. executor.map で全URLを処理して結果を受け取る
5. 結果を for ループで回して表示する
```

---

### 問題3：as_completed で完了順に処理する

`python/lesson18/03_as_completed_order.py` に回答を書いてください。

`executor.submit` と `as_completed` を使って、完了した順番に結果を表示するプログラムを作成してください。

```python
import random

def fetch_random_delay(url):
    delay = random.uniform(0.5, 2.0)  # 0.5〜2秒のランダムな遅延
    time.sleep(delay)
    return {"url": url, "delay": round(delay, 2)}

urls = [f"https://example.com/{i}" for i in range(1, 6)]
```

期待する出力例（遅いものが後になる）：

```
完了: https://example.com/3 (0.61秒)
完了: https://example.com/1 (0.89秒)
完了: https://example.com/5 (1.12秒)
完了: https://example.com/2 (1.55秒)
完了: https://example.com/4 (1.98秒)
```

**考え方:**

```
1. executor.submit(fetch_random_delay, url) でそれぞれを登録する
2. futures に溜める
3. as_completed(futures) でループを回すと完了した順番に取れる
4. future.result() で結果を取り出す
```

---

### 問題4：tenacity と組み合わせる

`python/lesson18/04_tenacity_parallel.py` に回答を書いてください。

以下の条件でプログラムを作成してください。

```
条件:
- 10件のURLを max_workers=3 で並列処理
- 各URLへのリクエストは最大3回リトライ
- タイムアウトは5秒
- 成功・失敗をカウントして最後に表示

URLリスト:
urls = [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/200",
    "https://httpbin.org/delay/6",     # タイムアウトさせる
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/500",
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/200",
]
```

期待する出力例：

```
成功: 7件
失敗: 3件
```

**考え方:**

```
1. @retry デコレータをつけた fetch 関数を作る
2. 成功なら True、失敗なら False を返す
3. executor.map で results を取得
4. sum(results) で成功件数、len - sum で失敗件数を計算
```

---

## 検索キーワード

| 知りたいこと                | 検索キーワード                     |
| --------------------------- | ---------------------------------- |
| ThreadPoolExecutor の使い方 | `Python ThreadPoolExecutor 使い方` |
| map と submit の違い        | `Python executor.map submit 違い`  |
| as_completed の使い方       | `Python as_completed 使い方`       |
| スレッドセーフとは          | `Python スレッドセーフ 意味`       |
| GIL とは                    | `Python GIL マルチスレッド`        |

---

## 困ったときは

### 「並列化したのに速くならない」

`max_workers` の数がURLの件数より多くても意味がありません。URLが5件なら `max_workers=5` 以上にしても速くなりません。また、CPUを大量に使う処理（画像処理など）はスレッドよりプロセスの並列化が向いています。

### 「途中でプログラムが止まる」

`with ThreadPoolExecutor` ブロックの中でエラーがキャッチされずに発生すると処理が中断します。`fetch` 関数の中に `try/except` を入れて、エラーを戻り値として返すようにしてください。

### 「結果の順番が毎回変わる」

`executor.map` は URLリストの順番通りに結果を返します。順番が変わる場合は `as_completed` を使っている可能性があります。順番を保ちたい場合は `executor.map` を使ってください。

### 「429 エラーが頻発する」

`max_workers` を減らしてください。また、リクエストとリクエストの間に `time.sleep(0.5)` などの待機を入れることも有効です。

---

## 確認事項

- [ ] 直列処理と並列処理の速度差を確認できた
- [ ] `ThreadPoolExecutor` を使った並列処理が書けた
- [ ] `executor.map` で結果を受け取れた
- [ ] `as_completed` で完了順に処理できた
- [ ] エラー処理と組み合わせた並列処理が書けた
- [ ] 適切な `max_workers` の考え方がわかった

---

**次回は「認証とセッション管理」です。ログインが必要なサイトのデータを取得する方法を学びます。**
