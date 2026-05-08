# 第7回：HTML解析実践【解答・解説】

## 📝 問題1の解答：CSSセレクタで取得

```python
from bs4 import BeautifulSoup

html = """
<div id="container">
  <nav class="menu">
    <a href="/">ホーム</a>
    <a href="/about">会社概要</a>
    <a href="/contact">お問い合わせ</a>
  </nav>
  <main>
    <article class="post article">
      <h2>記事1</h2>
      <p class="content">内容1</p>
    </article>
    <article class="post article">
      <h2>記事2</h2>
      <p class="content">内容2</p>
    </article>
  </main>
</div>
"""

soup = BeautifulSoup(html, "html.parser")

# 1. nav の中のすべてのリンクを取得して表示
links = soup.select("nav a")
print("ナビゲーションのリンク:")
for link in links:
    print(f"- {link.text}: {link['href']}")

# 出力:
# - ホーム: /
# - 会社概要: /about
# - お問い合わせ: /contact

# 2. すべての class="post" を取得して、タイトルを表示
posts = soup.select(".post")
print("\n記事タイトル:")
for post in posts:
    title = post.select_one("h2").text
    print(f"- {title}")

# 出力:
# - 記事1
# - 記事2

# 3. id="container" の要素を取得
container = soup.select_one("#container")
print(f"\nコンテナが見つかりました: {container is not None}")
# 出力: True

# 4. class="article" である要素を取得して要素数を表示
articles = soup.select(".article")
print(f"\n記事の数: {len(articles)}個")
# 出力: 2個
```

### なぜこう書くの？

```python
# CSSセレクタの基本
"nav a"      # nav の中の a（子孫セレクタ）
".post"      # class="post" （クラスは . を付ける）
"#container" # id="container" （IDは # を付ける）
".article"       # class="article" （クラスは . を付ける）

# select() はリストを返す
links = soup.select("nav a")  # リスト
for link in links:
    print(link.text)

# select_one() は1つだけ返す
container = soup.select_one("#container")  # 1つの要素
print(container is not None)
```

### CSSセレクタの記法まとめ

| セレクタ | 意味 | 例 |
|---------|------|-----|
| `タグ` | そのタグ | `soup.select("p")` |
| `.クラス` | class属性 | `soup.select(".post")` |
| `#ID` | id属性 | `soup.select("#main")` |
| `親 子孫` | 子孫要素 | `soup.select("div p")` |
| `親 > 子` | 直接の子 | `soup.select("div > p")` |

---

## 📝 問題2の解答：テーブルを辞書のリストに変換

```python
from bs4 import BeautifulSoup

html = """
<table>
  <thead>
    <tr>
      <th>商品名</th>
      <th>価格</th>
      <th>在庫</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>りんご</td>
      <td>150円</td>
      <td>あり</td>
    </tr>
    <tr>
      <td>バナナ</td>
      <td>100円</td>
      <td>あり</td>
    </tr>
    <tr>
      <td>みかん</td>
      <td>200円</td>
      <td>なし</td>
    </tr>
  </tbody>
</table>
"""

soup = BeautifulSoup(html, "html.parser")

# 1. ヘッダー（キー）を取得
headers = [th.text for th in soup.select("th")]
# ['商品名', '価格', '在庫']

# 2. データ行を処理
products = []
rows = soup.select("tbody tr")

for row in rows:
    # この行の td をすべて取得
    cells = [td.text for td in row.select("td")]

    # ヘッダーと値を対応させて辞書を作る
    product = dict(zip(headers, cells))
    products.append(product)

print(products)

# 出力:
# [
#   {'商品名': 'りんご', '価格': '150円', '在庫': 'あり'},
#   {'商品名': 'バナナ', '価格': '100円', '在庫': 'あり'},
#   {'商品名': 'みかん', '価格': '200円', '在庫': 'なし'}
# ]
```

### なぜこう書くの？

