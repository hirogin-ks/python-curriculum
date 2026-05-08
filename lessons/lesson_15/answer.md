# 第15回：Selenium実践 - 解答・解説

## 問題1：ログインフォームの操作

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
    driver.get("https://quotes.toscrape.com/login")
    print("ログインページを開きました")

    # 2. ユーザー名を入力
    username_input = driver.find_element(By.ID, "username")
    username_input.send_keys("admin")
    print("ユーザー名を入力しました")

    # 3. パスワードを入力
    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys("admin")
    print("パスワードを入力しました")

    # 4. ログインボタンをクリック
    login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
    login_button.click()
    print("ログインボタンをクリックしました")

    # 5. ログイン後のページを確認
    time.sleep(2)  # ページ遷移を待つ
    print(f"現在のURL: {driver.current_url}")
    print(f"ページタイトル: {driver.title}")

    # ログイン成功の確認（ログアウトリンクが表示されているか）
    logout_link = driver.find_element(By.LINK_TEXT, "Logout")
    if logout_link:
        print("✓ ログインに成功しました！")

finally:
    # ブラウザを閉じる
    input("Enterキーを押すとブラウザを閉じます...")
    driver.quit()
```

---

## 問題2：検索フォームの操作

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

try:
    # 1. ページを開く
    driver.get("https://quotes.toscrape.com/")
    print("トップページを開きました")

    # 2. タグ「love」をクリック
    love_tag = driver.find_element(By.LINK_TEXT, "love")
    love_tag.click()
    print("タグ「love」をクリックしました")

    # 3. 名言が表示されるまで待つ
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "quote")))

    # 4. 表示された名言を取得
    quotes = driver.find_elements(By.CLASS_NAME, "quote")

    print(f"\n「love」タグの名言が {len(quotes)} 件見つかりました\n")

    for i, quote in enumerate(quotes, 1):
        # テキストを取得
        text_element = quote.find_element(By.CLASS_NAME, "text")
        text = text_element.text

        # 著者を取得
        author_element = quote.find_element(By.CLASS_NAME, "author")
        author = author_element.text

        print(f"【名言{i}】")
        print(f"テキスト: {text}")
        print(f"著者: {author}")
        print()

finally:
    input("Enterキーを押すとブラウザを閉じます...")
    driver.quit()
```

---

## 問題3：待機処理を使った操作

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

try:
    # 1. ページを開く
    driver.get("https://quotes.toscrape.com/scroll")
    print("スクロールページを開きました")

    # 最初の読み込みを待つ
    time.sleep(2)

    # 2. スクロールして全ての名言を取得
    last_count = 0
    scroll_count = 0

    while True:
        # 現在の名言数を取得
        quotes = driver.find_elements(By.CLASS_NAME, "quote")
        current_count = len(quotes)

        print(f"スクロール {scroll_count} 回目: {current_count} 件")

        # 名言数が変わらなければ終了
        if current_count == last_count:
            print("\nこれ以上名言が読み込まれません")
            break

        last_count = current_count
        scroll_count += 1

        # 最下部までスクロール
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 新しいコンテンツが読み込まれるまで待つ
        time.sleep(2)

    # 3. すべての名言を取得して表示
    print(f"\n合計 {len(quotes)} 件の名言を取得しました\n")

    for i, quote in enumerate(quotes[:5], 1):  # 最初の5件だけ表示
        text = quote.find_element(By.CLASS_NAME, "text").text
        author = quote.find_element(By.CLASS_NAME, "author").text
        print(f"【{i}】{text} - {author}")

    if len(quotes) > 5:
        print(f"\n... 他 {len(quotes) - 5} 件")

finally:
    input("Enterキーを押すとブラウザを閉じます...")
    driver.quit()
```

---

## 問題4：フォーム送信とスクリーンショット

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

try:
    # 1. ページを開く
    driver.get("https://quotes.toscrape.com/search.aspx")
    print("検索ページを開きました")

    # ページの読み込みを待つ
    time.sleep(2)

    # 2. 著者名で検索
    author_input = driver.find_element(By.NAME, "author")
    author_input.send_keys("Einstein")
    print("著者名「Einstein」を入力しました")

    # 検索ボタンをクリック（またはフォームを送信）
    search_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
    search_button.click()
    print("検索ボタンをクリックしました")

    # 3. 検索結果を待つ
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "quote")))

    # 検索結果を取得
    quotes = driver.find_elements(By.CLASS_NAME, "quote")
    print(f"\nアインシュタインの名言が {len(quotes)} 件見つかりました\n")

    for i, quote in enumerate(quotes, 1):
        text = quote.find_element(By.CLASS_NAME, "text").text
        print(f"【{i}】{text}")

    # 4. スクリーンショットを保存
    screenshot_path = "einstein_quotes.png"
    driver.save_screenshot(screenshot_path)
    print(f"\nスクリーンショットを保存しました: {screenshot_path}")

finally:
    input("Enterキーを押すとブラウザを閉じます...")
    driver.quit()
```

