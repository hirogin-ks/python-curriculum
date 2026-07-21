# 第23回：デバッグとテスト

## 今回のゴール

- `loguru` を使って見やすいログ出力ができる
- ログをファイルに保存してローテーションできる
- `pytest` を使って関数のテストが書ける
- スクレイピングコードにテストを追加して品質を高められる

## 所要時間：90分

---

## 導入：なぜログとテストが必要なのか

スクレイピングプログラムが完成して動き始めたとします。しばらくして「昨日は動いていたのに今日はデータが取れていない」という状況が起きました。このとき、ログがなければ原因を調べることができません。

ログとは、プログラムの動作記録です。「いつ・何が起きたか」を記録しておくことで、問題が起きたときに振り返って調べられます。

```text
ログなし → 「なぜ動かないのか？」が全くわからない
ログあり → 「12:30にこのURLでHTTPエラーが起きた」とわかる
```

一方、テストとは「この関数が正しく動くか」を自動で確認する仕組みです。スクレイピングでは「HTMLのパース関数が正しい値を返すか」「価格の文字列を正しく数値に変換できるか」といったテストが特に重要です。

```text
テストなし → コードを変えるたびに手動で全部確認が必要
テストあり → コマンド1つで全部まとめて確認できる
```

今回はこの2つのツール、`loguru`（ログ）と `pytest`（テスト）を学びます。

---

## ハンズオン：loguru を試してみよう

以下のコードをファイルに保存して実行してください。

```python
from loguru import logger

logger.debug("デバッグ情報")
logger.info("通常のメッセージ")
logger.warning("注意が必要")
logger.error("エラーが発生")
logger.success("処理完了")
```

実行すると、カラフルなログがコンソールに表示されます。標準の `logging` と比べて、設定なしでもきれいな出力が得られるのが `loguru` の特徴です。

---

## 解説

### loguru の基本

`loguru` は標準ライブラリの `logging` をシンプルにしたサードパーティライブラリです。設定が少なく、見やすい出力が特徴です。

```python
from loguru import logger

# ログレベル（下ほど重要）
logger.debug("詳細な開発者向け情報")    # 開発中のデバッグ
logger.info("通常の進捗報告")           # 正常系のメッセージ
logger.success("処理が成功した")         # 成功を明示したいとき
logger.warning("注意が必要な状況")       # 軽い問題
logger.error("エラーが発生した")         # 対処が必要な問題
logger.critical("致命的なエラー")        # プログラムが続行不能
```

### ファイルへのログ保存

```python
from loguru import logger

# ファイルに保存する（1MB を超えたら新しいファイルに切り替える）
logger.add("scraping.log", rotation="1 MB", encoding="utf-8")

# 以降のログはコンソールとファイルの両方に出力される
logger.info("スクレイピングを開始します")
```

`rotation` にはファイルサイズ（`"1 MB"`）や時間（`"1 day"`・`"1 week"`）を指定できます。ログファイルが肥大化しすぎるのを防げます。

#### 保存先・フォーマット・レベルを細かく設定する

```python
logger.add(
    "logs/scraping_{time:YYYY-MM-DD}.log",  # 日付入りのファイル名
    rotation="1 day",        # 1日ごとに新しいファイルに切り替える
    retention="7 days",      # 7日以上古いファイルを自動削除する
    level="INFO",            # INFO以上のみ保存する
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss} [{level}] {message}",
)
```

### 例外のログ記録

エラーが発生したときのスタックトレース（どこでエラーが起きたかの詳細）を自動で記録できます。

以下の例では、**ゼロ除算（0 で割る演算）** という絶対にエラーが起きる操作を意図的に行い、例外処理をテストしています。このように `try-except` ブロックでエラーをキャッチし、`logger.exception()` を呼ぶことで、エラーの詳細情報（スタックトレース）がログに記録されます。

```python
try:
    result = 1 / 0
except ZeroDivisionError:
    logger.exception("計算中にエラーが発生しました")
    # → エラーのスタックトレースも一緒に記録される
```

### pytest の基本

`pytest` は Python の代表的なテストライブラリです。「関数に値を渡したとき、期待通りの結果が返ってくるか」をコマンド1つで自動的に確認できます。本番環境にデプロイする前や、コードを修正した後に実行することで、意図しないバグを早期に発見できます。また、テストがあることで「このコードは正しく動く」という根拠が生まれ、安心してリファクタリングや機能追加ができるようになります。`test_` で始まる関数や `_test` で終わるファイルが自動的にテストとして認識されます。詳しい命名規則は後述の「テストファイルの命名規則」セクションを参照してください。
もしテスト以外の命名規則を知りたい場合は、HTML後半のカリキュラムの「命名規則」セクションを確認してみてください。

```python
# test_sample.py というファイルに書く

def add(a, b):
    return a + b

def test_add():
    assert add(1, 2) == 3      # 期待値と一致するか確認
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
```

