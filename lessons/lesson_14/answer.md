# 第14回：Selenium入門【解答・解説】

この解答は、問題に対する一例です。動作すれば、別の書き方でも正解です。

---

## 問題1：基本的なページの開き方【解答】

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ヘッドレスモードで起動
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
# Linux コンテナ環境などで必要な場合のみ使用
# options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

try:
    # Googleを開く
    print("Googleを開いています...")
    driver.get("https://www.google.com")

    # タイトルを取得して表示
    title = driver.title
    print(f"ページタイトル: {title}")

    # URLも確認
    current_url = driver.current_url
    print(f"現在のURL: {current_url}")

finally:
    # ブラウザを閉じる
    driver.quit()
    print("ブラウザを閉じました")
```

### 実行結果

```
Googleを開いています...
ページタイトル: Google
現在のURL: https://www.google.com/
ブラウザを閉じました
```

**注:** ページタイトルと URL は地域や言語設定によって異なる場合があります。環境によっては異なる結果が表示されることがあります。

### 解説

#### try-finally の重要性

```python
try:
    # 処理
finally:
    driver.quit()  # エラーが起きても必ず実行される
```

`try-finally` を使うことで、途中でエラーが発生してもブラウザが確実に閉じられます。これを忘れると、Chrome や ChromeDriver のプロセスが残るなどのリソースリークが発生します。

#### driver.title と driver.current_url

```python
# ページタイトル
title = driver.title

# 現在のURL
url = driver.current_url

# ページソース（HTML全体）
html = driver.page_source
```

これらのプロパティで、現在開いているページの情報を取得できます。

---

## 問題2：動的サイトからデータ取得【解答】

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
# Linux コンテナ環境などで必要な場合のみ使用
# options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

try:
    url = "https://quotes.toscrape.com/js/"
    print(f"ページを開いています: {url}\n")
    driver.get(url)

    # JavaScriptの実行を待つ
    print("JavaScriptの実行を待機中...")
    time.sleep(2)

    # 名言を取得
    quotes = driver.find_elements(By.CSS_SELECTOR, ".quote")
    print(f"取得した名言の数: {len(quotes)}\n")

    # 各名言について、テキストと著者名を表示
    print("=" * 80)
    for i, quote in enumerate(quotes, 1):
        # テキストを取得
        text = quote.find_element(By.CSS_SELECTOR, ".text").text

        # 著者名を取得
        author = quote.find_element(By.CSS_SELECTOR, ".author").text

        print(f"{i}. {text}")
        print(f"   - {author}\n")

    print("=" * 80)

finally:
    driver.quit()
    print("\nブラウザを閉じました")
```

### 実行結果

```
ページを開いています: https://quotes.toscrape.com/js/

JavaScriptの実行を待機中...
取得した名言の数: 10

================================================================================
1. "The world as we have created it is a process of our thinking..."
   - Albert Einstein

2. "It is our choices, Harry, that show what we truly are..."
   - J.K. Rowling

...
================================================================================

ブラウザを閉じました
```

### 解説

#### find_elements() の使い方

```python
# 複数の要素を取得（リストが返る）
quotes = driver.find_elements(By.CSS_SELECTOR, ".quote")

# 要素が見つからない場合は空リスト
print(len(quotes))  # 0の場合もある
```

`find_elements()` は要素が見つからなくてもエラーにならず、空のリストを返します。

#### 子要素の取得

```python
# driver からではなく、quote 要素から探す
text = quote.find_element(By.CSS_SELECTOR, ".text").text
```

`quote.find_element()` とすることで、その要素の中だけを検索できます。

---

## 問題3：待機処理の実装【解答】

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
# Linux コンテナ環境などで必要な場合のみ使用
# options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

try:
    url = "https://quotes.toscrape.com/js/"
    print(f"ページを開いています: {url}\n")
    driver.get(url)

    # WebDriverWait を使って要素を待機
    print("要素が表示されるまで待機中...")
    wait = WebDriverWait(driver, 10)

    # .quote 要素が表示されるまで最大10秒待つ
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".quote"))
    )
    print("要素が表示されました！\n")

    # 名言を取得して表示
    quotes = driver.find_elements(By.CSS_SELECTOR, ".quote")
    print(f"取得した名言の数: {len(quotes)}\n")

    # 最初の5件を表示
    for i, quote in enumerate(quotes[:5], 1):
        text = quote.find_element(By.CSS_SELECTOR, ".text").text
        author = quote.find_element(By.CSS_SELECTOR, ".author").text
        print(f"{i}. {text}")
        print(f"   - {author}\n")

finally:
    driver.quit()
    print("ブラウザを閉じました")