---

## 問題5：動的サイトのスクレイピング

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import csv

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

try:
    # 1. ページを開く
    driver.get("https://quotes.toscrape.com/js/")
    print("動的ページを開きました")

    # 2. JavaScriptの実行を待つ（名言が表示されるまで）
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "quote")))
    print("JavaScriptで生成された名言を検出しました")

    # 3. 名言を取得
    quotes = driver.find_elements(By.CLASS_NAME, "quote")
    print(f"{len(quotes)} 件の名言を取得しました")

    # データを格納するリスト
    quotes_data = []

    for quote in quotes:
        # テキストを取得
        text_element = quote.find_element(By.CLASS_NAME, "text")
        text = text_element.text

        # 著者を取得
        author_element = quote.find_element(By.CLASS_NAME, "author")
        author = author_element.text

        # タグを取得
        tag_elements = quote.find_elements(By.CLASS_NAME, "tag")
        tags = [tag.text for tag in tag_elements]
        tags_str = ", ".join(tags)

        quotes_data.append({
            "text": text,
            "author": author,
            "tags": tags_str
        })

    # 4. CSVファイルに保存
    output_file = "quotes_js.csv"

    with open(output_file, "w", encoding="utf-8", newline="") as f:
        fieldnames = ["text", "author", "tags"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(quotes_data)

    print(f"\nCSVファイルに保存しました: {output_file}")

    # 保存したデータを確認
    print("\n【保存されたデータの一部】")
    for i, data in enumerate(quotes_data[:3], 1):
        print(f"\n{i}. {data['text']}")
        print(f"   著者: {data['author']}")
        print(f"   タグ: {data['tags']}")

finally:
    input("Enterキーを押すとブラウザを閉じます...")
    driver.quit()

print(f"\n✓ 完了: {output_file} に {len(quotes_data)} 件のデータを保存しました")
```

---

## なぜこう書くの？

### 問題1：なぜログイン処理は段階的に行うのか？

```python
# ❌ 悪い例：一気に処理
driver.get("https://quotes.toscrape.com/login")
driver.find_element(By.ID, "username").send_keys("admin")
driver.find_element(By.ID, "password").send_keys("admin")
driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

# ✅ 良い例：段階的に処理
driver.get("https://quotes.toscrape.com/login")

username_input = driver.find_element(By.ID, "username")
username_input.send_keys("admin")

password_input = driver.find_element(By.ID, "password")
password_input.send_keys("admin")

login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
login_button.click()
```

**理由:**
1. **デバッグしやすい** - エラーが起きた時にどの段階で失敗したかわかる
2. **読みやすい** - 各ステップが明確
3. **ログ出力できる** - 各段階で進捗を確認できる

### 問題2：なぜWebDriverWaitを使うのか？

```python
# ❌ 悪い例：time.sleep()
love_tag.click()
time.sleep(5)  # 5秒待つ（長すぎる or 短すぎる可能性）
quotes = driver.find_elements(By.CLASS_NAME, "quote")

# ✅ 良い例：WebDriverWait
love_tag.click()
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "quote")))
quotes = driver.find_elements(By.CLASS_NAME, "quote")
```

**理由:**
1. **最適な待機時間** - 要素が表示されたら即座に次へ進む
2. **安定性** - ネットワークが遅い時も対応できる
3. **時間短縮** - 不要な待機時間を削減

### 問題3：なぜスクロール後に待機が必要なのか？

```python
# ❌ 悪い例：待たずにすぐ確認
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
quotes = driver.find_elements(By.CLASS_NAME, "quote")  # まだ読み込まれていない

# ✅ 良い例：読み込みを待つ
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)  # 新しいコンテンツの読み込みを待つ
quotes = driver.find_elements(By.CLASS_NAME, "quote")
```

**理由:**
- スクロールしても、JavaScriptによる新しいコンテンツの読み込みには時間がかかる
- 待たないと、まだ読み込まれていない状態でデータを取得してしまう

### 問題4：なぜtry-finallyを使うのか？

```python
# ❌ 悪い例：ブラウザが閉じられない可能性
driver = webdriver.Chrome(service=service)
driver.get(url)
# エラーが発生したらここで停止
driver.quit()  # 実行されない