テストを実行するにはターミナルで以下を実行します。

```bash
pytest test_sample.py -v
```

`-v` オプションを付けると、各テストの合否が1行ずつ表示されます。

### assert の書き方

```python
# 等しいか確認
assert parse_price("¥1,500") == 1500

# True / False の確認
assert is_valid_url("https://example.com") is True

# 例外が発生することを確認
import pytest
with pytest.raises(ValueError):
    parse_price("invalid")

# リストの要素を確認
assert "python" in tags
```

### スクレイピングで特にテストしたい関数

スクレイピングプロジェクトでは、HTMLのパース処理は特にテストが重要です。サイトが更新されてHTML構造が変わったとき、テストがあればすぐに気づけます。

```python
# parser.py（パース処理をまとめたファイル）

from bs4 import BeautifulSoup

def parse_price(text):
    """価格文字列を数値に変換する。例: '¥1,500' → 1500"""
    # ¥, $, カンマ, スペースを除去してから変換する
    cleaned = text.replace("¥", "").replace("$", "").replace(",", "").strip()
    return float(cleaned) if "." in cleaned else int(cleaned)

def parse_title(html):
    """HTMLから記事タイトルを取り出す"""
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("h1")
    return tag.get_text(strip=True) if tag else None
```

```python
# test_parser.py（テストファイル）

from parser import parse_price, parse_title

def test_parse_price_yen():
    assert parse_price("¥1,500") == 1500

def test_parse_price_dollar():
    assert parse_price("$29.99") == 29.99

def test_parse_price_no_symbol():
    assert parse_price("1000") == 1000

def test_parse_title():
    html = "<html><body><h1>テスト記事</h1></body></html>"
    assert parse_title(html) == "テスト記事"

def test_parse_title_missing():
    html = "<html><body></body></html>"
    assert parse_title(html) is None
```

### テストファイルの命名規則

`pytest` は以下のファイルとファイル名を自動で認識します。

```
test_parser.py     ← test_ で始まるファイル
parser_test.py     ← _test で終わるファイル

def test_xxx():    ← test_ で始まる関数
class TestXxx:     ← Test で始まるクラス
```

---

## 練習問題

### 問題1：loguru でスクレイピングのログを記録する

以下の条件でログ設定を行い、スクレイピングの各ステップでログを出力してください。

```
条件:
- コンソールには全レベルのログを出力する
- ファイル（scraping.log）には INFO 以上のみ保存する
- ファイルは 1 MB ごとにローテーションする
- 古いファイルは 7 日後に自動削除する
- requests でページを取得し、成功・失敗をログに記録する
```

以下の URL リストを処理してください。

```python
urls = [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/200",
]
```

期待するログ出力例：

```
2025-01-01 12:00:00 | INFO | スクレイピング開始
2025-01-01 12:00:01 | SUCCESS | 成功 (200): https://httpbin.org/status/200
2025-01-01 12:00:02 | ERROR | HTTPエラー (404): https://httpbin.org/status/404
2025-01-01 12:00:03 | SUCCESS | 成功 (200): https://httpbin.org/status/200
2025-01-01 12:00:03 | INFO | スクレイピング完了
```

**考え方:**

```
1. logger.add で scraping.log にファイル出力を設定する
2. URL を for ループで処理する
3. try/except で requests のエラーをキャッチする
4. 成功なら logger.success、HTTPエラーなら logger.error を使う
```

---

### 問題2：parser.py と test_parser.py を作る

以下の関数を `python/lesson23/parser.py` に実装し、`python/lesson23/test_parser.py` にテストを書いてください。
`test_` で始まるファイルは `pytest` が自動で見つけるテスト用ファイルです。

#### 実装する関数

```python
def parse_price(text: str) -> int | float:
    """
    価格文字列を数値に変換する。
    例: "¥1,500" → 1500 / "$29.99" → 29.99 / "1,000円" → 1000
    変換できない場合は ValueError を発生させる。
    """

def parse_quote(html: str) -> dict | None:
    """
    quotes.toscrape.com の1件分の名言 HTML から
    {"text": "...", "author": "..."} を返す。
    取得できなければ None を返す。
    """
```

#### テストする項目

```
parse_price:
- "¥1,500" → 1500 になるか
- "$29.99" → 29.99 になるか
- "1,000円" → 1000 になるか
- "1000" → 1000 になるか
- "" (空文字) → ValueError が発生するか

parse_quote:
- 正しいHTMLから {"text": ..., "author": ...} が返るか
- {"author": ...} の値が正しく抽出されるか
- .text または .author 要素がないHTMLで None が返るか
- 空文字列で None が返るか
```

**考え方:**

```
1. parse_price は ¥・$・円・カンマを除去して int または float に変換する
2. 変換できなければ ValueError を raise する
3. pytest.raises(ValueError) で例外発生のテストができる
4. parse_quote は BeautifulSoup で .text と .author を取り出す
```

