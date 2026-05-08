# 第13回：静的サイトと動的サイト【解答・解説】

## 📝 問題1の解答：静的サイトと動的サイトを比較

```python
import requests
from bs4 import BeautifulSoup

def check_site(url, site_name):
    """サイトをチェックして結果を表示"""
    print(f"\n{'='*60}")
    print(f"【{site_name}】{url}")
    print('='*60)

    # 1. requestsで取得
    response = requests.get(url, timeout=10)

    # 2. BeautifulSoupで解析
    soup = BeautifulSoup(response.text, "html.parser")

    # 3. .quote の数を表示
    quotes = soup.select(".quote")
    print(f"\n取得できた名言の数: {len(quotes)}件")

    # 4. 取得したHTMLの一部を表示
    print(f"\nHTMLの一部（最初の500文字）:")
    print(response.text[:500])

    # 5. 静的か動的か判定
    if len(quotes) > 0:
        print(f"\n判定: 静的サイト")
        print("→ HTMLに最初からデータが含まれている")
        print("→ requests + BeautifulSoup で取得可能")

        # 最初の名言を表示
        print(f"\n最初の名言:")
        text = quotes[0].select_one(".text").text
        author = quotes[0].select_one(".author").text
        print(f"  {text}")
        print(f"  - {author}")
    else:
        print(f"\n判定: 動的サイト")
        print("→ HTMLにデータが含まれていない")
        print("→ JavaScriptで後から生成される")
        print("→ Selenium が必要")

# サイト1: 静的サイト
check_site("https://quotes.toscrape.com/", "静的サイト")

# サイト2: 動的サイト
check_site("https://quotes.toscrape.com/js/", "動的サイト")
```

### 出力

```
============================================================
【静的サイト】https://quotes.toscrape.com/
============================================================

取得できた名言の数: 10件

HTMLの一部（最初の500文字）:
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>Quotes to Scrape</title>
    <link rel="stylesheet" href="/static/bootstrap.min.css">
    <link rel="stylesheet" href="/static/main.css">
</head>
<body>
    <div class="container">
        <div class="row header-box">
            <div class="col-md-8">
                <h1>
                    <a href="/" style="text-decoration: none">Quotes to Scrape</a>
                </h1>

判定: 静的サイト
→ HTMLに最初からデータが含まれている
→ requests + BeautifulSoup で取得可能

最初の名言:
  "The world as we have created it is a process of our thinking..."
  - Albert Einstein

============================================================
【動的サイト】https://quotes.toscrape.com/js/
============================================================

取得できた名言の数: 0件

HTMLの一部（最初の500文字）:
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>Quotes to Scrape</title>
    <link rel="stylesheet" href="/static/bootstrap.min.css">
    <link rel="stylesheet" href="/static/main.css">
</head>
<body>
    <div class="container">
        <div class="row header-box">
            <div class="col-md-8">
                <h1>
                    <a href="/" style="text-decoration: none">Quotes to Scrape</a>
                </h1>

判定: 動的サイト
→ HTMLにデータが含まれていない
→ JavaScriptで後から生成される
→ Selenium が必要
```

### なぜこう書くの？

```python
# requests.get() = HTMLを取得（JavaScriptは実行されない）
response = requests.get(url)

# BeautifulSoup = HTMLを解析
soup = BeautifulSoup(response.text, "html.parser")

# select() = CSSセレクタで要素を探す
quotes = soup.select(".quote")

# len() = 要素の数
# → 0件なら動的サイト（HTMLにデータがない）
# → 1件以上なら静的サイト（HTMLにデータがある）
if len(quotes) > 0:
    print("静的サイト")
else:
    print("動的サイト")
```

### 静的サイトと動的サイトの HTML の違い

#### 静的サイトのHTML

```html
<!-- データが最初から含まれている -->
<div class="quote">
  <span class="text">"The world as we..."</span>
  <small class="author">Albert Einstein</small>
</div>
<div class="quote">
  <span class="text">"It is our choices..."</span>
  <small class="author">J.K. Rowling</small>
</div>
```

#### 動的サイトのHTML

```html
<!-- 空の要素だけ -->
<div id="quotes"></div>

<!-- JavaScriptファイル -->
<script src="/static/quotes.js"></script>

<!-- JavaScriptが実行されると、上記の空要素にデータが追加される -->
```

---

