# 第21回：定期実行と自動化【解答・解説】

この解答は、問題に対する一例です。動作すれば、別の書き方でも正解です。

---

## 📝 問題1の解答：schedule の基本を使ってみる

```python
import schedule
import time

def job_a():
    now = time.strftime("%H:%M:%S")
    print(f"[{now}] 現在時刻: {now}")

def job_b():
    now = time.strftime("%H:%M:%S")
    print(f"[{now}] 定期レポート")

schedule.every(3).seconds.do(job_a)
schedule.every(10).seconds.do(job_b)

print("スケジュールを開始します（Ctrl+C で終了）")
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("終了しました")
```

実行結果の例：

```
スケジュールを開始します（Ctrl+C で終了）
[12:00:03] 現在時刻: 12:00:03
[12:00:06] 現在時刻: 12:00:06
[12:00:09] 現在時刻: 12:00:09
[12:00:10] 定期レポート
[12:00:10] 現在時刻: 12:00:10
```

### なぜこう書くの？

```python
# schedule.every(3).seconds.do(job_a)
# → 「3秒ごとに job_a を実行する」というジョブを登録する
# → この時点では実行されない

# while True の中で run_pending() を呼ぶことで
# 「実行すべき時刻になったジョブ」が実行される
while True:
    schedule.run_pending()  # 時刻になったジョブを実行
    time.sleep(1)           # 1秒待機（CPU使用率を抑える）

# try/except KeyboardInterrupt で Ctrl+C を処理すると
# 終了メッセージを表示してきれいに終われる
```

**ポイント: ジョブの登録と実行は別物。`run_pending()` を `while True` で呼び続けて初めて動く！**

---

## 📝 問題2の解答：ハッシュを使って変更を検知する

```python
import os
import hashlib
import requests

HASH_FILE = "last_hash.txt"

def load_previous_hash():
    """前回のハッシュをファイルから読み込む"""
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f:
            return f.read().strip()
    return None

def save_hash(hash_value):
    """ハッシュをファイルに保存する"""
    with open(HASH_FILE, "w") as f:
        f.write(hash_value)

def check_for_changes(url):
    """ページの変更を検知する。変更あり→ True、変更なし→ False を返す"""
    # ページを取得してハッシュを計算する
    response = requests.get(url, timeout=10)
    current_hash = hashlib.md5(response.text.encode()).hexdigest()

    # 前回のハッシュを読み込む
    previous_hash = load_previous_hash()

    if previous_hash is None:
        print("初回取得完了。次回から変更を検知します")
        save_hash(current_hash)
        return False

    if current_hash != previous_hash:
        print(f"変更を検知しました！")
        print(f"  前回: {previous_hash}")
        print(f"  今回: {current_hash}")
        save_hash(current_hash)
        return True
    else:
        print("変更なし")
        return False


# 動作確認
url = "https://quotes.toscrape.com/"
check_for_changes(url)  # 1回目: 初回取得
check_for_changes(url)  # 2回目: 変更なし
```

実行結果：

```
初回取得完了。次回から変更を検知します
変更なし
```

### なぜこう書くの？

```python
# hashlib.md5(text.encode()).hexdigest() の流れ
text = response.text            # HTMLテキスト（str）
encoded = text.encode()         # bytes に変換（md5 は bytes を受け取る）
hash_obj = hashlib.md5(encoded) # ハッシュオブジェクトを作る
current_hash = hash_obj.hexdigest()  # 16進数の文字列（32文字）に変換

# ファイルに保存することで、プログラムを再起動しても前回の状態を引き継げる
# → os.path.exists でファイルの有無を確認して初回実行を判定
```

### ハッシュ値の特性

```
同じ文字列 → 必ず同じハッシュ値
"Hello"   → 8b1a9953c4611296a827abf8c47804d7

1文字でも違えば全く別のハッシュ値
"hello"   → 5d41402abc4b2a76b9719d911017c592
```

