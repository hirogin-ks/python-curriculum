# 第6回：HTML解析入門【解答・解説】

## 📝 問題1の解答：基本的な取得

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
h1 = soup.find("h1")
print("タイトル:", h1.text)  # ようこそ

# 2. class="intro" の p を取得して表示
intro = soup.find(class_="intro")
print("紹介文:", intro.text)  # これは紹介文です

# 3. リンクの URL を取得して表示
link = soup.find("a")
print("URL:", link["href"])  # https://example.com

# 4. すべての p タグのテキストを表示
all_p = soup.find_all("p")
print("\nすべてのp要素:")
for p in all_p:
    print("-", p.text)
# - これは紹介文です
# - これは本文です
```

### なぜこう書くの？

**`.text` = タグの中身のテキストだけを取得**

そのため h1 のテキストだけを抽出したければ、`h1.text` で「ようこそ」を取り出せます。

```python
h1.text  # <h1>ようこそ</h1> → "ようこそ"
```

**`class_` とアンダースコア**

`class` は Python の予約語なので、`class_` とアンダースコアを付ける必要があります。

```python
soup.find(class_="intro")
```

**`["属性名"]` で属性の値を取得**

リンクの href 属性を取得するには、辞書のようにアクセスします。

```python
link["href"]  # <a href="URL"> の href を取得
```

**`find_all()` でリストを返す**

`find_all()` は複数の要素をリストのように扱える ResultSet を返すので、for で1つずつ取り出して処理できます。

```python
for p in all_p:
    print(p.text)
```

---

## 📝 問題2の解答：商品情報を取り出す

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

# 各要素を取得
name = soup.find(class_="name").text
price = soup.find(class_="price").text
stock = soup.find(class_="stock").text

# 辞書にまとめる
product = {
    "name": name,
    "price": price,
    "stock": stock
}

print(product)
# {'name': 'りんご', 'price': '¥150', 'stock': '在庫あり'}
```

### なぜこう書くの？

**要素取得とテキスト取得を1行で書く**

1行で書くと短くなります。

```python
name = soup.find(class_="name").text
```

分解すると、こういう意味です：

```python
element = soup.find(class_="name")  # まず要素を取得
name = element.text                  # その要素のテキストを取得
```

**辞書を作る**

複数の値を辞書にまとめます。

```python
product = {
    "name": name,      # キー: 値
    "price": price,
    "stock": stock
}
```

### 処理の流れ（図で説明）

```
HTML:
<div class="product">
  <h2 class="name">りんご</h2>        ← これを見つける
  <span class="price">¥150</span>     ← これを見つける
  <span class="stock">在庫あり</span> ← これを見つける
</div>

↓ find(class_="name") で探す

<h2 class="name">りんご</h2>

↓ .text でテキストだけ取る

"りんご"

↓ 辞書にまとめる

{"name": "りんご", "price": "¥150", "stock": "在庫あり"}
```

---

## 📝 問題3の解答：複数の商品を処理

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

# すべての item を取得
items = soup.find_all("div", class_="item")

# 空のリストを用意
products = []

# 1つずつ処理
for item in items:
    # この item の中から h3 と price を探す
    name = item.find("h3").text
    price = item.find(class_="price").text

    # 辞書にまとめる
    product = {
        "name": name,
        "price": price
    }

    # リストに追加
    products.append(product)

print(products)
# [{'name': '商品A', 'price': '1000円'},
#  {'name': '商品B', 'price': '2000円'},
#  {'name': '商品C', 'price': '1500円'}]
```

### なぜこう書くの？（処理の流れ）

```
1. すべての class="item" を取得
   items = [item1, item2, item3]

2. 空のリストを用意
   products = []

3. for で1つずつ処理

   1周目: item = item1
          name = "商品A"
          price = "1000円"
          product = {"name": "商品A", "price": "1000円"}
          products.append(product)
          → products = [{"name": "商品A", "price": "1000円"}]

   2周目: item = item2
          name = "商品B"
          price = "2000円"
          product = {"name": "商品B", "price": "2000円"}
          products.append(product)
          → products = [{"name": "商品A", "price": "1000円"}, {"name": "商品B", "price": "2000円"}]

   3周目: item = item3
          name = "商品C"
          price = "1500円"
          product = {"name": "商品C", "price": "1500円"}
          products.append(product)
          → products = [{"name": "商品A", "price": "1000円"}, {"name": "商品B", "price": "2000円"}, {"name": "商品C", "price": "1500円"}]
```

### 重要なポイント！

```python
# ❌ 間違い: soup.find("h3") と書くと、全体から探してしまう
for item in items:
    name = soup.find("h3").text  # 常に最初の h3（商品A）になる

# ✅ 正しい: item.find("h3") と書くと、その item の中だけ探す
for item in items:
    name = item.find("h3").text  # この item の h3 を探す
```

---

## 📝 問題4の解答：リンクの一覧を取得

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

# すべての a タグを取得
links = soup.find_all("a")

# 1つずつ処理
for link in links:
    url = link["href"]
    text = link.text
    print(f"{url} - {text}")

# 出力:
# https://example.com/page1 - ページ1
# https://example.com/page2 - ページ2
# https://example.com/page3 - ページ3
```