# ✅ 良い例：必ず閉じる
try:
    driver = webdriver.Chrome(service=service)
    driver.get(url)
    # エラーが発生しても...
finally:
    driver.quit()  # 必ず実行される
```

**理由:**
1. **リソース管理** - エラーが発生してもブラウザを必ず閉じる
2. **メモリリーク防止** - ブラウザプロセスが残り続けるのを防ぐ

### 問題5：なぜ動的サイトでWebDriverWaitが必須なのか？

```python
# ❌ 悪い例：即座に取得しようとする
driver.get("https://quotes.toscrape.com/js/")
quotes = driver.find_elements(By.CLASS_NAME, "quote")  # まだない
# quotes = [] (空のリスト)

# ✅ 良い例：要素が表示されるまで待つ
driver.get("https://quotes.toscrape.com/js/")
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "quote")))
quotes = driver.find_elements(By.CLASS_NAME, "quote")  # 正しく取得できる
```

**理由:**
- 動的サイトでは、ページが読み込まれた時点ではHTMLにコンテンツが存在しない
- JavaScriptが実行されてからコンテンツが生成される
- その実行を待たずに取得すると、空のリストが返される

---

## 処理の流れ

### 問題1：ログイン処理の流れ

```
1. ページを開く
   ↓
2. フォーム要素を探す（ユーザー名入力欄）
   ↓
3. テキストを入力
   ↓
4. パスワード入力欄を探す
   ↓
5. テキストを入力
   ↓
6. 送信ボタンを探す
   ↓
7. クリック
   ↓
8. ページ遷移を待つ
   ↓
9. ログイン成功を確認
```

### 問題3：無限スクロールの処理の流れ

```
1. ページを開く
   ↓
2. 現在の名言数を確認（初回）
   ↓
3. 最下部までスクロール
   ↓
4. 新しいコンテンツの読み込みを待つ（2秒）
   ↓
5. 再度名言数を確認
   ↓
6. 名言数が増えた？
   Yes → 3へ戻る（繰り返し）
   No → 終了（これ以上読み込まれない）
```

### 問題5：動的サイトのスクレイピングの流れ

```
1. ページを開く（HTMLだけが読み込まれる）
   ↓
2. JavaScriptの実行を待つ
   ↓ ← ここで待たないと空のデータになる
3. 要素が表示されるまで待機（WebDriverWait）
   ↓
4. 要素を取得
   ↓
5. データを抽出
   ↓
6. CSVに保存
```

---

## ポイントまとめ

### ポイント1：待機処理の選び方

| 方法 | 使い所 | メリット | デメリット |
|------|--------|----------|----------|
| `time.sleep()` | デバッグ時のみ | シンプル | 時間の無駄、不安定 |
| `implicitly_wait()` | 全体的な待機 | 設定が簡単 | 細かい制御ができない |
| `WebDriverWait` | 特定の条件を待つ | 最も柔軟、推奨 | コードが少し長い |

**推奨:**
- 基本は `WebDriverWait` を使う
- 動的コンテンツの読み込みには必須

### ポイント2：要素の探し方の優先順位

```python
# 1. ID（最も推奨）
driver.find_element(By.ID, "username")

# 2. NAME属性
driver.find_element(By.NAME, "email")

# 3. CSS セレクタ
driver.find_element(By.CSS_SELECTOR, ".btn-primary")

# 4. XPATH（最終手段）
driver.find_element(By.XPATH, "//div[@class='content']/p[1]")
```

**理由:**
- IDは一意で高速
- XPathは複雑で壊れやすい

### ポイント3：スクロール処理のパターン

```python
# パターン1：一番下までスクロール
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# パターン2：特定の要素までスクロール
element = driver.find_element(By.ID, "target")
driver.execute_script("arguments[0].scrollIntoView();", element)

# パターン3：少しずつスクロール
for i in range(5):
    driver.execute_script(f"window.scrollTo(0, {(i+1) * 500});")
    time.sleep(1)
```

### ポイント4：データ取得のベストプラクティス

```python
# ✅ 良い例：1つの要素から複数の情報を取得
quotes = driver.find_elements(By.CLASS_NAME, "quote")
for quote in quotes:
    # quote要素の中から探す（効率的）
    text = quote.find_element(By.CLASS_NAME, "text").text
    author = quote.find_element(By.CLASS_NAME, "author").text