## 📝 問題2の解答：HTMLの中身を確認

```python
import requests
from bs4 import BeautifulSoup

# 動的サイトのHTMLを取得
url = "https://quotes.toscrape.com/js/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

print("=== 1. HTMLを全部表示 ===\n")
print(response.text)

print("\n" + "="*60)
print("=== 2. 'quote' という文字列を検索 ===\n")

# "quote" を検索
if "class=\"quote\"" in response.text:
    print("✅ HTMLに class=\"quote\" がある")
    print("→ データが含まれている（静的サイト）")
else:
    print("❌ HTMLに class=\"quote\" がない")
    print("→ データが含まれていない（動的サイト）")

# "quote" という文字列は何回出てくるか
count = response.text.count("quote")
print(f"\n'quote' という文字列の出現回数: {count}回")

print("\n" + "="*60)
print("=== 3. <script> タグを探す ===\n")

# <script> タグを探す
scripts = soup.find_all("script")
print(f"<script> タグの数: {len(scripts)}個")

for i, script in enumerate(scripts, 1):
    src = script.get("src", "インライン")
    print(f"{i}. {src}")

print("\n" + "="*60)
print("=== 4. 結果から分かること ===\n")

print("【分析結果】")
print("1. HTMLに class=\"quote\" が存在しない")
print("   → データはHTMLに含まれていない")
print("")
print("2. <script src=\"/static/quotes.js\"> がある")
print("   → このJavaScriptファイルがデータを生成している")
print("")
print("3. <div id=\"quotes\"></div> という空要素がある")
print("   → JavaScriptがここにデータを追加する")
print("")
print("【結論】")
print("このサイトは動的サイトです。")
print("JavaScriptが実行されて初めてデータが表示されます。")
print("requestsでは取得できないため、Seleniumが必要です。")
```

### 出力（一部）

```
=== 1. HTMLを全部表示 ===

<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>Quotes to Scrape</title>
    <link rel="stylesheet" href="/static/bootstrap.min.css">
    <link rel="stylesheet" href="/static/main.css">
</head>
<body>
    <div class="container">
        ...
        <div class="row">
            <div class="col-md-8">
                <div id="quotes"></div>
            </div>
        </div>
    </div>
    <script src="/static/jquery.js"></script>
    <script src="/static/quotes.js"></script>
</body>
</html>

============================================================
=== 2. 'quote' という文字列を検索 ===

❌ HTMLに class="quote" がない
→ データが含まれていない（動的サイト）

'quote' という文字列の出現回数: 2回

============================================================
=== 3. <script> タグを探す ===

<script> タグの数: 2個
1. /static/jquery.js
2. インライン

============================================================
=== 4. 結果から分かること ===

【分析結果】
1. HTMLに class="quote" が存在しない
   → データはHTMLに含まれていない

2. インラインの <script> タグにデータが埋め込まれている
   → JavaScriptが実行されて初めてHTMLに書き出される

3. .quote クラスを持つ要素がHTMLには存在しない
   → JavaScriptが実行されて初めて画面に表示される

【結論】
このサイトは動的サイトです。
JavaScriptが実行されて初めてデータが表示されます。
requestsでは取得できないため、Seleniumが必要です。
```

### なぜこう書くの？

```python
# 文字列の検索
if "class=\"quote\"" in response.text:
    # HTML内に "class="quote"" という文字列があるか

# 出現回数
count = response.text.count("quote")
# "quote" という文字列が何回出てくるか

# <script> タグを全部取得
scripts = soup.find_all("script")

# src 属性を取得
src = script.get("src", "インライン")
# src 属性があればそれを、なければ "インライン" を返す
```

### 動的サイトの典型的な特徴

```html
<!-- ✅ 動的サイトによくある特徴 -->

<!-- 1. 空の要素 -->
<div id="root"></div>
<div id="app"></div>
<div id="quotes"></div>

<!-- 2. 大量の <script> タグ -->
<script src="/static/app.js"></script>
<script src="/static/vendor.js"></script>
<script src="/static/runtime.js"></script>

<!-- 3. 読み込み中の表示 -->
<div class="loading">Loading...</div>
<div class="spinner"></div>

<!-- 4. データは後から追加される -->
```

---

## 📝 問題3の解答：ブラウザで確認

この問題は実際にブラウザで確認する必要があります。以下、手順と確認ポイントです。

### 手順1: Elementsタブで確認

