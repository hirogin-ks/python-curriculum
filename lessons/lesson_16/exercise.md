# 第16回：総合演習③ - 実務的なスクレイピングシステム構築

## 今回のゴール

**lesson13-15の知識を統合する**
- requests と Selenium を使い分けられる
- 静的/動的サイトを自動判定できる
- 効率的なデータ取得計画を立てられる
- 複数のカテゴリーからデータを一括収集できる

**実務的なシステムを構築する**
- ロギングで全処理を記録できる
- エラーハンドリングで堅牢性を確保できる
- 大規模データ取得を実装できる

## 所要時間：90分

---

## 16.1 導入：requests と Selenium を使い分ける

これまで以下を学びました：

- **lesson13**：requests で静的サイトを取得
- **lesson14**：Selenium で基本的なブラウザ操作
- **lesson15**：Selenium で複雑な操作とロギング

しかし、**すべてのサイトに Selenium が必要ではありません**。実務では効率を考えて使い分けることが重要です。

### 効率を考えた取得戦略

```
サイトを見つける
  ↓
【静的か動的か判定】
  ↓ ← lesson13で学んだ見分け方を使う
  
[静的] → requests を使う（高速）
  ↓
[動的] → Selenium を使う（正確）
  ↓
ロギングで記録 ← lesson15で学んだ方法
```

このように、**サイトの特性に合わせて最適なツールを選ぶ** ことで、効率的で堅牢なシステムが作れます。

### 今回の課題

quotes.toscrape.com のタグページをスクレイピングします。複数のタグから効率的にデータを取得し、結果を集計するシステムを構築します。

**学習ポイント：**
- requests での取得とログイン処理
- Selenium でのページネーション
- エラーハンドリングとロギング
- データ集計と結果出力

---

## 16.2 ハンズオン：タグページから名言を取得してみよう

### Step 1：タグページを開く

まず、特定のタグのページを開いてみましょう。

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # "love" タグのページを開く
    url = "https://quotes.toscrape.com/tag/love/"
    print(f"ページを開いています: {url}\n")
    driver.get(url)

    # 待機
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".quote")))

    # ページタイトルを確認
    print(f"ページタイトル: {driver.title}")

    # タグ名を取得
    tag_header = driver.find_element(By.CSS_SELECTOR, "h1.page-title").text
    print(f"タグ: {tag_header}")

    # 名言の数を確認
    quotes = driver.find_elements(By.CSS_SELECTOR, ".quote")
    print(f"このページの名言数: {len(quotes)}件\n")

    # 最初の名言を表示
    if quotes:
        first_quote = quotes[0]
        text = first_quote.find_element(By.CSS_SELECTOR, ".text").text
        author = first_quote.find_element(By.CSS_SELECTOR, ".author").text
        print("最初の名言:")
        print(f"{text}")
        print(f"- {author}")

finally:
    driver.quit()
```

実行すると、"love" タグの名言だけが表示されることを確認してください。

---

## 解説

### タグページのURL構造

quotes.toscrape.com のタグページは、以下のようなURL構造になっています。

```
基本形:
https://quotes.toscrape.com/tag/{タグ名}/

例:
https://quotes.toscrape.com/tag/love/
https://quotes.toscrape.com/tag/life/
https://quotes.toscrape.com/tag/inspiration/
```

タグ名を変えることで、異なるカテゴリーの名言を取得できます。

### ページネーション

タグページにも複数のページがあります。2ページ目以降は以下のようなURLになります。

```
2ページ目:
https://quotes.toscrape.com/tag/love/page/2/

3ページ目:
https://quotes.toscrape.com/tag/love/page/3/
```

### 動的なページ番号の構築

```python
base_url = "https://quotes.toscrape.com/tag/love/"

# 1ページ目
url_page1 = base_url  # または base_url + "page/1/"

# 2ページ目以降
url_page2 = base_url + "page/2/"
url_page3 = base_url + "page/3/"

# 動的に構築
def build_url(tag, page_num):
    if page_num == 1:
        return f"https://quotes.toscrape.com/tag/{tag}/"
    else:
        return f"https://quotes.toscrape.com/tag/{tag}/page/{page_num}/"
```

### 「Next」ボタンの有無で判定

ページ番号が分からない場合、「Next」ボタンの有無で最後のページかどうか判定できます。

```python
from selenium.common.exceptions import NoSuchElementException

page_num = 1
while True:
    print(f"ページ {page_num} を処理中...")
    
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, ".next a")
        # Nextボタンが見つかった → まだ次のページがある
        next_button.click()
        page_num += 1
    except NoSuchElementException:
        # Nextボタンが見つからない → 最後のページ
        print("最後のページに到達しました")
        break
