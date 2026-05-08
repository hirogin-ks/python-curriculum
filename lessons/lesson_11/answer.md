# 第11回：データベース保存 - SQLite入門【解答・解説】

## 📝 問題1の解答：基本的なCRUD操作

```python
import sqlite3

# データベースに接続
conn = sqlite3.connect("shop.db")
cursor = conn.cursor()

# 1. products テーブルを作成
print("=== 1. テーブル作成 ===")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price INTEGER,
        stock INTEGER
    )
""")
print("テーブルを作成しました")

# 2. 3つの商品を挿入
print("\n=== 2. データ挿入 ===")
products = [
    ("りんご", 150, 100),
    ("バナナ", 100, 50),
    ("みかん", 200, 80),
]

for product in products:
    cursor.execute("""
        INSERT INTO products (name, price, stock)
        VALUES (?, ?, ?)
    """, product)
    print(f"{product[0]} を追加しました")

conn.commit()

# 3. すべての商品を表示
print("\n=== 3. 全商品表示 ===")
cursor.execute("SELECT * FROM products")
rows = cursor.fetchall()

for row in rows:
    print(f"ID: {row[0]}, 商品名: {row[1]}, 価格: {row[2]}円, 在庫: {row[3]}個")

# 4. 特定の商品の価格を更新
print("\n=== 4. 価格更新 ===")
cursor.execute("""
    UPDATE products
    SET price = ?
    WHERE name = ?
""", (180, "りんご"))
conn.commit()
print("りんごの価格を150円→180円に更新しました")

# 5. 特定の商品を削除
print("\n=== 5. 商品削除 ===")
cursor.execute("DELETE FROM products WHERE name = ?", ("バナナ",))
conn.commit()
print("バナナを削除しました")

# 6. 最終的なデータを表示
print("\n=== 6. 最終データ ===")
cursor.execute("SELECT * FROM products")
rows = cursor.fetchall()

for row in rows:
    print(f"ID: {row[0]}, 商品名: {row[1]}, 価格: {row[2]}円, 在庫: {row[3]}個")

conn.close()
```

### 出力

```
=== 1. テーブル作成 ===
テーブルを作成しました

=== 2. データ挿入 ===
りんご を追加しました
バナナ を追加しました
みかん を追加しました

=== 3. 全商品表示 ===
ID: 1, 商品名: りんご, 価格: 150円, 在庫: 100個
ID: 2, 商品名: バナナ, 価格: 100円, 在庫: 50個
ID: 3, 商品名: みかん, 価格: 200円, 在庫: 80個

=== 4. 価格更新 ===
りんごの価格を150円→180円に更新しました

=== 5. 商品削除 ===
バナナを削除しました

=== 6. 最終データ ===
ID: 1, 商品名: りんご, 価格: 180円, 在庫: 100個
ID: 3, 商品名: みかん, 価格: 200円, 在庫: 80個
```

### なぜこう書くの？

```python
# CREATE TABLE IF NOT EXISTS
# → テーブルが既にあってもエラーにならない
cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price INTEGER,
        stock INTEGER
    )
""")

# INTEGER PRIMARY KEY AUTOINCREMENT
# → 自動で 1, 2, 3... と増えるID

# ? プレースホルダー
cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
# → SQLインジェクション攻撃を防ぐ
# → SQL文とデータを分離することで、悪意のあるSQL文が実行されるのを防止

# conn.commit()
# → 変更を確定（これがないと保存されない）

# fetchall()
# → すべての行を取得（リストで返る）

# fetchone()
# → 1行だけ取得（タプルで返る）
```

### CRUD操作のまとめ

| 操作 | SQL | Python |
|------|-----|--------|
| **C**reate | `INSERT INTO` | `cursor.execute("INSERT ...")` |
| **R**ead | `SELECT` | `cursor.execute("SELECT ...")` + `fetchall()` |
| **U**pdate | `UPDATE` | `cursor.execute("UPDATE ...")` |
| **D**elete | `DELETE` | `cursor.execute("DELETE ...")` |

### 処理の流れ

```
1. データベースに接続
   conn = sqlite3.connect("shop.db")
   ↓
2. カーソルを作成
   cursor = conn.cursor()
   ↓
3. テーブルを作成
   cursor.execute("CREATE TABLE IF NOT EXISTS products (...)")
   ↓
4. データを挿入
   cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", ...)
   ↓
5. commit で確定
   conn.commit()
   ↓
6. データを取得
   cursor.execute("SELECT * FROM products")
   ↓
7. 更新・削除
   cursor.execute("UPDATE ... / DELETE ...")
   ↓
8. 接続を閉じる
   conn.close()
```