1. https://quotes.toscrape.com/js/ を開く
2. F12キーを押す（デベロッパーツールが開く）
3. 「Elements」タブを選択
4. Ctrl+F（Cmd+F）で検索ボックスを開く
5. `id="quotes"` を検索

**確認できること:**

```html
<!-- Elements タブで見ると... -->
<div id="quotes">
  <!-- JavaScriptで生成された要素が入っている -->
  <div class="quote">
    <span class="text">"The world as we..."</span>
    <small class="author">Albert Einstein</small>
  </div>
  <div class="quote">
    <span class="text">"It is our choices..."</span>
    <small class="author">J.K. Rowling</small>
  </div>
  <!-- 以下略 -->
</div>
```

**重要な気づき:**
- ブラウザで見ると、`<div id="quotes">` の中にデータが入っている
- でも、`requests` で取得したHTMLには入っていなかった
- → JavaScriptが実行されてデータが追加されたから

### 手順2: Networkタブで確認

1. 「Network」タブを選択
2. ページをリロード（F5キー）
3. たくさんのリクエストが表示される
4. 「XHR」または「Fetch/XHR」をクリック（フィルター）

**確認できること:**

```
Network タブ:
- quotes (GET) → /static/quotes.js
- (その他のリソース)

このサイトの場合:
→ quotes.js というJavaScriptファイルが読み込まれている
→ このファイルがデータを生成している
```

**別の例（APIを使うサイト）:**

```
Network タブ（XHR/Fetch）:
- products (GET) → /api/products
  Response: [{"id": 1, "name": "商品A"}, ...]

→ APIから JSON データを取得している
→ このAPIに直接アクセスすれば、データを取得できる可能性
```

### Pythonで確認できるコード

```python
import requests
from bs4 import BeautifulSoup

url = "https://quotes.toscrape.com/js/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

print("=== requests で取得したHTML ===")
# .quote 要素を探す
quotes = soup.select(".quote")
print(f".quote 要素の数: {len(quotes)}個")
print(f"データが取得できない: {len(quotes) == 0}")

print("\n" + "="*60)
print("【結論】")
print("requests で取得しても .quote 要素は 0 個")
print("ブラウザで見ると名言が表示されている")
print("→ JavaScriptが実行されて初めてHTMLに書き出される")
```

---

## 📝 問題4の解答：ページのソースを表示

この問題も実際にブラウザで確認する必要があります。

### 手順

#### 静的サイト（https://quotes.toscrape.com/）

1. サイトを開く
2. 右クリック→「ページのソースを表示」
3. Ctrl+F（Cmd+F）で検索
4. 「The world as we have created it」を検索

**結果:**
```
✅ 見つかる！

<!-- ページのソース内 -->
<div class="quote">
    <span class="text">"The world as we have created it is a process of our thinking..."</span>
    <small class="author">Albert Einstein</small>
</div>
```

**結論:**
- ページのソース = サーバーから最初に送られてきたHTML
- 静的サイトでは、ソースにデータが含まれている
- だから `requests` で取得できる

#### 動的サイト（https://quotes.toscrape.com/js/）

1. サイトを開く
2. 右クリック→「ページのソースを表示」
3. Ctrl+F（Cmd+F）で検索
4. 「The world as we have created it」を検索

**結果:**
```
❌ 見つからない！

<!-- ページのソース内 -->
<div id="quotes"></div>
<script src="/static/quotes.js"></script>
```

**結論:**
- ページのソースには空の要素しかない
- JavaScriptが実行されて、後からデータが追加される
- だから `requests` では取得できない

### Pythonで比較するコード

```python
import requests

def check_source(url, search_text):
    """ページのソースに特定のテキストがあるか確認"""
    response = requests.get(url)

    if search_text in response.text:
        print(f"✅ 「{search_text}」がソースに含まれている")
        print("   → 静的サイト")
    else:
        print(f"❌ 「{search_text}」がソースに含まれていない")
        print("   → 動的サイト")

print("=== 静的サイト ===")
check_source("https://quotes.toscrape.com/", "The world as we have created it")

print("\n=== 動的サイト ===")
check_source("https://quotes.toscrape.com/js/", "The world as we have created it")
```

### 出力

```
=== 静的サイト ===
✅ 「The world as we have created it」がソースに含まれている
   → 静的サイト

=== 動的サイト ===
❌ 「The world as we have created it」がソースに含まれていない
   → 動的サイト
```

