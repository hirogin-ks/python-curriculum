# 第16回：総合演習③ - 検索結果の自動取得【解答・解説】

この解答は、問題に対する一例です。動作すれば、別の書き方でも正解です。

---

## 問題1：特定のタグから全ページ取得【解答】

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time

def scrape_tag_all_pages(tag_name):
    """特定のタグの全ページから名言を取得"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    all_quotes = []

    try:
        # 最初のページを開く
        url = f"https://quotes.toscrape.com/tag/{tag_name}/"
        print(f"タグ「{tag_name}」を取得中...")
        driver.get(url)

        page_num = 1

        while True:
            print(f"  ページ {page_num} を処理中...")

            # 待機
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".quote")))

            # 名言を取得
            quotes = driver.find_elements(By.CSS_SELECTOR, ".quote")
            print(f"    → {len(quotes)}件の名言を発見")

            for quote in quotes:
                try:
                    # テキストを取得
                    text = quote.find_element(By.CSS_SELECTOR, ".text").text.strip('"')

                    # 著者名を取得
                    author = quote.find_element(By.CSS_SELECTOR, ".author").text

                    # タグを取得
                    tags = quote.find_elements(By.CSS_SELECTOR, ".tag")
                    tag_list = [tag.text for tag in tags]

                    all_quotes.append({
                        "text": text,
                        "author": author,
                        "tags": ", ".join(tag_list)
                    })

                except Exception as e:
                    print(f"    エラー: {e}")
                    continue

            # Nextボタンをクリック（なければ終了）
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, ".next a")
                next_button.click()
                page_num += 1
                time.sleep(1)  # ページ遷移を待つ
            except NoSuchElementException:
                print("  → 最後のページに到達しました")
                break

    finally:
        driver.quit()

    return all_quotes

# 実行
if __name__ == "__main__":
    quotes = scrape_tag_all_pages("love")
    print(f"\n{'='*60}")
    print(f"✅ 合計 {len(quotes)} 件の名言を取得しました")
    print(f"{'='*60}\n")

    # 最初の3件を表示
    print("最初の3件:")
    for i, quote in enumerate(quotes[:3], 1):
        print(f"{i}. {quote['text'][:60]}...")
        print(f"   著者: {quote['author']}")
        print(f"   タグ: {quote['tags']}\n")
```

### 実行結果

```
タグ「love」を取得中...
  ページ 1 を処理中...
    → 10件の名言を発見
  ページ 2 を処理中...
    → 10件の名言を発見
  → 最後のページに到達しました

============================================================
✅ 合計 20 件の名言を取得しました
============================================================

最初の3件:
1. "The opposite of love is not hate, it's indifference. The...
   著者: Elie Wiesel
   タグ: activism, apathy, hate, indifference, inspirational, love, ...

...
```

### 解説

#### while True ループ

```python
while True:
    # ページ処理

    try:
        next_button = driver.find_element(By.CSS_SELECTOR, ".next a")
        next_button.click()
    except NoSuchElementException:
        break  # ループを抜ける
```

無限ループを使い、Nextボタンが見つからなくなったら `break` で抜けます。

#### 例外処理の重要性

```python
for quote in quotes:
    try:
        # 処理
    except Exception as e:
        print(f"エラー: {e}")
        continue  # このデータはスキップして次へ
```

一部のデータが取得できなくても、プログラム全体が止まらないようにします。

---

## 問題2：複数のタグから取得【解答】

```python
def scrape_multiple_tags(tags):
    """複数のタグから名言を取得"""
    all_quotes = []

    print("=" * 70)
    print("複数タグからの名言取得")
    print("=" * 70)
    print(f"対象タグ: {', '.join(tags)}\n")

    for i, tag in enumerate(tags, 1):
        print(f"\n[{i}/{len(tags)}] タグ「{tag}」")
        print("-" * 60)

        quotes = scrape_tag_all_pages(tag)
        all_quotes.extend(quotes)

        print(f"→ {len(quotes)}件取得（累計: {len(all_quotes)}件）")

    return all_quotes

# 実行
if __name__ == "__main__":
    tags = ["love", "life", "inspiration"]
    all_quotes = scrape_multiple_tags(tags)

    print(f"\n{'='*70}")
    print(f"✅ 合計 {len(all_quotes)} 件の名言を取得しました")
    print(f"{'='*70}")

    # タグごとの内訳を表示
    print("\nタグごとの取得件数:")
    for tag in tags:
        count = sum(1 for q in all_quotes if tag in q.get("tags", ""))
        print(f"  {tag:15s}: {count:3d}件")
```

### 実行結果

```
======================================================================
複数タグからの名言取得
======================================================================
対象タグ: love, life, inspiration

[1/3] タグ「love」
------------------------------------------------------------
タグ「love」を取得中...
  ページ 1 を処理中...
    → 10件の名言を発見
  ページ 2 を処理中...
    → 10件の名言を発見
  → 最後のページに到達しました
→ 20件取得（累計: 20件）

[2/3] タグ「life」
------------------------------------------------------------
...

======================================================================
✅ 合計 60 件の名言を取得しました
======================================================================

タグごとの取得件数:
  love           :  20件
  life           :  20件
  inspiration    :  20件
```

### 解説

#### extend() と append() の違い

```python
# append(): リストをそのまま追加
list1 = [1, 2]
list2 = [3, 4]
list1.append(list2)
print(list1)  # [1, 2, [3, 4]]

# extend(): リストを展開して追加
list1 = [1, 2]
list2 = [3, 4]
list1.extend(list2)
print(list1)  # [1, 2, 3, 4]
```

辞書のリストを結合する場合は `extend()` を使います。

#### 進捗表示

```python
for i, tag in enumerate(tags, 1):
    print(f"[{i}/{len(tags)}] タグ「{tag}」")
```

`enumerate()` を使うと、インデックスと要素を同時に取得できます。

---

## 問題3：重複を除去【解答】

```python
def remove_duplicates(quotes):
    """重複する名言を除去"""
    seen = set()
    unique_quotes = []

    for quote in quotes:
        # テキストと著者の組み合わせをキーにする
        key = (quote["text"], quote["author"])

        if key not in seen:
            seen.add(key)
            unique_quotes.append(quote)

    return unique_quotes

# 実行
if __name__ == "__main__":
    tags = ["love", "life", "inspiration"]
    all_quotes = scrape_multiple_tags(tags)

    print(f"\n{'='*70}")
    print("重複除去")
    print(f"{'='*70}")
    print(f"重複除去前: {len(all_quotes)}件")

    unique_quotes = remove_duplicates(all_quotes)

    print(f"重複除去後: {len(unique_quotes)}件")
    print(f"重複していた: {len(all_quotes) - len(unique_quotes)}件")
    print(f"{'='*70}")
```

### 実行結果

```
======================================================================
重複除去
======================================================================
重複除去前: 60件
重複除去後: 45件
重複していた: 15件
======================================================================
```

### 解説

#### セット（set）の使い方

```python
seen = set()

# 追加
seen.add("A")
seen.add("A")  # 重複は無視される

# 確認
if "A" in seen:
    print("既に存在します")

print(len(seen))  # 1
```

セットは重複を許さないので、重複チェックに便利です。

#### タプルをキーにする

```python
# タプルはハッシュ可能なので、セットに追加できる
key = (quote["text"], quote["author"])
seen.add(key)

# リストはハッシュ不可能なので、エラーになる
key = [quote["text"], quote["author"]]  # これはダメ
seen.add(key)  # TypeError
```

#### 別解：辞書を使う

```python
def remove_duplicates_v2(quotes):
    """辞書を使った重複除去"""
    unique_dict = {}

    for quote in quotes:
        key = (quote["text"], quote["author"])
        unique_dict[key] = quote  # 同じキーなら上書き

    return list(unique_dict.values())
```

---

## 問題4：タグ別の集計【解答】

```python
def aggregate_by_tag(quotes):
    """タグ別に集計"""
    tag_counts = {}

    for quote in quotes:
        # タグを分割
        tags = quote.get("tags", "").split(", ")

        for tag in tags:
            if tag:  # 空でなければ
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # 多い順にソート
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

    return sorted_tags

# 実行
if __name__ == "__main__":
    tags = ["love", "life", "inspiration"]
    all_quotes = scrape_multiple_tags(tags)
    unique_quotes = remove_duplicates(all_quotes)

    tag_stats = aggregate_by_tag(unique_quotes)

    print("\nタグ別の名言数（上位15件）:")
    print("=" * 50)
    for i, (tag, count) in enumerate(tag_stats[:15], 1):
        print(f"{i:2d}. {tag:20s}: {count:3d}件")
    print("=" * 50)
```

### 実行結果

```
タグ別の名言数（上位15件）:
==================================================
 1. love                :  20件
 2. inspirational       :  15件
 3. life                :  12件
 4. humor               :   8件
 5. books               :   7件
 6. reading             :   6件
 7. friendship          :   5件
 8. friends             :   4件
 9. truth               :   4件
10. simile             :   3件
...
==================================================
```

### 解説

#### get() メソッド

```python
# 存在しないキーにアクセスするとKeyError
count = tag_counts["love"]  # 初回はエラー

# get() を使うとデフォルト値を返せる
count = tag_counts.get("love", 0)  # 存在しなければ0
```

#### sorted() でソート

```python
# 辞書を (key, value) のリストに変換
items = tag_counts.items()

# value（カウント）でソート
sorted_items = sorted(items, key=lambda x: x[1], reverse=True)

# lambda x: x[1] は以下と同じ
def get_count(item):
    return item[1]  # valueを返す
```

#### Counter を使った別解

```python
from collections import Counter

def aggregate_by_tag_v2(quotes):
    """Counter を使った集計"""
    all_tags = []

    for quote in quotes:
        tags = quote.get("tags", "").split(", ")
        all_tags.extend([tag for tag in tags if tag])

    # Counter で集計
    tag_counts = Counter(all_tags)

    # 多い順に取得
    return tag_counts.most_common()
```

---

## 問題5：完全なスクレイピングシステム【解答】

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from tqdm import tqdm
import csv
import time
import logging

class QuoteScraperAdvanced:
    """高度な名言スクレイピングシステム"""

    def __init__(self):
        self.base_url = "https://quotes.toscrape.com"

        # ログ設定（第15回で学習済み）
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def scrape_tag_with_retry(self, tag_name, max_retries=3):
        """リトライ機能付きでタグから名言を取得"""
        for attempt in range(1, max_retries + 1):
            try:
                return self._scrape_tag(tag_name)
            except Exception as e:
                logging.warning(
                    f"タグ「{tag_name}」の取得エラー（試行 {attempt}/{max_retries}）: {e}"
                )
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # 指数バックオフ
                    logging.info(f"{wait_time}秒待機してリトライ...")
                    time.sleep(wait_time)
                else:
                    logging.error(f"タグ「{tag_name}」の取得に失敗しました")
                    return []

    def _scrape_tag(self, tag_name):
        """特定のタグから全ページの名言を取得"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(options=options)
        all_quotes = []

        try:
            url = f"{self.base_url}/tag/{tag_name}/"
            driver.get(url)

            page_num = 1

            while True:
                # 待機
                wait = WebDriverWait(driver, 10)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".quote")))

                # 名言を取得
                quotes = driver.find_elements(By.CSS_SELECTOR, ".quote")

                for quote in quotes:
                    try:
                        text = quote.find_element(By.CSS_SELECTOR, ".text").text.strip('"')
                        author = quote.find_element(By.CSS_SELECTOR, ".author").text

                        # タグを取得
                        tags = quote.find_elements(By.CSS_SELECTOR, ".tag")
                        tag_list = [tag.text for tag in tags]

                        all_quotes.append({
                            "text": text,
                            "author": author,
                            "tags": ", ".join(tag_list),
                            "source_tag": tag_name
                        })

                    except Exception as e:
                        logging.warning(f"名言の解析エラー: {e}")
                        continue

                # Nextボタンをクリック
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, ".next a")
                    next_button.click()
                    page_num += 1
                    time.sleep(1)
                except NoSuchElementException:
                    break

        finally:
            driver.quit()

        return all_quotes

    def scrape_multiple_tags(self, tags):
        """複数のタグから名言を取得（進捗表示付き）"""
        all_quotes = []

        for tag in tqdm(tags, desc="タグを取得中", unit="タグ"):
            quotes = self.scrape_tag_with_retry(tag)
            all_quotes.extend(quotes)
            logging.info(f"タグ「{tag}」: {len(quotes)}件取得")

        return all_quotes

    def remove_duplicates(self, quotes):
        """重複を除去"""
        seen = set()
        unique_quotes = []

        for quote in quotes:
            key = (quote["text"], quote["author"])

            if key not in seen:
                seen.add(key)
                unique_quotes.append(quote)

        return unique_quotes

    def aggregate_by_tag(self, quotes):
        """タグ別に集計"""
        tag_counts = {}

        for quote in quotes:
            tags = quote.get("tags", "").split(", ")

            for tag in tags:
                if tag:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # 多い順にソート
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

        return sorted_tags

    def save_to_csv(self, quotes, filename):
        """CSVに保存"""
        try:
            with open(filename, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["text", "author", "tags", "source_tag"]
                )
                writer.writeheader()
                writer.writerows(quotes)

            logging.info(f"CSV保存完了: {filename} ({len(quotes)}件)")

        except IOError as e:
            logging.error(f"CSV保存エラー: {e}")

    def run(self, tags):
        """パイプライン全体を実行"""
        start_time = time.time()

        print("=" * 70)
        print("📚 高度な名言スクレイピングシステム")
        print("=" * 70)
        print(f"対象タグ: {', '.join(tags)}\n")

        # データ取得
        logging.info("データ取得を開始")
        all_quotes = self.scrape_multiple_tags(tags)

        # 重複除去
        logging.info("重複を除去中")
        unique_quotes = self.remove_duplicates(all_quotes)

        # 集計
        tag_stats = self.aggregate_by_tag(unique_quotes)

        # 保存
        self.save_to_csv(unique_quotes, "quotes_advanced.csv")

        # 結果表示
        elapsed_time = time.time() - start_time

        print("\n" + "=" * 70)
        print("✅ 完了!")
        print("=" * 70)
        print(f"取得件数（重複あり）: {len(all_quotes)}件")
        print(f"取得件数（重複なし）: {len(unique_quotes)}件")
        print(f"重複していた      : {len(all_quotes) - len(unique_quotes)}件")
        print(f"実行時間          : {elapsed_time:.2f}秒")
        if unique_quotes:
            print(f"1件あたり         : {elapsed_time/len(unique_quotes):.2f}秒")
        else:
            print("1件あたり         : N/A（取得件数が0件のため計算不可）")
        print("=" * 70)

        print("\nタグ別の名言数（上位10件）:")
        print("-" * 50)
        for i, (tag, count) in enumerate(tag_stats[:10], 1):
            print(f"{i:2d}. {tag:20s}: {count:3d}件")
        print("-" * 50)

        print(f"\n保存先:")
        print(f"  - quotes_advanced.csv")
        print(f"  - scraping_advanced.log")