```python
# リスト内包表記で th のテキストを取得
headers = [th.text for th in soup.select("th")]
# ↓ 通常の書き方
headers = []
for th in soup.select("th"):
    headers.append(th.text)

# zip() でリストを組み合わせる
keys = ["商品名", "価格", "在庫"]
values = ["りんご", "150円", "あり"]
dict(zip(keys, values))
# → {'商品名': 'りんご', '価格': '150円', '在庫': 'あり'}
```

### 処理の流れ（図で説明）

```
1. ヘッダーを取得
   <th>商品名</th><th>価格</th><th>在庫</th>
   ↓
   headers = ['商品名', '価格', '在庫']

2. 各行を処理
   1周目:
   <tr>
     <td>りんご</td><td>150円</td><td>あり</td>
   </tr>
   ↓
   cells = ['りんご', '150円', 'あり']
   ↓
   zip(['商品名', '価格', '在庫'], ['りんご', '150円', 'あり'])
   ↓
   {'商品名': 'りんご', '価格': '150円', '在庫': 'あり'}
   ↓
   products.append({'商品名': 'りんご', '価格': '150円', '在庫': 'あり'})

3. 最終結果
   products = [
     {'商品名': 'りんご', '価格': '150円', '在庫': 'あり'},
     {'商品名': 'バナナ', '価格': '100円', '在庫': 'あり'},
     {'商品名': 'みかん', '価格': '200円', '在庫': 'なし'}
   ]
```

---

## 📝 問題3の解答：テキストの整形

```python
from bs4 import BeautifulSoup

html = """
<div class="product">
  <h3>  商品名：りんご  </h3>
  <p class="price">  価格：¥150  </p>
  <p class="desc">
    新鮮なりんごです。
    産地：青森県
  </p>
</div>
"""

soup = BeautifulSoup(html, "html.parser")

# 商品名を取得して整形
name_text = soup.select_one("h3").text
name = name_text.strip().replace("商品名：", "")
print(f"商品名: {name}")  # りんご

# 価格を取得して整形
price_text = soup.select_one(".price").text
price = price_text.strip().replace("価格：", "").replace("¥", "")
print(f"価格: {price}")  # 150

# 説明を取得して整形
desc_text = soup.select_one(".desc").text
# 空白や改行を除去して1つの文字列にまとめる
desc = "".join(desc_text.split())
print(f"説明: {desc}")  # 新鮮なりんごです。産地：青森県
```

### なぜこう書くの？

```python
# .strip() = 前後の空白・改行を削除
text = "  こんにちは  \n"
text.strip()  # → "こんにちは"

# .replace() = 文字列を置換
text = "価格：¥150"
text.replace("価格：", "")  # → "¥150"
text.replace("¥", "")       # → "150"

# .split() と .join() で連続する空白を整理
text = "こんにちは    世界"
text.split()       # → ['こんにちは', '世界']
" ".join(text.split())      # → "こんにちは 世界"
```

### 整形のステップ（図で説明）

```
元のテキスト: "  商品名：りんご  "
     ↓ .strip()
"商品名：りんご"
     ↓ .replace("商品名：", "")
"りんご"

元のテキスト: "  価格：¥150  "
     ↓ .strip()
"価格：¥150"
     ↓ .replace("価格：", "")
"¥150"
     ↓ .replace("¥", "")
"150"

元のテキスト: "\n    新鮮なりんごです。\n    産地：青森県\n  "
     ↓ .split()
['新鮮なりんごです。', '産地：青森県']
     ↓ " ".join(text.split())
"新鮮なりんごです。 産地：青森県"
```

---

## 📝 問題4の解答：複雑な構造の解析

