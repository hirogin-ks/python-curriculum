# 第23回：デバッグとテスト【解答・解説】

以下の解答はあくまでも一例です。同じ動作をするコードであれば、別の書き方でも正解です。自分のコードと見比べながら、考え方の違いを確認してみてください。

---

## 📝 問題1 の解答

```python
import requests
from loguru import logger

# ファイルへのログ出力を設定（デフォルトのコンソール出力はそのまま残る）
logger.add(
    "scraping.log",
    level="INFO",
    rotation="1 MB",
    retention="7 days",
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)

urls = [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/200",
]

logger.info("スクレイピング開始")

for url in urls:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        logger.success(f"成功 ({response.status_code}): {url}")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTPエラー ({response.status_code}): {url} → {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"リクエストエラー: {url} → {e}")

logger.info("スクレイピング完了")
```

**実行結果（コンソール）:**

```
2025-01-01 12:00:00.000 | INFO     | __main__:<module>:17 - スクレイピング開始
2025-01-01 12:00:01.123 | SUCCESS  | __main__:<module>:23 - 成功 (200): https://httpbin.org/status/200
2025-01-01 12:00:02.456 | ERROR    | __main__:<module>:25 - HTTPエラー (404): https://httpbin.org/status/404
2025-01-01 12:00:03.789 | SUCCESS  | __main__:<module>:23 - 成功 (200): https://httpbin.org/status/200
2025-01-01 12:00:03.901 | INFO     | __main__:<module>:29 - スクレイピング完了
```

### なぜこう書くの？

`logger.add()` を呼び出すと、その後のすべてのログがファイルにも出力されます。`logger.add()` を呼ばなくても、コンソールへの出力は最初から有効になっています。

| 設定項目             | 意味                                                                       |
| -------------------- | -------------------------------------------------------------------------- |
| `level="INFO"`       | ファイルには INFO 以上のみ保存。DEBUG ログは保存しない                     |
| `rotation="1 MB"`    | ファイルが 1 MB を超えたら `scraping.1.log` に退避して新しいファイルに書く |
| `retention="7 days"` | 7 日以上前のファイルを自動的に削除する                                     |

---

## 📝 問題2 の解答

```python
# parser.py
from bs4 import BeautifulSoup


def parse_price(text: str) -> int | float:
    """
    価格文字列を数値に変換する。
    例: "¥1,500" → 1500 / "$29.99" → 29.99 / "1,000円" → 1000
    変換できない場合は ValueError を発生させる。
    """
    # 通貨記号・単位・カンマ・空白を除去する
    cleaned = (
        text.replace("¥", "")
            .replace("$", "")
            .replace("円", "")
            .replace(",", "")
            .strip()
    )

    if not cleaned:
        raise ValueError(f"変換できない価格文字列です: '{text}'")

    try:
        # 小数点があれば float、なければ int で返す
        return float(cleaned) if "." in cleaned else int(cleaned)
    except ValueError:
        raise ValueError(f"変換できない価格文字列です: '{text}'")


def parse_quote(html: str) -> dict | None:
    """
    quotes.toscrape.com の1件分の名言 HTML から
    {"text": "...", "author": "..."} を返す。
    取得できなければ None を返す。
    """
    soup = BeautifulSoup(html, "html.parser")
    text_tag = soup.find(class_="text")
    author_tag = soup.find(class_="author")

    if text_tag is None or author_tag is None:
        return None

    return {
        "text": text_tag.get_text(strip=True),
        "author": author_tag.get_text(strip=True),
    }
```

```python
# test_parser.py
import pytest
from parser import parse_price, parse_quote


# ── parse_price のテスト ──────────────────────────

def test_parse_price_yen():
    assert parse_price("¥1,500") == 1500

def test_parse_price_dollar():
    assert parse_price("$29.99") == 29.99

def test_parse_price_en():
    assert parse_price("1,000円") == 1000

def test_parse_price_plain():
    assert parse_price("1000") == 1000

def test_parse_price_invalid():
    with pytest.raises(ValueError):
        parse_price("")


# ── parse_quote のテスト ──────────────────────────

VALID_HTML = """
<div class="quote">
  <span class="text">&#8220;The world as we have created it...&#8221;</span>
  <span><small class="author">Albert Einstein</small></span>
</div>
"""

MISSING_HTML = """
<div>
  <p>何もない</p>
</div>
"""

def test_parse_quote_valid():
    result = parse_quote(VALID_HTML)
    assert result is not None
    assert "Einstein" in result["author"]

def test_parse_quote_author():
    result = parse_quote(VALID_HTML)
    assert result["author"] == "Albert Einstein"

def test_parse_quote_missing():
    result = parse_quote(MISSING_HTML)
    assert result is None

def test_parse_quote_empty():
    result = parse_quote("")
    assert result is None
```

### なぜこう書くの？

**`parse_price` について:**

`.replace()` をメソッドチェーンで連続して呼ぶことで、1行ずつ書くより読みやすくなります。`"." in cleaned` で小数点の有無を判定し、`float` か `int` かを分けて返すのがポイントです。

**`parse_quote` について:**

`find(class_="text")` で BeautifulSoup が該当要素を1つ返します。見つからなければ `None` が返るため、`if text_tag is None` でチェックしてから値を取り出します。

