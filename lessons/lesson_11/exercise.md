# 第11回：データベース保存 - SQLite入門

## 今回のゴール

- データベースとは何かがわかる
- SQLiteにデータを保存できる
- データを検索・更新・削除できる
- 重複チェックができる
- スクレイピングデータをデータベースで管理できる

## 所要時間：90分

---

## 11.1 導入：なぜデータベースが必要なのか

前回、CSVやJSONファイルにデータを保存する方法を学びました。これらは手軽で便利ですが、以下のような場面では不便です。

### CSVやJSONファイルの課題

| 課題 | （例） |
|------|--------|
| 重複チェックが大変 | 毎日スクレイピングして蓄積する場合 |
| 大量データで遅い | 数万件のデータから検索 |
| 更新が難しい | 価格を更新したい |
| 複雑な検索ができない | 「価格が1000円以上で評価4以上」のような条件 |

### データベースを使うメリット

| メリット | 説明 |
|---------|------|
| 高速な検索 | インデックスにより大量データでも高速 |
| 重複チェックが簡単 | データが既にあるか即座に判定 |
| 更新・削除が容易 | 特定のデータだけ変更できる |
| 複雑な検索 | 条件を組み合わせた検索が可能 |
| データの整合性 | 不正なデータを防げる |

### SQLiteとは

**SQLite**は、ファイル1つで動作する軽量なデータベースです。

#### SQLiteの特徴

| 特徴 | 説明 |
|------|------|
| インストール不要 | Pythonに標準で付属 |
| 軽量 | 1つのファイルで完結 |
| サーバー不要 | 複雑な設定がいらない |
| 十分高速 | 個人プロジェクトには十分 |

#### SQLiteが向いている場面

```
○ 向いている:
- 個人プロジェクト、学習用
- 数万〜数十万件のデータ
- 単一ユーザー

△ 向いていない:
- 大規模Webサービス（MySQL/PostgreSQLを使う）
- 複数ユーザーの同時書き込みが多い
```

---

## 11.2 ハンズオン：SQLiteを使ってみよう

以下のコードをファイルに保存して実行してください。

```python
import sqlite3

# データベースに接続（ファイルがなければ作成される）
conn = sqlite3.connect("books.db")
cursor = conn.cursor()

# テーブルを作成
cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT,
        price INTEGER
    )
""")

# データを挿入
cursor.execute("""
    INSERT INTO books (title, author, price)
    VALUES (?, ?, ?)
""", ("Python入門", "田中太郎", 2800))

cursor.execute("""
    INSERT INTO books (title, author, price)
    VALUES (?, ?, ?)
""", ("データ分析", "佐藤花子", 3200))

# 変更を確定
conn.commit()

# データを取得
cursor.execute("SELECT * FROM books")
rows = cursor.fetchall()

print("=== 書籍一覧 ===")
for row in rows:
    print(f"ID: {row[0]}, タイトル: {row[1]}, 著者: {row[2]}, 価格: {row[3]}円")

# 接続を閉じる
conn.close()
```

実行すると、`books.db` というファイルが作成され、書籍データが保存されます。

---

## 解説

### データベースの基本概念

#### テーブル（表）

データベースは**テーブル**という表形式でデータを管理します。

```
books テーブル:
+----+------------------+------------+-------+
| id | title            | author     | price |
+----+------------------+------------+-------+
|  1 | Python入門       | 田中太郎   | 2800  |
|  2 | データ分析       | 佐藤花子   | 3200  |
+----+------------------+------------+-------+
```

| 用語 | 意味 | 例 |
|------|------|-----|
| テーブル | データの集まり | `books` |
| 行（レコード） | 1件のデータ | 1冊の本 |
| 列（カラム） | データの項目 | `title`, `price` |
| 主キー（Primary Key） | 各行を一意に識別するID | `id` |

#### SQL（Structured Query Language）

データベースを操作するための言語を**SQL**（エスキューエル、Structured Query Language）と呼びます。

```sql
-- データを挿入
INSERT INTO books (title, price) VALUES ('Python入門', 2800);

-- データを取得
SELECT * FROM books;

-- データを更新
-- SQLはone-based indexのため、id=1は一番最初の要素を指している
UPDATE books SET price = 3000 WHERE id = 1;

-- データを削除
DELETE FROM books WHERE id = 1;
```

