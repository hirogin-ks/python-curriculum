# 第10回：データの保存 - CSV・JSON・pandas【解答・解説】

## 📝 問題1の解答：基本的なCSV保存

> 第8回でチャレンジ問題として紹介したCSV保存を、ここで改めて基礎から丁寧に学びます。第8回ですでに解けた方はスキップしてOKです！

```python
import csv

books = [
    {"title": "Python入門", "author": "田中太郎", "price": 2800},
    {"title": "データ分析", "author": "佐藤花子", "price": 3200},
    {"title": "機械学習", "author": "鈴木一郎", "price": 3500},
]

# CSVファイルに保存
with open("books.csv", "w", newline="", encoding="utf-8") as f:
    # DictWriter を作成
    fieldnames = ["title", "author", "price"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)

    # ヘッダー行を書く
    writer.writeheader()

    # データ行を書く
    writer.writerows(books)

print("books.csv に保存しました")

# 確認のため読み込んで表示
with open("books.csv", "r", encoding="utf-8") as f:
    print(f.read())
```

### 出力（books.csv）

```csv
title,author,price
Python入門,田中太郎,2800
データ分析,佐藤花子,3200
機械学習,鈴木一郎,3500
```

### なぜこう書くの？

```python
import csv

books = [
    {"title": "Python入門", "author": "田中太郎", "price": 2800},
    {"title": "データ分析", "author": "佐藤花子", "price": 3200},
]

# with open() = ファイルを開く・自動で閉じる
with open("books.csv", "w", newline="", encoding="utf-8") as f:
    # "w" = 書き込みモード
    # newline="" = CSV特有の設定（改行コードの問題を防ぐ）
    # encoding="utf-8" = 日本語を正しく保存

    # csv.DictWriter = 辞書のリストを書き込める
    fieldnames = ["title", "author", "price"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    # fieldnames = 列の順番を指定

    # writeheader() = ヘッダー行を書く
    writer.writeheader()  # → title,author,price

    # writerows() = データ行を一括で書く
    writer.writerows(books)
    # → Python入門,田中太郎,2800
    # → データ分析,佐藤花子,3200
    # → ...
```

### csv.writer と csv.DictWriter の違い

```python
import csv

# csv.writer（リストのリスト）
data = [
    ["title", "author", "price"],  # ヘッダーを自分で書く
    ["Python入門", "田中太郎", 2800],
    ["データ分析", "佐藤花子", 3200],
]

with open("books.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(data)

# csv.DictWriter（辞書のリスト）
data = [
    {"title": "Python入門", "author": "田中太郎", "price": 2800},
    {"title": "データ分析", "author": "佐藤花子", "price": 3200},
]

with open("books.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "author", "price"])
    writer.writeheader()  # ヘッダーを自動で書ける
    writer.writerows(data)
```

**DictWriter のメリット:**
- 辞書をそのまま書き込める
- スクレイピングで取得したデータと相性が良い
- 列の順番を fieldnames で制御できる

### 処理の流れ

```
1. ファイルを開く
   open("books.csv", "w", ...)
   ↓
2. DictWriter を作成
   writer = csv.DictWriter(f, fieldnames=[...])
   ↓
3. ヘッダー行を書く
   writer.writeheader()
   → title,author,price
   ↓
4. データ行を書く
   writer.writerows(books)
   → Python入門,田中太郎,2800
   → データ分析,佐藤花子,3200
   → 機械学習,鈴木一郎,3500
   ↓
5. ファイルを閉じる（自動）
```

---

## 📝 問題2の解答：CSVを読み込んで分析

### 方法1: csv モジュールで読み込む