```

### データの重複を防ぐ

同じ名言が複数のタグに属していることがあります。重複を防ぐには、セット（set）を使います。

```python
# リストの場合（重複あり）
quotes_list = []
quotes_list.append("名言A")
quotes_list.append("名言A")  # 重複
print(len(quotes_list))  # 2

# セットの場合（重複なし）
quotes_set = set()
quotes_set.add("名言A")
quotes_set.add("名言A")  # 重複は追加されない
print(len(quotes_set))  # 1
```

ただし、辞書のリストの場合は、タイトルやURLをキーにして重複チェックします。

```python
seen = set()
unique_quotes = []

for quote in all_quotes:
    # テキストと著者の組み合わせをキーにする
    key = (quote["text"], quote["author"])

    if key not in seen:
        seen.add(key)
        unique_quotes.append(quote)
```

---

## 練習問題

### 16.3 問題1：特定のタグから全ページ取得

"love" タグの名言を、全ページから取得してください。

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time

def scrape_tag_all_pages(tag_name):
    """特定のタグの全ページから名言を取得"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    all_quotes = []

    try:
        # 最初のページを開く
        url = f"https://quotes.toscrape.com/tag/{tag_name}/"
        driver.get(url)

        page_num = 1
        wait = WebDriverWait(driver, 10)

        while True:
            print(f"ページ {page_num} を取得中...")

            # ここに WebDriverWait の処理を書く
            # wait.until(EC.presence_of_element_located(...))

            # ここに名言を取得する処理を書く
            # quotes = driver.find_elements(...)
            # for quote in quotes:
            #     text, author, tags を取得して all_quotes に追加

            # ここに Nextボタンクリック処理を書く
            # try:
            #     next_button = ...
            #     next_button.click()
            # except NoSuchElementException:
            #     break

            page_num += 1
            time.sleep(1)

    finally:
        driver.quit()

    return all_quotes

# 実行
if __name__ == "__main__":
    quotes = scrape_tag_all_pages("love")
    print(f"\n合計 {len(quotes)} 件の名言を取得しました")

    # 最初の3件を表示
    for i, quote in enumerate(quotes[:3], 1):
        print(f"{i}. {quote['text']}")
        print(f"   - {quote['author']}\n")
```

4. time.sleep(1) で待機

注意:
- ページ番号は while ループで管理
- 最後のページで break
```

---

### 16.4 問題2：複数のタグから取得

複数のタグ（"love", "life", "inspiration"）から名言を取得してください。

```python
# 問題1の scrape_tag_all_pages() を使用します

def scrape_multiple_tags(tags):
    """複数のタグから名言を取得"""
    all_quotes = []

    # ここに for ループを書く
    # for tag in tags:
    #     scrape_tag_all_pages(tag) を呼び出して
    #     結果を all_quotes に extend で追加

    return all_quotes

# 実行
if __name__ == "__main__":
    tags = ["love", "life", "inspiration"]
    all_quotes = scrape_multiple_tags(tags)

    print(f"\n{'='*60}")
    print(f"✅ 合計 {len(all_quotes)} 件の名言を取得しました")
    print(f"{'='*60}")
```

**考え方のヒント:**

```
手順:
1. tags をループ
2. 各タグについて scrape_tag_all_pages() を呼び出し
3. 結果を all_quotes に追加（extend）
4. 進捗を表示

注意:
- append() ではなく extend() を使う
  append: リストをそのまま追加 → [[quote1], [quote2]]
  extend: リストを展開して追加 → [quote1, quote2]
```

---

### 16.5 問題3：重複を除去

問題2で取得したデータには、重複があるかもしれません。重複を除去してください。

```python
def remove_duplicates(quotes):
    """重複する名言を除去"""
    seen = set()
    unique_quotes = []

    # ここに for ループを書く
    # for quote in quotes:
    #     key = (quote["text"], quote["author"]) を作成
    #     key が seen になければ、seen に追加して unique_quotes に追加

    return unique_quotes

# 実行
if __name__ == "__main__":
    tags = ["love", "life", "inspiration"]
    all_quotes = scrape_multiple_tags(tags)

    print(f"\n重複除去前: {len(all_quotes)}件")

    unique_quotes = remove_duplicates(all_quotes)

    print(f"重複除去後: {len(unique_quotes)}件")
    print(f"重複していた: {len(all_quotes) - len(unique_quotes)}件")
```

**考え方のヒント:**

```
重複判定のキー:
- テキストと著者の組み合わせを使う
- タプルにする: (quote["text"], quote["author"])