### sqlite3モジュールの基本

Pythonの標準ライブラリ `sqlite3` を使ってSQLiteを操作します。

#### 基本的な流れ

```python
import sqlite3

# 1. データベースに接続
conn = sqlite3.connect("database.db")

# 2. カーソルを作成
cursor = conn.cursor()

# 3. SQLを実行
cursor.execute("SQL文")

# 4. 変更を確定（INSERT/UPDATE/DELETEの場合）
conn.commit()

# 5. 接続を閉じる
conn.close()
```

#### テーブルの作成

```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT,
        price INTEGER
    )
""")
```

**各部分の意味:**

| 部分 | 意味 |
|------|------|
| `CREATE TABLE IF NOT EXISTS` | テーブルがなければ作成 |
| `books` | テーブル名 |
| `id INTEGER PRIMARY KEY AUTOINCREMENT` | 自動で増える主キー |
| `title TEXT NOT NULL` | 文字列型、必須 |
| `author TEXT` | 文字列型、省略可 |
| `price INTEGER` | 整数型 |

#### データ型

| SQLiteの型 | Pythonの型 | 例 |
|-----------|-----------|-----|
| `INTEGER` | `int` | 1, 100 |
| `REAL` | `float` | 3.14 |
| `TEXT` | `str` | "Python" |
| `BLOB` | `bytes` | バイナリデータ |
| `NULL` | `None` | None |

### CRUD操作

データベースの基本操作は**CRUD**と呼ばれます。

| 操作 | SQL | 意味 |
|------|-----|------|
| **C**reate | INSERT | データを挿入 |
| **R**ead | SELECT | データを取得 |
| **U**pdate | UPDATE | データを更新 |
| **D**elete | DELETE | データを削除 |

#### Create（挿入）

```python
# A: ?プレースホルダー（推奨）
cursor.execute("""
    INSERT INTO books (title, author, price)
    VALUES (?, ?, ?)
""", ("Python入門", "田中太郎", 2800))

# B: 名前付きプレースホルダー
cursor.execute("""
    INSERT INTO books (title, author, price)
    VALUES (:title, :author, :price)
""", {"title": "Python入門", "author": "田中太郎", "price": 2800})

# 変更を確定
conn.commit()
```

**重要:** `?` を使ってプレースホルダーにすることで、SQLインジェクション攻撃を防げます。

```python
# ❌ 危険な書き方（絶対にやらない）
title = "Python入門"
cursor.execute(f"INSERT INTO books (title) VALUES ('{title}')")

# ✅ 安全な書き方
cursor.execute("INSERT INTO books (title) VALUES (?)", (title,))
```

#### Read（取得）

```python
# すべてのデータを取得
cursor.execute("SELECT * FROM books")
rows = cursor.fetchall()

for row in rows:
    print(row)  # (1, 'Python入門', '田中太郎', 2800)

# 特定の列だけ取得
cursor.execute("SELECT title, price FROM books")
rows = cursor.fetchall()

# 条件付きで取得
cursor.execute("SELECT * FROM books WHERE price > ?", (3000,))
rows = cursor.fetchall()

# 1件だけ取得
cursor.execute("SELECT * FROM books WHERE id = ?", (1,))
row = cursor.fetchone()
```

#### Update（更新）

```python
# 特定のデータを更新
cursor.execute("""
    UPDATE books
    SET price = ?
    WHERE id = ?
""", (3000, 1))

conn.commit()
```

#### Delete（削除）

```python
# 特定のデータを削除
cursor.execute("DELETE FROM books WHERE id = ?", (1,))
conn.commit()
```

### 重複チェック

スクレイピングでデータを蓄積する場合、同じデータを何度も保存しないようにする必要があります。そこで、重複した際にデータを保存しないようにする操作を紹介します。

#### 方法1: 事前に確認してから挿入

```python
# 既に存在するか確認
cursor.execute("SELECT COUNT(*) FROM books WHERE title = ?", (title,))
count = cursor.fetchone()[0]

if count == 0:
    # 存在しない場合のみ挿入
    cursor.execute("""
        INSERT INTO books (title, author, price)
        VALUES (?, ?, ?)
    """, (title, author, price))
    conn.commit()
    print("新規追加しました")
else:
    print("既に存在します")
```

#### 方法2: UNIQUE制約を使う