```python
import csv

with open("books.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    books = list(reader)

# 価格を数値に変換
prices = [int(book["price"]) for book in books]

# 1. 平均価格
average_price = sum(prices) / len(prices)
print(f"平均価格: {average_price:.0f}円")  # 3167円

# 2. 最高価格の本
max_price = max(prices)
max_book = [book for book in books if int(book["price"]) == max_price][0]
print(f"最高価格: {max_book['title']} - {max_price}円")

# 3. 最安価格の本
min_price = min(prices)
min_book = [book for book in books if int(book["price"]) == min_price][0]
print(f"最安価格: {min_book['title']} - {min_price}円")
```

### なぜこう書くの？

```python
# book for book in books = books の各要素をループ
# if int(book["price"]) == max_price = 価格が最高価格と同じ本を選ぶ
max_book = [book for book in books if int(book["price"]) == max_price]
# リスト内包表記を使って条件に合う本をリストで取得

# [0] = リストの最初の要素を取得
max_book = [book for book in books if int(book["price"]) == max_price][0]
```

### 方法2: pandas を使う（推奨）

```python
import pandas as pd

# CSVを読み込む
df = pd.read_csv("books.csv")

# 1. 平均価格
average_price = df["price"].mean()
print(f"平均価格: {average_price:.0f}円")  # 3167円

# 2. 最高価格の本
max_book = df[df["price"] == df["price"].max()]
print(f"最高価格: {max_book['title'].values[0]} - {max_book['price'].values[0]}円")

# 3. 最安価格の本
min_book = df[df["price"] == df["price"].min()]
print(f"最安価格: {min_book['title'].values[0]} - {min_book['price'].values[0]}円")

# または、より簡潔に
print("\n統計情報:")
print(df.describe())

print("\n最高価格の本:")
print(df.loc[df["price"].idxmax()])

print("\n最安価格の本:")
print(df.loc[df["price"].idxmin()])
```

### 出力

```
平均価格: 3167円
最高価格: 機械学習 - 3500円
最安価格: Python入門 - 2800円

統計情報:
           price
count     3.000000
mean   3166.666667
std     360.555128
min    2800.000000
25%    3000.000000
50%    3200.000000
75%    3350.000000
max    3500.000000

最高価格の本:
title       機械学習
author    鈴木一郎
price      3500
Name: 2, dtype: object

最安価格の本:
title       Python入門
author      田中太郎
price        2800
Name: 0, dtype: object
```

### なぜこう書くの？

```python
# csv.DictReader で読み込むと...
with open("books.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    # ヘッダー行を自動で認識
    # 各行を辞書として読み込む

    for row in reader:
        print(row)
        # {'title': 'Python入門', 'author': '田中太郎', 'price': '2800'}
        # 注意: すべて文字列！

# pandas で読み込むと...
df = pd.read_csv("books.csv")
# 自動で型を推測（price は数値として読み込まれる）
# すぐに分析できる

# 平均を計算
df["price"].mean()  # pandas なら1行

# 条件で絞り込み
df[df["price"] == df["price"].max()]  # 最大値の行
```

### pandas の基本的なメソッド

| メソッド | 意味 | 例 |
|---------|------|-----|
| `.mean()` | 平均 | `df["price"].mean()` |
| `.max()` | 最大値 | `df["price"].max()` |
| `.min()` | 最小値 | `df["price"].min()` |
| `.sum()` | 合計 | `df["price"].sum()` |
| `.count()` | 個数 | `df["price"].count()` |
| `.describe()` | 統計情報 | `df.describe()` |

---

## 📝 問題3の解答：JSON形式で保存

```python
import json

books = [
    {"title": "Python入門", "author": "田中太郎", "price": 2800},
    {"title": "データ分析", "author": "佐藤花子", "price": 3200},
    {"title": "機械学習", "author": "鈴木一郎", "price": 3500},
]

# JSONファイルに保存
with open("books.json", "w", encoding="utf-8") as f:
    json.dump(books, f, ensure_ascii=False, indent=2)

print("books.json に保存しました")

# 確認のため読み込んで表示
with open("books.json", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)
```

### 出力（books.json）