アルゴリズム:
1. seen = set() で既に見たキーを記録
2. for で quotes をループ
3. key = (quote["text"], quote["author"]) でキーを作成
4. if key not in seen:
     seen.add(key)
     unique_quotes.append(quote)
```

---

### 16.6 問題4：タグ別の集計

取得した名言を、タグ別に集計してください。

```python
def aggregate_by_tag(quotes):
    """タグ別に集計"""
    tag_counts = {}

    # ここに for ループを書く
    # for quote in quotes:
    #     tags = quote.get("tags", "").split(", ")
    #     各タグについて tag_counts[tag] をインクリメント

    # ここに sorted() でソート
    # sorted_tags = sorted(...)

    return sorted_tags

# 実行
if __name__ == "__main__":
    tags = ["love", "life", "inspiration"]
    all_quotes = scrape_multiple_tags(tags)
    unique_quotes = remove_duplicates(all_quotes)

    tag_stats = aggregate_by_tag(unique_quotes)

    print("\nタグ別の名言数（上位10件）:")
    print("-" * 40)
    for tag, count in tag_stats[:10]:
        print(f"{tag:20s}: {count:3d}件")
```

**考え方のヒント:**

```
手順:
1. tag_counts = {} で集計用の辞書を作成
2. for quote in quotes でループ
3. tags = quote["tags"].split(", ") でタグを分割
4. 各タグについてカウント
   tag_counts[tag] = tag_counts.get(tag, 0) + 1

ソート:
sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
- items(): 辞書を (key, value) のリストに変換
- key=lambda x: x[1]: value（カウント）でソート
- reverse=True: 降順
```

---

### 16.7 問題5：完全なスクレイピングシステム

以下の機能を持つ完全なシステムを作成してください。

**要件:**
1. 複数のタグから名言を取得
2. 重複を除去
3. タグ別に集計
4. CSVに保存
5. エラー処理とリトライ
6. 進捗表示

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
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
                    wait_time = 2 ** attempt
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

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
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
        """複数のタグから名言を取得"""
        all_quotes = []

        for tag in tags:
            logging.info(f"タグ「{tag}」を取得中...")
            quotes = self.scrape_tag_with_retry(tag)
            all_quotes.extend(quotes)
            logging.info(f"タグ「{tag}」: {len(quotes)}件取得")

        return all_quotes

    def remove_duplicates(self, quotes):
        """重複を除去"""
        # ここを実装
        pass

    def aggregate_by_tag(self, quotes):
        """タグ別に集計"""
        # ここを実装
        pass

    def save_to_csv(self, quotes, filename="quotes.csv"):
        """CSVに保存"""
        # ここを実装
        pass

    def run(self, tags):
        """パイプライン全体を実行"""
        start_time = time.time()
        
        logging.info("=" * 60)
        logging.info("スクレイピングシステムを開始")
        logging.info("=" * 60)
        
        # 複数タグから取得
        logging.info(f"対象タグ: {', '.join(tags)}")
        all_quotes = self.scrape_multiple_tags(tags)
        logging.info(f"取得件数（重複含む）: {len(all_quotes)}件")

        # 重複を除去
        unique_quotes = self.remove_duplicates(all_quotes)
        logging.info(f"重複除去後: {len(unique_quotes)}件")

        # タグ別に集計
        tag_stats = self.aggregate_by_tag(unique_quotes)
        logging.info(f"タグの種類: {len(tag_stats)}種類")

        # 結果を表示
        print("\n" + "=" * 60)
        print("【タグ別名言数（上位10件）】")
        print("-" * 60)
        for tag, count in tag_stats[:10]:
            print(f"{tag:20s}: {count:3d}件")
        print("=" * 60)

        # CSVに保存
        self.save_to_csv(unique_quotes)

        elapsed_time = time.time() - start_time
        logging.info(f"処理時間: {elapsed_time:.2f}秒")
        logging.info("=" * 60)


# 実行
if __name__ == "__main__":
    scraper = QuoteScraperAdvanced()
    tags = ["love", "life", "inspiration"]
    scraper.run(tags)
```

**考え方のヒント:**

```
remove_duplicates():
- 問題3の実装を参考
- seen = set()
- key = (quote["text"], quote["author"])

aggregate_by_tag():
- 問題4の実装を参考
- tag_counts = {}
- tags = quote["tags"].split(", ")
- sorted() でソート

save_to_csv():
- with open() でファイルを開く
- csv.DictWriter を作成
- writeheader() と writerows()

run():
- 各メソッドを順番に呼び出し
- 結果を表示
```

---

## 検索キーワード