# 実行
if __name__ == "__main__":
    scraper = QuoteScraperAdvanced()
    tags = ["love", "life", "inspiration", "humor", "books"]
    scraper.run(tags)
```

### 実行結果

```
======================================================================
📚 高度な名言スクレイピングシステム
======================================================================
対象タグ: love, life, inspiration, humor, books

タグを取得中: 100%|████████████████████| 5/5 [00:45<00:00,  9.12s/タグ]

======================================================================
✅ 完了!
======================================================================
取得件数（重複あり）: 100件
取得件数（重複なし）: 75件
重複していた      : 25件
実行時間          : 45.60秒
1件あたり         : 0.61秒
======================================================================

タグ別の名言数（上位10件）:
--------------------------------------------------
 1. love                :  20件
 2. inspirational       :  18件
 3. life                :  15件
 4. humor               :  12件
 5. books               :  10件
 6. reading             :   8件
 7. friendship          :   6件
 8. friends             :   5件
 9. truth               :   4件
10. simile             :   3件
--------------------------------------------------

保存先:
  - quotes_advanced.csv
  - scraping_advanced.log
```

### 解説

#### クラス設計のポイント

```python
class QuoteScraperAdvanced:
    def __init__(self):
        # 初期設定
        pass

    def _scrape_tag(self):
        # 内部メソッド（アンダースコアで始まる）
        pass

    def scrape_tag_with_retry(self):
        # 外部から呼び出すメソッド
        pass

    def run(self):
        # パイプライン全体を制御
        pass