```json
[
  {
    "title": "Python入門",
    "author": "田中太郎",
    "price": 2800
  },
  {
    "title": "データ分析",
    "author": "佐藤花子",
    "price": 3200
  },
  {
    "title": "機械学習",
    "author": "鈴木一郎",
    "price": 3500
  }
]
```

### なぜこう書くの？

```python
import json

# json.dump() = Python のデータ → JSON ファイル
with open("books.json", "w", encoding="utf-8") as f:
    json.dump(books, f, ensure_ascii=False, indent=2)
    #         ↑データ ↑ファイル

# ensure_ascii=False
# False にしないと...
# → "田中太郎" が "\u7530\u4e2d\u592a\u90ce" になる
# True（デフォルト）= ASCII文字のみ使用（日本語はエスケープ）
# False = 日本語をそのまま保存

# indent=2
# 指定しないと...
# → [{"title": "Python入門", ...}, {"title": "データ分析", ...}]
# → 1行になって読みにくい
# 指定すると...
# → 見やすくインデント（字下げ）される
```

### json.dump() と json.dumps() の違い

```python
import json

data = {"name": "田中", "age": 25}

# json.dump() = ファイルに書き込む
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f)

# json.dumps() = 文字列に変換
json_string = json.dumps(data, ensure_ascii=False)
print(json_string)  # {"name": "田中", "age": 25}
```

### JSON読み込み

```python
import json

# 読み込み
with open("books.json", "r", encoding="utf-8") as f:
    books = json.load(f)

# データを表示
for book in books:
    print(f"{book['title']}: {book['price']}円")

# 出力:
# Python入門: 2800円
# データ分析: 3200円
# 機械学習: 3500円
```

### CSV と JSON の比較

```
CSV:
title,author,price
Python入門,田中太郎,2800

JSON:
[
  {
    "title": "Python入門",
    "author": "田中太郎",
    "price": 2800
  }
]
```

| | CSV | JSON |
|---|-----|------|
| サイズ | 小さい | やや大きい |
| 可読性 | シンプル | 構造が分かりやすい |
| 階層構造 | 難しい | 得意 |
| 型 | 文字列のみ | 数値・真偽値・null対応 |

---

## 📝 問題4の解答：階層構造のデータをJSON保存

```python
import json

users = [
    {
        "name": "田中太郎",
        "age": 25,
        "address": {
            "city": "東京",
            "zipcode": "150-0001"
        },
        "hobbies": ["読書", "旅行"]
    },
    {
        "name": "佐藤花子",
        "age": 30,
        "address": {
            "city": "大阪",
            "zipcode": "530-0001"
        },
        "hobbies": ["料理", "ヨガ"]
    }
]

# JSONファイルに保存
with open("users.json", "w", encoding="utf-8") as f:
    json.dump(users, f, ensure_ascii=False, indent=2)

print("users.json に保存しました")

# 読み込んで表示
with open("users.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 見やすく表示
print(json.dumps(data, ensure_ascii=False, indent=2))

# データにアクセス
for user in data:
    print(f"\n名前: {user['name']}")
    print(f"年齢: {user['age']}歳")
    print(f"住所: {user['address']['city']} ({user['address']['zipcode']})")
    print(f"趣味: {', '.join(user['hobbies'])}")
```

### 出力（users.json）

```json
[
  {
    "name": "田中太郎",
    "age": 25,
    "address": {
      "city": "東京",
      "zipcode": "150-0001"
    },
    "hobbies": [
      "読書",
      "旅行"
    ]
  },
  {
    "name": "佐藤花子",
    "age": 30,
    "address": {
      "city": "大阪",
      "zipcode": "530-0001"
    },
    "hobbies": [
      "料理",
      "ヨガ"
    ]
  }
]
```

### 表示出力

```
名前: 田中太郎
年齢: 25歳
住所: 東京 (150-0001)
趣味: 読書, 旅行

名前: 佐藤花子
年齢: 30歳
住所: 大阪 (530-0001)
趣味: 料理, ヨガ
```

### なぜこう書くの？

