# 第8回：総合演習① - 実際のサイトからデータ収集【解答・解説】

## 📝 問題1の解答：基本的なデータ取得

```python
import requests
from bs4 import BeautifulSoup

url = "https://books.toscrape.com"
response = requests.get(url, timeout=10)
response.encoding = "utf-8"
soup = BeautifulSoup(response.text, "html.parser")

# すべての書籍カードを取得
book_cards = soup.select("article.product_pod")[:5]  # 最初の5冊

books = []

for book in book_cards:
    # タイトルを取得（h3 > a の title 属性）
    title = book.select_one("h3 a")["title"]

    # 価格を取得
    price = book.select_one(".price_color").text

    # 評価を取得（class 属性の2番目）
    rating_element = book.select_one(".star-rating")
    rating = rating_element["class"][1]  # "Three" など

    # 辞書にまとめる
    book_data = {
        "title": title,
        "price": price,
        "rating": rating
    }

    books.append(book_data)

# 結果を表示
for book in books:
    print(book)

# 出力例:
# {'title': 'A Light in the Attic', 'price': '£51.77', 'rating': 'Three'}
# {'title': 'Tipping the Velvet', 'price': '£53.74', 'rating': 'One'}
# {'title': 'Soumission', 'price': '£22.65', 'rating': 'One'}
# (以下同様)
```

### なぜこう書くの？

```python
# article.product_pod を全部取得
soup.select("article.product_pod")

# [:5] で最初の5件だけ
book_cards[:5]

# title 属性を取得
# <a title="A Light in the Attic">A Light in ...</a>
book.select_one("h3 a")["title"]

# class 属性はリストで返される
# <p class="star-rating Three">
# → ["star-rating", "Three"]
rating_element["class"]     # ['star-rating', 'Three']
rating_element["class"][1]  # 'Three'
```

### 処理の流れ

```
1. ページを取得
   requests.get(url) → HTMLテキスト

2. HTML を解析
   BeautifulSoup(html, "html.parser") → soup オブジェクト

3. 書籍カードを取得
   soup.select("article.product_pod")[:5]
   → [card1, card2, card3, card4, card5]

4. 各カードからデータを抽出
   card1:
     title:  "A Light in the Attic"
     price:  "£51.77"
     rating: "Three"
   → {"title": "A Light in the Attic", "price": "£51.77", "rating": "Three"}

5. リストに追加
   books = [book1, book2, book3, book4, book5]
```

---

## 📝 問題2の解答：データの整形

```python
import requests
from bs4 import BeautifulSoup

url = "https://books.toscrape.com"
response = requests.get(url, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")

# 評価を数値に変換するマップ
rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

book_cards = soup.select("article.product_pod")[:5]

books = []

for book in book_cards:
    # タイトル
    title = book.select_one("h3 a")["title"]

    # 価格を整形（£を削除して数値に変換）
    price_text = book.select_one(".price_color").text
    price = float(price_text.replace("£", ""))

    # 評価を取得（class 属性の2番目の値）
    rating_element = book.select_one(".star-rating")
    rating_text = rating_element["class"][1]
    
    # 評価を整形（文字列から数値に変換）
    rating = rating_map.get(rating_text, 0)

    book_data = {
        "title": title,
        "price": price,      # 数値
        "rating": rating     # 数値
    }

    books.append(book_data)

# 結果を表示
for book in books:
    print(f"{book['title']}: £{book['price']:.2f}, 評価: {book['rating']}/5")

# 出力例:
# A Light in the Attic: £51.77, 評価: 3/5
# Tipping the Velvet: £53.74, 評価: 1/5
```

### なぜこう書くの？

```python
# 文字列から数値への変換
price_text = "£51.77"
price = float(price_text.replace("£", ""))
# → 51.77 (数値)

# 辞書で変換
rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
rating_map.get("Three", 0)  # → 3
# get() を使うと、キーがなくても 0 が返る（エラーにならない）

# または
rating_map["Three"]  # → 3
# こちらはキーがないと KeyError になる
```

### 整形のステップ

```
価格の整形:
"£51.77"
  ↓ .replace("£", "")
"51.77"
  ↓ float()
51.77 (数値)

評価の整形:
"Three"
  ↓ rating_map.get()
3 (数値)
```

---

## 📝 問題3の解答：条件でフィルタリング