**ポイント: ハッシュ値を比較すれば、テキスト全体を比べなくても変更を素早く検知できる！**

---

## 📝 問題3の解答：定期実行と変更検知を組み合わせる

```python
import os
import time
import hashlib
import logging
import requests
import schedule

TARGET_URL = "https://quotes.toscrape.com/"
HASH_FILE = "last_hash.txt"

# logging の設定（コンソールとファイルの両方に出力）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("monitor.log", encoding="utf-8"),
        logging.StreamHandler(),
    ]
)

def load_previous_hash():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f:
            return f.read().strip()
    return None

def save_hash(hash_value):
    with open(HASH_FILE, "w") as f:
        f.write(hash_value)

def check_for_changes(url):
    try:
        response = requests.get(url, timeout=10)
        current_hash = hashlib.md5(response.text.encode()).hexdigest()
        previous_hash = load_previous_hash()

        if previous_hash is None:
            logging.info("初回取得完了。次回から変更を検知します")
        elif current_hash != previous_hash:
            logging.info("変更を検知しました！")
        else:
            logging.info("変更なし")

        save_hash(current_hash)

    except Exception as e:
        logging.error(f"取得エラー: {e}")


logging.info(f"監視を開始します: {TARGET_URL}")

# 起動時にすぐ1回実行する
check_for_changes(TARGET_URL)

# 30秒ごとに実行するスケジュールを登録する
schedule.every(30).seconds.do(check_for_changes, url=TARGET_URL)

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    logging.info("監視を終了しました")
```

ログ出力例（monitor.log にも同じ内容が保存される）：

```
2025-01-01 12:00:00 [INFO] 監視を開始します: https://quotes.toscrape.com/
2025-01-01 12:00:01 [INFO] 初回取得完了。次回から変更を検知します
2025-01-01 12:00:31 [INFO] 変更なし
2025-01-01 12:01:01 [INFO] 変更なし
```

### なぜこう書くの？

```python
# do() に引数付きの関数を渡すには url=... のようにキーワード引数で渡す
schedule.every(30).seconds.do(check_for_changes, url=TARGET_URL)

# FileHandler でファイルに、StreamHandler でコンソールに同時出力
logging.basicConfig(
    handlers=[
        logging.FileHandler("monitor.log", encoding="utf-8"),
        logging.StreamHandler(),
    ]
)

# 起動直後に1回実行してから while True に入ることで
# 最大30秒待たずにすぐ動作確認できる
check_for_changes(TARGET_URL)  # 初回実行
while True:
    schedule.run_pending()
    time.sleep(1)  # 1秒待機
```

**ポイント: `do()` に引数付き関数を渡すときは `do(func, 引数名=値)` の形で書く！**

---

## 📝 問題4の解答：変更箇所を差分で表示する