# ❌ 悪い例：毎回全体から探す
quotes = driver.find_elements(By.CLASS_NAME, "quote")
texts = driver.find_elements(By.CLASS_NAME, "text")
authors = driver.find_elements(By.CLASS_NAME, "author")
# どれがどれに対応するか不明確
```

### ポイント5：エラー処理の重要性

```python
# ✅ 良い例：必ずブラウザを閉じる
try:
    driver = webdriver.Chrome(service=service)
    # 処理
except Exception as e:
    print(f"エラー: {e}")
finally:
    driver.quit()  # 必ず実行

# ❌ 悪い例：エラー時にブラウザが残る
driver = webdriver.Chrome(service=service)
# エラーが起きると...
driver.quit()  # 実行されない
```

---

## よくある間違い

### 間違い1：待機処理を忘れる

```python
# ❌ 間違い
driver.get("https://quotes.toscrape.com/js/")
quotes = driver.find_elements(By.CLASS_NAME, "quote")
print(len(quotes))  # 0 （要素がまだ生成されていない）

# ✅ 正しい
driver.get("https://quotes.toscrape.com/js/")
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "quote")))
quotes = driver.find_elements(By.CLASS_NAME, "quote")
print(len(quotes))  # 正しい数が表示される
```

**解決策:** 動的コンテンツには必ずWebDriverWaitを使う

### 間違い2：driver.quit()を忘れる

```python
# ❌ 間違い：ブラウザが残り続ける
driver = webdriver.Chrome()
driver.get(url)
# 処理
# driver.quit()を書き忘れ

# ✅ 正しい：finallyで必ず閉じる
try:
    driver = webdriver.Chrome()
    driver.get(url)
finally:
    driver.quit()
```

**解決策:** 必ずtry-finallyを使う

### 間違い3：スクロール後すぐに要素を取得

```python
# ❌ 間違い：スクロール直後に取得
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
quotes = driver.find_elements(By.CLASS_NAME, "quote")
# まだ読み込まれていない

# ✅ 正しい：読み込みを待つ
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)  # または WebDriverWait
quotes = driver.find_elements(By.CLASS_NAME, "quote")
```

**解決策:** スクロール後は必ず待機する

### 間違い4：セレクタのミス

```python
# ❌ 間違い：find_elementとfind_elementsを混同
quotes = driver.find_element(By.CLASS_NAME, "quote")  # 1つだけ取得
for quote in quotes:  # エラー！WebElementはiterableではない
    print(quote.text)

# ✅ 正しい：複数取得するならfind_elements
quotes = driver.find_elements(By.CLASS_NAME, "quote")  # 複数取得
for quote in quotes:
    print(quote.text)
```

**解決策:**
- 1つ取得 → `find_element()`
- 複数取得 → `find_elements()`

### 間違い5：要素が見つからない時の対処不足

```python
from selenium.common.exceptions import NoSuchElementException

# ❌ 間違い：エラーで停止
element = driver.find_element(By.ID, "not_exist")  # NoSuchElementException

# ✅ 正しい：存在確認してから取得
try:
    element = driver.find_element(By.ID, "target")
    print(element.text)
except NoSuchElementException:
    print("要素が見つかりませんでした")

# または、要素が複数の場合は空リストで処理
elements = driver.find_elements(By.CLASS_NAME, "optional")
if elements:
    print(f"{len(elements)} 件見つかりました")
else:
    print("要素が見つかりませんでした")
```

---

## 実践的なテクニック

### テクニック1：ヘッドレスモード（ブラウザを表示しない）

開発・デバッグ時は通常モード、本番実行時はヘッドレスモードを使い分けます。

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")  # ヘッドレスモード
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

try:
    # 処理は通常と同じ
    driver.get("https://quotes.toscrape.com/")
    # find_elements で要素を取得...
finally:
    driver.quit()
```

**メリット:**
- 高速（画面描画しない）
- サーバーでの実行に必須
- リソース消費が少ない

### テクニック2：スクリーンショットでデバッグ

エラーが起きた時の状態を画像で保存します。

```python
try:
    driver.get(url)
    # 処理
except Exception as e:
    # エラー時のスクリーンショット
    driver.save_screenshot("error_screenshot.png")
    print(f"エラー: {e}")
    print("スクリーンショットを保存しました: error_screenshot.png")
    raise
finally:
    driver.quit()
```

### テクニック3：要素の存在確認

要素がない場合にエラーにしない方法です。

```python
# find_elements()を使う（要素がなければ空リスト）
elements = driver.find_elements(By.CLASS_NAME, "optional-element")

if elements:
    print(f"{len(elements)} 件見つかりました")
    for element in elements:
        print(element.text)
else:
    print("要素が見つかりませんでした（エラーではない）")
```

