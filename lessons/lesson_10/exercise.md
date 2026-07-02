# 第10回：データの保存 - CSV・JSON・pandas

## 今回のゴール

- CSVファイルにデータを保存できる
- JSONファイルにデータを保存できる
- pandasでデータを扱える
- データを読み込んで分析できる
- CSVとJSONの使い分けがわかる

## 所要時間：90分

---

## 10.1 導入：取得したデータを保存する

これまでのレッスンで、Webサイトからデータを取得し、整形する方法を学びました。しかし、取得したデータをプログラムの中だけで使っていては、せっかくの情報を活用できません。

データを**ファイルに保存**することで、以下のようなことができるようになります。

- **後で分析する**: Excelや他のツールで開いて分析
- **他の人と共有する**: CSVやJSONファイルを渡す
- **データベースに取り込む**: CSVをインポート
- **自動化する**: 定期的にデータを収集して蓄積

特に重要なのは、**取得したデータを一度保存することで、分析する前の段階でセーブできる**ということです。これにより、複数の分析方法を試したり、後から参照したりできます。

この回では、Pythonでデータを保存する主要な方法を3つ学びます。

| 方法 | ファイル形式 | 特徴 |
|------|-------------|------|
| csv モジュール | CSV | 標準ライブラリ、表形式データ向け |
| json モジュール | JSON | 標準ライブラリ、階層構造に対応 |
| pandas | CSV/JSON/Excel等 | 強力なデータ分析ライブラリ |

---

## 10.2 ハンズオン：CSVファイルに保存してみよう

以下のコードをファイルに保存して実行してください。

```python
import csv

# 商品データ
products = [
    {"name": "りんご", "price": 150, "stock": 100},
    {"name": "バナナ", "price": 100, "stock": 50},
    {"name": "みかん", "price": 200, "stock": 80},
]

# CSVファイルに保存
with open("products.csv", "w", newline="", encoding="utf-8") as f:
    # DictWriter を使う（辞書のリストを書き込める）
    fieldnames = ["name", "price", "stock"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)

    # ヘッダー行を書く
    writer.writeheader()

    # データ行を書く
    writer.writerows(products)

print("products.csv を保存しました")

# 確認のため読み込んで表示
with open("products.csv", "r", encoding="utf-8") as f:
    print(f.read())
```

実行すると、`products.csv` というファイルが作成され、以下のような内容が保存されます。

```csv
name,price,stock
りんご,150,100
バナナ,100,50
みかん,200,80
```

このファイルはExcelやGoogleスプレッドシートで開くことができます。

---

## 解説

### CSVとは

**CSV**（Comma-Separated Values）は、データをカンマで区切ったテキストファイルです。

```csv
列1,列2,列3
値1,値2,値3
値4,値5,値6
```

#### CSVの特徴

| 特徴 | 説明 |
|------|------|
| シンプル | テキストファイルなので軽い |
| 互換性が高い | Excel、Googleスプレッドシート等で開ける |
| 表形式向け | 行と列で整理されたデータに最適 |
| 階層構造は苦手 | ネストしたデータは扱いにくい |

#### CSVが向いているデータ

```python
# ○ 向いている: 表形式のデータ
products = [
    {"name": "りんご", "price": 150},
    {"name": "バナナ", "price": 100},
]

# △ 向いていない: 階層構造のデータ
user = {
    "name": "田中太郎",
    "address": {
        "city": "東京",
        "street": "渋谷1-2-3"
    },
    "hobbies": ["読書", "旅行"]
}
```

### JSONとは

**JSON**（JavaScript Object Notation）は、データを構造化して保存できるテキストファイルです。

```json
{
  "name": "田中太郎",
  "age": 25,
  "hobbies": ["読書", "旅行"]
}
```

#### JSONの特徴

| 特徴 | 説明 |
|------|------|
| 階層構造 | ネストしたデータを自然に表現できる |
| 型を保持 | 数値、文字列、真偽値、リスト、辞書 |
| API連携 | Web APIのデータ形式として標準的 |
| 人間が読める | テキストなので開いて確認できる |