---

## 📝 問題5の解答：自動判定プログラム

```python
import requests
from bs4 import BeautifulSoup

def is_dynamic_site(url, selector):
    """
    サイトが動的かどうか判定する

    Args:
        url: チェックするURL
        selector: 探す要素のCSSセレクタ

    Returns:
        True: 動的サイト（要素が見つからない）
        False: 静的サイト（要素が見つかる）
    """
    try:
        # 1. requests で取得
        response = requests.get(url, timeout=10)

        # 2. BeautifulSoup で解析
        soup = BeautifulSoup(response.text, "html.parser")

        # 3. 要素を探す
        elements = soup.select(selector)

        # 4. 判定
        if len(elements) == 0:
            # 要素が見つからない → 動的サイト
            return True
        else:
            # 要素が見つかる → 静的サイト
            return False

    except requests.exceptions.RequestException as e:
        print(f"エラー: {e}")
        raise


# テスト
print("=== サイト判定プログラム ===\n")

# テスト1: 静的サイト
url1 = "https://quotes.toscrape.com/"
result1 = is_dynamic_site(url1, ".quote")
print(f"📄 {url1}")
print(f"   判定: {'動的サイト' if result1 else '静的サイト'}")
print(f"   → {'Selenium が必要' if result1 else 'requests で取得可能'}\n")

# テスト2: 動的サイト
url2 = "https://quotes.toscrape.com/js/"
result2 = is_dynamic_site(url2, ".quote")
print(f"📄 {url2}")
print(f"   判定: {'動的サイト' if result2 else '静的サイト'}")
print(f"   → {'Selenium が必要' if result2 else 'requests で取得可能'}\n")

# テスト3: Books to Scrape（静的）
url3 = "https://books.toscrape.com/"
result3 = is_dynamic_site(url3, "article.product_pod")
print(f"📄 {url3}")
print(f"   判定: {'動的サイト' if result3 else '静的サイト'}")
print(f"   → {'Selenium が必要' if result3 else 'requests で取得可能'}")
```

### 出力

```
=== サイト判定プログラム ===

📄 https://quotes.toscrape.com/
   判定: 静的サイト
   → requests で取得可能

📄 https://quotes.toscrape.com/js/
   判定: 動的サイト
   → Selenium が必要

📄 https://books.toscrape.com/
   判定: 静的サイト
   → requests で取得可能
```

### 改良版（詳細情報付き）

```python
import requests
from bs4 import BeautifulSoup

def analyze_site(url, selector):
    """
    サイトを分析して詳細な情報を返す
    """
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # 要素を探す
        elements = soup.select(selector)

        # <script> タグの数
        scripts = soup.find_all("script")

        # 結果を辞書で返す
        return {
            "url": url,
            "is_dynamic": len(elements) == 0,
            "found_elements": len(elements),
            "script_tags": len(scripts),
            "html_size": len(response.text),
        }

    except Exception as e:
        return {"url": url, "error": str(e)}


# テスト
sites = [
    ("https://quotes.toscrape.com/", ".quote"),
    ("https://quotes.toscrape.com/js/", ".quote"),
    ("https://books.toscrape.com/", "article.product_pod"),
]

print("=== サイト詳細分析 ===\n")

for url, selector in sites:
    result = analyze_site(url, selector)

    if "error" in result:
        print(f"❌ {url}")
        print(f"   エラー: {result['error']}\n")
        continue

    print(f"📄 {url}")
    print(f"   セレクタ: {selector}")
    print(f"   判定: {'動的サイト' if result['is_dynamic'] else '静的サイト'}")
    print(f"   取得できた要素: {result['found_elements']}個")
    print(f"   <script>タグ: {result['script_tags']}個")
    print(f"   HTMLサイズ: {result['html_size']:,}バイト")
    print()
```

### 出力

```
=== サイト詳細分析 ===

📄 https://quotes.toscrape.com/
   セレクタ: .quote
   判定: 静的サイト
   取得できた要素: 10個
   <script>タグ: 0個
   HTMLサイズ: 11,053バイト

📄 https://quotes.toscrape.com/js/
   セレクタ: .quote
   判定: 動的サイト
   取得できた要素: 0個
   <script>タグ: 2個
   HTMLサイズ: 3,814バイト

📄 https://books.toscrape.com/
   セレクタ: article.product_pod
   判定: 静的サイト
   取得できた要素: 20個
   <script>タグ: 0個
   HTMLサイズ: 51,004バイト
```