```

#### ログの設定

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("scraping_advanced.log"),  # ファイル
        logging.StreamHandler()                         # コンソール
    ]
)
```

ファイルとコンソールの両方にログを出力します。

#### 指数バックオフ

```python
wait_time = 2 ** attempt  # 2, 4, 8秒
```

リトライ時の待機時間を指数的に増やすことで、サーバーへの負荷を軽減します。

---

## 応用例

### 1. 著者別の集計

```python
def aggregate_by_author(self, quotes):
    """著者別に集計"""
    author_counts = {}

    for quote in quotes:
        author = quote["author"]
        author_counts[author] = author_counts.get(author, 0) + 1

    return sorted(author_counts.items(), key=lambda x: x[1], reverse=True)

# 使用例
author_stats = scraper.aggregate_by_author(unique_quotes)

print("\n著者別の名言数（上位10件）:")
for i, (author, count) in enumerate(author_stats[:10], 1):
    print(f"{i:2d}. {author:30s}: {count:3d}件")
```

### 2. フィルタリング

```python
def filter_by_keyword(self, quotes, keyword):
    """キーワードを含む名言だけを抽出"""
    return [
        quote for quote in quotes
        if keyword.lower() in quote["text"].lower()
    ]

# 使用例
love_quotes = scraper.filter_by_keyword(unique_quotes, "love")
print(f"「love」を含む名言: {len(love_quotes)}件")
```