```python
from bs4 import BeautifulSoup

html = """
<div class="articles">
  <article class="post">
    <header>
      <h2 class="title">Pythonの基礎</h2>
      <div class="meta">
        <span class="author">山田太郎</span>
        <span class="date">2024-01-01</span>
      </div>
    </header>
    <p class="summary">Pythonの基礎を学びます。</p>
  </article>
  <article class="post">
    <header>
      <h2 class="title">スクレイピング入門</h2>
      <div class="meta">
        <span class="author">佐藤花子</span>
        <span class="date">2024-01-02</span>
      </div>
    </header>
    <p class="summary">スクレイピングの基礎を学びます。</p>
  </article>
</div>
"""

soup = BeautifulSoup(html, "html.parser")

# すべての記事を取得
posts = soup.select(".post")

articles = []
for post in posts:
    # この post の中から各要素を取得
    title = post.select_one(".title").text
    author = post.select_one(".author").text
    date = post.select_one(".date").text

    article = {
        "title": title,
        "author": author,
        "date": date
    }
    articles.append(article)

print(articles)

# 出力:
# [
#   {'title': 'Pythonの基礎', 'author': '山田太郎', 'date': '2024-01-01'},
#   {'title': 'スクレイピング入門', 'author': '佐藤花子', 'date': '2024-01-02'}
# ]
```

### なぜこう書くの？

```python
# ❌ 間違い: soup.select_one() を使うと常に最初の記事を取得
for post in posts:
    title = soup.select_one(".title").text  # 常に最初の記事

# ✅ 正しい: post.select_one() を使う
for post in posts:
    title = post.select_one(".title").text  # この post の title
```

### 処理の流れ

```
1. すべての .post を取得
   posts = [post1, post2]

2. 各 post を処理

   1周目: post = post1
   <article class="post">
     <h2 class="title">Pythonの基礎</h2>
     <span class="author">山田太郎</span>
     <span class="date">2024-01-01</span>
   </article>

   post.select_one(".title").text   → "Pythonの基礎"
   post.select_one(".author").text  → "山田太郎"
   post.select_one(".date").text    → "2024-01-01"

   → {"title": "Pythonの基礎", "author": "山田太郎", "date": "2024-01-01"}

   2周目: post = post2
   （同様に処理）
```

---

## 📝 問題5の解答：属性で絞り込み

```python
from bs4 import BeautifulSoup

html = """
<nav>
  <a href="/">ホーム</a>
  <a href="/about">会社概要</a>
  <a href="https://example.com">外部サイト1</a>
  <a href="http://example.org">外部サイト2</a>
  <a href="/contact">お問い合わせ</a>
</nav>
"""

soup = BeautifulSoup(html, "html.parser")

# すべての a タグを取得
links = soup.select("a")

print("外部リンク:")
for link in links:
    href = link.get("href")

    # http:// または https:// で始まるリンクのみ
    if href and (href.startswith("http://") or href.startswith("https://")):
        print(f"{href} - {link.text}")

# 出力:
# https://example.com - 外部サイト1
# http://example.org - 外部サイト2
```

### 別の書き方（より簡潔）

```python
for link in soup.select("a"):
    href = link.get("href", "")
    if href.startswith(("http://", "https://")):
        print(f"{href} - {link.text}")
```

### なぜこう書くの？

```python
# .startswith() = 文字列が指定の文字で始まるか確認
url = "https://example.com"
url.startswith("https://")  # → True
url.startswith("http://")   # → False

# タプルを渡すと、どれか1つに該当すれば True
url.startswith(("http://", "https://"))  # → True

# .get() は属性がなくても None を返す（エラーにならない）
link.get("href")  # href がなければ None
link["href"]      # href がなければエラー
```

### 条件分岐の図解

```
リンク一覧:
1. href="/" → "/" で始まる？ → No → スキップ
2. href="/about" → "/" で始まる？ → No → スキップ
3. href="https://example.com" → "http://" or "https://" で始まる？ → Yes → 表示
4. href="http://example.org" → "http://" or "https://" で始まる？ → Yes → 表示
5. href="/contact" → "/" で始まる？ → No → スキップ

結果:
https://example.com - 外部サイト1
http://example.org - 外部サイト2
```