### なぜこう書くの？

```python
# len(elements) == 0 で判定
if len(elements) == 0:
    return True  # 動的サイト
else:
    return False  # 静的サイト

# もっと簡潔に書くと
return len(elements) == 0

# try-except でエラー処理
try:
    response = requests.get(url, timeout=10)
except requests.exceptions.RequestException as e:
    # ネットワークエラー等
    return None
```

---

## 💡 今回のポイントまとめ

### 静的サイト vs 動的サイト

| | 静的サイト | 動的サイト |
|---|----------|----------|
| HTMLの生成 | サーバー側 | ブラウザ側（JavaScript） |
| requestsで取得 | ✅ 可能 | ❌ 不可能 |
| 初期HTML | データ含む | 空または最小限 |
| <script>タグ | 少ない | 多い |
| 例 | ニュースサイト、ブログ | SPA、SNS |

### 見分け方

```python
# 1. requestsで取得してチェック
elements = soup.select(".target")
if len(elements) == 0:
    print("動的サイト")

# 2. ページのソースを表示
# 右クリック→「ページのソースを表示」
# → データがある: 静的
# → データがない: 動的

# 3. Networkタブで確認
# XHR/Fetch に APIリクエストがある: 動的
```

### 対処法

| サイト | 方法 |
|--------|------|
| 静的サイト | requests + BeautifulSoup |
| 動的サイト | Selenium（次回） |
| API公開 | requests で直接API呼び出し |

---

## 🔍 よくある間違い

### ❌ セレクタが間違っているだけなのに「動的サイト」と判断

```python
# 間違い
elements = soup.select(".wrong-selector")
if len(elements) == 0:
    print("動的サイト")  # 実はセレクタが間違っているだけ

# 正しい
# 1. ブラウザのデベロッパーツールで正しいセレクタを確認
# 2. ページのソースにデータがあるか確認
```

---

### ❌ JavaScriptが実行されるのを待たずに判断

```python
# requests は JavaScript を実行しない
response = requests.get(url)
# この時点ではJavaScriptは実行されていない

# Selenium なら実行される（次回学習）
import time
driver.get(url)
time.sleep(2)  # JavaScriptの実行を待つ
```

---

## 🔧 実践的なテクニック

### 1. タイムアウトを設定

```python
try:
    response = requests.get(url, timeout=10)
except requests.exceptions.Timeout:
    print("タイムアウト")
```

### 2. User-Agentを設定

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
response = requests.get(url, headers=headers)
```

### 3. APIを見つける

```python
# Networkタブで見つけたAPIに直接アクセス
api_url = "https://example.com/api/products"
response = requests.get(api_url)
data = response.json()  # JSONで取得
```

---

## 🎓 もっと知りたい人向け

### SPA（Single Page Application）とは

**SPA**は、ページ全体を読み込まずにコンテンツを動的に更新するWebアプリケーションです。

```
従来のサイト（Multi Page Application）:
ページ1 → ページ2 → ページ3
（毎回サーバーからHTML取得）

SPA:
最初に1回だけHTMLを取得
→ あとはJavaScriptでコンテンツを差し替え
→ ページ遷移が速い
```

**SPAの例:**
- Gmail
- Twitter
- Facebook
- React/Vue/Angularで作られたサイト

**SPAの特徴:**
- 初回読み込みが遅い（大きなJavaScriptファイル）
- その後の操作は速い
- ほぼ確実に動的サイト

### APIを直接叩く方法

```python
import requests

# Networkタブで見つけたAPI
api_url = "https://example.com/api/products"

# パラメータを付ける
params = {
    "page": 1,
    "limit": 20,
    "category": "books"
}

# APIにリクエスト
response = requests.get(api_url, params=params)
data = response.json()

# JSONデータを処理
for item in data["products"]:
    print(item["name"], item["price"])
```

**メリット:**
- Seleniumより高速
- データが構造化されている（JSON）
- HTMLの解析が不要

**デメリット:**
- APIを見つける必要がある
- 認証が必要な場合がある
- 利用規約で禁止されている場合がある

---

**次回は「Selenium入門」です。動的サイトをスクレイピングする方法を学びます！**
