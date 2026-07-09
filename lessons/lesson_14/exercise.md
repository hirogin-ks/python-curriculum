# 第14回：Selenium入門

## 今回のゴール

- Seleniumとは何かを理解する
- Seleniumでブラウザを自動操作できる
- 動的サイト（JavaScript）からデータを取得できる
- 要素の待機処理ができる
- ヘッドレスモードを使える

## 所要時間：90分

---

## 導入：requestsでは取得できないページがある

JavaScript で動的にコンテンツを生成するページでは、`requests` では取得できません。前回学んだように、`requests` はHTMLを取得するだけで、JavaScriptを実行しません。

このような場合に活躍するのが **Selenium** です。Seleniumは実際にブラウザを起動してJavaScriptを実行しながらページを開くツールです。人間がブラウザを操作するように、プログラムからブラウザを自動操作できます。

---

## ハンズオン：Seleniumでページを開いてみよう

### Step 1：Seleniumのインストール

まず、Seleniumをインストールします。

```bash
pip install selenium
```

### Step 2：シンプルなコードを動かす

以下のコードをファイルに保存して実行してください。

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Chromeの設定
options = Options()
options.add_argument("--headless")  # ヘッドレスモード（画面を表示しない）

# ブラウザを起動
driver = webdriver.Chrome(options=options)

try:
    # ページを開く
    url = "https://quotes.toscrape.com/js/"
    print(f"ページを開いています: {url}")
    driver.get(url)

    # JavaScriptの実行を待つ
    time.sleep(2)

    # 名言を取得
    quotes = driver.find_elements(By.CSS_SELECTOR, ".quote .text")
    print(f"\n取得した名言の数: {len(quotes)}")

    # 最初の3件を表示
    for i, quote in enumerate(quotes[:3], 1):
        print(f"{i}. {quote.text}")

finally:
    # ブラウザを閉じる（重要！）
    driver.quit()
    print("\nブラウザを閉じました")
```

実行すると、JavaScript で生成された名言が取得できることを確認してください。

---

## 解説

### Seleniumとは

**Selenium** は、Webブラウザを自動操作するためのツールです。もともとはWebアプリケーションのテストツールとして開発されましたが、スクレイピングにも広く使われています。

### requestsとSeleniumの違い

| | requests | Selenium |
|---|----------|----------|
| 仕組み | HTTPリクエストを送信してHTMLを取得 | 実際にブラウザを起動してページを開く |
| JavaScript | ❌ 実行されない | ✅ 実行される |
| 速度 | ⚡ 速い | 🐢 遅い（ブラウザの起動が必要） |
| メモリ | 💾 少ない | 💾💾💾 多い |
| 向いているケース | 静的なページ | 動的なページ、ログイン、ボタンクリックが必要なページ |

### いつSeleniumを使うべきか

以下の場合はSeleniumが必要です：

1. **JavaScript で動的にコンテンツが生成される**
   - 例: quotes.toscrape.com/js/
2. **ページ内でボタンをクリックする必要がある**
   - 例: 「もっと見る」ボタンをクリックして追加データを読み込む
3. **ログインが必要**
   - 例: フォームにIDとパスワードを入力してログイン
4. **スクロールが必要**
   - 例: 無限スクロールでデータを読み込むページ

逆に、通常の静的なページには `requests` を使う方が高速で効率的です。

> **相性という考え方**
> 
> 孫子の兵法に「常によい手段というものはなく、状況に応じて変化させることが大切」という考え方があります。
> 
> スクレイピングにおいても同じ。JavaScriptを実行する強力な Selenium も、高速な requests も、どちらが常に正しいわけではありません。
> サイトの特性に応じて、最適なツールを選び分けることが、効率的なスクレイピングへの道です。

### Seleniumの基本的な使い方

#### 1. ブラウザの起動

```python
from selenium import webdriver

driver = webdriver.Chrome()  # Chromeを起動
```

#### 2. ページを開く

```python
driver.get("https://example.com")
```

#### 3. 要素を取得

```python
from selenium.webdriver.common.by import By

# 1つの要素を取得
element = driver.find_element(By.CLASS_NAME, "title")

# 複数の要素を取得
elements = driver.find_elements(By.CLASS_NAME, "item")
```

#### 4. テキストや属性を取得

```python
# テキストを取得
text = element.text