**テストについて:**

`pytest.raises(ValueError)` を使うと、`with` ブロック内で `ValueError` が発生することを確認できます。例外が発生しなかった場合はテストが `FAILED` になります。

---

## 📝 問題3 の解答

問題2のファイルが正しく作成できていれば、以下のコマンドで確認できます。

```bash
cd lessons/lesson_23
pytest test_parser.py -v
```

**期待する出力:**

```
================== test session starts ==================
platform darwin -- Python 3.12.x
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

**`FAILED` になったときの読み方:**

```
FAILED test_parser.py::test_parse_price_yen - AssertionError: assert 1500.0 == 1500
```

`assert 実際の値 == 期待する値` の形式で表示されます。上の例では `1500.0`（float）が返ったが `1500`（int）を期待しているため、`parse_price` で `int()` に変換する処理を確認してください。

---

## 📝 問題4 の解答

```python
# scraper.py
import requests
from bs4 import BeautifulSoup
from loguru import logger
from parser import parse_price


def fetch_and_parse(url: str, price_selector: str) -> int | float | None:
    """
    URL からページを取得し、CSSセレクターで価格を取り出して数値で返す。
    取得・パースに失敗したら None を返す。
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"取得失敗: {url} → {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    tag = soup.select_one(price_selector)

    if tag is None:
        logger.warning(f"セレクター '{price_selector}' が見つかりません: {url}")
        return None

    try:
        return parse_price(tag.get_text(strip=True))
    except ValueError as e:
        logger.error(f"パース失敗: {e}")
        return None
```

```python
# test_scraper.py
import requests
from unittest.mock import MagicMock, patch
from scraper import fetch_and_parse


def test_fetch_and_parse_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '<div class="price">¥1,500</div>'
    mock_response.raise_for_status = MagicMock()

    with patch("scraper.requests.get", return_value=mock_response):
        result = fetch_and_parse("https://example.com", ".price")
        assert result == 1500


def test_fetch_and_parse_missing_selector():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<div>価格要素がない</div>"
    mock_response.raise_for_status = MagicMock()

    with patch("scraper.requests.get", return_value=mock_response):
        result = fetch_and_parse("https://example.com", ".price")
        assert result is None


def test_fetch_and_parse_http_error():
    with patch("scraper.requests.get", side_effect=requests.exceptions.ConnectionError("接続エラー")):
        result = fetch_and_parse("https://example.com", ".price")
        assert result is None
```

### なぜこう書くの？

**mock について:**

`patch("scraper.requests.get", return_value=mock_response)` は「`scraper.py` の中で `requests.get` が呼ばれたとき、代わりに `mock_response` を返す」という意味です。`with` ブロックを抜けると元の `requests.get` に戻ります。

```
テスト時：scraper.py の requests.get → mock_response（偽物）
本番時  ：scraper.py の requests.get → 実際のHTTPレスポンス
```

**`side_effect` について:**

`return_value` は「この値を返す」ですが、`side_effect` は「この例外を発生させる」という意味です。接続エラーのテストに使います。

---

## 💡 今回のポイントまとめ

### loguru の設定パターン

```python
from loguru import logger

# ファイル出力を追加（コンソール出力は自動でオン）
logger.add(
    "app.log",
    level="INFO",          # ファイルに保存するレベル
    rotation="1 MB",       # ローテーションのトリガー
    retention="7 days",    # 古いファイルの保持期間
    encoding="utf-8",
)

# ログレベルの選び方
logger.debug("開発中のみ確認したい詳細情報")
logger.info("通常の進捗")
logger.success("成功したとき")
logger.warning("問題があるが続行できるとき")
logger.error("問題があり対処が必要なとき")
logger.exception("except ブロック内でスタックトレースも記録したいとき")
```

### pytest のパターン早見表

```python
# 値が等しい
assert result == 1500

# None チェック
assert result is None
assert result is not None

# 型チェック
assert isinstance(result, int)

# リスト・文字列の包含チェック
assert "python" in tags
assert "エラー" in message

# 例外が発生することを確認
with pytest.raises(ValueError):
    parse_price("")

# 例外メッセージも確認したい場合
with pytest.raises(ValueError, match="変換できない"):
    parse_price("")
```

### mock の使い方

```python
from unittest.mock import MagicMock, patch

# 関数の戻り値を差し替える
with patch("モジュール名.関数名", return_value=偽の戻り値):
    result = テスト対象の関数()

# 例外を発生させる
with patch("モジュール名.関数名", side_effect=Exception("エラー")):
    result = テスト対象の関数()
```

---

## 🔍 もっと知りたい人向け

| トピック                                           | 検索キーワード                  |
| -------------------------------------------------- | ------------------------------- |
| loguru のフォーマット詳細                          | `loguru format record`          |
| pytest のフィクスチャ（共通セットアップ）          | `pytest fixture 使い方`         |
| カバレッジ（何%のコードがテストされているか）      | `pytest-cov coverage`           |
| parameterize（同じテストを複数の値で実行）         | `pytest parametrize`            |
| responses ライブラリ（HTTP mock の専用ライブラリ） | `Python responses library mock` |

---

**次回は「総合演習⑤」です。これまでの全知識を使って完成度の高いスクレイピングシステムを構築します。**