```python
# テーブル作成時に UNIQUE 制約を付ける
cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL UNIQUE,
        author TEXT,
        price INTEGER
    )
""")

# 挿入を試みる（重複ならエラー）
try:
    cursor.execute("""
        INSERT INTO books (title, author, price)
        VALUES (?, ?, ?)
    """, (title, author, price))
    conn.commit()
    print("新規追加しました")
except sqlite3.IntegrityError:
    print("既に存在します")
```

#### 方法3: INSERT OR IGNORE

```python
# 重複している場合は無視（エラーにならない）
cursor.execute("""
    INSERT OR IGNORE INTO books (title, author, price)
    VALUES (?, ?, ?)
""", (title, author, price))
conn.commit()
```

#### 方法4: INSERT OR REPLACE（上書き）

```python
# 重複している場合は上書き
cursor.execute("""
    INSERT OR REPLACE INTO books (title, author, price)
    VALUES (?, ?, ?)
""", (title, author, price))
conn.commit()
```

### with文を使った安全な接続

```python
import sqlite3

# with文を使うとトランザクションの処理が自動化される
with sqlite3.connect("books.db") as conn:
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO books (title, price)
        VALUES (?, ?)
    """, ("Python入門", 2800))
    # with を抜ける際に自動的に commit() が実行される
```

### 辞書形式で取得

```python
import sqlite3

conn = sqlite3.connect("books.db")
conn.row_factory = sqlite3.Row  # 辞書形式で取得できるようにする
cursor = conn.cursor()

cursor.execute("SELECT * FROM books")
rows = cursor.fetchall()

for row in rows:
    # 列名でアクセスできる
    print(f"タイトル: {row['title']}, 価格: {row['price']}円")
```

---

## 練習問題

### 11.3 問題1：基本的なCRUD操作

以下の操作を順番に実行してください。

1. `products` テーブルを作成（id, name, price, stock）
2. 3つの商品を挿入
3. すべての商品を表示
4. 特定の商品の価格を更新
5. 特定の商品を削除
6. 最終的なデータを表示

**考え方のヒント:**

```
手順:
1. CREATE TABLE で products テーブルを作成
2. INSERT で3回挿入
3. SELECT * で全件取得
4. UPDATE で価格を変更
5. DELETE で1件削除
6. SELECT * で確認
```

---

### 11.4 問題2：重複チェック付きで保存

以下のデータを重複しないように保存してください。

```python
books = [
    {"title": "Python入門", "author": "田中太郎", "price": 2800},
    {"title": "Python入門", "author": "田中太郎", "price": 2800},  # 重複
    {"title": "データ分析", "author": "佐藤花子", "price": 3200},
    {"title": "Python入門", "author": "田中太郎", "price": 3000},  # 重複（価格違い）
]

# タイトルが同じなら保存しない
# 何件追加されたか表示
```

**考え方のヒント:**

```
方法1: 事前チェック
for book in books:
    cursor.execute("SELECT COUNT(*) FROM books WHERE title = ?", (title,))
    count = cursor.fetchone()[0]
    if count == 0:
        # 挿入

方法2: UNIQUE制約 + try-except
try:
    cursor.execute("INSERT INTO ...")
except sqlite3.IntegrityError:
    # 重複
```

---

### 11.5 問題3：条件検索

問題2で作成したデータベースから、以下の条件で検索してください。

1. 価格が3000円以上の本
2. 著者が「田中太郎」の本
3. タイトルに「Python」が含まれる本
4. 価格の平均値

**考え方のヒント:**

```
# 価格が3000円以上
SELECT * FROM books WHERE price >= 3000

# 著者が「田中太郎」
SELECT * FROM books WHERE author = ?

# タイトルに「Python」が含まれる
SELECT * FROM books WHERE title LIKE ?
# → LIKE '%Python%'

# 平均値
SELECT AVG(price) FROM books
```

---

### 11.6 問題4：スクレイピングデータをデータベースに保存

Books to Scrape から取得した以下のデータをSQLiteに保存してください。

```python
books = [
    {"title": "A Light in the Attic", "price": 51.77, "rating": 3},
    {"title": "Tipping the Velvet", "price": 53.74, "rating": 1},
    {"title": "Soumission", "price": 50.10, "rating": 1},
]

# 1. テーブルを作成
# 2. データを保存
# 3. 評価が3以上の本を検索
# 4. 平均価格を計算
```