```python
import requests
from bs4 import BeautifulSoup

url = "https://books.toscrape.com"
response = requests.get(url, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")

rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

book_cards = soup.select("article.product_pod")

# 評価が4以上の本だけを取得
high_rated_books = []

for book in book_cards:
    title = book.select_one("h3 a")["title"]
    price_text = book.select_one(".price_color").text
    price = float(price_text.replace("£", ""))

    rating_element = book.select_one(".star-rating")
    rating_text = rating_element["class"][1]
    rating = rating_map.get(rating_text, 0)

    # 評価が4以上の場合のみ追加
    if rating >= 4:
        high_rated_books.append({
            "title": title,
            "price": price,
            "rating": rating
        })

print(f"評価4以上の書籍: {len(high_rated_books)}冊\n")

for book in high_rated_books:
    print(f"{book['title']}: 評価 {book['rating']}/5")
```

### 別の書き方（リスト内包表記）

```python
# まず全部取得
all_books = []
for book in book_cards:
    # title, price, rating を取得して辞書を作成
    all_books.append(book_data)

# フィルタリング
high_rated_books = [book for book in all_books if book["rating"] >= 4]
```

### なぜこう書くの？

```python
# if 文で条件をチェック
if rating >= 4:
    high_rated_books.append(book_data)

# リスト内包表記（上級者向け）
high_rated_books = [book for book in all_books if book["rating"] >= 4]
# 「book を all_books から取り出して、rating が 4 以上のもの」
```

---

## 📝 問題4の解答：複数ページからデータ収集

```python
import requests
from bs4 import BeautifulSoup
import time

# 書籍データを取得する関数
def get_books_from_page(url):
    """指定されたURLのページから書籍データを取得"""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    book_cards = soup.select("article.product_pod")

    books = []
    for book in book_cards:
        title = book.select_one("h3 a")["title"]
        price = float(book.select_one(".price_color").text.replace("£", ""))

        rating_element = book.select_one(".star-rating")
        rating = rating_map.get(rating_element["class"][1], 0)

        books.append({
            "title": title,
            "price": price,
            "rating": rating
        })

    return books

# メイン処理
base_url = "https://books.toscrape.com/catalogue/page-{}.html"
all_books = []

for page in range(1, 4):  # ページ 1〜3
    url = base_url.format(page)
    print(f"ページ {page} を取得中...")

    books = get_books_from_page(url)
    all_books.extend(books)

    print(f"  {len(books)}冊取得しました")

    # サーバーに負荷をかけないよう1秒待つ
    time.sleep(1)

print(f"\n合計: {len(all_books)}冊")
```

### なぜこう書くの？

```python
# 関数にまとめると再利用できる
def get_books_from_page(url):
    # ページを取得してHTMLを解析し、書籍リストを返す
    return books

# 各ページで同じ処理を呼び出す
for page in range(1, 4):
    books = get_books_from_page(url)
    all_books.extend(books)

# extend() でリストを結合
all_books = []
all_books.extend([1, 2, 3])  # → [1, 2, 3]
all_books.extend([4, 5, 6])  # → [1, 2, 3, 4, 5, 6]

# append() だとリストがネストされる
all_books.append([1, 2, 3])  # → [[1, 2, 3]]
all_books.append([4, 5, 6])  # → [[1, 2, 3], [4, 5, 6]]

# time.sleep(1) で1秒待つ（マナー）
import time
time.sleep(1)  # 1秒間停止
```

### 処理の流れ

```
ページ1:
  URL: https://books.toscrape.com/catalogue/page-1.html
  取得: 20冊
  all_books = [book1, book2, book3, ...(合計20冊)]
  1秒待つ

ページ2:
  URL: https://books.toscrape.com/catalogue/page-2.html
  取得: 20冊
  all_books = [book1〜book20, book21〜book40]
  1秒待つ

ページ3:
  URL: https://books.toscrape.com/catalogue/page-3.html
  取得: 20冊
  all_books = [book1〜book60]
  1秒待つ

合計: 60冊
```

---

## 📝 問題5の解答：CSVファイルに保存

```python
import csv

# 問題4で取得したデータを使用
books = [
    {"title": "A Light in the Attic", "price": 51.77, "rating": 3},
    {"title": "Tipping the Velvet", "price": 53.74, "rating": 1},
    {"title": "Soumission", "price": 50.10, "rating": 1},
]

# CSVファイルに保存
with open("books.csv", "w", encoding="utf-8", newline="") as f:
    # DictWriter を使う
    fieldnames = ["title", "price", "rating"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)

    # ヘッダー行を書く
    writer.writeheader()

    # データ行を書く
    writer.writerows(books)

print("books.csv に保存しました")
```

### 保存されるCSVファイル

```csv
title,price,rating
A Light in the Attic,51.77,3
Tipping the Velvet,53.74,1
Soumission,50.1,1
```