# 属性を取得
href = element.get_attribute("href")
```

#### 5. ブラウザを閉じる

```python
driver.quit()  # 必ず実行！
```

### 要素の取得方法（By）

| 取得方法 | 説明 | 例 |
|---------|------|-----|
| `By.ID` | IDで取得 | `driver.find_element(By.ID, "main")` |
| `By.CLASS_NAME` | クラス名で取得 | `driver.find_element(By.CLASS_NAME, "title")` |
| `By.TAG_NAME` | タグ名で取得 | `driver.find_element(By.TAG_NAME, "h1")` |
| `By.CSS_SELECTOR` | CSSセレクタで取得 | `driver.find_element(By.CSS_SELECTOR, "div.item > p")` |
| `By.XPATH` | XPathで取得 | `driver.find_element(By.XPATH, "//div[@class='item']")` |

**推奨**: `By.CSS_SELECTOR` が最も使いやすく、第7回で学んだ `soup.select("~~~")` と同じ記法が使えます。

### find_element と find_elements の違い

| メソッド | 戻り値 | 要素が見つからない場合 |
|---------|--------|----------------------|
| `find_element()` | 1つの要素 | 例外が発生 |
| `find_elements()` | リスト（複数） | 空のリスト `[]` |

```python
# 1つだけ取得（見つからないとエラー）
title = driver.find_element(By.CLASS_NAME, "title")

# 複数取得（見つからなくても空リスト）
items = driver.find_elements(By.CLASS_NAME, "item")
print(len(items))  # 0の場合もある
```

### 待機処理

JavaScript の実行には時間がかかることがあります。要素が表示される前に取得しようとするとエラーになります。

#### 方法A: time.sleep()（簡単だが推奨されない）

```python
import time

driver.get("https://example.com")
time.sleep(2)  # 2秒待つ
```

**問題点**: 必要以上に待つことがあり、無駄な時間が発生します。

#### 方法B: WebDriverWait（推奨）

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# 最大10秒待って、要素が表示されるまで待機
wait = WebDriverWait(driver, 10)
element = wait.until(
    EC.presence_of_element_located((By.CLASS_NAME, "quote"))
)
```

要素が表示されたらすぐに次の処理に進むので、効率的です。

### ヘッドレスモード

**ヘッドレスモード** とは、ブラウザのウィンドウを表示せずにバックグラウンドで動作させるモードです。

```python
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")  # ヘッドレスモード
options.add_argument("--disable-gpu")  # GPU無効化（Windows推奨）

driver = webdriver.Chrome(options=options)
```

**メリット**:
- 画面が表示されないので、他の作業の邪魔にならない
- サーバー環境でも動作する
- わずかに速い

**デメリット**:
- デバッグしにくい（何が起きているか見えない）

開発中はヘッドレスモードをオフにして、完成したらオンにするのがおすすめです。

---

## 練習問題

### 問題1：基本的なページの開き方

`python/lesson14/01_basic_page_open.py` に回答を書いてください。

Selenium を使って Google のトップページを開き、タイトルを取得してください。

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ヘッドレスモードで起動
options = Options()
options.add_argument("--headless")

driver = webdriver.Chrome(options=options)

try:
    # Googleを開く
    # ここを実装

    # タイトルを取得して表示
    # ここを実装

finally:
    driver.quit()
```

**考え方のヒント:**

```
手順:
1. driver.get("https://www.google.com") でページを開く
2. driver.title でタイトルを取得
3. print() で表示
4. finally ブロックで driver.quit() を実行（必ず閉じる）

注意:
- try-finally を使うことで、エラーが起きてもブラウザが確実に閉じられる
```

---

### 問題2：動的サイトからデータ取得

`python/lesson14/02_dynamic_data_fetch.py` に回答を書いてください。

https://quotes.toscrape.com/js/ から、すべての名言を取得してください。

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--headless")

driver = webdriver.Chrome(options=options)

try:
    url = "https://quotes.toscrape.com/js/"
    driver.get(url)

    # JavaScriptの実行を待つ
    time.sleep(2)

    # 名言を取得
    # ここを実装

    # 各名言について、テキストと著者名を表示
    # ここを実装

finally:
    driver.quit()
```

**考え方のヒント:**

```
HTML構造:
<div class="quote">
  <span class="text">"名言の内容"</span>
  <small class="author">著者名</small>
</div>

手順:
1. driver.find_elements(By.CSS_SELECTOR, ".quote") で全ての名言要素を取得
2. for でループ
3. 各要素から .text と .author を取得
   - quote.find_element(By.CSS_SELECTOR, ".text").text
   - quote.find_element(By.CSS_SELECTOR, ".author").text
4. 表示

注意:
- find_elements (複数形) を使う
- time.sleep(2) でJavaScriptの実行を待つ
```

---

### 問題3：待機処理の実装

`python/lesson14/03_waiting_process.py` に回答を書いてください。

WebDriverWait を使って、より確実に要素を取得してください。

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument("--headless")

driver = webdriver.Chrome(options=options)