```

### 解説

#### WebDriverWait の仕組み

```python
# 待機オブジェクトを作成（最大10秒待つ）
wait = WebDriverWait(driver, 10)

# 条件が満たされるまで待つ
element = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".quote"))
)
```

`until()` メソッドは、指定した条件が満たされるまで繰り返しチェックします。10秒以内に条件が満たされない場合は `TimeoutException` が発生します。

#### よく使う Expected Conditions

| 条件 | 説明 |
|------|------|
| `presence_of_element_located` | 要素がDOMに存在する |
| `visibility_of_element_located` | 要素が見える状態（display: none でない） |
| `element_to_be_clickable` | 要素がクリック可能 |
| `text_to_be_present_in_element` | 要素に特定のテキストが含まれる |

#### time.sleep() との比較

```python
# time.sleep() の場合
driver.get(url)
time.sleep(5)  # 常に5秒待つ（無駄な待機が発生）

# WebDriverWait の場合
driver.get(url)
wait.until(EC.presence_of_element_located(...))
# 要素が表示されたらすぐ次へ（最大10秒）
```

WebDriverWait の方が効率的です。

---

## 問題4：複数ページの取得【解答】

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
# Linux コンテナ環境などで必要な場合のみ使用
# options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

all_quotes = []

try:
    url = "https://quotes.toscrape.com/js/"
    print(f"ページを開いています: {url}\n")
    driver.get(url)

    # 最初の3ページから名言を取得
    for page_num in range(1, 4):
        print(f"ページ {page_num} を取得中...")

        # 要素が表示されるまで待機
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".quote")))

        # 名言を取得
        quotes = driver.find_elements(By.CSS_SELECTOR, ".quote")
        print(f"  → {len(quotes)}件の名言を取得")

        for quote in quotes:
            text = quote.find_element(By.CSS_SELECTOR, ".text").text
            author = quote.find_element(By.CSS_SELECTOR, ".author").text
            all_quotes.append({"text": text, "author": author})

        # Nextボタンをクリック（最後のページでなければ）
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, ".next a")
            next_button.click()
            time.sleep(1)  # ページ遷移を待つ
        except NoSuchElementException:
            print("  → 最後のページに到達しました")
            break

    print(f"\n{'='*60}")
    print(f"✅ 合計 {len(all_quotes)} 件の名言を取得しました")
    print(f"{'='*60}")

    # 最初の3件を表示
    print("\n最初の3件:")
    for i, quote in enumerate(all_quotes[:3], 1):
        print(f"{i}. {quote['text']}")
        print(f"   - {quote['author']}\n")

finally:
    driver.quit()
    print("ブラウザを閉じました")
```

### 実行結果

```
ページを開いています: https://quotes.toscrape.com/js/

ページ 1 を取得中...
  → 10件の名言を取得
ページ 2 を取得中...
  → 10件の名言を取得
ページ 3 を取得中...
  → 10件の名言を取得

============================================================
✅ 合計 30 件の名言を取得しました
============================================================

最初の3件:
1. "The world as we have created it is a process of our thinking..."
   - Albert Einstein

2. "It is our choices, Harry, that show what we truly are..."
   - J.K. Rowling

3. "There are only two ways to live your life..."
   - Albert Einstein

ブラウザを閉じました
```

### 解説

#### ボタンのクリック

```python
# ボタンを探す
next_button = driver.find_element(By.CSS_SELECTOR, ".next a")

# クリック
next_button.click()

# ページ遷移を待つ
time.sleep(1)
```

`click()` メソッドでボタンをクリックできます。

#### try-except でエラー処理（例外を明示的に指定）

```python
from selenium.common.exceptions import NoSuchElementException

try:
    next_button = driver.find_element(By.CSS_SELECTOR, ".next a")
    next_button.click()
except NoSuchElementException:
    print("最後のページに到達しました")
    break  # ループを抜ける
```

最後のページには「Next」ボタンがないため、`find_element()` が `NoSuchElementException` を発生させます。特定の例外を明示的にキャッチすることで、他のエラー（クリック失敗など）と区別でき、デバッグが容易になります。

#### 避けるべき書き方（裸の except）

```python
# これは避けるべき
try:
    next_button = driver.find_element(By.CSS_SELECTOR, ".next a")
    next_button.click()
except:  # すべての例外をキャッチするため、デバッグが難しい
    print("最後のページに到達しました")
    break
```

`except:` の裸キャッチは、予期しないエラー（クリック失敗、タイムアウトなど）も握りつぶしてしまい、原因特定が難しくなります。

---

## 問題5：データの整形と保存【解答】

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import csv
import time

