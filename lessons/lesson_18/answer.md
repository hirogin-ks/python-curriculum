# 第18回：並列処理【解答・解説】

この解答は、問題に対する一例です。動作すれば、別の書き方でも正解です。

---

## 📝 問題1の解答：直列と並列の実行時間を比較する

```python
import time
import requests
from concurrent.futures import ThreadPoolExecutor

urls = ["https://httpbin.org/delay/1"] * 8

def fetch(url):
    response = requests.get(url, timeout=10)
    return response.status_code

# 直列処理
start = time.time()
for url in urls:
    fetch(url)
serial_time = time.time() - start
print(f"直列: {serial_time:.1f}秒")

# 並列処理
start = time.time()
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(fetch, urls))
parallel_time = time.time() - start
print(f"並列: {parallel_time:.1f}秒")

print(f"速くなった倍率: {serial_time / parallel_time:.1f}倍")
```

実行結果の例：

```
直列: 8.3秒
並列: 2.1秒
速くなった倍率: 4.0倍
```

### なぜこう書くの？

```python
# time.time() は現在時刻を秒単位で返す
# 開始時刻と終了時刻の差が経過時間になる
start = time.time()
# 処理...
elapsed = time.time() - start

# max_workers=4 なら4件同時にリクエストを送れる
# 8件を4並列で処理すると、理論上 8/4 = 2回転で完了する
# → 1秒×2 = 約2秒
```

**ポイント: 並列数を増やすほど速くなるが、max_workers は URLの件数を超えても意味がない！**

---

## 📝 問題2の解答：エラーが混在するURLを並列処理する

```python
import requests
from concurrent.futures import ThreadPoolExecutor

urls = [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/500",
    "https://httpbin.org/status/200",
]

def fetch(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return {"url": url, "ok": True, "code": response.status_code}
    except requests.exceptions.HTTPError as e:
        return {"url": url, "ok": False, "code": e.response.status_code}
    except Exception as e:
        return {"url": url, "ok": False, "code": None}

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(fetch, urls))

for result in results:
    if result["ok"]:
        print(f"✅ 成功: {result['url']}")
    else:
        print(f"❌ 失敗 ({result['code']}): {result['url']}")
```

実行結果：

```
✅ 成功: https://httpbin.org/status/200
❌ 失敗 (404): https://httpbin.org/status/404
✅ 成功: https://httpbin.org/status/200
❌ 失敗 (500): https://httpbin.org/status/500
✅ 成功: https://httpbin.org/status/200
```

### なぜこう書くの？

```python
# fetch 関数の中でエラーをキャッチして辞書で返すことがポイント
# → 関数の外にエラーが漏れると executor.map が停止することがある

def fetch(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return {"url": url, "ok": True, "code": response.status_code}
    except requests.exceptions.HTTPError as e:
        return {"url": url, "ok": False, "code": e.response.status_code}

# executor.map は URLリストの順番通りに結果を返す
# → 元の順番が保たれるので、どのURLの結果かわかりやすい
results = list(executor.map(fetch, urls))
```

**ポイント: fetch 関数の中で try/except してエラーを戻り値にする。関数の外に漏らさない！**

---

## 📝 問題3の解答：as_completed で完了順に処理する

```python
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_random_delay(url):
    delay = random.uniform(0.5, 2.0)
    time.sleep(delay)
    return {"url": url, "delay": round(delay, 2)}

urls = [f"https://example.com/{i}" for i in range(1, 6)]

futures = []
with ThreadPoolExecutor(max_workers=5) as executor:
    for url in urls:
        future = executor.submit(fetch_random_delay, url)
        futures.append(future)

    for future in as_completed(futures):
        result = future.result()
        print(f"完了: {result['url']} ({result['delay']}秒)")
```

実行結果の例（ランダムな順番になる）：

```
完了: https://example.com/3 (0.61秒)
完了: https://example.com/1 (0.89秒)
完了: https://example.com/5 (1.12秒)
完了: https://example.com/2 (1.55秒)
完了: https://example.com/4 (1.98秒)
```

