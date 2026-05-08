# 第12回：総合演習② - 完全なスクレイピングパイプライン【解答・解説】

この解答は、問題に対する一例です。動作すれば、別の書き方でも正解です。

---

## 問題1：複数ページからデータ取得【解答】

```python
import requests
from bs4 import BeautifulSoup
import csv
import time
import re

def fetch_page(url):
    """ページを取得する"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"エラー: {e}")
        return None

def parse_books(html):
    """HTMLから書籍情報を抽出する"""
    soup = BeautifulSoup(html, "html.parser")
    books = []

    for book in soup.select("article.product_pod"):
        try:
            # タイトルを取得
            title = book.select_one("h3 a")["title"]

            # 価格を取得して数値に変換
            price_text = book.select_one(".price_color").text
            # 正規表現で数字とドットだけを抽出（制御文字や通貨記号を除去）
            price_match = re.search(r'\d+\.?\d*', price_text)
            price = float(price_match.group()) if price_match else 0.0

            # 評価を取得
            rating_element = book.select_one(".star-rating")
            rating = rating_element["class"][1]

            books.append({
                "title": title,
                "price": price,
                "rating": rating
            })
        except (AttributeError, KeyError) as e:
            print(f"書籍の解析エラー: {e}")
            continue

    return books

def scrape_multiple_pages(num_pages):
    """複数ページから書籍を取得"""
    all_books = []

    for page_num in range(1, num_pages + 1):
        url = f"https://books.toscrape.com/catalogue/page-{page_num}.html"
        print(f"ページ {page_num}/{num_pages} を取得中...")

        html = fetch_page(url)
        if html:
            books = parse_books(html)
            all_books.extend(books)
            print(f"  → {len(books)}冊取得（累計: {len(all_books)}冊）")
        else:
            print(f"  → ページ {page_num} の取得に失敗")

        # サーバーに負荷をかけないよう待機
        if page_num < num_pages:  # 最後のページでは待機不要
            time.sleep(1)

    return all_books

def save_to_csv(books, filename):
    """書籍データをCSVに保存する"""
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "price", "rating"])
        writer.writeheader()
        writer.writerows(books)
    print(f"\n{filename} に {len(books)}冊を保存しました")

# メイン処理
if __name__ == "__main__":
    print("=" * 60)
    print("書籍スクレイピング - 複数ページ取得")
    print("=" * 60)

    all_books = scrape_multiple_pages(5)
    save_to_csv(all_books, "books_all.csv")

    print("\n" + "=" * 60)
    print(f"✅ 完了! 合計 {len(all_books)} 冊を取得しました")
    print("=" * 60)
```

### 解説

#### ポイント1: エラー処理

```python
try:
    title = book.select_one("h3 a")["title"]
    # ...
except (AttributeError, KeyError) as e:
    print(f"書籍の解析エラー: {e}")
    continue  # このデータはスキップして次へ
```

一部のデータが取得できなくても、プログラム全体が止まらないようにしています。

#### ポイント2: 進捗表示

```python
print(f"ページ {page_num}/{num_pages} を取得中...")
print(f"  → {len(books)}冊取得（累計: {len(all_books)}冊）")
```

現在の進捗と累計を表示することで、どこまで進んでいるか分かりやすくなります。

#### ポイント3: 適切な待機

```python
if page_num < num_pages:  # 最後のページでは待機不要
    time.sleep(1)
```

ページ間で1秒待機することで、サーバーに負荷をかけないようにしています。

---

## 問題2：データベースへの保存【解答】

```python
import sqlite3

def create_database(db_name):
    """データベースとテーブルを作成"""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()

        # テーブルを作成（重複防止のため title に UNIQUE 制約）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                price REAL,
                rating TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

    print(f"{db_name} を作成しました")

def save_to_database(books, db_name):
    """書籍データをデータベースに保存"""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()

        # データを挿入（重複は無視）
        for book in books:
            cursor.execute("""
                INSERT OR IGNORE INTO books (title, price, rating)
                VALUES (?, ?, ?)
            """, (book["title"], book["price"], book["rating"]))

        conn.commit()

    print(f"{db_name} に {len(books)}冊を保存しました")

def query_database(db_name):
    """データベースから高額な書籍を検索"""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()

        # 価格が50以上の書籍を検索
        cursor.execute("""
            SELECT title, price, rating
            FROM books
            WHERE price >= 50
            ORDER BY price DESC
        """)

        results = cursor.fetchall()

    print(f"\n価格が50以上の書籍: {len(results)}冊")
    print("-" * 80)
    for title, price, rating in results[:10]:  # 最初の10冊だけ表示
        print(f"£{price:6.2f} | {rating:5s} | {title}")

# 実行
if __name__ == "__main__":
    # 問題1のコードを実行してデータ取得
    all_books = scrape_multiple_pages(5)

    # データベースに保存
    create_database("books.db")
    save_to_database(all_books, "books.db")

    # 検索
    query_database("books.db")
```