### 短く書くと

```python
for link in soup.find_all("a"):
    print(f"{link['href']} - {link.text}")
```

### なぜこう書くの？

```python
# link["href"] = href 属性の値を取得
# <a href="URL"> の URL の部分

# link.text = タグの中身のテキスト
# <a>ページ1</a> の "ページ1" の部分

# f文字列で整形
f"{url} - {text}"  # → "https://example.com - ページ1"
```

---

## 📝 問題5の解答：階層構造の処理

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

# タイトルを取得
title = soup.find("h2").text
print("タイトル:", title)  # Python入門

# 著者名を取得
author = soup.find(class_="author").text
print("著者:", author)  # 山田太郎
```

### なぜこう書くの？

```python
# find() は階層の深さに関係なく、子孫要素をすべて検索する

# 例: この HTML で soup.find("h2") を実行すると
# <div class="article">
#   <div class="header">
#     <h2>Python入門</h2>  ← これが見つかる

# 深い階層でも見つけてくれる
soup.find(class_="author")
# <div class="article">
#   <div class="header">
#     <div class="meta">
#       <span class="author">山田太郎</span>  ← これが見つかる
```

### 段階的に探す方法（参考）

```python
# 1. まず class="article" を取得
article = soup.find(class_="article")

# 2. その中から class="header" を取得
header = article.find(class_="header")

# 3. その中から h2 を取得
title = header.find("h2").text

# でも、階層が深くなければ1行で OK
title = soup.find("h2").text
```

---

## 💡 今回のポイントまとめ

### BeautifulSoup の基本

```python
# HTML を解析
soup = BeautifulSoup(html, "html.parser")

# 1つ探す
element = soup.find("タグ名")
element = soup.find(class_="クラス名")
element = soup.find(id="ID")

# 全部探す
elements = soup.find_all("タグ名")

# テキストを取得
text = element.text

# 属性を取得
value = element["属性名"]
value = element.get("属性名")  # なくてもエラーにならない
```

### よく使うパターン

| やりたいこと | コード |
|-------------|--------|
| h1 のテキストを取得 | `soup.find("h1").text` |
| class="intro" を取得 | `soup.find(class_="intro")` |
| すべての p を取得 | `soup.find_all("p")` |
| リンクの URL を取得 | `soup.find("a")["href"]` |
| 複数の item を処理 | `for item in soup.find_all(class_="item"):` |

### データの整理

```python
# 1つの商品 → 辞書
product = {
    "name": name,
    "price": price
}

# 複数の商品 → 辞書のリスト
products = []
for item in items:
    product = {"name": item.find("h3").text, "price": item.find("span", class_="price").text}
    products.append(product)
```

---

## 🔍 よくある間違い

### ❌ class にアンダースコアを付け忘れる

```python
# 間違い
soup.find(class="intro")  # SyntaxError

# 正しい
soup.find(class_="intro")
```

**理由**: `class` は Python の予約語なので `class_` と書く

---

### ❌ find_all() の結果に .text を使う

```python
# 間違い
all_p = soup.find_all("p")
print(all_p.text)  # AttributeError

# 正しい
all_p = soup.find_all("p")
for p in all_p:
    print(p.text)
```

**理由**: `find_all()` はリストを返すので、for で回す必要がある

---

### ❌ None チェックをしない

```python
# 間違い（要素が見つからないとエラー）
element = soup.find("p")
print(element.text)  # element が None だと AttributeError

# 正しい
element = soup.find("p")
if element:
    print(element.text)
else:
    print("要素が見つかりませんでした")
```

---

### ❌ soup と item を間違える

```python
# 間違い（常に最初の要素になる）
for item in soup.find_all(class_="item"):
    name = soup.find("h3").text  # ← soup になっている

# 正しい（その item の中から探す）
for item in soup.find_all(class_="item"):
    name = item.find("h3").text  # ← item にする
```

---

## 🔧 デバッグのコツ

### HTML が正しく取得できているか確認

```python
# HTML 全体を表示
print(soup)

# または整形して表示
print(soup.prettify())
```

### 要素が見つかっているか確認

```python
element = soup.find("p")
print(element)  # None なら見つかっていない
```

### 属性の内容を確認

```python
link = soup.find("a")
print(link)  # <a href="https://example.com">詳細はこちら</a> 全体が表示される
print(link["href"])  # href 属性の値だけ
```

---

## 🎓 もっと知りたい人向け

### 検索キーワード

- `BeautifulSoup select` - CSS セレクタで探す方法
- `BeautifulSoup 子要素 取得` - 直下の要素だけを取得
- `BeautifulSoup strip` - テキストの前後の空白を削除

### 参考情報

**CSS セレクタを使う方法（上級者向け）:**

```python
# select() を使うと CSS セレクタが使える
elements = soup.select("div.item > h3")
# "div の中の class=item の直下の h3" を取得
```

CSS セレクタを知っていると、より複雑な検索ができます。

---

**次回は「HTML解析実践」です！**