---

## 📝 問題2の解答：重複チェック付きで保存

### 方法1: 事前にチェックしてから挿入

```python
import sqlite3

books = [
    {"title": "Python入門", "author": "田中太郎", "price": 2800},
    {"title": "Python入門", "author": "田中太郎", "price": 2800},  # 重複
    {"title": "データ分析", "author": "佐藤花子", "price": 3200},
    {"title": "Python入門", "author": "田中太郎", "price": 3000},  # 重複
]

conn = sqlite3.connect("books.db")
cursor = conn.cursor()

# テーブル作成
cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT,
        price INTEGER
    )
""")

added_count = 0
skipped_count = 0

for book in books:
    # 既に存在するか確認
    cursor.execute("""
        SELECT COUNT(*) FROM books WHERE title = ?
    """, (book["title"],))

    count = cursor.fetchone()[0]

    if count == 0:
        # 存在しない場合のみ挿入
        cursor.execute("""
            INSERT INTO books (title, author, price)
            VALUES (?, ?, ?)
        """, (book["title"], book["author"], book["price"]))
        print(f"✅ 追加: {book['title']}")
        added_count += 1
    else:
        print(f"⏭️  スキップ: {book['title']} (既に存在)")
        skipped_count += 1

conn.commit()

print(f"\n追加: {added_count}件")
print(f"スキップ: {skipped_count}件")

# 確認
cursor.execute("SELECT * FROM books")
rows = cursor.fetchall()
print(f"\n現在のデータ: {len(rows)}件")
for row in rows:
    print(f"  {row[1]}: {row[3]}円")

conn.close()
```

### 方法2: UNIQUE制約 + try-except

```python
import sqlite3

books = [
    {"title": "Python入門", "author": "田中太郎", "price": 2800},
    {"title": "Python入門", "author": "田中太郎", "price": 2800},  # 重複
    {"title": "データ分析", "author": "佐藤花子", "price": 3200},
    {"title": "Python入門", "author": "田中太郎", "price": 3000},  # 重複
]

conn = sqlite3.connect("books_unique.db")
cursor = conn.cursor()

# テーブル作成（title に UNIQUE 制約を付ける）
cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL UNIQUE,
        author TEXT,
        price INTEGER
    )
""")

added_count = 0
skipped_count = 0

for book in books:
    try:
        cursor.execute("""
            INSERT INTO books (title, author, price)
            VALUES (?, ?, ?)
        """, (book["title"], book["author"], book["price"]))
        conn.commit()
        print(f"✅ 追加: {book['title']}")
        added_count += 1
    except sqlite3.IntegrityError:
        print(f"⏭️  スキップ: {book['title']} (既に存在)")
        skipped_count += 1

print(f"\n追加: {added_count}件")
print(f"スキップ: {skipped_count}件")

conn.close()
```

### 方法3: INSERT OR IGNORE

```python
import sqlite3

books = [
    {"title": "Python入門", "author": "田中太郎", "price": 2800},
    {"title": "Python入門", "author": "田中太郎", "price": 2800},  # 重複
    {"title": "データ分析", "author": "佐藤花子", "price": 3200},
    {"title": "Python入門", "author": "田中太郎", "price": 3000},  # 重複
]

conn = sqlite3.connect("books_ignore.db")
cursor = conn.cursor()

# UNIQUE 制約付きテーブル
cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL UNIQUE,
        author TEXT,
        price INTEGER
    )
""")

for book in books:
    # INSERT OR IGNORE = 重複なら無視（エラーにならない）
    cursor.execute("""
        INSERT OR IGNORE INTO books (title, author, price)
        VALUES (?, ?, ?)
    """, (book["title"], book["author"], book["price"]))

conn.commit()

# 何件追加されたか確認
cursor.execute("SELECT COUNT(*) FROM books")
count = cursor.fetchone()[0]
print(f"追加されたデータ: {count}件")

conn.close()
```

### 出力

```
✅ 追加: Python入門
⏭️  スキップ: Python入門 (既に存在)
✅ 追加: データ分析
⏭️  スキップ: Python入門 (既に存在)

追加: 2件
スキップ: 2件

現在のデータ: 2件
  Python入門: 2800円
  データ分析: 3200円
```