### 解説

#### SQLiteの基本構造

```python
# 1. 接続
conn = sqlite3.connect("books.db")
cursor = conn.cursor()

# 2. SQL実行
cursor.execute("SELECT * FROM books")

# 3. 結果取得
results = cursor.fetchall()  # すべて取得
# または
result = cursor.fetchone()   # 1件だけ取得

# 4. 保存して切断
conn.commit()  # データを保存（INSERTやUPDATE時）
conn.close()   # 接続を閉じる
```

#### プレースホルダーの使用

```python
# 良い例: プレースホルダーを使う（SQLインジェクション対策）
cursor.execute("""
    INSERT INTO books (title, price) VALUES (?, ?)
""", (title, price))

# 悪い例: 文字列連結（危険！）
cursor.execute(f"""
    INSERT INTO books (title, price) VALUES ('{title}', {price})
""")
```

`?` を使うと、SQLインジェクション攻撃を防げます。

#### created_at カラムの追加

```python
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

いつデータを挿入したかが自動的に記録されます。

---

## 問題3：評価別の集計【解答】

```python
def aggregate_by_rating(db_name):
    """評価別に書籍数を集計"""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()

        # 評価別に集計
        cursor.execute("""
            SELECT rating, COUNT(*) as count
            FROM books
            GROUP BY rating
            ORDER BY
                CASE rating
                    WHEN 'Five' THEN 1
                    WHEN 'Four' THEN 2
                    WHEN 'Three' THEN 3
                    WHEN 'Two' THEN 4
                    WHEN 'One' THEN 5
                END
        """)

        results = cursor.fetchall()

    print("\n評価別の書籍数:")
    print("-" * 40)
    total = 0
    for rating, count in results:
        print(f"{rating:5s}: {count:3d}冊")
        total += count
    print("-" * 40)
    print(f"合計: {total}冊")

# 実行
if __name__ == "__main__":
    aggregate_by_rating("books.db")
```

### 別解：Pythonで集計

```python
def aggregate_by_rating_python(db_name):
    """Pythonで評価別に集計"""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()

        # すべてのデータを取得
        cursor.execute("SELECT rating FROM books")
        ratings = [row[0] for row in cursor.fetchall()]

    # 辞書で集計
    rating_counts = {}
    for rating in ratings:
        rating_counts[rating] = rating_counts.get(rating, 0) + 1

    # 表示
    print("\n評価別の書籍数:")
    print("-" * 40)
    # 評価の順番を指定
    for rating in ["Five", "Four", "Three", "Two", "One"]:
        count = rating_counts.get(rating, 0)
        print(f"{rating:5s}: {count:3d}冊")
    print("-" * 40)
    print(f"合計: {sum(rating_counts.values())}冊")
```

### 解説

#### SQLでの集計

```sql
SELECT rating, COUNT(*) as count
FROM books
GROUP BY rating
```

- `GROUP BY rating`: rating カラムでグループ化
- `COUNT(*)`: 各グループの行数をカウント

#### 順序の制御

```sql
ORDER BY
    CASE rating
        WHEN 'Five' THEN 1
        WHEN 'Four' THEN 2
        WHEN 'Three' THEN 3
        WHEN 'Two' THEN 4
        WHEN 'One' THEN 5
    END
```

評価が文字列なので、CASE文を使って並び順を指定しています。

---

## 問題4：進捗バーの実装【解答】

```python
from tqdm import tqdm
import time
import requests
from bs4 import BeautifulSoup
import re