#### JSONが向いているデータ

```python
# JSON向き: 階層構造のデータ
user = {
    "name": "田中太郎",
    "age": 25,
    "address": {
        "city": "東京",
        "zipcode": "150-0001"
    },
    "hobbies": ["読書", "旅行"]
}
```

### CSVとJSONの使い分け

| 用途 | CSV | JSON |
|------|-----|------|
| Microsoft Excelで開きたい | ○ | △ |
| 階層構造のデータ | △ | ○ |
| データ分析 | ○ | △ |
| API連携 | △ | ○ |
| ファイルサイズ | 小さい | やや大きい |

### CSV保存/save

#### 方法1: csv.writer（リストで構成されたリスト）

```python
import csv

data = [
    ["name", "price", "stock"],  # ヘッダー
    ["りんご", 150, 100],
    ["バナナ", 100, 50],
]

with open("products.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(data)
```

#### 方法2: csv.DictWriter（辞書のリスト）

```python
import csv

data = [
    {"name": "りんご", "price": 150, "stock": 100},
    {"name": "バナナ", "price": 100, "stock": 50},
]

with open("products.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = ["name", "price", "stock"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()  # ヘッダー行
    writer.writerows(data)  # データ行
```

**DictWriterのメリット:**
- 辞書のリストをそのまま書き込める
- キー名が列名になる
- スクレイピングで取得したデータと相性が良い

#### newline="" と encoding="utf-8" の意味

```python
with open("file.csv", "w", newline="", encoding="utf-8") as f:
    # newline="" = 改行コードの問題を防ぐ（CSV特有の設定）
    # encoding="utf-8" = 日本語を正しく保存
```

Windows の Excel で開く場合、文字化けする場合は `encoding="utf-8-sig"` を使うと BOM 付き UTF-8 になり、正しく表示されます。

### CSV読み込み/load

```python
import csv

with open("products.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row)
        # {'name': 'りんご', 'price': '150', 'stock': '100'}
```

**注意:** `csv.DictReader` で読み込むと、すべての値が**文字列**になります。数値に変換する必要があります。

```python
for row in reader:
    name = row["name"]
    price = int(row["price"])  # 文字列 → 整数
    stock = int(row["stock"])
```

### JSON保存/save

```python
import json

data = [
    {"name": "りんご", "price": 150, "stock": 100},
    {"name": "バナナ", "price": 100, "stock": 50},
]

with open("products.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

**オプションの意味:**

| オプション | 意味 |
|-----------|------|
| `ensure_ascii=False` | 日本語をそのまま保存（文字化けしない） |
| `indent=2` | インデント（字下げ）を2スペースにして見やすく |

保存されるファイル（products.json）:

```json
[
  {
    "name": "りんご",
    "price": 150,
    "stock": 100
  },
  {
    "name": "バナナ",
    "price": 100,
    "stock": 50
  }
]
```

### JSON読み込み/load

```python
import json