### なぜこう書くの？

```python
# SELECT COUNT(*) = 件数を取得
cursor.execute("SELECT COUNT(*) FROM books WHERE title = ?", (title,))
count = cursor.fetchone()[0]  # → 0 または 1以上

# if count == 0 で存在チェック
if count == 0:
    # 存在しない → 挿入

# UNIQUE 制約
cursor.execute("""
    CREATE TABLE books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL UNIQUE
    )
""")

# try-except で IntegrityError をキャッチ
try:
    cursor.execute("INSERT INTO books (title) VALUES (?)", (title,))
except sqlite3.IntegrityError:
    # 重複エラー

# INSERT OR IGNORE
# → 重複なら何もしない（エラーにならない）
```

### 重複チェックの方法比較

| 方法 | メリット | デメリット |
|------|---------|-----------|
| 事前チェック | 柔軟な処理が可能 | 2回SQLを実行（やや遅い） |
| UNIQUE + try-except | シンプル | エラー処理が必要 |
| INSERT OR IGNORE | 最もシンプル | 挿入されたか分からない |

---

## 📝 問題3の解答：条件検索

```python
import sqlite3

conn = sqlite3.connect("books.db")
conn.row_factory = sqlite3.Row  # 辞書形式で取得
cursor = conn.cursor()

# 1. 価格が3000円以上の本
print("=== 1. 価格が3000円以上の本 ===")
cursor.execute("SELECT * FROM books WHERE price >= ?", (3000,))
rows = cursor.fetchall()

for row in rows:
    print(f"  {row['title']}: {row['price']}円")

# 2. 著者が「田中太郎」の本
print("\n=== 2. 著者が「田中太郎」の本 ===")
cursor.execute("SELECT * FROM books WHERE author = ?", ("田中太郎",))
rows = cursor.fetchall()

for row in rows:
    print(f"  {row['title']} by {row['author']}")

# 3. タイトルに「Python」が含まれる本
print("\n=== 3. タイトルに「Python」が含まれる本 ===")
cursor.execute("SELECT * FROM books WHERE title LIKE ?", ("%Python%",))
rows = cursor.fetchall()

for row in rows:
    print(f"  {row['title']}")

# 4. 価格の平均値
print("\n=== 4. 価格の平均値 ===")
cursor.execute("SELECT AVG(price) FROM books")
average = cursor.fetchone()[0]
print(f"  平均価格: {average:.0f}円")

# おまけ: 統計情報
print("\n=== おまけ: 統計情報 ===")
cursor.execute("""
    SELECT
        COUNT(*) as count,
        AVG(price) as avg_price,
        MIN(price) as min_price,
        MAX(price) as max_price
    FROM books
""")
stats = cursor.fetchone()
print(f"  件数: {stats['count']}件")
print(f"  平均: {stats['avg_price']:.0f}円")
print(f"  最安: {stats['min_price']}円")
print(f"  最高: {stats['max_price']}円")

conn.close()
```

### 出力

```
=== 1. 価格が3000円以上の本 ===
  データ分析: 3200円

=== 2. 著者が「田中太郎」の本 ===
  Python入門 by 田中太郎

=== 3. タイトルに「Python」が含まれる本 ===
  Python入門

=== 4. 価格の平均値 ===
  平均価格: 3000円

=== おまけ: 統計情報 ===
  件数: 2件
  平均: 3000円
  最安: 2800円
  最高: 3200円
```

### なぜこう書くの？

```python
# conn.row_factory = sqlite3.Row
# → 辞書のようにアクセスできる
# row['title'] で取得できる

# WHERE 句で条件を指定
SELECT * FROM books WHERE price >= 3000
SELECT * FROM books WHERE author = '田中太郎'

# LIKE でパターンマッチ
# % = 任意の文字列
WHERE title LIKE '%Python%'  # Python を含む
WHERE title LIKE 'Python%'   # Python で始まる
WHERE title LIKE '%入門'     # 入門 で終わる

# 集計関数
AVG(price)   # 平均
COUNT(*)     # 件数
MIN(price)   # 最小
MAX(price)   # 最大
SUM(price)   # 合計
```

### SQL の WHERE 句まとめ