def scrape_with_progress(num_pages):
    """進捗バー付きでスクレイピング"""
    all_books = []

    # tqdm() を使ってプログレスバーを表示
    for page_num in tqdm(range(1, num_pages + 1), desc="ページ取得中", unit="ページ"):
        url = f"https://books.toscrape.com/catalogue/page-{page_num}.html"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            html = response.text

            soup = BeautifulSoup(html, "html.parser")
            books = []

            for book in soup.select("article.product_pod"):
                try:
                    title = book.select_one("h3 a")["title"]
                    price_text = book.select_one(".price_color").text
                    # 正規表現で数字とドットだけを抽出（制御文字や通貨記号を除去）
                    price_match = re.search(r'\d+\.?\d*', price_text)
                    price = float(price_match.group()) if price_match else 0.0
                    rating = book.select_one(".star-rating")["class"][1]

                    books.append({
                        "title": title,
                        "price": price,
                        "rating": rating
                    })
                except (AttributeError, KeyError, ValueError) as e:
                    # HTML構造変化などの解析エラー
                    tqdm.write(f"ページ {page_num} の書籍解析エラー: {e}")
                    continue

            all_books.extend(books)

        except requests.exceptions.RequestException as e:
            # ネットワークエラー
            tqdm.write(f"ページ {page_num} でネットワークエラー: {e}")

        time.sleep(1)

    return all_books

# 実行
if __name__ == "__main__":
    all_books = scrape_with_progress(10)
    print(f"\n合計 {len(all_books)} 冊を取得しました")
```

### 解説

#### tqdm の基本的な使い方

```python
from tqdm import tqdm

# リストをループ
for item in tqdm([1, 2, 3, 4, 5]):
    # 処理
    pass

# range をループ
for i in tqdm(range(100)):
    # 処理
    pass
```

#### パラメータ

```python
tqdm(
    iterable,           # ループする対象
    desc="説明",        # 進捗バーの説明
    unit="単位",        # 単位（デフォルトは "it"）
    total=100,          # 総数（自動計算されることもある）
    ncols=80,           # 進捗バーの幅
    disable=False       # True にすると進捗バーを非表示
)
```

#### tqdm.write() の使用

```python
# 悪い例: print() を使うと進捗バーが崩れる
for i in tqdm(range(10)):
    print("メッセージ")  # 進捗バーが崩れる

# 良い例: tqdm.write() を使う
for i in tqdm(range(10)):
    tqdm.write("メッセージ")  # 進捗バーの上に表示される
```

---

## 問題5：完全なパイプラインの構築【解答】

```python
import requests
from bs4 import BeautifulSoup
import csv
import sqlite3
import time
from tqdm import tqdm
import logging
import re

