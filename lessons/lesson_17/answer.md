# 第17回：エラー処理とリトライ【解答・解説】

この解答は、問題に対する一例です。動作すれば、別の書き方でも正解です。

---

## 📝 問題1の解答：try/except でエラーをキャッチする

```python
import requests

def fetch_page(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        print(f"{status_code}: HTTPエラーのためスキップ")
        return None

urls = [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
]

for url in urls:
    result = fetch_page(url)
    if result is not None:
        print("200: 成功")
```

実行結果：

```
200: 成功
404: HTTPエラーのためスキップ
500: HTTPエラーのためスキップ
```

### なぜこう書くの？

```python
# try の中でエラーが起きると、即座に except に飛ぶ
# except の中で None を返すことで
# 呼び出し側が「失敗した」と判断できる

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()   # 4xx / 5xx でエラーを発生させる
    return response.text
except requests.exceptions.HTTPError as e:
    # e.response.status_code で実際のステータスコードが取れる
    print(f"{e.response.status_code}: HTTPエラーのためスキップ")
    return None

# 呼び出し側では None かどうかで成否を判断する
if result is not None:
    # 成功した場合だけ処理する
```

**ポイント: `try/except` があれば、エラーが起きてもプログラムが止まらない！**

---

## 📝 問題2の解答：手動でリトライを実装する

```python
import time
import requests

def fetch_with_retry(url, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.text

        except requests.exceptions.HTTPError as e:
            # 404 はリトライしない
            if e.response.status_code == 404:
                print(f"404: ページが存在しません → スキップ: {url}")
                return None
            # 500 などはリトライ対象
            print(f"HTTPエラー ({e.response.status_code})、リトライします ({attempt}/{max_retries})")

        except (requests.exceptions.Timeout,
                requests.exceptions.ConnectionError) as e:
            print(f"接続エラー: {e}、リトライします ({attempt}/{max_retries})")

        # 最後の試行でなければ待ってリトライ
        if attempt < max_retries:
            wait = 2 ** (attempt - 1)  # 1秒 → 2秒 → 4秒
            print(f"{wait}秒待機します...")
            time.sleep(wait)

    print(f"{max_retries}回失敗しました。処理を中止します: {url}")
    return None
```

### なぜこう書くの？（待機時間の変化）

```
attempt=1: wait = 2 ** (1-1) = 2 ** 0 = 1秒
attempt=2: wait = 2 ** (2-1) = 2 ** 1 = 2秒
attempt=3: wait = 2 ** (3-1) = 2 ** 2 = 4秒
→ だんだん長くなる（指数バックオフ）
```

### リトライの判断フロー

```
リクエスト実行
    ↓
成功 → return response.text

失敗（HTTPError）
    ├─ 404 → return None（リトライしない）
    └─ それ以外 → リトライ

失敗（Timeout / ConnectionError）
    └─ リトライ

attempt が max_retries に達したら → return None
```

---

## 📝 問題3の解答：tenacity を使ってリトライを実装する

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
import requests

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(
        (requests.exceptions.Timeout, requests.exceptions.ConnectionError)
    )
)
def fetch(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as e:
        # 404 はリトライさせない（None を返してリトライを中断）
        if e.response.status_code == 404:
            print(f"404: ページが存在しません → スキップ: {url}")
            return None
        # その他の HTTPError（500 など）もリトライしない
        # (@retry は Timeout と ConnectionError のときだけ動作する)
        raise
```

### なぜこう書くの？

```python
# @retry はデコレータ
# 関数の上に付けるだけでリトライ機能が追加される
@retry(
    stop=stop_after_attempt(3),        # 最大3回
    wait=wait_exponential(multiplier=1, min=1, max=8),  # 指数バックオフで待機
    retry=retry_if_exception_type((Timeout, ConnectionError))  # このエラーのときだけリトライ
)

# retry_if_exception_type で指定したエラー以外が起きたら
# tenacity はリトライせずに即エラーを伝播する
# → 404 は HTTPError なので対象外 → 中で return None にして止める
# → Timeout / ConnectionError は対象 → tenacity が自動でリトライ
```

**ポイント: `retry_if_exception_type` でリトライするエラーを絞り込める！**

### 問題2との比較

|                | 問題2（手動実装） | 問題3（tenacity） |
| -------------- | ----------------- | ----------------- |
| コードの量     | 多い              | 少ない            |
| 待機時間の管理 | 自前で計算        | ライブラリが担当  |
| リトライ条件   | if文で判定        | デコレータで宣言  |
| 読みやすさ     | やや複雑          | シンプル          |

---

## 📝 問題4の解答：複数URLを処理してエラーログを記録する

```python
import logging
import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError
)