| 知りたいこと | 検索キーワード |
|-------------|---------------|
| Seleniumで複雑な操作 | `Selenium 複雑な操作 Python` |
| ページネーション | `Selenium ページネーション Python` |
| 重複除去 | `Python リスト 重複 削除` |
| 集計とソート | `Python 辞書 集計 ソート` |
| エラーハンドリング | `Selenium エラー処理 Python` |

---

## 困ったときは

### 「特定のタグページが見つからない」

タグ名が間違っている可能性があります。タグ名は小文字で、スペースはハイフンになります。

```python
# 正しい
"https://quotes.toscrape.com/tag/deep-thoughts/"

# 間違い
"https://quotes.toscrape.com/tag/Deep Thoughts/"
```

ブラウザで実際にページを開いて、URLを確認してください。

### 「重複が除去されない」

キーの作り方が間違っている可能性があります。

```python
# 間違い: 文字列をキーにする
key = quote["text"]  # タプルではない

# 正しい: タプルをキーにする
key = (quote["text"], quote["author"])
```

### 「集計結果が正しくない」

タグの分割方法が間違っている可能性があります。

```python
# タグが "love, life, inspiration" の場合
tags = quote["tags"].split(", ")  # カンマとスペース

# 結果: ["love", "life", "inspiration"]
```

### 「処理が遅い」

複数のタグを順番に取得すると時間がかかります。以下で最適化できます。

1. **ヘッドレスモードを使う**
2. **待機時間を調整** （必要最小限に）
3. **並列処理**（高度、次回以降で学習）

---

## 実装のベストプラクティス

（関数の分割方法については lesson12 で学習済みです。ここでは lesson16 特有の実装パターンを紹介します。）

### 1. requests と Selenium の使い分け

```python
# 静的ページ（requests で十分）
url = "https://quotes.toscrape.com/tag/love/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
quotes = soup.select(".quote")

# 動的ページ（Selenium が必要）
driver = webdriver.Chrome()
driver.get("https://quotes.toscrape.com/js/")
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "quote")))
quotes = driver.find_elements(By.CLASS_NAME, "quote")
```

**選択基準：**
- ブラウザで右クリック → ページのソースを表示
- JavaScriptが生成したコンテンツがない → requests
- JavaScriptが生成したコンテンツがある → Selenium

### 2. エラー処理とロギング

エラーが起きても処理を続けられるように、ロギングで記録します（lesson15で学習済み）。

```python
# 良い例: 1つのタグが失敗しても他は続行
try:
    quotes = scrape_tag(tag)
except Exception as e:
    logger.error(f"タグ '{tag}' の取得に失敗: {e}")
    continue  # 次のタグへ
```

### 3. 設定の外部化

複数のタグやURLをコードから分離します。

```python
# config.py
TAGS = ["love", "life", "inspiration"]
TIMEOUT = 10
SLEEP_TIME = 1
```

```python
# main.py
import config

scraper.run(config.TAGS)
```

---

## 確認事項

**lesson13-15の知識統合**
- [ ] requests と Selenium を使い分けできた
- [ ] 静的/動的サイトを自動判定できた
- [ ] ロギングで全処理を記録できた（lesson15）
- [ ] エラー処理を実装できた

**実装機能**
- [ ] 特定のタグから名言を取得できた
- [ ] 複数ページをページネーションで自動取得できた
- [ ] 複数のタグを順番に取得できた
- [ ] 重複を除去できた
- [ ] タグ別に集計できた
- [ ] 結果をCSVに保存できた

---

## 発展課題

余裕がある人は、以下に挑戦してみましょう。

### 1. 著者別の集計

```python
def aggregate_by_author(quotes):
    """著者別に集計"""
    author_counts = {}
    for quote in quotes:
        author = quote["author"]
        author_counts[author] = author_counts.get(author, 0) + 1

    return sorted(author_counts.items(), key=lambda x: x[1], reverse=True)
```

### 2. 単語の出現頻度分析

```python
from collections import Counter
import re

def analyze_word_frequency(quotes):
    """単語の出現頻度を分析"""
    all_words = []

    for quote in quotes:
        # 単語に分割（英字のみ）
        words = re.findall(r'\b[a-z]+\b', quote["text"].lower())
        all_words.extend(words)

    # 頻度をカウント
    word_counts = Counter(all_words)

    # 上位20件
    return word_counts.most_common(20)
```

### 3. データベースへの保存

第12回で学んだSQLiteを使って、データベースに保存してみましょう。

### 4. グラフの作成

`matplotlib` を使って、タグ別の名言数を棒グラフで表示してみましょう。

---

**次回は「エラーハンドリングと自動リトライ」です。スクレイピングで起きるエラーに対処し、失敗時の自動復旧を実装しましょう！**