| 条件 | SQL | 例 |
|------|-----|-----|
| 等しい | `=` | `WHERE price = 100` |
| 大きい | `>` | `WHERE price > 100` |
| 以上 | `>=` | `WHERE price >= 100` |
| 小さい | `<` | `WHERE price < 100` |
| 以下 | `<=` | `WHERE price <= 100` |
| 含む | `LIKE '%文字%'` | `WHERE title LIKE '%Python%'` |
| AND条件 | `AND` | `WHERE price > 100 AND stock > 0` |
| OR条件 | `OR` | `WHERE price < 100 OR stock < 10` |

---

## 📝 問題4の解答：スクレイピングデータをデータベースに保存

```python
import sqlite3

books = [
    {"title": "A Light in the Attic", "price": 51.77, "rating": 3},
    {"title": "Tipping the Velvet", "price": 53.74, "rating": 1},
    {"title": "Soumission", "price": 50.10, "rating": 1},
    {"title": "Sharp Objects", "price": 47.82, "rating": 4},
    {"title": "Sapiens", "price": 54.23, "rating": 5},
]

# データベースに接続
conn = sqlite3.connect("books_scraping.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 1. テーブルを作成
print("=== 1. テーブル作成 ===")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        price REAL,
        rating INTEGER
    )
""")
print("テーブルを作成しました")

# 2. データを保存
print("\n=== 2. データ保存 ===")
for book in books:
    cursor.execute("""
        INSERT INTO books (title, price, rating)
        VALUES (?, ?, ?)
    """, (book["title"], book["price"], book["rating"]))
    print(f"追加: {book['title']}")

conn.commit()
print(f"合計 {len(books)} 件保存しました")

# 3. 評価が3以上の本を検索
print("\n=== 3. 評価3以上の本 ===")
cursor.execute("SELECT * FROM books WHERE rating >= ?", (3,))
high_rated = cursor.fetchall()

for row in high_rated:
    print(f"  {row['title']} (評価: {row['rating']}, 価格: £{row['price']})")

# 4. 平均価格を計算
print("\n=== 4. 統計情報 ===")
cursor.execute("SELECT AVG(price) as avg_price FROM books")
avg_price = cursor.fetchone()['avg_price']
print(f"平均価格: £{avg_price:.2f}")

# おまけ: 評価別の平均価格
print("\n=== おまけ: 評価別の平均価格 ===")
cursor.execute("""
    SELECT rating, AVG(price) as avg_price, COUNT(*) as count
    FROM books
    GROUP BY rating
    ORDER BY rating DESC
""")
rows = cursor.fetchall()

for row in rows:
    print(f"  評価{row['rating']}: £{row['avg_price']:.2f} ({row['count']}冊)")

conn.close()
```

### 出力

```
=== 1. テーブル作成 ===
テーブルを作成しました

=== 2. データ保存 ===
追加: A Light in the Attic
追加: Tipping the Velvet
追加: Soumission
追加: Sharp Objects
追加: Sapiens
合計 5 件保存しました

=== 3. 評価3以上の本 ===
  A Light in the Attic (評価: 3, 価格: £51.77)
  Sharp Objects (評価: 4, 価格: £47.82)
  Sapiens (評価: 5, 価格: £54.23)

=== 4. 統計情報 ===
平均価格: £51.53

=== おまけ: 評価別の平均価格 ===
  評価5: £54.23 (1冊)
  評価4: £47.82 (1冊)
  評価3: £51.77 (1冊)
  評価1: £51.92 (2冊)
```

### なぜこう書くの？

```python
# REAL 型 = 小数を保存できる
price REAL

# GROUP BY = グループ化
SELECT rating, AVG(price)
FROM books
GROUP BY rating
# → 評価ごとに平均価格を計算

# ORDER BY = 並び替え
ORDER BY rating DESC  # 降順（大きい順）
ORDER BY rating ASC   # 昇順（小さい順）
```

### スクレイピング → データベース保存のパターン

```python
import requests
from bs4 import BeautifulSoup
import sqlite3

# 1. スクレイピング
url = "https://books.toscrape.com"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# 2. データ抽出
books = []
for article in soup.select("article.product_pod"):
    title = article.select_one("h3 a")["title"]
    price = float(article.select_one(".price_color").text.replace("£", ""))
    books.append({"title": title, "price": price})

# 3. データベースに保存
conn = sqlite3.connect("books.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY,
        title TEXT UNIQUE,
        price REAL
    )
""")

for book in books:
    cursor.execute("""
        INSERT OR IGNORE INTO books (title, price)
        VALUES (?, ?)
    """, (book["title"], book["price"]))

conn.commit()
conn.close()
```