### map と as_completed の比較

```python
# executor.map → URLリストの順番通りに結果が返ってくる
results = list(executor.map(fetch, urls))
# urls = [URL1, URL2, URL3]
# results = [URL1の結果, URL2の結果, URL3の結果]  ← 順番が保証される

# as_completed → 完了した順番に結果が返ってくる
for future in as_completed(futures):
    result = future.result()  # 一番早く終わったものから順に取れる
```

### なぜこう書くの？

```python
# executor.submit は1件ずつ処理を登録する
# Future オブジェクトが返ってくる（まだ結果ではない）
future = executor.submit(fetch_random_delay, url)

# as_completed は完了したFutureから順番にyieldする
for future in as_completed(futures):
    # この時点で完了済み
    result = future.result()  # 結果を取り出す
```

**ポイント: 順番が大事なら `executor.map`、完了順に処理したいなら `as_completed`！**

---

## 📝 問題4の解答：tenacity と組み合わせる

```python
import requests
from concurrent.futures import ThreadPoolExecutor
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

urls = [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/200",
    "https://httpbin.org/delay/6",
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/500",
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/200",
]

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(
        (requests.exceptions.Timeout, requests.exceptions.ConnectionError)
    )
)
def fetch_with_retry(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError:
        return False

def fetch_safe(url):
    try:
        return fetch_with_retry(url)
    except Exception:
        return False

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(fetch_safe, urls))

success_count = sum(results)
fail_count = len(results) - success_count
print(f"成功: {success_count}件")
print(f"失敗: {fail_count}件")
```

実行結果：

```
成功: 7件
失敗: 3件
```

### なぜこう書くの？

```python
# @retry デコレータをつけた関数は tenacity が管理する
# Timeout は最大3回リトライ → それでも失敗すると RetryError が出る
# HTTPError (404, 500) は retry 対象外なので即エラーになる

# その外側に fetch_safe で全エラーをキャッチして False を返す
# → executor.map に例外が漏れないようにする
def fetch_safe(url):
    try:
        return fetch_with_retry(url)
    except Exception:
        return False

# sum([True, True, False, True]) → 3 (True = 1 として計算)
success_count = sum(results)
fail_count = len(results) - success_count
```

### 処理の流れ

```
fetch_safe(url)
    └─ fetch_with_retry(url)  ← tenacity が管理
          ├─ 成功 → True を返す
          ├─ HTTPError (404 / 500) → False を返す（リトライなし）
          ├─ Timeout (1〜3回目) → リトライ
          └─ Timeout (3回全部失敗) → RetryError → fetch_safe が False を返す
```

---

## 💡 今回のポイントまとめ

### ThreadPoolExecutor の基本

```python
from concurrent.futures import ThreadPoolExecutor

def fetch(url):
    # ここで1件分の処理を書く
    return result

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(fetch, urls))
```

### map と as_completed の使い分け

|                | `executor.map`     | `as_completed`             |
| -------------- | ------------------ | -------------------------- |
| 結果の順番     | URLリストと同じ順  | 完了した順                 |
| 向いている場面 | 順番を保ちたいとき | 速いものから処理したいとき |
| コードの量     | 少ない             | やや多い                   |

### max_workers の目安

| 状況              | 推奨値 |
| ----------------- | ------ |
| 一般的なWebサイト | 3〜5   |
| APIサーバー       | 1〜2   |
| 自前サーバー      | 10〜20 |

### エラー処理のパターン

```python
def fetch(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return {"ok": True, "data": response.text}
    except Exception as e:
        return {"ok": False, "error": str(e)}
# → fetch 関数の中で全エラーをキャッチして戻り値で返す
```

---

## 🔍 もっと知りたい人向け

### 検索キーワード

- `Python asyncio aiohttp` - スレッドより高速な非同期処理
- `Python ProcessPoolExecutor` - CPUを使う処理の並列化
- `Python threading Lock` - スレッドセーフな変数の操作
- `Python GIL` - Pythonのスレッドに関する制約

---

**次回は「データの保存と整形」です！**
