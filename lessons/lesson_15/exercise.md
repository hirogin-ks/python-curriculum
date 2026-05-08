# 第15回：Selenium実践 - ブラウザ操作の自動化

## 今回のゴール

**要素の操作をマスターする（重点）**
- 要素をクリックできる
- テキストを入力・クリアできる
- 要素のテキスト・属性を取得できる

**実践的なブラウザ操作**
- 待機処理を適切に使える
- スクロールができる
- フォーム送信ができる
- スクリーンショットを撮影できる
- 実践的なスクレイピングができる

## 所要時間：90分

---

## 導入：ブラウザを自動操作する

前回（lesson14）で、Seleniumの基本的な使い方と簡単な操作を学びました。lesson15では、より実践的なブラウザ操作に挑戦します。

**Seleniumでできることを、復習と新規内容で整理します：**

| できること | 例 | 内容 |
|-----------|-----|------|
| ページを開く | driver.get(url) | 【復習】lesson14で学習済み |
| 要素をクリック | button.click() | 【復習】lesson14で学習済み |
| テキスト入力 | input_box.send_keys("文字列") | 【復習】lesson14で学習済み |
| スクロール | driver.execute_script("window.scrollTo(...)") | 【新規】今回が初|
| 待機処理 | WebDriverWait(driver, 10).until(...) | 【新規】今回が初 |
| フォーム送信 | form.submit() | 【新規】今回が初 |
| スクリーンショット | driver.save_screenshot("image.png") | 【復習】lesson14で学習済み |

この回では、スクロール・待機・フォーム送信などの実践的なブラウザ操作をマスターします。

---

## 事前準備：Seleniumのセットアップ

lesson14で `selenium` と `webdriver-manager` をセットアップ済みであることを前提とします。

### ChromeDriverの自動インストール（推奨）

複数の新しいモジュールを一気にインストールする場合も同じ方法が使えるため、自動インストール方法を推奨します。

```python
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# ChromeDriverを自動インストール
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
```

### 別の方法：手動インストール

バージョン管理を厳密にしたい場合は、手動で配置する方法もあります。

1. Chrome のバージョンを確認
   - Chrome を開く → 右上メニュー → 「ヘルプ」 → 「Google Chrome について」

2. ChromeDriver をダウンロード
   - https://chromedriver.chromium.org/downloads

3. PATH に配置
   - Windows: `C:\Windows\`
   - Mac: `/usr/local/bin/`

---

## ハンズオン：基本的な操作を試してみよう

以下のコードをファイルに保存して実行してください。

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

# ChromeDriverを起動
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

try:
    # 1. ページを開く
    print("1. ページを開く")
    driver.get("https://quotes.toscrape.com/login")

    # 2. ユーザー名を入力
    print("2. ユーザー名を入力")
    username_input = driver.find_element(By.ID, "username")
    username_input.send_keys("test_user")

    # 3. パスワードを入力
    print("3. パスワードを入力")
    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys("test_password")

    # 4. ログインボタンをクリック
    print("4. ログインボタンをクリック")
    login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
    login_button.click()

    # 5. ログイン後のページを待つ
    time.sleep(2)

    # 6. ログイン成功を確認
    print("6. ログイン成功")
    print(f"現在のURL: {driver.current_url}")

    # 7. スクリーンショットを保存
    print("7. スクリーンショット保存")
    driver.save_screenshot("login_success.png")

finally:
    # ブラウザを閉じる
    print("\nブラウザを閉じる")
    driver.quit()
```

実行すると、自動でブラウザが開き、ログインフォームに入力してログインする様子が見られます。

---

## 解説

### Seleniumの基本的な流れ

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

# 1. ドライバーを起動
driver = webdriver.Chrome()

# 2. ページを開く
driver.get("https://example.com")

# 3. 要素を探す
element = driver.find_element(By.ID, "target")

# 4. 要素を操作
element.click()