### テクニック4：複数のページを巡回

```python
base_url = "https://quotes.toscrape.com/page/{}/"

all_quotes = []

for page_num in range(1, 6):  # 1〜5ページ
    url = base_url.format(page_num)
    driver.get(url)

    # ページ読み込みを待つ
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "quote")))

    # 名言を取得
    quotes = driver.find_elements(By.CLASS_NAME, "quote")

    for quote in quotes:
        text = quote.find_element(By.CLASS_NAME, "text").text
        author = quote.find_element(By.CLASS_NAME, "author").text
        all_quotes.append({"text": text, "author": author})

    print(f"ページ{page_num}: {len(quotes)} 件取得")

    # 次のページへ行く前に少し待つ
    time.sleep(1)

print(f"\n合計 {len(all_quotes)} 件の名言を取得しました")
```

### テクニック5：タイムアウトの最適化

```python
from selenium.common.exceptions import TimeoutException

# 通常は短めのタイムアウト
wait = WebDriverWait(driver, 5)

try:
    # 高速なサイトなら5秒で十分
    element = wait.until(EC.presence_of_element_located((By.ID, "fast-element")))
except TimeoutException:
    print("要素が見つかりませんでした（5秒以内）")

# 重いページの場合は長めに設定
wait_long = WebDriverWait(driver, 20)
element = wait_long.until(EC.presence_of_element_located((By.ID, "slow-element")))
```

### テクニック6：User-Agentの設定

Bot検出を回避するため、通常のブラウザのように見せます。

```python
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)
```

### テクニック7：要素が消えるまで待つ

ローディング画面が消えるのを待つ場合などに使います。

```python
from selenium.webdriver.support import expected_conditions as EC

# ローディング画面が消えるまで待つ
wait = WebDriverWait(driver, 10)
wait.until(EC.invisibility_of_element_located((By.ID, "loading")))

# その後、コンテンツを取得
content = driver.find_element(By.ID, "content")
```

### テクニック8：複数の条件のいずれかを待つ

```python
from selenium.common.exceptions import TimeoutException

wait = WebDriverWait(driver, 10)

try:
    # 成功メッセージまたはエラーメッセージのいずれかが表示されるまで待つ
    success = wait.until(
        EC.presence_of_element_located((By.ID, "success-message"))
    )
    print("成功しました")
except TimeoutException:
    # エラーメッセージを確認
    try:
        error = driver.find_element(By.ID, "error-message")
        print(f"エラー: {error.text}")
    except NoSuchElementException:
        print("タイムアウト")
```

### テクニック9：JavaScriptでのクリック（通常のクリックが効かない時）

```python
# 通常のクリックが効かない場合
button = driver.find_element(By.ID, "difficult-button")

# JavaScriptで強制的にクリック
driver.execute_script("arguments[0].click();", button)
```

### テクニック10：効率的なデータ収集（一度に取得）

```python
# ❌ 非効率：毎回全体を検索
for i in range(10):
    quote = driver.find_elements(By.CLASS_NAME, "quote")[i]
    text = driver.find_elements(By.CLASS_NAME, "text")[i]  # 遅い

# ✅ 効率的：一度に取得してから処理
quotes = driver.find_elements(By.CLASS_NAME, "quote")
for quote in quotes:
    # 各quote要素の中から探す
    text = quote.find_element(By.CLASS_NAME, "text").text
    author = quote.find_element(By.CLASS_NAME, "author").text
```

---

## まとめ

### Seleniumを使う上で重要なこと

1. **待機処理は必須**
   - 動的コンテンツには `WebDriverWait` を使う
   - `time.sleep()` は最終手段

2. **必ずブラウザを閉じる**
   - `try-finally` でリソース管理
   - `driver.quit()` を忘れない

3. **要素の探し方を工夫**
   - IDが最優先
   - CSS セレクタが次点
   - XPathは最終手段

4. **エラーハンドリング**
   - 要素が見つからない場合の対処
   - スクリーンショットでデバッグ

5. **効率的なデータ取得**
   - 一度に取得してから処理
   - 無駄な検索を減らす

### 次のステップ

- エラー処理とロギングを学ぶ
- より複雑な動的サイトに挑戦
- 実際のプロジェクトに応用

---

**お疲れ様でした！Seleniumの基本的な操作をマスターできました。次回は「エラー処理とロギング」で、より堅牢なスクレイピングプログラムを作成します。**