with open("products.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    print(data)
    # [{'name': 'りんご', 'price': 150, ...}, ...]
```

**CSVとの違い:** JSONは型が保持されるので、数値はそのまま数値として読み込まれます。

### pandasでデータを扱う

**pandas**は、Pythonで最も人気のあるデータ分析ライブラリです。

#### pandasのインストール

```bash
pip install pandas
```

#### DataFrameとは

pandas の中心的なデータ構造が **DataFrame** です。Excel のシートのようなテーブル形式のデータです。

```python
import pandas as pd

# 辞書のリスト → DataFrame
data = [
    {"name": "りんご", "price": 150, "stock": 100},
    {"name": "バナナ", "price": 100, "stock": 50},
]

df = pd.DataFrame(data)
print(df)
```

出力:

```
    name  price  stock
0  りんご    150    100
1  バナナ    100     50
```

#### pandasでCSV保存

```python
import pandas as pd

df = pd.DataFrame(data)

# CSV保存
df.to_csv("products.csv", index=False, encoding="utf-8")
```

`index=False` を指定すると、行番号（0, 1, 2...）を保存しません。

#### pandasでCSV読み込み

```python
import pandas as pd

df = pd.read_csv("products.csv")
print(df)
```

**標準ライブラリとの違い:**
- 自動で型を推測してくれる（数値は数値として読み込まれる）
- 1行で読み込める
- データ分析機能が豊富

#### pandasでJSON保存・読み込み

```python
import pandas as pd

# JSON保存
df.to_json("products.json", orient="records", force_ascii=False, indent=2)

# JSON読み込み
df = pd.read_json("products.json")
```

`orient="records"` を指定すると、辞書のリスト形式で保存されます。

#### pandasの基本的なデータ操作

```python
import pandas as pd

df = pd.read_csv("products.csv")

# 基本情報を表示
print(df.info())

# 統計情報を表示
print(df.describe())

# 特定の列を取得
prices = df["price"]
print(prices)

# 条件で絞り込み
expensive = df[df["price"] > 120]
print(expensive)

# 平均を計算
average_price = df["price"].mean()
print(f"平均価格: {average_price}円")

# 最大値
max_price = df["price"].max()
print(f"最高価格: {max_price}円")

# ソート
df_sorted = df.sort_values("price", ascending=False)
print(df_sorted)
```

---

## 練習問題

### 10.3 問題1：基本的なCSV保存

> 第8回でチャレンジ問題として紹介したCSV保存を、ここで改めて基礎から丁寧に学びます。第8回ですでに解けた方はスキップしてOKです！

以下のデータをCSVファイルに保存してください。

```python
books = [
    {"title": "Python入門", "author": "田中太郎", "price": 2800},
    {"title": "データ分析", "author": "佐藤花子", "price": 3200},
    {"title": "機械学習", "author": "鈴木一郎", "price": 3500},
]

# books.csv に保存
```

**考え方のヒント:**

```python
手順:
1. csv モジュールをインポート
2. open() でファイルを開く（"w" モード、newline="", encoding="utf-8"）
3. csv.DictWriter を作成
   → fieldnames = ["title", "author", "price"]
4. writeheader() でヘッダーを書く
5. writerows() でデータを書く
```

---

### 10.4 問題2：CSVを読み込んで分析

問題1で作成した `books.csv` を読み込んで、以下を計算してください。

1. 平均価格
2. 最高価格の本
3. 最安価格の本

**考え方のヒント:**

- `csv.DictReader` で読み込むとすべての値が文字列になるため、価格は `int()` で変換する
- `sum(prices) / len(prices)` で平均を計算できる
- pandas を使う場合は `df["price"].mean()` / `df["price"].max()` などで簡単に計算できる

---

### 10.5 問題3：JSON形式で保存

問題1のデータをJSON形式で保存してください。

```python
books = [
    {"title": "Python入門", "author": "田中太郎", "price": 2800},
    {"title": "データ分析", "author": "佐藤花子", "price": 3200},
    {"title": "機械学習", "author": "鈴木一郎", "price": 3500},
]

# books.json に保存
```

**考え方のヒント:**

```python
手順:
1. json モジュールをインポート
2. open() でファイルを開く（"w" モード）
3. json.dump() で保存
   → ensure_ascii=False（日本語対応）
   → indent=2（見やすく）
```

---

### 10.6 問題4：階層構造のデータをJSON保存

以下のような階層構造を持つデータをJSON形式で保存してください。

```python
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

# users.json に保存
# 保存後、読み込んで表示して確認
```

**考え方のヒント:**

```python
JSONは階層構造をそのまま保存できる
→ リストの中に辞書、辞書の中にリスト、辞書の中に辞書

保存:
json.dump(users, f, ensure_ascii=False, indent=2)

読み込み:
with open("users.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    print(json.dumps(data, ensure_ascii=False, indent=2))
```

---

### 10.7 問題5：スクレイピングデータをpandasで保存・分析

Books to Scrape から取得した以下のデータを、pandasを使ってCSVに保存し、分析してください。

```python
books = [
    {"title": "A Light in the Attic", "price": 51.77, "rating": 3},
    {"title": "Tipping the Velvet", "price": 53.74, "rating": 1},
    {"title": "Soumission", "price": 50.10, "rating": 1},
    {"title": "Sharp Objects", "price": 47.82, "rating": 4},
    {"title": "Sapiens", "price": 54.23, "rating": 5},
]

# 1. pandas で DataFrame を作成
# 2. CSV に保存
# 3. 以下を計算して表示:
#    - 平均価格
#    - 評価が4以上の本の数
#    - 最高価格の本のタイトル
#    - 価格でソートして表示
```

**考え方のヒント:**

1. `pd.DataFrame(books)` で辞書のリストを DataFrame に変換する
2. `df.to_csv("books.csv", index=False)` で CSV 保存（`index=False` で行番号を除外）
3. 平均は `.mean()`、条件絞り込みは `df[df["列"] >= 値]`、最大値の行は `.idxmax()` で取得できる
4. `df.sort_values("price", ascending=False)` で降順ソート

---

## 検索キーワード

| 知りたいこと | 検索キーワード |
|-------------|---------------|
| CSV保存の基本 | `Python csv DictWriter 使い方` |
| JSON保存 | `Python json dump 日本語` |
| pandas入門 | `pandas DataFrame 使い方 初心者` |
| CSV読み込み | `Python csv 読み込み DictReader` |
| pandasでの分析 | `pandas データ分析 基本` |
| Excel形式で保存 | `pandas to_excel 使い方` |

---

## 困ったときは

### 「CSV を Excel で開いたら文字化けした」

Windows の Excel で開く場合、BOM 付き UTF-8 を使うと文字化けしません。

```python
# 標準ライブラリの場合
with open("file.csv", "w", encoding="utf-8-sig", newline="") as f:
    # ...

# pandas の場合
df.to_csv("file.csv", index=False, encoding="utf-8-sig")
```

### 「CSV を読み込んだら数値が文字列になっている」

`csv.DictReader` で読み込むと、すべて文字列になります。

```python
# 読み込み時に変換
for row in reader:
    price = int(row["price"])

# または pandas を使う（自動で型を推測）
df = pd.read_csv("file.csv")
```

### 「JSON に日本語を保存したら \uxxxx になった」

`ensure_ascii=False` を指定してください。

```python
# 間違い
json.dump(data, f)  # → "\u65e5\u672c\u8a9e"

# 正しい
json.dump(data, f, ensure_ascii=False)  # → "日本語"
```

### 「pandas がインストールできない」

```bash
# pip を更新してから再試行
pip install --upgrade pip
pip install pandas

# または
python -m pip install pandas
```

### 「DataFrame の列を取得する方法が分からない」

```python
import pandas as pd

df = pd.DataFrame(data)

# 1列を取得（Series）
prices = df["price"]

# 複数列を取得（DataFrame）
subset = df[["title", "price"]]

# 条件で絞り込み
expensive = df[df["price"] > 100]
```

---

## 確認事項

- CSVファイルにデータを保存できた
- JSONファイルにデータを保存できた
- csv.writer と csv.DictWriter の違いがわかった
- CSVとJSONの使い分けがわかった
- pandasでDataFrameを作成できた
- pandasでCSVを保存・読み込みできた
- DataFrameで基本的なデータ分析ができた
- encoding="utf-8" の重要性がわかった

---

## まとめ：データ保存方法の選び方

### CSV を使う場合
- 表形式のシンプルなデータ
- Excel で開いて確認したい
- データ分析する予定

### JSON を使う場合
- 階層構造のあるデータ
- API連携でデータを受け渡しする
- 設定ファイルとして使う

### pandas を使う場合
- データ分析を行う
- 大量のデータを扱う
- 複数の形式（CSV、JSON、Excel）を統一的に扱いたい

---

**次回は「データベース保存 - SQLite入門」です。データベースの基礎を学び、スクレイピングデータをSQLiteに保存・検索・管理する方法を習得します。**