# 5. ブラウザを閉じる
driver.quit()
```

### 要素の操作

#### クリック

```python
# 要素をクリック
button = driver.find_element(By.ID, "submit")
button.click()
```

#### テキスト入力

```python
# テキストを入力
input_box = driver.find_element(By.ID, "search")
input_box.send_keys("Python")

# 既存のテキストをクリアしてから入力
input_box.clear()
input_box.send_keys("新しいテキスト")
```

#### テキストの取得

```python
# 要素のテキストを取得
element = driver.find_element(By.CLASS_NAME, "price")
price = element.text
print(price)  # "¥1,500"

# 属性を取得
link = driver.find_element(By.TAG_NAME, "a")
url = link.get_attribute("href")
print(url)  # "https://example.com"
```

### 待機処理

Seleniumでは、JavaScriptで動的に読み込まれる要素に対応するために、待機処理が必要です。

#### 推奨：WebDriverWait（明示的な待機）

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# 明示的な待機
wait = WebDriverWait(driver, 10)  # 最大10秒

# 要素が存在するまで待つ
element = wait.until(
    EC.presence_of_element_located((By.ID, "target"))
)

# 要素がクリック可能になるまで待つ
button = wait.until(
    EC.element_to_be_clickable((By.ID, "submit"))
)
button.click()
```

**特徴:**
- 特定の条件を満たすまで待つ
- 最も柔軟で、無駄な待機時間を削減
- 動的なコンテンツ対応に最適

#### expected_conditions（期待される条件）

| 条件 | 意味 |
|------|------|
| `presence_of_element_located` | 要素が存在する |
| `visibility_of_element_located` | 要素が表示されている |
| `element_to_be_clickable` | 要素がクリック可能 |
| `text_to_be_present_in_element` | テキストが含まれている |
| `title_is` | タイトルが一致 |
| `url_contains` | URLに文字列が含まれる |

```python
from selenium.webdriver.support import expected_conditions as EC

# 要素が表示されるまで待つ
wait.until(EC.visibility_of_element_located((By.ID, "result")))

# タイトルが変わるまで待つ
wait.until(EC.title_is("検索結果"))

# URLが変わるまで待つ
wait.until(EC.url_contains("/search"))
```

### スクロール

JavaScriptを実行してスクロールできます。

#### 最下部までスクロール

```python
# ページの最下部までスクロール
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
```

#### 特定の要素までスクロール

```python
# 要素までスクロール
element = driver.find_element(By.ID, "target")
driver.execute_script("arguments[0].scrollIntoView();", element)
```

#### 少しずつスクロール

```python
import time

# 少しずつスクロールして、動的に読み込まれるコンテンツを取得
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # 最下部までスクロール
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # 読み込みを待つ
    time.sleep(2)

    # 新しい高さを取得
    new_height = driver.execute_script("return document.body.scrollHeight")

    # これ以上スクロールできない場合は終了
    if new_height == last_height:
        break

    last_height = new_height
```

### スクリーンショット

```python
# ページ全体のスクリーンショット
driver.save_screenshot("screenshot.png")

# 特定の要素のスクリーンショット
element = driver.find_element(By.ID, "product")
element.screenshot("product.png")
```

### その他の便利な操作

#### ブラウザのサイズ変更

```python
# ウィンドウサイズを設定
driver.set_window_size(1920, 1080)

# 最大化
driver.maximize_window()
```

#### JavaScriptの実行

```python
# JavaScriptを実行
result = driver.execute_script("return document.title;")
print(result)

# 要素のスタイルを変更
element = driver.find_element(By.ID, "target")
driver.execute_script("arguments[0].style.border='3px solid red'", element)
```

#### ブラウザの戻る・進む

```python
# 戻る
driver.back()

# 進む
driver.forward()

# リロード
driver.refresh()
```

#### 現在のURLとタイトルを取得

```python
# 現在のURL
print(driver.current_url)

# ページタイトル
print(driver.title)
```

---

## 練習問題