---

## 💡 今回のポイントまとめ

### CSSセレクタの基本

```python
# タグ
soup.select("p")

# クラス（. を付ける）
soup.select(".intro")

# ID（# を付ける）
soup.select("#main")

# 組み合わせ
soup.select("div.post")       # div で class="post"
soup.select("nav a")          # nav の中の a
soup.select("main > article") # main の直下の article
```

### select() と select_one() の使い分け

| 用途 | メソッド | 戻り値 |
|------|---------|--------|
| 複数取得 | `select()` | リスト |
| 1つだけ取得 | `select_one()` | 要素または None |

### テキストの整形

```python
# 前後の空白を削除
text.strip()

# 文字列を置換
text.replace("古い", "新しい")

# 連続する空白を1つに
" ".join(text.split())
```

### テーブルの処理

```python
# ヘッダーを取得
headers = [th.text for th in soup.select("th")]

# 各行を辞書に
for row in soup.select("tbody tr"):
    cells = [td.text for td in row.select("td")]
    data = dict(zip(headers, cells))
```

---

## 🔍 よくある間違い

### ❌ クラスやIDの記号を忘れる

```python
# 間違い
soup.select("post")      # タグ名として扱われる
soup.select("main")      # id ではなくタグ名

# 正しい
soup.select(".post")     # class="post"
soup.select("#main")     # id="main"
```

---

### ❌ select() の結果に直接 .text を使う

```python
# 間違い
posts = soup.select(".post")
print(posts.text)  # AttributeError

# 正しい
posts = soup.select(".post")
for post in posts:
    print(post.text)
```

**理由**: `select()` はリストを返すので、for で回す必要がある

---

### ❌ soup と要素を混同する

```python
# 間違い（常に最初の要素になる）
for post in soup.select(".post"):
    title = soup.select_one("h2").text

# 正しい（その post の中から探す）
for post in soup.select(".post"):
    title = post.select_one("h2").text
```

---

### ❌ 子セレクタと子孫セレクタを混同する

```python
# 子孫セレクタ（スペース）= すべての子孫
soup.select("div p")  # div の中のすべての p

# 子セレクタ（>）= 直接の子のみ
soup.select("div > p")  # div の直下の p のみ

# 例:
# <div>
#   <p>これは見つかる</p>
#   <section>
#     <p>これも見つかる（div p）、見つからない（div > p）</p>
#   </section>
# </div>
```

---

## 🔧 デバッグのコツ

### CSSセレクタが正しいか確認

```python
# 何が取れたか確認
elements = soup.select(".post")
print(f"取得した要素の数: {len(elements)}")
print(elements[0] if elements else "見つかりませんでした")
```

### HTMLの構造を確認

```python
# 整形して表示
print(soup.prettify())
```

### 段階的に絞り込む

```python
# いきなり複雑なセレクタを書かず、段階的に
# 1. まず全体を取得
posts = soup.select(".post")
print(f"記事数: {len(posts)}")

# 2. その中から探す
for post in posts:
    title = post.select_one(".title")
    print(f"タイトル: {title.text if title else 'なし'}")
```

---

## 🎓 もっと知りたい人向け

### CSSセレクタの詳細

```python
# 複数のクラスを持つ要素
soup.select(".class1.class2")  # class="class1 class2"

# 属性で絞り込み
soup.select("a[target='_blank']")  # target="_blank" の a

# n番目の要素
soup.select("li:nth-child(2)")  # 2番目の li
```

### より高度な検索

```python
# 正規表現で検索
import re
soup.find_all("a", href=re.compile(r"^https://"))

# lambda で絞り込み
soup.find_all(lambda tag: tag.name == "p" and len(tag.text) > 10)
```

---

**次回は「実際のWebページをスクレイピング」です！**