```python
import os
import time
import hashlib
import logging
import difflib
import requests
import schedule
from bs4 import BeautifulSoup

TARGET_URL = "https://quotes.toscrape.com/"
HASH_FILE = "last_hash.txt"
QUOTES_FILE = "last_quotes.txt"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("monitor.log", encoding="utf-8"),
        logging.StreamHandler(),
    ]
)

def extract_quotes_text(html):
    """名言のテキストと著者名をリストで返す"""
    soup = BeautifulSoup(html, "html.parser")
    quotes = []
    for q in soup.select(".quote"):
        text = q.select_one(".text").get_text(strip=True)
        author = q.select_one(".author").get_text(strip=True)
        quotes.append(f"{text} - {author}")
    return quotes

def load_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def save_file(filepath, content):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def check_for_changes(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        quotes = extract_quotes_text(response.text)
        quotes_text = "\n".join(quotes)

        # 名言テキストのハッシュを計算する
        current_hash = hashlib.md5(quotes_text.encode()).hexdigest()
        previous_hash = load_file(HASH_FILE)

        if previous_hash is None:
            logging.info("初回取得完了。次回から変更を検知します")
        elif current_hash != previous_hash:
            logging.info("変更を検知しました！")

            # difflib で差分を表示する
            previous_content = load_file(QUOTES_FILE) or ""
            previous_lines = previous_content.splitlines()
            current_lines = quotes

            diff = list(difflib.unified_diff(previous_lines, current_lines, lineterm=""))
            for line in diff[2:]:  # ファイル情報ヘッダーをスキップ
                if line.startswith("+") and not line.startswith("+++"):
                    logging.info(f"+ 追加: {line[1:]}")
                elif line.startswith("-") and not line.startswith("---"):
                    logging.info(f"- 削除: {line[1:]}")
        else:
            logging.info("変更なし")

        save_file(HASH_FILE, current_hash)
        save_file(QUOTES_FILE, quotes_text)

    except Exception as e:
        logging.error(f"取得エラー: {e}")


logging.info(f"監視を開始します: {TARGET_URL}")
check_for_changes(TARGET_URL)

schedule.every(30).seconds.do(check_for_changes, url=TARGET_URL)

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    logging.info("監視を終了しました")
```

変更が起きたときのログ出力例：

```
2025-01-01 12:00:31 [INFO] 変更を検知しました！
2025-01-01 12:00:31 [INFO] + 追加: "New quote text." - New Author
2025-01-01 12:00:31 [INFO] - 削除: "Old quote text." - Old Author
```

### なぜこう書くの？

```python
# HTML全体でなく「名言テキスト」だけを抽出してハッシュ化する
# → 広告・タイムスタンプなど関係ない部分の変化を無視できる
quotes = extract_quotes_text(response.text)
quotes_text = "\n".join(quotes)
current_hash = hashlib.md5(quotes_text.encode()).hexdigest()

# set() 同士の差分演算で追加・削除を素早く検出する
previous_quotes = set(load_file(QUOTES_FILE).splitlines())
current_quotes = set(quotes)

added   = current_quotes - previous_quotes  # 今回にあって前回にないもの
removed = previous_quotes - current_quotes  # 前回にあって今回にないもの
```

### set 演算の仕組み

```
previous_quotes = {"A", "B", "C"}
current_quotes  = {"B", "C", "D"}

追加 (current - previous) = {"D"}   ← 今回に増えた
削除 (previous - current) = {"A"}   ← 今回に消えた
```

---

## 💡 今回のポイントまとめ

### schedule の基本

```python
import schedule, time

# ジョブを登録する
schedule.every(10).minutes.do(job)
schedule.every().day.at("09:00").do(job)

# 引数付きの関数を渡す
schedule.every(30).seconds.do(check, url="https://example.com")

# ループを動かす
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("終了")
```

### ハッシュを使った変更検知の流れ

```
1. ページを取得する
2. 注目したい部分だけ抽出する
3. md5 でハッシュ化する
4. 前回のハッシュ（ファイル）と比較する
5. 違えば変更あり → 処理 → 新しいハッシュを保存
6. 同じなら変更なし
```

### よく使うスケジュール設定

```python
schedule.every(30).seconds.do(job)         # 30秒ごと
schedule.every(10).minutes.do(job)         # 10分ごと
schedule.every(1).hours.do(job)            # 1時間ごと
schedule.every().day.at("09:00").do(job)   # 毎日9:00
schedule.every().monday.do(job)            # 毎週月曜
```

---

## 🔍 もっと知りたい人向け

### 検索キーワード

- `Python schedule キャンセル` - 登録済みジョブを削除する方法
- `Python cron 定期実行` - OS レベルで定期実行する方法（より本格的）
- `Python hashlib sha256` - md5 より安全なハッシュアルゴリズム
- `Python difflib unified_diff` - テキストの差分を詳しく表示する方法

---

**次回は「データの保存と整形」です！**