```python
# JSONは階層構造をそのまま保存できる
user = {
    "name": "田中太郎",
    "address": {          # 辞書の中に辞書
        "city": "東京"
    },
    "hobbies": ["読書"]   # 辞書の中にリスト
}

# アクセス方法
user["name"]                  # → "田中太郎"
user["address"]["city"]       # → "東京"
user["hobbies"][0]            # → "読書"

# CSVでは階層構造は難しい
# → 1行に収める必要がある
# → ネストした辞書やリストを表現しにくい
```

### JSONの型

JSONでサポートされている型:

| Pythonの型 | JSONの型 | 例 |
|-----------|---------|-----|
| dict | object | `{"key": "value"}` |
| list | array | `[1, 2, 3]` |
| str | string | `"text"` |
| int, float | number | `42`, `3.14` |
| True, False | true, false | `true` |
| None | null | `null` |

```python
data = {
    "name": "田中",        # string
    "age": 25,            # number
    "active": True,       # boolean
    "score": 85.5,        # number
    "address": None,      # null
    "tags": ["python"],   # array
}

# JSON保存後も型が保持される
```

---

## 📝 問題5の解答：スクレイピングデータをpandasで保存・分析

```python
import pandas as pd

books = [
    {"title": "A Light in the Attic", "price": 51.77, "rating": 3},
    {"title": "Tipping the Velvet", "price": 53.74, "rating": 1},
    {"title": "Soumission", "price": 50.10, "rating": 1},
    {"title": "Sharp Objects", "price": 47.82, "rating": 4},
    {"title": "Sapiens", "price": 54.23, "rating": 5},
]

# 1. pandas で DataFrame を作成
df = pd.DataFrame(books)

print("=== DataFrame ===")
print(df)

# 2. CSV に保存
df.to_csv("books.csv", index=False, encoding="utf-8")
print("\nbooks.csv に保存しました")

# 3. 分析

# 平均価格
average_price = df["price"].mean()
print(f"\n平均価格: £{average_price:.2f}")

# 評価が4以上の本の数
high_rated = df[df["rating"] >= 4]
print(f"評価4以上の本: {len(high_rated)}冊")

# 最高価格の本のタイトル
max_price_book = df[df["price"] == df["price"].max()]
max_title = max_price_book["title"].values[0]
max_price = max_price_book["price"].values[0]
print(f"最高価格: {max_title} (£{max_price})")

# 価格でソートして表示
print("\n=== 価格順（降順）===")
df_sorted = df.sort_values("price", ascending=False)
print(df_sorted)

# 追加の分析
print("\n=== 統計情報 ===")
print(df.describe())

print("\n=== 評価別の平均価格 ===")
print(df.groupby("rating")["price"].mean())
```

### 出力

```
=== DataFrame ===
                  title  price  rating
0  A Light in the Attic  51.77       3
1   Tipping the Velvet  53.74       1
2            Soumission  50.10       1
3         Sharp Objects  47.82       4
4               Sapiens  54.23       5

books.csv に保存しました

平均価格: £51.53
評価4以上の本: 2冊
最高価格: Sapiens (£54.23)

=== 価格順（降順）===
                  title  price  rating
4               Sapiens  54.23       5
1   Tipping the Velvet  53.74       1
0  A Light in the Attic  51.77       3
2            Soumission  50.10       1
3         Sharp Objects  47.82       4

=== 統計情報 ===
           price     rating
count   5.000000   5.000000
mean   51.532000   2.800000
std     2.481618   1.788854
min    47.820000   1.000000
25%    50.100000   1.000000
50%    51.770000   3.000000
75%    53.740000   4.000000
max    54.230000   5.000000

=== 評価別の平均価格 ===
rating
1    51.920
3    51.770
4    47.820
5    54.230
Name: price, dtype: float64
```

### なぜこう書くの？