### 問題1：ログインフォームの操作

https://quotes.toscrape.com/login にアクセスして、ログインしてください。

```python
# ユーザー名: admin
# パスワード: admin

# 1. ページを開く
# 2. ユーザー名を入力
# 3. パスワードを入力
# 4. ログインボタンをクリック
# 5. ログイン後のページを確認
```

**考え方のヒント:**

```
手順:
1. driver.get() でページを開く
2. find_element(By.ID, "username") で入力欄を探す
3. send_keys() でテキスト入力
4. find_element(By.CSS_SELECTOR, "input[type='submit']") でボタンを探す
5. click() でクリック
6. time.sleep(2) で待つ
7. driver.current_url で確認
```

---

### 問題2：検索フォームの操作

https://quotes.toscrape.com/ にアクセスして、タグ検索を行ってください。

```python
# 1. ページを開く
# 2. タグを選択（例: "love"）
# 3. 検索結果のページに移動
# 4. 表示された名言を取得
```

**考え方のヒント:**

```
手順:
1. driver.get() でトップページを開く
2. find_element(By.LINK_TEXT, "love") でタグリンクを探す
3. click() でクリック
4. WebDriverWait で名言が表示されるのを待つ
5. find_elements(By.CLASS_NAME, "quote") で名言を取得
6. for ループで表示
```

---

### 問題3：待機処理を使った操作

https://quotes.toscrape.com/scroll にアクセスして、スクロールで読み込まれる名言をすべて取得してください。

```python
# 1. ページを開く
# 2. スクロールする
# 3. 新しい名言が読み込まれるまで待つ
# 4. すべての名言を取得
```

**考え方のヒント:**

```
手順:
1. driver.get() でページを開く
2. ループを使い、以下を繰り返す:
   - driver.execute_script() でスクロール
   - time.sleep() で待機
   - find_elements() で現在の名言数を取得
   - 名言数が前回と同じなら break
```

---

### 問題4：フォーム送信とスクリーンショット

https://quotes.toscrape.com/search.aspx にアクセスして、以下を行ってください。

```python
# 1. 著者名で検索（例: "Einstein"）
# 2. 検索結果を取得
# 3. スクリーンショットを保存
```

**考え方のヒント:**

```
手順:
1. driver.get() でページを開く
2. find_element(By.NAME, "author") で入力欄を探す
3. send_keys("Einstein") で入力
4. フォームを送信
   → submit() メソッドを使う
   または検索ボタンをクリック
5. WebDriverWait で結果を待つ
6. find_elements() で結果を取得
7. driver.save_screenshot() で保存
```

---

### 問題5：動的サイトのスクレイピング

https://quotes.toscrape.com/js/ にアクセスして、JavaScriptで生成される名言を取得してください。

```python
# 1. ページを開く
# 2. JavaScriptの実行を待つ
# 3. 名言を取得
# 4. CSVファイルに保存
```

**考え方のヒント:**

```
手順:
1. driver.get() でページを開く
2. WebDriverWait と presence_of_element_located で .quote が表示されるまで待つ
3. find_elements(By.CLASS_NAME, "quote") で取得
4. ループで各要素を処理:
   - .text でテキスト取得
   - find_element(By.CSS_SELECTOR, ".author") で著者取得
5. csv.DictWriter でリストを CSV ファイルに保存
```

---

## 検索キーワード

| 知りたいこと | 検索キーワード |
|-------------|---------------|
| Seleniumの基本 | `Python Selenium 使い方` |
| 待機処理 | `Selenium WebDriverWait 使い方` |
| スクロール | `Selenium スクロール Python` |
| 要素の探し方 | `Selenium By クラス` |
| スクリーンショット | `Selenium screenshot Python` |
| ヘッドレスモード | `Selenium headless Chrome` |

---

## 困ったときは

### 「ChromeDriver のバージョンが合わない」

```
SessionNotCreatedException: session not created: This version of ChromeDriver only supports Chrome version 120
```