---

## 📝 問題5の解答：データベースの内容をCSV出力

### 方法1: csv モジュールを使う

```python
import sqlite3
import csv

# データベースから取得
conn = sqlite3.connect("books_scraping.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT * FROM books")
rows = cursor.fetchall()

# CSVに保存
with open("books_export.csv", "w", newline="", encoding="utf-8") as f:
    # 列名を取得
    fieldnames = rows[0].keys()

    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    # データを書き込み
    for row in rows:
        writer.writerow(dict(row))

print(f"books_export.csv に {len(rows)} 件保存しました")

conn.close()

# 確認
with open("books_export.csv", "r", encoding="utf-8") as f:
    print(f.read())
```

### 方法2: pandas を使う（推奨）

```python
import sqlite3
import pandas as pd

# データベースに接続
conn = sqlite3.connect("books_scraping.db")

# データベースから読み込み
df = pd.read_sql("SELECT * FROM books", conn)

print("=== DataFrame ===")
print(df)

# CSVに保存
df.to_csv("books_export.csv", index=False, encoding="utf-8")
print(f"\nbooks_export.csv に {len(df)} 件保存しました")

conn.close()
```

### 出力（CSV）

```csv
id,title,price,rating
1,A Light in the Attic,51.77,3
2,Tipping the Velvet,53.74,1
3,Soumission,50.1,1
4,Sharp Objects,47.82,4
5,Sapiens,54.23,5
```

### なぜこう書くの？

```python
# sqlite3.Row = 辞書のようにアクセス
conn.row_factory = sqlite3.Row
# → row['title'], row['price'] で取得できる
# → row.keys() で列名が取得できる

# pandas で読み込み
df = pd.read_sql("SELECT * FROM books", conn)
# → SQL の結果を DataFrame に変換
# → すぐに to_csv() で保存できる
```

### データベース ↔ CSV/JSON の変換まとめ

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect("data.db")

# CSV → データベース
df = pd.read_csv("data.csv")
df.to_sql("table_name", conn, if_exists="replace", index=False)

# データベース → CSV
df = pd.read_sql("SELECT * FROM table_name", conn)
df.to_csv("data.csv", index=False)

# データベース → JSON
df = pd.read_sql("SELECT * FROM table_name", conn)
df.to_json("data.json", orient="records", force_ascii=False, indent=2)
```

---

## 💡 今回のポイントまとめ

### SQLite の基本

```python
import sqlite3

# 接続
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# テーブル作成
cursor.execute("""
    CREATE TABLE IF NOT EXISTS table_name (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        value INTEGER
    )
""")

# 挿入
cursor.execute("INSERT INTO table_name (name, value) VALUES (?, ?)", (name, value))
conn.commit()

# 取得
cursor.execute("SELECT * FROM table_name WHERE value > ?", (100,))
rows = cursor.fetchall()

# 更新
cursor.execute("UPDATE table_name SET value = ? WHERE id = ?", (200, 1))
conn.commit()

# 削除
cursor.execute("DELETE FROM table_name WHERE id = ?", (1,))
conn.commit()

# 閉じる
conn.close()
```

### 重複チェック

```python
# 方法1: 事前チェック
cursor.execute("SELECT COUNT(*) FROM books WHERE title = ?", (title,))
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT ...")

# 方法2: UNIQUE + INSERT OR IGNORE
cursor.execute("CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT UNIQUE)")
cursor.execute("INSERT OR IGNORE INTO books (title) VALUES (?)", (title,))
```

### SQL の基本構文

| 操作 | SQL |
|------|-----|
| 挿入 | `INSERT INTO テーブル (列) VALUES (値)` |
| 取得 | `SELECT * FROM テーブル WHERE 条件` |
| 更新 | `UPDATE テーブル SET 列 = 値 WHERE 条件` |
| 削除 | `DELETE FROM テーブル WHERE 条件` |
| 件数 | `SELECT COUNT(*) FROM テーブル` |
| 平均 | `SELECT AVG(列) FROM テーブル` |

---

## 🔍 よくある間違い

### ❌ commit() を忘れる

```python
# 間違い
cursor.execute("INSERT INTO books (title, price) VALUES (?, ?)", (title, price))
# commit() がない → 保存されない