```python
import pandas as pd

books = [
    {"title": "A Light in the Attic", "price": 51.77, "rating": 3},
    {"title": "Tipping the Velvet", "price": 53.74, "rating": 1},
    {"title": "Sapiens", "price": 54.23, "rating": 5},
]

# DataFrame を作成
df = pd.DataFrame(books)
# 辞書のリスト → DataFrame に変換

# CSV保存
df.to_csv("books.csv", index=False)
# index=False → 行番号（0,1,2...）を保存しない

# 列を取得
df["price"]  # Series（1列）
df[["title", "price"]]  # DataFrame（複数列）

# 条件で絞り込み
df[df["rating"] >= 4]
# df["rating"] >= 4 → True/False のリスト
# df[True/Falseのリスト] → Trueの行だけ取得

# 統計
df["price"].mean()  # 平均
df["price"].max()   # 最大値
df.describe()       # 統計情報一覧

# ソート
df.sort_values("price", ascending=False)
# ascending=False → 降順（大きい順）
# ascending=True → 昇順（小さい順）

# グループ化
df.groupby("rating")["price"].mean()
# "rating" でグループ化して、各グループの "price" の平均
```

### pandas の便利なメソッド

```python
import pandas as pd

books = [
    {"title": "A Light in the Attic", "price": 51.77, "rating": 3},
    {"title": "Tipping the Velvet", "price": 53.74, "rating": 1},
    {"title": "Sapiens", "price": 54.23, "rating": 5},
]

df = pd.DataFrame(books)

# データフレームの情報
df.info()          # 列名、型、非null数
df.describe()      # 統計情報
df.head()          # 最初の5行
df.tail()          # 最後の5行
df.shape           # (行数, 列数)

# 列の操作
df["price"]        # 1列取得
df[["title", "price"]]  # 複数列取得
df.columns         # 列名のリスト

# 行の操作
df.loc[0]          # 0行目
df.iloc[0]         # 0番目（同じ）
df[df["price"] > 50]  # 条件で絞り込み

# ソート
df.sort_values("price")  # 昇順
df.sort_values("price", ascending=False)  # 降順

# グループ化
df.groupby("rating").mean()  # 評価ごとの平均
df.groupby("rating").count()  # 評価ごとの個数

# 新しい列を追加
df["price_yen"] = df["price"] * 150  # ポンドを円に変換
```

---

## 💡 今回のポイントまとめ

### CSV保存の基本

```python
import csv

# 辞書のリストを保存
with open("file.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["col1", "col2"])
    writer.writeheader()
    writer.writerows(data)

# 読み込み
with open("file.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    data = list(reader)
```

### JSON保存の基本

```python
import json

# 保存
with open("file.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 読み込み
with open("file.json", "r", encoding="utf-8") as f:
    data = json.load(f)
```

### pandas の基本

```python
import pandas as pd

# DataFrame作成
df = pd.DataFrame(data)

# CSV保存・読み込み
df.to_csv("file.csv", index=False)
df = pd.read_csv("file.csv")

# 分析
df["col"].mean()   # 平均
df["col"].max()    # 最大
df.describe()      # 統計情報
df[df["col"] > 10] # 絞り込み
```

---

## 🔍 よくある間違い

### ❌ newline="" を忘れる

```python
# 間違い
with open("file.csv", "w", encoding="utf-8") as f:
    # newline がない

# 正しい
with open("file.csv", "w", newline="", encoding="utf-8") as f:
    # newline="" が必要（CSV特有）
```

**理由**: CSV は改行コードの扱いが特殊なため、`newline=""` が必要

---

### ❌ ensure_ascii=False を忘れる

```python
import json

data = {"message": "こんにちは"}

# 間違い（日本語が \uxxxx になる）
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f)

# 正しい
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)
```

---

### ❌ CSV読み込み後に型変換を忘れる

```python
# csv.DictReader で読み込むと...
for row in reader:
    price = row["price"]  # "150"（文字列）
    total = price + 100   # エラー！

# 正しい
for row in reader:
    price = int(row["price"])  # 150（数値）
    total = price + 100  # OK
```