def scrape_quotes_with_selenium(num_pages=3):
    """Seleniumで名言を取得"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    # Linux コンテナ環境などで必要な場合のみ使用
    # options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    all_quotes = []

    try:
        print("=" * 70)
        print("Seleniumで名言を取得中...")
        print("=" * 70)

        driver.get("https://quotes.toscrape.com/js/")

        for page_num in range(1, num_pages + 1):
            print(f"\nページ {page_num}/{num_pages} を取得中...")

            # 待機
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".quote")))

            # 名言を取得して辞書に整形
            quotes = driver.find_elements(By.CSS_SELECTOR, ".quote")
            print(f"  → {len(quotes)}件の名言を発見")

            for quote in quotes:
                # テキストを取得（前後の引用符を削除）
                text = quote.find_element(By.CSS_SELECTOR, ".text").text
                text = text.strip('"')

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

            # Nextボタンをクリック
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, ".next a")
                next_button.click()
                time.sleep(1)  # ページ遷移を待つ
            except NoSuchElementException:
                print("  → 最後のページに到達しました")
                break

        print(f"\n{'='*70}")
        print(f"✅ 合計 {len(all_quotes)} 件の名言を取得しました")
        print(f"{'='*70}")

    finally:
        driver.quit()

    return all_quotes

def save_to_csv(quotes, filename):
    """CSVに保存"""
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "author", "tags"])
        writer.writeheader()
        writer.writerows(quotes)

    print(f"\n📄 {filename} に保存しました")

# 実行
if __name__ == "__main__":
    quotes = scrape_quotes_with_selenium(num_pages=5)
    save_to_csv(quotes, "quotes_selenium.csv")

    # サンプル表示
    print("\n最初の3件:")
    print("-" * 70)
    for i, quote in enumerate(quotes[:3], 1):
        print(f"{i}. {quote['text'][:60]}...")
        print(f"   著者: {quote['author']}")
        print(f"   タグ: {quote['tags']}\n")
```

### 実行結果

```
======================================================================
Seleniumで名言を取得中...
======================================================================

ページ 1/5 を取得中...
  → 10件の名言を発見

ページ 2/5 を取得中...
  → 10件の名言を発見

...

======================================================================
✅ 合計 50 件の名言を取得しました
======================================================================

📄 quotes_selenium.csv に保存しました

最初の3件:
----------------------------------------------------------------------
1. The world as we have created it is a process of our thinking...
   著者: Albert Einstein
   タグ: change, deep-thoughts, thinking, world

2. It is our choices, Harry, that show what we truly are, far ...
   著者: J.K. Rowling
   タグ: abilities, choices

3. There are only two ways to live your life. One is as thoug...
   著者: Albert Einstein
   タグ: inspirational, life, live, miracle, miracles
```

### 解説

#### 複数の要素を取得してリストにする

```python
# タグ要素を全て取得
tags = quote.find_elements(By.CSS_SELECTOR, ".tag")

# 各タグのテキストをリストにする
tag_list = [tag.text for tag in tags]

# カンマ区切りの文字列に変換
tags_str = ", ".join(tag_list)
```

リスト内包表記を使うと、シンプルに書けます。

#### 文字列のクリーニング

```python
text = '"この名言です"'

# 前後の引用符を削除
text = text.strip('"')  # → "この名言です"

# または、両端の特定の文字を削除
text = text.strip('"\' ')  # 引用符とスペースを削除
```

`strip()` メソッドで、前後の不要な文字を削除できます。

---

## requests と Selenium の使い分け

実際のプロジェクトでは、両方を使い分けることが多いです。

### 比較表

| 項目 | requests + BeautifulSoup | Selenium |
|------|-------------------------|----------|
| 速度 | ⚡⚡⚡ 非常に速い | 🐢 遅い |
| メモリ | 💾 少ない | 💾💾💾 多い |
| JavaScript | ❌ 実行されない | ✅ 実行される |
| ボタンクリック | ❌ できない | ✅ できる |
| ログイン | △ 可能だが難しい | ✅ 簡単 |
| 複雑さ | シンプル | 複雑 |

### 使い分けの例

```python
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

# 静的なページ → requests を使う
response = requests.get("https://books.toscrape.com")
soup = BeautifulSoup(response.text, "html.parser")

# 動的なページ → Selenium を使う
driver = webdriver.Chrome()
driver.get("https://quotes.toscrape.com/js/")
# ...
driver.quit()
```

### ハイブリッドな使い方

Selenium でページを開いて、BeautifulSoup で解析することもできます。

```python
from selenium import webdriver
from bs4 import BeautifulSoup
import time

driver = webdriver.Chrome()
driver.get("https://quotes.toscrape.com/js/")
time.sleep(2)

# Selenium で取得した HTML を BeautifulSoup で解析
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

# 以降は BeautifulSoup で処理
quotes = soup.select(".quote")
for quote in quotes:
    print(quote.select_one(".text").text)

driver.quit()
```

これにより、Selenium の柔軟性と BeautifulSoup の使いやすさを組み合わせられます。

---

## よくある間違いと対処法

### 間違い1: driver.quit() を忘れる

```python
# 間違い: quit() を忘れる
driver = webdriver.Chrome()
driver.get("https://example.com")
# quit() がない → ブラウザが開きっぱなし

# 正しい: try-finally を使う
driver = webdriver.Chrome()
try:
    driver.get("https://example.com")
finally:
    driver.quit()  # 必ず実行される
```

### 間違い2: 待機処理を忘れる

```python
# 間違い: JavaScript の実行を待たない
driver.get("https://quotes.toscrape.com/js/")
quotes = driver.find_elements(By.CSS_SELECTOR, ".quote")
# → 0件（要素がまだ表示されていない）

# 正しい: 待機する
driver.get("https://quotes.toscrape.com/js/")
time.sleep(2)  # または WebDriverWait を使う
quotes = driver.find_elements(By.CSS_SELECTOR, ".quote")
```

### 間違い3: find_element と find_elements を間違える

```python
# 間違い: find_elements() の結果に .text を使う
quotes = driver.find_elements(By.CSS_SELECTOR, ".quote")
print(quotes.text)  # エラー: リストには .text 属性がない

# 正しい: ループで処理
quotes = driver.find_elements(By.CSS_SELECTOR, ".quote")
for quote in quotes:
    print(quote.text)  # 各要素に対して .text を使う
```

### 間違い4: セレクタの指定方法を混同している

```python
# 間違い: By.CLASS_NAME に CSS セレクタの記法を渡している
element = driver.find_element(By.CLASS_NAME, ".quote")  # エラー

# 間違い: キーワード引数を使ってしまう
element = driver.find_element(By.CSS_SELECTOR, class_="quote")  # TypeError

# 正しい: クラス名で探すなら、. を付けずに指定
element = driver.find_element(By.CLASS_NAME, "quote")

# 正しい: CSS セレクタを使うなら文字列で記述
element = driver.find_element(By.CSS_SELECTOR, ".quote")
element = driver.find_element(By.CSS_SELECTOR, "div.quote > .text")  # これも OK
```

---

## パフォーマンスの最適化

### 1. ヘッドレスモード

```python
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
```

画面を表示しない分、わずかに速くなります。

### 2. 画像の読み込みを無効化

```python
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)
```

画像を読み込まないことで、ページの読み込みが速くなります。

### 3. 不要な待機を削除

```python
# 悪い例: 固定で3秒待つ
time.sleep(3)

# 良い例: 要素が表示されたらすぐ次へ
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".quote")))
```

### 4. 静的な部分は requests を使う

```python
# 一覧ページだけ Selenium で取得
driver.get("https://example.com/list")
links = driver.find_elements(By.CSS_SELECTOR, "a")
urls = [link.get_attribute("href") for link in links]
driver.quit()

# 詳細ページは requests で高速取得
import requests
for url in urls:
    response = requests.get(url)
    # 処理
```

---

## まとめ

### Selenium の特徴

**メリット**:
- JavaScript が実行される
- ブラウザを自動操作できる
- 人間と同じようにページを操作できる

**デメリット**:
- 遅い
- メモリを大量に消費する
- セットアップが複雑

### 使うべき場面

- JavaScript で動的にコンテンツが生成される
- ボタンのクリックが必要
- ログインが必要
- スクロールが必要

### 使わない方が良い場面

- 静的なページ（requests の方が速い）
- 大量のページを高速に処理したい（API があればそちらを使う）

---

## 次回予告：Seleniumで要素操作

第15回では、Seleniumを使った実践的なWeb自動化に進みます。

次回でできること:
- ボタンクリック、テキスト入力などの要素操作
- 待機処理（`time.sleep` と `WebDriverWait`）の使い分け
- ページスクロールでのデータ取得
- フォーム入力と送信
- スクリーンショット撮影
- 実践的なスクレイピングの実装

```python
# 次回の予告コード
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()

try:
    driver.get("https://example.com")
    
    # テキストを入力
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys("Python")
    
    # ボタンをクリック
    submit_button = driver.find_element(By.NAME, "btnK")
    submit_button.click()
    
    # ページをスクロール
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    # スクリーンショットを撮影
    driver.save_screenshot("result.png")
    
finally:
    driver.quit()
```

---

**次回は「Seleniumで要素操作」です。より複雑なWebサイトに対応しましょう！**