# ログの設定（プログラムの最初で1回だけ呼ぶ）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(
        (requests.exceptions.Timeout, requests.exceptions.ConnectionError)
    ),
    before_sleep=lambda retry_state: logging.warning(
        f"タイムアウト/接続エラー、リトライします "
        f"({retry_state.attempt_number}/3): "
        f"{retry_state.args[0] if retry_state.args else ''}"
    )
)
def fetch(url):
    response = requests.get(url, timeout=1)
    response.raise_for_status()
    return response.text


urls = [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/404",
    "https://httpbin.org/delay/2",      # timeout=1 なのでタイムアウトする
    "https://httpbin.org/status/500",
]

for url in urls:
    try:
        result = fetch(url)
        logging.info(f"成功: {url}")
    except RetryError:
        logging.error(f"3回失敗: {url}")
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTPエラー {e.response.status_code}: {url}")
    except Exception as e:
        logging.error(f"予期しないエラー: {url} → {e}")
```

実行結果の例：

```
2025-01-01 12:00:01 [INFO] 成功: https://httpbin.org/status/200
2025-01-01 12:00:01 [ERROR] HTTPエラー 404: https://httpbin.org/status/404
2025-01-01 12:00:02 [WARNING] タイムアウト、リトライします (1/3): https://httpbin.org/delay/2
2025-01-01 12:00:04 [WARNING] タイムアウト、リトライします (2/3): https://httpbin.org/delay/2
2025-01-01 12:00:09 [WARNING] タイムアウト、リトライします (3/3): https://httpbin.org/delay/2
2025-01-01 12:00:18 [ERROR] 3回失敗: https://httpbin.org/delay/2
2025-01-01 12:00:18 [ERROR] HTTPエラー 500: https://httpbin.org/status/500
```

### なぜこう書くの？

```python
# logging には5段階のレベルがある
# DEBUG < INFO < WARNING < ERROR < CRITICAL
# basicConfig の level= で、それ以上のレベルだけ表示される

logging.info("正常系のメッセージ")     # [INFO]
logging.warning("注意が必要なとき")    # [WARNING]
logging.error("エラーが起きたとき")    # [ERROR]

# tenacity が全リトライを使い切ったとき RetryError が発生する
# → except RetryError で捕まえて「3回失敗」と記録する
try:
    result = fetch(url)
except RetryError:
    logging.error(f"3回失敗: {url}")
```

### ログレベルの使い分け

```
INFO    → 通常の成功・進捗報告
WARNING → リトライなど注意が必要な状況
ERROR   → リトライ断念・スキップなど問題が発生した状況
```

---

## 💡 今回のポイントまとめ

### エラー処理の基本

```python
try:
    # エラーが起きるかもしれない処理
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text
except requests.exceptions.Timeout:
    # タイムアウトのとき
except requests.exceptions.ConnectionError:
    # 接続できないとき
except requests.exceptions.HTTPError as e:
    # 4xx / 5xx のとき
    print(e.response.status_code)
```

### エラーの種類と対処法

| エラー                        | 対処                       |
| ----------------------------- | -------------------------- |
| `Timeout` / `ConnectionError` | 待ってリトライ             |
| `HTTPError` (404)             | スキップ（リトライしない） |
| `HTTPError` (429 / 500)       | 待ってリトライ             |

### tenacity のよく使うオプション

```python
@retry(
    stop=stop_after_attempt(3),           # 最大3回
    wait=wait_exponential(min=1, max=10), # 指数バックオフ
    retry=retry_if_exception_type((Timeout, ConnectionError))  # 対象を絞る
)
```

### logging の基本設定

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logging.info("成功しました")
logging.warning("リトライします")
logging.error("失敗しました")
```

---

## 🔍 もっと知りたい人向け

### 検索キーワード

- `Python tenacity before_sleep` - リトライ前に処理を挟む方法
- `Python logging ファイル出力` - ログをファイルに保存する方法
- `requests Session` - 接続を使い回してパフォーマンスを上げる方法
- `Python contextlib suppress` - 特定のエラーを簡単に無視する方法

---

**次回は「大規模スクレイピング」です！**