class BookScraper:
    """書籍スクレイピングシステム"""

    def __init__(self, base_url="https://books.toscrape.com"):
        self.base_url = base_url
        self.rating_map = {
            "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
        }

        # ログ設定
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("scraping.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def fetch_page(self, url, max_retries=3):
        """リトライ機能付きでページを取得"""
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as e:
                self.logger.warning(
                    f"ページ取得エラー（試行 {attempt}/{max_retries}）: {e}"
                )
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # 指数バックオフ: 2, 4, 8秒
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"ページ取得失敗: {url}")
                    return None

    def parse_books(self, html):
        """HTMLから書籍情報を抽出して整形"""
        soup = BeautifulSoup(html, "html.parser")
        books = []

        for book in soup.select("article.product_pod"):
            try:
                # タイトルを取得
                title = book.select_one("h3 a")["title"]

                # 価格を取得して数値に変換
                price_text = book.select_one(".price_color").text
                # 正規表現で数字とドットだけを抽出（制御文字や通貨記号を除去）
                price_match = re.search(r'\d+\.?\d*', price_text)
                price = float(price_match.group()) if price_match else 0.0

                # 評価を取得して数値に変換
                rating_element = book.select_one(".star-rating")
                rating_text = rating_element["class"][1]
                rating = self.rating_map.get(rating_text, 0)

                books.append({
                    "title": title,
                    "price": price,
                    "rating": rating
                })

            except (AttributeError, KeyError, ValueError) as e:
                self.logger.warning(f"書籍の解析エラー: {e}")
                continue

        return books

    def scrape(self, num_pages):
        """複数ページから書籍を取得"""
        all_books = []

        self.logger.info(f"{num_pages}ページの取得を開始")

        # tqdm で進捗表示
        for page_num in tqdm(
            range(1, num_pages + 1),
            desc="ページ取得中",
            unit="ページ"
        ):
            url = f"{self.base_url}/catalogue/page-{page_num}.html"

            html = self.fetch_page(url)
            if html:
                books = self.parse_books(html)
                all_books.extend(books)
                self.logger.debug(
                    f"ページ {page_num}: {len(books)}冊取得（累計: {len(all_books)}冊）"
                )

            # 最後のページ以外は待機
            if page_num < num_pages:
                time.sleep(1)

        self.logger.info(f"取得完了: 合計 {len(all_books)}冊")
        return all_books

    def save_to_csv(self, books, filename):
        """CSVに保存"""
        try:
            with open(filename, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["title", "price", "rating"]
                )
                writer.writeheader()
                writer.writerows(books)

            self.logger.info(f"CSV保存完了: {filename} ({len(books)}冊)")

        except IOError as e:
            self.logger.error(f"CSV保存エラー: {e}")

    def save_to_database(self, books, db_name):
        """SQLiteに保存"""
        try:
            with sqlite3.connect(db_name) as conn:
                cursor = conn.cursor()

                # テーブルを作成（重複防止のため title に UNIQUE 制約）
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS books (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL UNIQUE,
                        price REAL,
                        rating INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # データを挿入（重複は無視）
                for book in books:
                    cursor.execute("""
                        INSERT OR IGNORE INTO books (title, price, rating)
                        VALUES (?, ?, ?)
                    """, (book["title"], book["price"], book["rating"]))

                conn.commit()

            self.logger.info(f"DB保存完了: {db_name} ({len(books)}冊)")

        except sqlite3.Error as e:
            self.logger.error(f"DB保存エラー: {e}")

    def get_statistics(self, books):
        """統計情報を取得"""
        if not books:
            return {}

        prices = [book["price"] for book in books]
        ratings = [book["rating"] for book in books]

        return {
            "total": len(books),
            "avg_price": sum(prices) / len(prices),
            "max_price": max(prices),
            "min_price": min(prices),
            "avg_rating": sum(ratings) / len(ratings),
        }

    def run(self, num_pages=5):
        """パイプライン全体を実行"""
        start_time = time.time()

        print("=" * 60)
        print("📚 書籍スクレイピングシステム")
        print("=" * 60)
        print(f"対象ページ数: {num_pages}")
        print()

        # データ取得
        books = self.scrape(num_pages)

        if not books:
            self.logger.error("データが取得できませんでした")
            return

        # 統計情報
        stats = self.get_statistics(books)

        # 保存
        self.save_to_csv(books, "books_complete.csv")
        self.save_to_database(books, "books_complete.db")

        # 結果表示
        elapsed_time = time.time() - start_time

        print("\n" + "=" * 60)
        print("✅ 完了!")
        print("=" * 60)
        print(f"取得冊数    : {stats['total']:,}冊")
        print(f"平均価格    : £{stats['avg_price']:.2f}")
        print(f"最高価格    : £{stats['max_price']:.2f}")
        print(f"最低価格    : £{stats['min_price']:.2f}")
        print(f"平均評価    : {stats['avg_rating']:.2f}/5.0")
        print(f"実行時間    : {elapsed_time:.2f}秒")
        print(f"1冊あたり   : {elapsed_time/stats['total']:.2f}秒")
        print("=" * 60)
        print(f"保存先:")
        print(f"  - books_complete.csv")
        print(f"  - books_complete.db")
        print(f"  - scraping.log")
        print("=" * 60)

# 実行
if __name__ == "__main__":
    scraper = BookScraper()
    scraper.run(num_pages=10)
```

### 解説

#### クラスの設計

```python
class BookScraper:
    def __init__(self):
        # 初期化処理
        self.base_url = "https://books.toscrape.com"
        self.rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    def fetch_page(self):
        # ページ取得
        pass

    def parse_books(self):
        # データ解析
        pass

    def save_to_csv(self):
        # CSV保存
        pass

    def run(self):
        # 全体の制御
        pass
```

各メソッドが1つの責任だけを持つように設計しています。

#### 指数バックオフ

```python
wait_time = 2 ** attempt  # 2, 4, 8秒
```

リトライ時の待機時間を指数的に増やすことで、サーバーへの負荷を軽減します。

#### ログの設定

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("scraping.log"),  # ファイルに記録
        logging.StreamHandler()                # コンソールに表示
    ]
)
```

ログをファイルとコンソールの両方に出力します。

#### 統計情報の計算

```python
def get_statistics(self, books):
    prices = [book["price"] for book in books]
    return {
        "avg_price": sum(prices) / len(prices),
        "max_price": max(prices),
        "min_price": min(prices),
    }
```

取得したデータの統計を計算して表示します。

---

## よくある間違いと対処法

### 間違い1: commitを忘れる

```python
# 間違い: commit() がないとデータが保存されない
conn = sqlite3.connect("books.db")
cursor = conn.cursor()
cursor.execute("INSERT INTO books (title, price) VALUES (?, ?)", (title, price))
conn.close()  # データが保存されない！

# 正しい
conn = sqlite3.connect("books.db")
cursor.execute("INSERT INTO ...")
conn.commit()  # これを忘れずに
conn.close()
```

### 間違い2: closeを忘れる

```python
# 間違い: close() しないと接続が残る
conn = sqlite3.connect("books.db")
# ...処理...
# close() を忘れる

# 正しい: with文を使うと自動でclose()される
with sqlite3.connect("books.db") as conn:
    # ...処理...
    # 自動的にclose()される
```

### 間違い3: エラー時に処理が止まる

```python
# 間違い: 1件でもエラーがあると全体が止まる
for book in books:
    title = book.select_one("h3 a")["title"]  # エラーで停止
    # ...

# 正しい: try-exceptで個別にエラー処理
for book in books:
    try:
        title = book.select_one("h3 a")["title"]
        # ...
    except (AttributeError, KeyError):
        continue  # このデータはスキップして次へ
```

---

## 発展課題の解答例

### 発展1: カテゴリー別の取得

```python
def scrape_category(self, category_name, num_pages=5):
    """特定のカテゴリーの書籍を取得"""
    # カテゴリー名をURLに変換
    # 例: "Travel" → "travel_2"
    category_url = f"{self.base_url}/catalogue/category/books/{category_name.lower()}_2/index.html"

    # 以降は通常のスクレイピングと同じ
    # ...
```

### 発展2: 詳細ページの情報取得

```python
def fetch_book_detail(self, detail_url):
    """書籍の詳細ページから追加情報を取得"""
    html = self.fetch_page(detail_url)
    if not html:
        return {}

    soup = BeautifulSoup(html, "html.parser")

    # 説明文を取得
    description = ""
    desc_element = soup.select_one("#product_description + p")
    if desc_element:
        description = desc_element.text.strip()

    # 在庫数を取得
    stock_text = soup.select_one(".instock.availability").text.strip()
    # "In stock (22 available)" から数字を抽出
    import re
    stock_match = re.search(r"\((\d+) available\)", stock_text)
    stock = int(stock_match.group(1)) if stock_match else 0

    return {
        "description": description,
        "stock": stock
    }
```

---

## まとめ

この演習では、以下の技術を統合しました。躓いたときは、対応する回の教材を見直すと解決できます：

**基本技術（カリキュラムで学んだもの）:**

1. **データ取得**: requests でHTTPリクエスト（第5回 → try-except でエラー処理）
2. **データ解析**: BeautifulSoup でHTML解析（第6回 → 要素の抽出と属性アクセス）
3. **要素取得**: CSSセレクタで効率的に検索（第7回 → 効率的な要素検索）
4. **データ整形**: 正規表現や型変換（第9回 → 型変換（str → float）と正規表現）
5. **データ保存**: CSV、SQLite（第10回・第11回 → ファイル操作とデータベース操作）
6. **エラー処理**: try-except、リトライ（第5回で学んだ try-except をさらに活用）

**発展的なテクニック（この回で紹介）:**

- **進捗表示**: tqdm
- **ログ記録**: logging
- **コード構造**: クラス設計（自走学習で習得）

基本技術を組み合わせることで、実践的なスクレイピングシステムを構築できます。発展的なテクニックは、プロジェクトで必要に応じて導入してください。

**次のステップ:**
- より複雑なサイトに挑戦
- 非同期処理で高速化
- データ分析や可視化
- Webアプリケーションとの統合
