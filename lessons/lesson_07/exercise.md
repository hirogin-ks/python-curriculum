# 第7回：HTML解析実践

**目安時間：約90分**

## 今回のゴール

- CSSセレクタで要素を取得できる
- 複雑なHTML構造を解析できる
- テキストの整形ができる
- テーブルデータを辞書のリストに変換できる

---

## 導入：より効率的にデータを取り出す

前回、`find()` と `find_all()` を使ってHTML要素を取得する方法を学びました。しかし実際のWebページはより複雑な構造をしており、「特定のクラスを持つdivの中のリンク」のような複雑な条件を簡潔に記述する必要があります。

CSSセレクタを使えば、このような条件を簡潔に記述できます。また、取得したテキストには余分な空白や改行が含まれるため、データの整形方法も必要です。

この回では、より実践的なHTML解析のテクニックを学びます。

---

## ハンズオン：CSSセレクタを使ってみよう

以下のコードをファイルに保存して実行してください。

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
    <article class="post">
      <h2>記事タイトル</h2>
      <p class="content">記事の本文です。</p>
    </article>
  </main>
</div>
"""

soup = BeautifulSoup(html, "html.parser")

# CSSセレクタで要素を取得
# nav の中のすべての a タグ
links = soup.select("nav a")
print("ナビゲーションのリンク:")
for link in links:
    print("-", link.text)

# class="post" の要素
post = soup.select_one(".post")
print("\n記事タイトル:", post.select_one("h2").text)

# id="container" の要素
container = soup.select_one("#container")
print("コンテナが見つかりました:", container is not None)
```

実行すると、CSSセレクタを使って要素を取得できることが確認できます。`select()` は複数の要素を、`select_one()` は1つの要素を返します。

---

## 解説

### CSSセレクタとは

CSSセレクタは、HTML要素を指定するための記法です。もともとはCSSでスタイルを適用する対象を指定するために使われていましたが、BeautifulSoupでも同じ記法で要素を検索できます。

### select() と select_one()

| メソッド | 戻り値 | 用途 |
|---------|--------|------|
| `select()` | リスト（複数の要素） | すべてのマッチする要素を取得 |
| `select_one()` | 1つの要素（または None） | 最初にマッチした要素のみを取得 |

```python
# select() は find_all() に似ている
elements = soup.select(".post")  # リストが返る

# select_one() は find() に似ている
element = soup.select_one(".post")  # 1つの要素が返る
```

### CSSセレクタの基本

旧HTML CSS 17回で学んだように、セレクタはタグ、クラス、IDでそれぞれ異なる記法を使って指定します。BeautifulSoupではこの同じ記法で要素を検索できます。

#### 基本

**タグ名で指定**

```python
soup.select("p")  # すべての p タグ
soup.select("a")  # すべての a タグ
```

**クラス名で指定**

```python
soup.select(".intro")  # class="intro" の要素
soup.select(".post")   # class="post" の要素
```

クラス名の前には `.` を付けます。

**IDで指定**

```python
soup.select("#main")      # id="main" の要素
soup.select("#container") # id="container" の要素
```

IDの前には `#` を付けます。

#### セレクタの組み合わせ方

**タグとクラスの組み合わせ**

```python
soup.select("div.post")    # div タグで class="post"
soup.select("p.intro")     # p タグで class="intro"
```

**子孫セレクタ（スペース）**

```python
soup.select("div p")       # div の中にあるすべての p（孫も含む）
soup.select("nav a")       # nav の中にあるすべての a
```

**子セレクタ（>）**

```python
soup.select("div > p")     # div の直下の p のみ
soup.select("ul > li")     # ul の直下の li のみ
```

`>` を使うと、直接の子要素だけを取得できます。

### よく使うCSSセレクタ

| セレクタ | 意味 | 例 |
|---------|------|-----|
| `タグ名` | そのタグの要素 | `soup.select("p")` |
| `.クラス名` | そのクラスの要素 | `soup.select(".intro")` |
| `#ID` | そのIDの要素 | `soup.select("#main")` |
| `親 子孫` | 親の中の子孫要素 | `soup.select("div p")` |
| `親 > 子` | 親の直下の子要素 | `soup.select("div > p")` |
| `要素.クラス` | そのタグでそのクラス | `soup.select("div.post")` |

### find() と select() の比較

**◯ 対象となる要素をひとつ取得するとき**

| やりたいこと | find系 | select系 |
|-------------|--------|----------|
| class="intro" を取得 | `find(class_="intro")` | `select_one(".intro")` |
| p タグを取得 | `find("p")` | `select_one("p")` |
| id="main" を取得 | `find(id="main")` | `select_one("#main")` |

**◯ 該当するすべての要素を取得するとき**

| やりたいこと | find系 | select系 |
|-------------|--------|----------|
| class="intro" を取得 | `find_all(class_="intro")` | `select(".intro")` |
| p タグを取得 | `find_all("p")` | `select("p")` |
| id="main" を取得 | `find_all(id="main")` | `select("#main")` |

**◯ 入れ子構造になった要素（例：div の中の p）を取得するとき**

```python
# find系では一旦 div を用意してから find あるいは find_all する必要がある
div = soup.find("div")
ps = div.find_all("p")

# select ならこれだけでOK
soup.select("div p")
```

複雑な条件の場合、`select()` の方が簡潔に書けることが多いです。

### テキストの整形

Webページから取得したテキストには、余分な空白や改行が含まれていることがよくあります。

#### strip() で前後の空白を削除

```python
text = "  こんにちは  \n"
clean_text = text.strip()
print(clean_text)  # "こんにちは"
```

#### replace() で文字を置換

```python
text = "価格：¥1,000"
price = text.replace("価格：", "").replace("¥", "").replace(",", "")
print(price)  # "1000"
```

#### よくある整形パターン

```python
# 複数の空白を1つにまとめる
import re
text = "こんにちは    世界"
clean_text = re.sub(r"\s+", " ", text)
print(clean_text)  # "こんにちは 世界"

# 改行を削除
text = "こんにちは\n世界"
clean_text = text.replace("\n", "")
print(clean_text)  # "こんにちは世界"
```

### 【補足】`is not None` について

ハンズオンのプログラムにある `print("コンテナが見つかりました:", container is not None)` はどういう構造かというと、文章の後に `container is not None` という条件式を置いています。条件式であるため、`container` に要素があれば（`is not None`）この値は `True` となり、そうでなければ `False` となります。プログラムを実行すれば、この `True` か `False` が表示され、コンテナの有無が確認できます。

---

## 練習問題

### 問題1：CSSセレクタで取得

`python/lesson07/01_css_selector_fetch.py` に回答を書いてください。

以下のHTMLから、CSSセレクタを使って要素を取得してください。

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
# 2. すべての class="post" を取得して、タイトルを表示
# 3. id="container" の要素を取得してコンテナがあるかどうか表示
# 4. class="article" である要素を取得して要素数を表示
```

**🔑 考え方のヒント**

1. "nav の中の a" → "nav a"
2. "class=post" → ".post"
3. "id=container" → "#container"
4. "class=article" → ".article"

select() はリストを返すので for で回す（要素数は `len()` で確認できる）  
select_one() は1つだけ返す

---

### 問題2：テーブルを辞書のリストに変換

`python/lesson07/02_table_to_dict_list.py` に回答を書いてください。

以下のHTMLテーブルから、商品情報を辞書のリストとして取得してください。

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

# 以下のような辞書のリストを作成
# [
#   {"商品名": "りんご", "価格": "150円", "在庫": "あり"},
#   {"商品名": "バナナ", "価格": "100円", "在庫": "あり"},
#   {"商品名": "みかん", "価格": "200円", "在庫": "なし"}
# ]
```

**🔑 考え方のヒント**

手順:
1. th からヘッダー（キー）を取得 → ["商品名", "価格", "在庫"]
2. tbody の中の tr をすべて取得
3. 各 tr について:
   - td をすべて取得 → ["りんご", "150円", "あり"]
   - ヘッダーと値を対応させて辞書を作る
   - リストに追加

zip() を使うと便利です：
```python
keys = ["商品名", "価格", "在庫"]
values = ["りんご", "150円", "あり"]
dict(zip(keys, values))
# → {"商品名": "りんご", "価格": "150円", "在庫": "あり"}
```

**【補足】リスト内包表記について**

解答では以下のような書き方が登場します：

```python
headers = [th.text for th in soup.select("th")]
```

これは**リスト内包表記**という書き方で、通常の for ループと同じ意味です：

```python
# 通常の書き方（同じ結果）
headers = []
for th in soup.select("th"):
    headers.append(th.text)
```

---

### 問題3：テキストの整形

`python/lesson07/03_text_formatting.py` に回答を書いてください。

以下のHTMLから商品情報を取得し、テキストを整形してください。

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

# 取得して整形:
# 商品名: "りんご" （前後の空白と「商品名：」を削除）
# 価格: "150" （数字だけ）
# 説明: "新鮮なりんごです。産地：青森県" （余分な空白・改行を削除）
```

**🔑 考え方のヒント**

1. 要素を取得
2. .text でテキストを取得
3. .strip() で前後の空白を削除
4. .replace() で不要な文字を削除

例：
```python
text = "  価格：¥150  "
text = text.strip()           # "価格：¥150"
text = text.replace("価格：", "")  # "¥150"
text = text.replace("¥", "")      # "150"
```

---

### 問題4：複雑な構造の解析

`python/lesson07/04_complex_structure_parse.py` に回答を書いてください。

以下のHTMLから、各記事のタイトル、著者、日付を取得してください。

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

# 各記事について、以下の辞書を作成
# [
#   {"title": "Pythonの基礎", "author": "山田太郎", "date": "2024-01-01"},
#   {"title": "スクレイピング入門", "author": "佐藤花子", "date": "2024-01-02"}
# ]
```

**🔑 考え方のヒント**

手順:
1. すべての article.post を取得 → select(".post")
2. 空のリストを用意
3. 各 article について:
   - その中から .title を探す → article.select_one(".title")
   - その中から .author を探す
   - その中から .date を探す
   - 辞書にまとめてリストに追加

ポイント: article の中から探すときは article.select_one() を使う

---

### 問題5：属性で絞り込み

`python/lesson07/05_attribute_filtering.py` に回答を書いてください。

以下のHTMLから、外部リンク（http:// または https:// で始まるリンク）のみを取得してください。

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

# 外部リンクのみを表示
# https://example.com - 外部サイト1
# http://example.org - 外部サイト2
```

**🔑 考え方のヒント**

手順:
1. すべての a タグを取得
2. for で1つずつ処理
3. href が "http://" または "https://" で始まるか確認
   → startswith() メソッドを使う
4. 条件に合うものだけ表示

例：
```python
url = "https://example.com"
if url.startswith("http://") or url.startswith("https://"):
    print("外部リンク")
```

---

## 検索キーワード

| 知りたいこと | 検索キーワード |
|-------------|---------------|
| CSSセレクタの書き方 | `CSS セレクタ 書き方 一覧` |
| BeautifulSoup select | `BeautifulSoup select 使い方` |
| 子孫セレクタと子セレクタ | `CSS セレクタ 子孫 子 違い` |
| テキスト整形 | `Python 文字列 strip replace` |
| 正規表現で置換 | `Python re.sub 使い方` |

---

## 困ったときは

### 「`select(".post h2")` で各記事のタイトルを一気に取れない？」

実は取れます。試してみましょう。

```python
titles = soup.select(".post h2")
print(titles)
```

では、問題1の問2で使った「記事ごとにループする書き方」と何が違うのでしょうか？両方を実行して、結果を比べてみてください。どんな場合に使い分けが必要になるか考えてみましょう。

### 「select() で要素が見つからない」

CSSセレクタの記法が間違っている可能性があります。HTMLを表示して、構造を確認してください。

```python
print(soup.prettify())  # HTML全体を整形して表示
```

また、以下を確認してください：
- クラス名の前に `.` を付けているか
- IDの前に `#` を付けているか
- タグ名は小文字で書いているか

### 「select() と select_one() の使い分けがわからない」

```python
# 1つだけ取得したい → select_one()
title = soup.select_one("h1")
print(title.text)

# 複数取得したい → select()
links = soup.select("a")
for link in links:
    print(link.text)
```

`select_one()` は要素が見つからない場合 `None` を返すので、`.text` を使う前に確認してください。

### 「子孫セレクタと子セレクタの違いがわからない」

```python
# 子孫セレクタ（スペース）: すべての子孫を取得
# <div><p><span>テキスト</span></p></div>
soup.select("div span")  # span が見つかる（孫でもOK）

# 子セレクタ（>）: 直接の子だけを取得
# <div><p><span>テキスト</span></p></div>
soup.select("div > span")  # span は見つからない（孫なので）
soup.select("div > p")     # p は見つかる（直接の子）
```

### 「テキストに余分な空白や改行がある」

`strip()` と `replace()` を組み合わせて整形してください。

```python
text = element.text.strip()  # 前後の空白を削除
text = text.replace("\n", " ")  # 改行をスペースに
text = " ".join(text.split())  # 連続する空白を1つに
```

---

## 確認事項

- CSSセレクタの基本的な記法を理解した
- select() と select_one() を使い分けられる
- クラス、ID、タグを組み合わせて要素を検索できた
- テーブルデータを辞書のリストに変換できた
- テキストを整形できた
- 複雑なHTML構造を解析できた

---

**次回は「実際のWebページをスクレイピング」です。これまで学んだ技術を使って、実際のWebサイトからデータを取得します。**