### なぜこう書くの？

```python
# DictWriter = 辞書をCSVに書き出す
# fieldnames = 列の名前（ヘッダー）
writer = csv.DictWriter(f, fieldnames=["title", "price", "rating"])

# writeheader() = ヘッダー行を書く
writer.writeheader()  # → title,price,rating

# writerows() = データ行を複数書く
writer.writerows(books)
# → A Light in the Attic,51.77,3
# → Tipping the Velvet,53.74,1

# encoding="utf-8" = 文字化け防止
# newline="" = 改行コードの問題を防ぐ
```

### Excel で開く場合

```python
# Windows の Excel で開く場合は BOM 付き UTF-8 を使う
with open("books.csv", "w", encoding="utf-8-sig", newline="") as f:
    # utf-8-sig 以外はUTF-8と同じ処理
```

---

## 💡 今回のポイントまとめ

### スクレイピングの基本フロー

```python
# 1. ページを取得
response = requests.get(url)

# 2. HTML を解析
soup = BeautifulSoup(response.text, "html.parser")

# 3. 要素を取得
elements = soup.select("セレクタ")

# 4. データを抽出
for element in elements:
    data = element.select_one("h3 a").text

# 5. データをまとめる
results.append({"key": data})
```

### データの整形

```python
# 文字列 → 数値
price = float(text.replace("£", ""))

# マップで変換
rating = rating_map.get(text, 0)

# 前後の空白を削除
text = text.strip()
```

### 複数ページの処理

```python
# ページ番号でループ
for page in range(1, 4):
    url = base_url.format(page)
    # データ取得
    time.sleep(1)  # 待機（マナー）
```

### CSV保存

```python
import csv

with open("file.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["col1", "col2"])
    writer.writeheader()
    writer.writerows(data)
```

---

## 🔍 よくある間違い

### ❌ 要素が見つからないのに属性にアクセス

```python
# 間違い
title = book.select_one("h3 a")["title"]  # None だとエラー

# 正しい
element = book.select_one("h3 a")
if element:
    title = element["title"]
else:
    title = "タイトルなし"
```

---

### ❌ class 属性の取り方を間違える

```python
# class 属性はリストで返される
# <p class="star-rating Three">

# 間違い
rating = element["class"]  # → ['star-rating', 'Three']

# 正しい
rating = element["class"][1]  # → 'Three'
```

---

### ❌ append と extend を混同する

```python
all_books = []

# append = リストをそのまま追加
all_books.append([1, 2, 3])
# → [[1, 2, 3]]

# extend = リストの要素を追加
all_books.extend([1, 2, 3])
# → [1, 2, 3]
```

---

### ❌ time.sleep() を忘れる

```python
# 間違い（サーバーに負荷）
for page in range(1, 100):
    get_page(page)  # 連続でアクセス

# 正しい
for page in range(1, 100):
    get_page(page)
    time.sleep(1)  # 1秒待つ
```

---

## 🔧 エラー対処法

### ステータスコードのチェック

```python
response = requests.get(url)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
else:
    print(f"エラー: {response.status_code}")
```

### try-except でエラー処理

```python
try:
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    # データを取得して返す処理
except requests.exceptions.Timeout:
    print("タイムアウトしました")
except requests.exceptions.RequestException as e:
    print(f"エラー: {e}")
```

### デバッグ用の表示

```python
# 取得した要素の数を確認
books = soup.select("article.product_pod")
print(f"取得した書籍数: {len(books)}")

# 最初の1件を詳しく見る
if books:
    print(books[0].prettify())
```

---

## 🎓 実践的なテクニック

### 関数化して再利用

```python
def scrape_page(url):
    """ページから書籍データを取得"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    # データを取得して books リストを構築
    return books

# 使う
books1 = scrape_page("https://books.toscrape.com/catalogue/page-1.html")
books2 = scrape_page("https://books.toscrape.com/catalogue/page-2.html")
```

### エラー時のリトライ

```python
import time

def get_with_retry(url, max_retries=3):
    """リトライ機能付きでページを取得"""
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"エラー ({i+1}/{max_retries}): {e}")
            if i < max_retries - 1:
                time.sleep(2)  # 2秒待ってリトライ
    return None
```

### 進捗状況の表示

```python
from tqdm import tqdm  # pip install tqdm

for page in tqdm(range(1, 11), desc="ページ取得中"):
    # データを取得して all_books に追加
    time.sleep(1)

# 出力:
# ページ取得中: 100%|██████████| 10/10 [00:15<00:00,  1.50s/it]
```

---

**次回は「第9回：データ整形とクリーニング」です！**