try:
    url = "https://quotes.toscrape.com/js/"
    driver.get(url)

    # WebDriverWait を使って要素を待機
    # ここを実装

    # 名言を取得して表示
    # ここを実装

finally:
    driver.quit()
```

**考え方のヒント:**

```
WebDriverWait の基本:
wait = WebDriverWait(driver, 10)  # 最大10秒待つ
element = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".quote"))
)

よく使う expected_conditions:
- presence_of_element_located: 要素がDOMに存在する
- visibility_of_element_located: 要素が見える状態
- element_to_be_clickable: 要素がクリック可能

手順:
1. WebDriverWait のインスタンスを作成
2. until() で条件を指定
3. 要素が表示されたら、find_elements() で全要素を取得
4. ループで表示
```

---

### 問題4：複数ページの取得

`python/lesson14/04_multi_page_fetch.py` に回答を書いてください。

https://quotes.toscrape.com/js/ には「Next」ボタンがあります。「Next」ボタンをクリックして、複数ページから名言を取得してください。

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = Options()
options.add_argument("--headless")

driver = webdriver.Chrome(options=options)

all_quotes = []

try:
    url = "https://quotes.toscrape.com/js/"
    driver.get(url)

    # 最初の3ページから名言を取得
    for page_num in range(1, 4):
        print(f"ページ {page_num} を取得中...")

        # 要素が表示されるまで待機
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".quote")))

        # 名言を取得
        # ここを実装

        # Nextボタンをクリック（最後のページでなければ）
        # ここを実装

        time.sleep(1)

    print(f"\n合計 {len(all_quotes)} 件の名言を取得しました")

finally:
    driver.quit()
```

**考え方のヒント:**

```
手順:
1. ページを開く
2. 名言を取得して all_quotes に追加
3. Nextボタンを探す
   next_button = driver.find_element(By.CSS_SELECTOR, ".next a")
4. クリック
   next_button.click()
5. 少し待つ
   time.sleep(1)
6. 繰り返す

注意:
- 最後のページには Nextボタンがないので、要素が見つからない場合は終了
- try-except で処理すると良い
```

例:
```python
from selenium.common.exceptions import NoSuchElementException

try:
    next_button = driver.find_element(By.CSS_SELECTOR, ".next a")
    next_button.click()
except NoSuchElementException:
    print("最後のページに到達しました")
    break
```


---

### 問題5：データの整形と保存

`python/lesson14/05_format_save_data.py` に回答を書いてください。

取得した名言を辞書のリストにまとめて、CSVファイルに保存してください。

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

def scrape_quotes_with_selenium(num_pages=3):
    """Seleniumで名言を取得"""
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    all_quotes = []

    try:
        driver.get("https://quotes.toscrape.com/js/")

        for page_num in range(1, num_pages + 1):
            print(f"ページ {page_num} を取得中...")

            # 待機
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".quote")))

            # 名言を取得して辞書に整形
            quotes = driver.find_elements(By.CSS_SELECTOR, ".quote")
            for quote in quotes:
                text = quote.find_element(By.CSS_SELECTOR, ".text").text
                author = quote.find_element(By.CSS_SELECTOR, ".author").text

                # タグも取得
                tags = quote.find_elements(By.CSS_SELECTOR, ".tag")
                tag_list = [tag.text for tag in tags]

                all_quotes.append({
                    "text": text.strip('"'),  # 前後の引用符を削除
                    "author": author,
                    "tags": ", ".join(tag_list)  # タグをカンマ区切りで結合
                })

            # Nextボタンをクリック
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, ".next a")
                next_button.click()
                time.sleep(1)
            except NoSuchElementException:
                print("最後のページに到達しました")
                break

    finally:
        driver.quit()

    return all_quotes

def save_to_csv(quotes, filename):
    """CSVに保存"""
    # ここを実装
    pass

# 実行
if __name__ == "__main__":
    quotes = scrape_quotes_with_selenium(num_pages=5)
    save_to_csv(quotes, "quotes_selenium.csv")
    print(f"\n{len(quotes)}件の名言を取得しました")
```

**考え方のヒント:**

```
save_to_csv() の実装:
1. with open() でファイルを開く
2. csv.DictWriter を作成
   writer = csv.DictWriter(f, fieldnames=["text", "author", "tags"])
3. writeheader() でヘッダーを書く
4. writerows(quotes) でデータを書く

引用符の削除:
text = '"この名言"'
text = text.strip('"')  # → "この名言"