---

### ❌ pandas で index を保存してしまう

```python
# 間違い
df.to_csv("file.csv")
# → 0列目に 0,1,2... が保存される

# 正しい
df.to_csv("file.csv", index=False)
# → 行番号を保存しない
```

---

### ❌ fieldnames の順番を間違える

```python
# 間違い
fieldnames = ["price", "name"]  # 順番が違う
writer = csv.DictWriter(f, fieldnames=fieldnames)
writer.writerows(data)
# → CSV: price,name（意図した順番と違う）

# 正しい
fieldnames = ["name", "price"]  # 意図した順番
```

---

## 🔧 実践的なテクニック

### 1. 既存のCSVに追記

```python
import csv

# 追記モード（"a"）で開く
with open("books.csv", "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "author", "price"])
    # ヘッダーは書かない（既にある）
    writer.writerow({"title": "新しい本", "author": "著者名", "price": 3000})
```

### 2. pandasで複数のファイル形式を扱う

```python
import pandas as pd

df = pd.DataFrame(data)

# CSV
df.to_csv("data.csv", index=False)

# JSON
df.to_json("data.json", orient="records", force_ascii=False, indent=2)

# Excel
df.to_excel("data.xlsx", index=False)  # pip install openpyxl が必要

# TSV（タブ区切り）
df.to_csv("data.tsv", sep="\t", index=False)
```

### 3. 大きなCSVを読み込む

```python
import pandas as pd

# チャンクに分けて読み込む（メモリ節約）
for chunk in pd.read_csv("large.csv", chunksize=1000):
    # 1000行ずつ処理
    print(chunk.shape)
```

### 4. CSVの文字コードを指定

```python
import pandas as pd

# Shift-JIS（日本の古いCSV）
df = pd.read_csv("old_data.csv", encoding="shift-jis")

# UTF-8 BOM付き
df = pd.read_csv("data.csv", encoding="utf-8-sig")
```

### 5. データの検証

```python
import pandas as pd

df = pd.read_csv("data.csv")

# 欠損値をチェック
print(df.isnull().sum())

# 重複をチェック
print(df.duplicated().sum())

# データ型を確認
print(df.dtypes)

# 欠損値を削除
df_clean = df.dropna()

# 重複を削除
df_clean = df.drop_duplicates()
```

---

## 🎓 もっと知りたい人向け

### pandas の高度な操作

```python
import pandas as pd

books = [
    {"title": "A Light in the Attic", "price": 51.77, "rating": 3},
    {"title": "Tipping the Velvet", "price": 53.74, "rating": 1},
    {"title": "Sapiens", "price": 54.23, "rating": 5},
]

df = pd.DataFrame(books)

# 列を追加
df["price_yen"] = df["price"] * 150

# 列を削除
df = df.drop("rating", axis=1)

# 条件による値の変更
df.loc[df["price"] > 50, "expensive"] = True

# 複数の条件
expensive_high_rated = df[(df["price"] > 50) & (df["rating"] >= 4)]

# ピボットテーブル
pivot = df.pivot_table(values="price", index="rating", aggfunc="mean")
```

### JSONの高度な操作

```python
import json

# 美しく表示
print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))

# 特定の型をJSONに変換
from datetime import datetime

def date_handler(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError

data = {"date": datetime.now()}
json.dumps(data, default=date_handler)
```

### CSVの詳細設定

```python
import csv

# カスタム区切り文字
with open("data.tsv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="\t")  # タブ区切り

# クォート設定
with open("data.csv", "w", newline="") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)  # すべてクォート
```

---

**次回は「データベース保存 - SQLite入門」です！**

この回ではデータベースの基本概念を学び、SQLiteを使ってデータを保存・検索・更新・削除する方法を習得します。スクレイピングで収集したデータをデータベースで管理することで、重複チェックや効率的なデータ管理ができるようになります。
