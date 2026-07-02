# 第6回：HTML解析入門

## 今回のゴール

- HTMLの構造がわかる
- BeautifulSoupでHTMLを解析できる
- タグ、クラス、IDで要素を取得できる
- 取得したデータを辞書やリストにまとめられる

## 所要時間：90分

---

## 6.1 導入：取得したHTMLからデータを取り出す

前回、`requests` を使ってWebページのHTMLを取得する方法を学びました。しかし、取得したHTMLは長い文字列であり、そのままでは必要なデータを取り出すことができません。

例えば、ニュースサイトから記事のタイトルと本文だけを取り出したい場合、HTMLの中から該当する部分を探し出す必要があります。これを手作業で行うのは非常に困難です。

**BeautifulSoup** というライブラリを使えば、HTMLを解析して、必要なデータを簡単に取り出すことができます。

---

## 6.2 ハンズオン：HTMLを解析してみよう

以下のコードをファイルに保存して実行してください。

```python
from bs4 import BeautifulSoup

# サンプルのHTML
html = """
<html>
  <body>
    <h1>Pythonスクレイピング入門</h1>
    <p class="intro">この記事では、スクレイピングの基礎を学びます。</p>
    <p class="content">まずはHTMLの構造を理解しましょう。</p>
    <a href="https://example.com">詳細はこちら</a>
  </body>
</html>
"""

# BeautifulSoupでHTMLを解析
soup = BeautifulSoup(html, "html.parser")

# h1タグを取得
h1 = soup.find("h1")
print("タイトル:", h1.text)

# class="intro" のpタグを取得
intro = soup.find("p", class_="intro")
print("紹介文:", intro.text)

# すべてのpタグを取得
all_p = soup.find_all("p")
print("\nすべてのp要素:")
for p in all_p:
    print("-", p.text)

# リンクのURLを取得
link = soup.find("a")
print("\nリンク:", link["href"])
```

実行すると、HTMLの中から必要な部分だけが取り出されて表示されます。これがHTML解析の基本です。

---

## 解説

### HTMLの構造

HTMLはタグ・属性・クラス・IDで構造化された言語です。スクレイピングでよく扱うタグは以下の通りです。

#### よく使うHTMLタグ

| タグ | 意味 | 用途 |
|------|------|------|
| `<h1>` 〜 `<h6>` | 見出し | ページのタイトルや章題 |
| `<p>` | 段落 | 本文のテキスト |
| `<a>` | リンク | 他のページへのリンク |
| `<div>` | ブロック | 要素をまとめる |
| `<span>` | インライン | 文中の一部を囲む |
| `<ul>`, `<li>` | リスト | 箇条書き |

### BeautifulSoupの基本

BeautifulSoupは、HTMLやXMLを解析するためのPythonライブラリです。HTMLを解析して、タグやクラスの情報を一気に取得することができます。

#### 基本的な使い方

BeautifulSoupは `bs4` モジュールからインポートして使うクラスです。HTMLを渡すと、タグを検索・操作できる `soup` オブジェクトが得られます。

```python
from bs4 import BeautifulSoup

# HTMLを解析
soup = BeautifulSoup(html文字列, "html.parser")
```

`"html.parser"` は、Pythonに標準で含まれているHTMLパーサーを使うという指定です。

#### 要素を取得する方法

HTML、CSSでやったタグとかクラスの内容を一気に取得することができます。得られた `soup` オブジェクトから、タグ・クラス・IDなどを使ってさまざまな方法で情報を取得できます。まずは `find()` と `find_all()` の基本的な使い分けを理解しましょう。

#### find() と find_all() の違い

| メソッド | 戻り値 | 用途 |
|---------|--------|------|
| `find()` | 最初の1つの要素 | 特定の要素を1つだけ取得したいとき |
| `find_all()` | すべての要素（リスト） | 複数の要素をまとめて取得したいとき |

```python
# find() は1つだけ
p = soup.find("p")
print(type(p))  # <class 'bs4.element.Tag'>

# find_all() はリスト
all_p = soup.find_all("p")
print(type(all_p))  # <class 'bs4.element.ResultSet'>
```