**考え方のヒント:**

```
手順:
1. CREATE TABLE books (id, title, price, rating)
2. for で回して INSERT
3. SELECT * FROM books WHERE rating >= 3
4. SELECT AVG(price) FROM books
```

---

### 11.7 問題5：データベースの内容をCSV出力

問題4で作成したデータベースから、すべてのデータを取得してCSVファイルに出力してください。

```python
# 1. データベースからすべてのデータを取得
# 2. CSVファイルに保存（books_export.csv）
```

**考え方のヒント:**

```
手順:
1. SELECT * FROM books でデータ取得
2. csv.DictWriter で保存

または:
1. pandasでデータベースから読み込む
   df = pd.read_sql("SELECT * FROM books", conn)
2. to_csv() で保存
```

---

## 検索キーワード

| 知りたいこと | 検索キーワード |
|-------------|---------------|
| SQLiteの基本 | `Python sqlite3 使い方 初心者` |
| SQL文の書き方 | `SQL 入門 SELECT INSERT` |
| 重複チェック | `SQLite UNIQUE 制約` |
| プレースホルダー | `Python sqlite3 プレースホルダー` |
| pandas連携 | `pandas read_sql to_sql` |
| SQLAlchemy | `Python SQLAlchemy 入門` |

---

## 困ったときは

### 「データベースファイルがロックされている」

```
sqlite3.OperationalError: database is locked
```

**原因:** 別のプログラムやターミナルでデータベースを開いている

**対処法:**
1. 他のプログラムを終了する
2. `conn.close()` を確実に実行する
3. `with` 文を使う

### 「テーブルが既に存在する」

```
sqlite3.OperationalError: table books already exists
```

**対処法:**

```python
# CREATE TABLE に IF NOT EXISTS を付ける
cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT,
        price INTEGER
    )
""")
```

### 「列の数が合わない」

```
sqlite3.OperationalError: table books has 3 columns but 2 values were supplied
```

**対処法:**

```python
# 列名を明示的に指定
INSERT INTO books (title, price) VALUES (?, ?)
# id は AUTOINCREMENT なので指定不要
```

### 「SQL文の書き方が分からない」

基本的なSQLパターン:

```sql
-- 挿入
INSERT INTO テーブル名 (列1, 列2) VALUES (値1, 値2)

-- 取得
SELECT * FROM テーブル名 WHERE 列 = 値

-- 更新
UPDATE テーブル名 SET 列 = 値 WHERE 条件

-- 削除
DELETE FROM テーブル名 WHERE 条件
```

### 「データベースの中身を確認したい」

#### 方法1: Pythonで確認

```python
cursor.execute("SELECT * FROM books")
rows = cursor.fetchall()
for row in rows:
    print(row)
```

#### 方法2: SQLiteツールを使う

- **DB Browser for SQLite** (https://sqlitebrowser.org/)
- GUIでデータベースを見られる無料ツール

---

## 確認事項

- SQLiteとは何かを説明できる
- データベースの基本用語（テーブル、行、列）がわかった
- テーブルを作成できた
- データを挿入・取得・更新・削除できた
- 重複チェックができた
- プレースホルダーの重要性がわかった
- スクレイピングデータをデータベースに保存できた

---

## まとめ：いつデータベースを使うべきか

### データベースを使う場合

- 大量のデータ（数千件以上）
- 定期的にデータを追加・更新する
- 複雑な検索が必要
- 重複チェックが必要

### CSVを使う場合

- 小規模なデータ（数百件以内）
- 一度だけ保存して終わり
- Excelで開きたい
- シンプルな表形式

### JSONを使う場合

- 階層構造のデータ
- API連携
- 設定ファイル

---

## 発展：SQLAlchemy（上級者向け）

より高度な操作には**SQLAlchemy**というライブラリが便利です。

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True)
    price = Column(Integer)

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
```

SQLAlchemyのメリット:
- オブジェクト指向でデータを扱える
- SQL文を書かなくて良い
- データベースの種類（SQLite、MySQL等）を簡単に変更できる

---

**次回は「総合演習②」です。これまでの知識を統合して、データ収集・CSV/SQLite保存・エラー処理・進捗表示を含む完全なスクレイピングシステムを構築します。**