---

### 問題3：テストを実行して結果を確認する

問題2で作成したテストを実行してください。

```bash
cd python/lesson23
pytest test_parser.py -v
```

すべてのテストが `PASSED` になることを確認してください。

もし `FAILED` になるテストがある場合は、`parser.py` の実装を修正してすべて通るようにしてください。

期待する出力例：

```
================== test session starts ==================
collected 9 items

test_parser.py::test_parse_price_yen PASSED          [ 11%]
test_parser.py::test_parse_price_dollar PASSED        [ 22%]
test_parser.py::test_parse_price_en PASSED            [ 33%]
test_parser.py::test_parse_price_plain PASSED         [ 44%]
test_parser.py::test_parse_price_invalid PASSED       [ 55%]
test_parser.py::test_parse_quote_valid PASSED         [ 66%]
test_parser.py::test_parse_quote_author PASSED        [ 77%]
test_parser.py::test_parse_quote_missing PASSED       [ 88%]
test_parser.py::test_parse_quote_empty PASSED         [100%]

================== 9 passed in 0.12s ==================
```

**考え方:**

```
FAILED になったテストのメッセージを読む
→ AssertionError: assert X == Y のように「実際の値」と「期待する値」が表示される
→ parser.py の対応する処理を修正する
→ 再度 pytest を実行して PASSED になることを確認する
```

---

### 問題4：loguru と pytest を組み合わせる

以下の `fetch_and_parse` 関数を実装し、テストを書いてください。

```python
# scraper.py
import requests
from loguru import logger
from parser import parse_price

def fetch_and_parse(url: str, price_selector: str) -> int | float | None:
    """
    URL からページを取得し、CSS セレクターで価格を取り出して数値で返す。
    取得・パースに失敗したら None を返す。
    """
```

テストでは実際にHTTPリクエストを送らず、`unittest.mock` でレスポンスを偽物に置き換えてください。

```python
# test_scraper.py
from unittest.mock import MagicMock, patch
from scraper import fetch_and_parse

def test_fetch_and_parse_success():
    # 偽のHTMLを返す mock を作る
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '<div class="price">¥1,500</div>'
    mock_response.raise_for_status = MagicMock()

    with patch("scraper.requests.get", return_value=mock_response):
        result = fetch_and_parse("https://example.com", ".price")
        assert result == 1500
```

**考え方:**

```
1. fetch_and_parse は requests.get → raise_for_status → BeautifulSoup でパース → parse_price の順に処理する
2. エラーなら logger.error を呼んで None を返す
3. テストでは requests.get を mock に差し替えて HTTP 通信をしない
4. patch("scraper.requests.get", return_value=mock_response) で差し替える
```

---

## 検索キーワード

| 知りたいこと       | 検索キーワード                |
| ------------------ | ----------------------------- |
| loguru の使い方    | `Python loguru 使い方`        |
| pytest の基本      | `Python pytest 使い方 初心者` |
| assert の書き方    | `pytest assert 書き方`        |
| 例外テストの書き方 | `pytest raises 例外 テスト`   |
| mock の使い方      | `Python unittest.mock 使い方` |

---

## 困ったときは

### 「pytest が見つからない」

仮想環境が有効になっているか確認してください。`pip install pytest` を実行してインストールした後、`pytest --version` でインストールを確認してください。

### 「テストファイルが認識されない」

ファイル名が `test_` で始まっているか、または `_test` で終わっているか確認してください。また、テスト関数名も `test_` で始まっている必要があります。

### 「assert が失敗したときのメッセージが読み方がわからない」

```
AssertionError: assert 1500.0 == 1500
```

左が「実際の値」、右が「期待する値」です。この例では `float(1500.0)` が返ったが `int(1500)` を期待していることがわかります。`parse_price` の戻り値の型を確認してみてください。

### 「mock って何？」

mock（モック）は「偽物のオブジェクト」です。テスト中に実際のHTTPリクエストを送ると時間がかかりますし、ネットワークの状態によってテストが失敗することがあります。mock を使うと、`requests.get` が呼ばれたときに「偽のレスポンス」を返すように差し替えられるため、ネットワーク通信なしでテストできます。

---

## 確認事項

- [ ] `loguru` でコンソールとファイルへのログ出力ができた
- [ ] `rotation` でログのローテーションを設定できた
- [ ] `pytest` でテスト関数を書けた
- [ ] `assert` でテストの期待値を書けた
- [ ] `pytest.raises` で例外発生のテストを書けた
- [ ] テストがすべて `PASSED` になった

---

**次回は「卒業制作 - 求人情報収集システム」です。これまで学んだ全スキルを1つのプロジェクトに統合して、実用的なスクレイピングシステムを設計・実装します。**