#### 1. タグ名で検索

```python
# 最初に見つかった h1 を取得
h1 = soup.find("h1")
print(h1.text)  # タグの中身のテキスト

# すべての p を取得
all_p = soup.find_all("p")
for p in all_p:
    print(p.text)
```

#### 2. クラスで検索

```python
# class="intro" の要素を取得
intro = soup.find(class_="intro")

# 注意: class_ とアンダースコアを付ける
# （class は Python の予約語なため）

# すべての class="product" を取得
products = soup.find_all(class_="product")
```

#### 3. IDで検索

```python
# id="main-title" の要素を取得
title = soup.find(id="main-title")
```

#### 4. タグとクラスを組み合わせる

```python
# p タグで class="intro" の要素を取得
intro = soup.find("p", class_="intro")
```

### テキストと属性を取得する

要素を取得したら、その中身のテキストや属性を抽出します。

#### テキストを取得

`.text` を使うと、タグの中身のテキストだけを取得できます。

```python
element = soup.find("p")
print(element.text)  # タグの中身のテキスト
```

#### 属性を取得

リンクを取得するにはこのようにします。属性を取得するには2つの方法があります。

```python
link = soup.find("a")

# 方法1: 辞書のようにアクセス
url = link["href"]

# 方法2: get() を使う（属性がなくてもエラーにならない）
url = link.get("href")
```

`get()` を使うと、属性が存在しない場合に `None` が返されるため、エラーを防げます。

---

## 練習問題

### 6.3 問題1：基本的な取得

以下のHTMLから、指定された要素を取得してください。

```python
from bs4 import BeautifulSoup

html = """
<html>
  <h1>ようこそ</h1>
  <p class="intro">これは紹介文です</p>
  <p class="content">これは本文です</p>
  <a href="https://example.com">リンク</a>
</html>
"""

soup = BeautifulSoup(html, "html.parser")

# 1. h1 のテキストを取得して表示
# 2. class="intro" の p を取得して表示
# 3. リンクの URL を取得して表示
# 4. すべての p タグのテキストを表示
```

**考え方のヒント:**

```python
1. soup.find("h1") で h1 を取得 → .text でテキスト
2. soup.find(class_="intro") でクラス指定
3. soup.find("a") でリンクを取得 → ["href"] で URL
4. soup.find_all("p") ですべての p を取得 → for で回す
```

---

### 6.4 問題2：商品情報を取り出す

以下のHTMLから、商品情報を辞書形式で取り出してください。

```python
from bs4 import BeautifulSoup

html = """
<div class="product">
  <h2 class="name">りんご</h2>
  <span class="price">¥150</span>
  <span class="stock">在庫あり</span>
</div>
"""

soup = BeautifulSoup(html, "html.parser")

# 辞書形式で取り出す
# {"name": "りんご", "price": "¥150", "stock": "在庫あり"}
```

**考え方のヒント:**

```python
手順:
1. soup を作成
2. class="name" の要素を探す → .text で名前を取得
3. class="price" の要素を探す → .text で価格を取得
4. class="stock" の要素を探す → .text で在庫を取得
5. 辞書にまとめる

辞書の作り方:
product = {
    "name": name,
    "price": price,
    "stock": stock
}
```

---

### 6.5 問題3：複数の商品を処理

以下のHTMLから、すべての商品を辞書のリストにしてください。

```python
from bs4 import BeautifulSoup

html = """
<div class="products">
  <div class="item">
    <h3>商品A</h3>
    <p class="price">1000円</p>
  </div>
  <div class="item">
    <h3>商品B</h3>
    <p class="price">2000円</p>
  </div>
  <div class="item">
    <h3>商品C</h3>
    <p class="price">1500円</p>
  </div>
</div>
"""

soup = BeautifulSoup(html, "html.parser")

# すべての商品を辞書のリストにする
# 期待される結果:
# [{"name": "商品A", "price": "1000円"}, {"name": "商品B", "price": "2000円"}]
```

**考え方のヒント:**