# 正しい
cursor.execute("INSERT INTO books (title, price) VALUES (?, ?)", (title, price))
conn.commit()  # これが必要！
```

---

### ❌ プレースホルダーを使わない

```python
# ❌ 危険（SQLインジェクション攻撃のリスク）
title = "Python入門"
cursor.execute(f"INSERT INTO books (title) VALUES ('{title}')")

# ✅ 安全
cursor.execute("INSERT INTO books (title) VALUES (?)", (title,))
```

---

### ❌ fetchone() と fetchall() を間違える

```python
# fetchone() = 1行だけ取得（タプル）
cursor.execute("SELECT * FROM books WHERE id = 1")
row = cursor.fetchone()
print(row[0])  # OK

# fetchall() = すべて取得（リスト）
cursor.execute("SELECT * FROM books")
rows = cursor.fetchall()
print(rows[0][0])  # OK

# 間違い：複数行を処理したいなら fetchall() を使う
cursor.execute("SELECT * FROM books")
row = cursor.fetchone()  # 最初の1件だけ取得
print(row)  # 1行だけ出力される

# 正しい：複数行を処理したいなら fetchall() を使う
cursor.execute("SELECT * FROM books")
rows = cursor.fetchall()
for row in rows:
    print(row)  # すべての行を処理できる
```

---

### ❌ 接続を閉じ忘れる

```python
# 間違い
conn = sqlite3.connect("db.db")
# ... 処理 ...
# conn.close() がない → ファイルロックされる

# 正しい
with sqlite3.connect("db.db") as conn:
    # ... 処理 ...
    conn.commit()  # 変更を確定
# コンテキストマネージャーが自動的に close() と rollback を処理
```

---

## 🔧 実践的なテクニック

### 1. トランザクション

```python
try:
    cursor.execute("INSERT INTO books ...")
    cursor.execute("UPDATE stock ...")
    conn.commit()  # 両方成功したら確定
except Exception as e:
    conn.rollback()  # エラーなら取り消し
    print(f"エラー: {e}")
```

### 2. 一括挿入

```python
# executemany() で高速化
books = [
    ("Python入門", 2800),
    ("データ分析", 3200),
    ("機械学習", 3500),
]

cursor.executemany("""
    INSERT INTO books (title, price) VALUES (?, ?)
""", books)
conn.commit()
```

### 3. インデックスで高速化

```python
# よく検索する列にインデックスを作成
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_title
    ON books(title)
""")
# → title での検索が高速になる
```

### 4. 外部キー（リレーション）

```python
# 著者テーブル
cursor.execute("""
    CREATE TABLE authors (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
""")

# 書籍テーブル（author_id で関連付け）
cursor.execute("""
    CREATE TABLE books (
        id INTEGER PRIMARY KEY,
        title TEXT,
        author_id INTEGER,
        FOREIGN KEY (author_id) REFERENCES authors(id)
    )
""")

# JOIN で結合
cursor.execute("""
    SELECT books.title, authors.name
    FROM books
    JOIN authors ON books.author_id = authors.id
""")
```

### 5. バックアップ

```python
import sqlite3
import shutil

# ファイルをコピー
shutil.copy("books.db", "books_backup.db")

# または SQL で
source = sqlite3.connect("books.db")
dest = sqlite3.connect("books_backup.db")
source.backup(dest)
dest.close()
source.close()
```

---

## 🎓 もっと知りたい人向け

### SQLAlchemy（ORM）

```python
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True, nullable=False)
    price = Column(Float)

# データベース作成
engine = create_engine("sqlite:///books.db")
Base.metadata.create_all(engine)

# セッション作成
Session = sessionmaker(bind=engine)
session = Session()

# データ追加
book = Book(title="Python入門", price=2800)
session.add(book)
session.commit()

# データ取得
books = session.query(Book).filter(Book.price > 3000).all()
for book in books:
    print(book.title, book.price)

# データ更新
book = session.query(Book).filter_by(id=1).first()
book.price = 3000
session.commit()

# データ削除
session.query(Book).filter_by(id=1).delete()
session.commit()
```

### DB Browser for SQLite

GUIでデータベースを確認できる無料ツール:
- https://sqlitebrowser.org/
- テーブルの中身を視覚的に確認できる
- SQLを書かずにデータを編集できる

---

**次回は「総合演習②」です！**