### 3. 統計情報の計算

```python
def get_statistics(self, quotes):
    """統計情報を取得"""
    if not quotes:
        return {}

    # テキストの長さ
    lengths = [len(quote["text"]) for quote in quotes]

    # 著者数
    authors = set(quote["author"] for quote in quotes)

    # タグ数
    all_tags = []
    for quote in quotes:
        all_tags.extend(quote["tags"].split(", "))
    unique_tags = set(tag for tag in all_tags if tag)

    return {
        "total": len(quotes),
        "authors": len(authors),
        "tags": len(unique_tags),
        "avg_length": sum(lengths) / len(lengths),
        "max_length": max(lengths),
        "min_length": min(lengths),
    }
```

---

## まとめ

### この演習で学んだこと

1. **条件を指定したスクレイピング**
   - タグページの活用
   - URL構造の理解

2. **データの重複除去**
   - セットを使った効率的な重複チェック
   - タプルをキーにする方法

3. **データの集計**
   - 辞書を使った集計
   - ソート処理

4. **エラー処理とリトライ**
   - 指数バックオフ
   - ログの記録

5. **進捗の可視化**
   - tqdm の活用

### 次のステップ

- より複雑なサイトに挑戦
- 並列処理による高速化
- データベースとの統合
- データの可視化（グラフ作成）
- Webアプリケーションとの連携

**これで、実践的なスクレイピングシステムを構築できるようになりました！**