タグの結合:
tags = ["love", "life", "poetry"]
tags_str = ", ".join(tags)  # → "love, life, poetry"
```

---

## 検索キーワード

| 知りたいこと | 検索キーワード |
|-------------|---------------|
| Seleniumのインストール | `Selenium Python インストール` |
| WebDriverのセットアップ | `Selenium Chrome WebDriver セットアップ` |
| 要素の取得方法 | `Selenium find_element Python` |
| 待機処理 | `Selenium WebDriverWait Python` |
| ヘッドレスモード | `Selenium headless Chrome Python` |
| ボタンのクリック | `Selenium click button Python` |
| スクロール | `Selenium scroll Python` |

---

## 困ったときは

### 「WebDriver not found」エラーが出る

Chrome WebDriver が見つからないというエラーです。

**原因**: Selenium 4.6以降は自動でWebDriverをダウンロードするはずですが、うまくいかない場合があります。

**対処法1**: Chromeのバージョンを確認

```bash
# Chrome のバージョンを確認
google-chrome --version  # Linux
# または
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version  # Mac
```

**対処法2**: ChromeDriver を手動でインストール

```bash
pip install webdriver-manager
```

```python
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
```

### 「Element not found」エラーが出る

要素が見つからないというエラーです。

**原因**:
1. JavaScriptの実行が完了していない
2. セレクタが間違っている
3. 要素が別のフレームにある

**対処法**:

```python
# 1. 待機時間を増やす
time.sleep(3)  # 2秒 → 3秒

# 2. WebDriverWait を使う
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 10)
element = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".quote"))
)

# 3. セレクタを確認
# ブラウザの開発者ツールで要素を確認
```

### 「ブラウザが閉じない」

プログラムがエラーで終了すると、ブラウザが開きっぱなしになることがあります。

**対処法**: `try-finally` を必ず使う

```python
driver = webdriver.Chrome()

try:
    # 処理
    driver.get("https://example.com")
finally:
    # エラーが起きても必ず実行される
    driver.quit()
```

### 「ヘッドレスモードで動かない」

ヘッドレスモードでは動作するが、通常モードでは動かない（またはその逆）ことがあります。

**対処法**: 追加のオプションを設定

```python
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")  # Linux で必要なことがある
options.add_argument("--disable-dev-shm-usage")  # メモリ不足対策
options.add_argument("--disable-gpu")  # GPU無効化（Windows推奨）
options.add_argument("--window-size=1920,1080")  # ウィンドウサイズ指定
```

### 「処理が遅い」

Selenium はブラウザを起動するため、requests に比べて遅いです。

**高速化のコツ**:

1. **ヘッドレスモードを使う**
2. **画像の読み込みを無効化**

```python
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)
```

3. **CSS の読み込みを無効化**（表示が崩れるが速い）
4. **不要な待機を削除**（WebDriverWaitを活用）

---

## Selenium使用時の注意点

### 1. リソース消費が大きい

Selenium はブラウザを起動するため、メモリとCPUを大量に消費します。同時に複数のブラウザを開くとパソコンが重くなります。

### 2. driver.quit() を忘れない

ブラウザを閉じないと、メモリリークが発生します。必ず `finally` ブロックで `driver.quit()` を実行してください。

```python
try:
    driver.get("https://example.com")
    # 処理
finally:
    driver.quit()  # 必ず実行
```

### 3. 静的なページには使わない

JavaScript が不要なページには `requests` を使う方が高速で効率的です。

### 4. サーバーへの配慮

Selenium でも、通常のスクレイピングと同様にサーバーに負荷をかけないよう注意してください。

---

## 確認事項

- [ ] Selenium をインストールできた
- [ ] ブラウザを起動してページを開けた
- [ ] 動的サイトからデータを取得できた
- [ ] find_element() と find_elements() の違いが分かった
- [ ] 待機処理（time.sleep と WebDriverWait）を実装できた
- [ ] ヘッドレスモードを使えた
- [ ] ボタンをクリックできた
- [ ] try-finally で確実にブラウザを閉じられた
- [ ] requests との使い分けが分かった

---

## 発展課題

余裕がある人は、以下に挑戦してみましょう。

### 1. スクロールの実装

無限スクロールのページでは、スクロールしないと全データが表示されません。

```python
# ページの最下部までスクロール
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)
```

### 2. スクリーンショットの取得

```python
driver.get("https://example.com")
driver.save_screenshot("screenshot.png")
```

### 3. フォームへの入力

```python
# 入力フォームに文字を入力
search_box = driver.find_element(By.NAME, "q")
search_box.send_keys("Python")
search_box.submit()  # フォームを送信
```

### 4. ドロップダウンの選択

```python
from selenium.webdriver.support.ui import Select

dropdown = Select(driver.find_element(By.ID, "dropdown"))
dropdown.select_by_visible_text("Option 1")
```

---

**次回は「Selenium実践」です。要素のクリック・テキスト入力・スクロール・フォーム送信など、ブラウザ操作の自動化をより深く学びます。**