**対処法:**

```bash
# webdriver-manager を使う（推奨）
pip install webdriver-manager

# コード内で自動インストール
from webdriver_manager.chrome import ChromeDriverManager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
```

### 「要素が見つからない」

```
NoSuchElementException: no such element: Unable to locate element
```

**対処法:**

1. **待機処理を追加**
```python
wait = WebDriverWait(driver, 10)
element = wait.until(EC.presence_of_element_located((By.ID, "target")))
```

2. **セレクタを確認**
   - デベロッパーツールで正しいセレクタを確認
   - ID、クラス名、CSS セレクタを試す

3. **iframe内の要素の場合**
```python
# iframeに切り替え
driver.switch_to.frame("frame_name")
element = driver.find_element(By.ID, "target")
driver.switch_to.default_content()  # 元に戻す
```

### 「要素がクリックできない」

```
ElementClickInterceptedException: element click intercepted
```

**対処法:**

1. **スクロールして表示**
```python
element = driver.find_element(By.ID, "button")
driver.execute_script("arguments[0].scrollIntoView();", element)
element.click()
```

2. **JavaScriptでクリック**
```python
driver.execute_script("arguments[0].click();", element)
```

3. **クリック可能になるまで待つ**
```python
wait = WebDriverWait(driver, 10)
button = wait.until(EC.element_to_be_clickable((By.ID, "submit")))
button.click()
```

### 「ブラウザが開きすぎる」

**対処法:**

```python
try:
    driver = webdriver.Chrome()
    # 処理
finally:
    driver.quit()  # 必ず閉じる
```

### 「動作が遅い」

**対処法:**

1. **ヘッドレスモードを使う**

ヘッドレスモードは第14回で学習済みです。第14回の「ヘッドレスモード」セクションを参照してください。

2. **画像を読み込まない**
```python
options = Options()
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=options)
```

---

## ログで実行状況を記録しよう

長時間かかるスクレイピングでは、実行状況をファイルに記録しておくと問題発生時に原因を特定しやすくなります。Python標準の `logging` モジュールを使います。

### 基本設定

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("スクレイピング開始")         # 通常の処理記録
logging.warning("ページ3の取得に失敗")     # 注意が必要な状況
logging.error("接続エラーが発生しました")  # エラー発生時
```

### ログレベルの使い分け

| レベル | メソッド | 用途 |
|--------|---------|------|
| INFO | `logging.info()` | 通常の処理記録 |
| WARNING | `logging.warning()` | 問題になりうる状況 |
| ERROR | `logging.error()` | エラー発生時 |

### Seleniumスクレイピングでの活用例

```python
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

try:
    for page_num in range(1, 4):
        logging.info(f"ページ {page_num} を取得中")
        driver.get(f"https://quotes.toscrape.com/page/{page_num}/")
        # ... 取得処理 ...
        logging.info(f"ページ {page_num} 完了")
except Exception as e:
    logging.error(f"エラーが発生しました: {e}")
finally:
    driver.quit()
```

---

## 確認事項

- Seleniumでブラウザを起動できた
- 要素を探して操作できた（クリック、入力）
- 待機処理を使えた（WebDriverWait）
- スクロールができた
- スクリーンショットを撮影できた
- 動的サイトからデータを取得できた

---

## まとめ：Seleniumを使うべき場面

### Selenium を使う

- JavaScriptで生成されるコンテンツ
- ログインが必要なサイト
- ボタンクリックが必要
- スクロールで読み込まれるコンテンツ

### requests を使う

- 静的サイト
- APIが公開されている
- 高速に大量データを取得したい

---

**次回は『総合演習③』です。**

次回では以下を達成します：
- Seleniumで複雑なページ操作ができる
- 条件を指定してデータを絞り込める
- 複数のカテゴリーからデータを効率的に収集できる
- これまでの知識を統合して実践的なスクレイピングシステムを構築できる

具体的には、タグ別の名言収集・集計システムを作ります。