```python
手順:
1. class="item" をすべて取得 → find_all("div", class_="item")
2. 空のリストを用意 → products = []
3. for で item を1つずつ処理
   - その item の中から h3 を探す → item.find("h3")
   - その item の中から class="price" を探す → item.find(class_="price")
   - 辞書にまとめる
   - リストに追加 → products.append(辞書)
4. リストを表示

重要: item の中から探すときは soup ではなく item を使う
```

---

### 6.6 問題4：リンクの一覧を取得

以下のHTMLから、すべてのリンクのURLとテキストを取得してください。

```python
from bs4 import BeautifulSoup

html = """
<html>
  <body>
    <a href="https://example.com/page1">ページ1</a>
    <a href="https://example.com/page2">ページ2</a>
    <a href="https://example.com/page3">ページ3</a>
  </body>
</html>
"""

soup = BeautifulSoup(html, "html.parser")

# すべてのリンクについて、URLとテキストを表示
# 例: https://example.com/page1 - ページ1
```

**考え方のヒント:**

```python
1. すべての a タグを取得 → soup.find_all("a")
2. for で1つずつ処理
   - link["href"] で URL
   - link.text でテキスト
   - f文字列で表示
```

---

### 6.7 問題5：階層構造の処理

以下のHTMLから、記事のタイトルと著者名を取得してください。

```python
from bs4 import BeautifulSoup

html = """
<div class="article">
  <div class="header">
    <h2>Python入門</h2>
    <div class="meta">
      <span class="author">山田太郎</span>
      <span class="date">2024-01-01</span>
    </div>
  </div>
  <div class="body">
    <p>このコースではHTMLの基本を学びます。</p>
  </div>
</div>
"""

soup = BeautifulSoup(html, "html.parser")

# タイトルと著者名を取得
# タイトル: Python入門
# 著者: 山田太郎
```

**考え方のヒント:**

```python
1. class="article" の div を取得
2. その中から h2 を探す
3. その中から class="author" を探す

ポイント: 階層が深い場合でも、find() は子孫要素をすべて検索する
```

---

## 検索キーワード

| 知りたいこと | 検索キーワード |
|-------------|---------------|
| BeautifulSoupの基本 | `BeautifulSoup 使い方 Python` |
| クラスで要素を探す | `BeautifulSoup class 取得` |
| 属性を取得する | `BeautifulSoup href 取得` |
| find と find_all の違い | `BeautifulSoup find find_all 違い` |
| テキストを取得する | `BeautifulSoup text 取得` |

---

## 困ったときは

### 「None が返ってくる」

`find()` で要素が見つからない場合、`None` が返されます。タグ名やクラス名が間違っていないか確認してください。

```python
# デバッグ方法
print(soup)  # HTML全体を表示して、タグを確認
```

### 「AttributeError: 'NoneType' object has no attribute 'text'」

`find()` が `None` を返しているのに、`.text` を取得しようとしています。

```python
# エラーになる例
element = soup.find("p")
print(element.text)  # element が None だとエラー

# 正しい書き方
element = soup.find("p")
if element:
    print(element.text)
else:
    print("要素が見つかりませんでした")
```

### 「class_ とアンダースコアを付け忘れた」

```python
# 誤り
soup.find(class="intro")  # SyntaxError

# 正しい
soup.find(class_="intro")
```

`class` は Python の予約語なので、`class_` とアンダースコアを付ける必要があります。

### 「リストの中身を1つずつ取り出せない」

`find_all()` はリストを返すので、for でループする必要があります。

```python
# 誤り
all_p = soup.find_all("p")
print(all_p.text)  # エラー

# 正しい
all_p = soup.find_all("p")
for p in all_p:
    print(p.text)
```

---

## 確認事項

- BeautifulSoupでHTMLを解析できた
- find() で要素を1つ取得できた
- find_all() で複数の要素を取得できた
- タグ名、クラス、IDで要素を検索できた
- テキストと属性を取り出せた
- 複数の要素をforループで処理できた

---

**次回は「HTML解析実践」です。実際のWebページからデータを取得する方法を学びます。**
