# 第9回：データ整形とクリーニング

## 今回のゴール

- スクレイピングで取得したデータを整形できる
- 正規表現で必要な情報を抽出できる
- 価格データを数値に変換できる
- 日付データを統一フォーマットに変換できる
- 文字列のクリーニングができる

## 所要時間：90分

---

## 導入：取得したデータは「汚い」

スクレイピングで取得したデータは、そのままでは使いにくいことがほとんどです。例えば、以下のようなデータが取得されることがあります。

```python
# 価格
price = "¥1,500（税込）"
# → 計算に使うには数値にしたい

# 日付
date = "2024年1月15日"
# → データベースに保存するには統一フォーマットにしたい

# テキスト
text = "  前後に空白があります  \n"
# → 余分な空白や改行を削除したい

# 数量
stock = "在庫：残り5個"
# → 数字だけ取り出したい
```

このような「汚い」データを「きれいな」データに変換する処理を**データ整形**または**データクリーニング**と呼びます。

すでに第7回でreplace、第8回でrating_mapを使った整形を学びましたが、この回ではさらにレベルアップさせて、データ整形のための様々なテクニックを学びます。

---

## ハンズオン：文字列をクリーニングしてみよう

以下のコードをファイルに保存して実行してください。

```python
import re

# 価格データ
price_text = "¥1,500（税込）"
print(f"元のデータ: {price_text}")

# 1. 数字だけを取り出す
numbers_only = re.sub(r"[^\d]", "", price_text)
print(f"数字だけ: {numbers_only}")  # 1500

# 2. 数値に変換
price = int(numbers_only)
print(f"数値: {price}")  # 1500
print(f"型: {type(price)}")  # <class 'int'>

# 3. 計算できることを確認
tax = price * 0.1
print(f"消費税（10%）: ¥{tax:.0f}")  # ¥150
```

実行すると、文字列から数字だけを取り出して、計算に使える数値に変換できることが確認できます。

---

## 解説

### 文字列の基本的なクリーニング

#### strip() で前後の空白を削除

```python
text = "  こんにちは  \n"
clean_text = text.strip()
print(f"[{clean_text}]")  # [こんにちは]
```

`strip()` は、文字列の前後にある**空白**、**タブ**、**改行**を削除します。

#### replace() で文字を置換

```python
price = "¥1,500"
price = price.replace("¥", "")  # "1,500"
price = price.replace(",", "")  # "1500"
price_value = int(price)        # 1500
```

複数の文字を削除したい場合は、`replace()` を連続して使います。

### 正規表現（Regular Expression）

正規表現は、文字列のパターンを表現するための記法です。複雑な文字列処理を簡潔に書けます。

#### re.sub() で置換

```python
import re

# 基本的な使い方
text = "電話番号: 090-1234-5678"
result = re.sub(r"-", "", text)
print(result)  # "電話番号: 09012345678"
```

`re.sub()` は正規表現で指定したパターンにマッチした文字列を置換します。上記の例では、ハイフン(-)を空文字に置換（削除）しています。

`re.sub(r"~~~", "", text)` の `r"~~~"` の部分に削除したい文字を指定します。例えば以下のようにパラメータを設定することで、特定の文字を削除できます：

```python
# カンマを削除
text = "価格は1,500円です"
result = re.sub(r",", "", text)
print(result)  # "価格は1500円です"

# スペースを削除
text = "Hello World"
result = re.sub(r" ", "", text)
print(result)  # "HelloWorld"
```

#### よく使う正規表現パターン

| パターン | 意味 | 例 |
|---------|------|-----|
| `\d` | 数字（0-9） | `re.sub(r"\d", "X", "abc123")` → `"abcXXX"` |
| `\D` | 数字以外 | `re.sub(r"\D", "", "abc123")` → `"123"` |
| `\s` | 空白文字 | `re.sub(r"\s", "", "a b c")` → `"abc"` |
| `[0-9]` | 数字（0-9） | `\d` と同じ |
| `[a-z]` | 英小文字（a-z） | - |
| `[^\d]` | 数字以外（^は否定） | `\D` と同じ |
| `+` | 1回以上の繰り返し | `\d+` で「1つ以上の数字」 |

#### re.findall() で抽出

```python
import re

text = "価格は1,500円、送料は500円です"

# すべての数字（カンマ含む）を抽出
numbers = re.findall(r"\d+,?\d*", text)
print(numbers)  # ['1,500', '500']

# カンマを含まない数字だけ
numbers = re.findall(r"\d+", text)
print(numbers)  # ['1', '500', '500']
```

### 数値への変換

先ほど紹介した方法によって数字を取得することはできますが、このままだといろいろな操作を加えるにあたって不便です。例えば、得られた数字の合計をする、ということはできません。

このような演算を行うためには、今考えている数字のデータ型（第2回で触れた内容）を**文字列**から**数値**に変換する必要があります。数値といっても整数と小数の2つの型があり、それぞれ変換する関数がPythonでは用意されています。

#### int() と float()

```python
# 整数に変換
price = int("1500")  # 1500

# 小数に変換
price = float("29.99")  # 29.99

# エラーになる例
price = int("1,500")  # ValueError（カンマがあるとダメ）
```

数値に変換する前に、カンマや通貨記号を削除する必要があります。この処理を行うには、`re.sub()` や `replace()` を使います。

```python
# replace() で削除してから変換
price = "¥1,500"
price = price.replace("¥", "").replace(",", "")
price = int(price)  # 1500

# re.sub() で数字だけを取り出す
import re
price = "¥1,500"
numbers_only = re.sub(r"[^\d]", "", price)
price = int(numbers_only)  # 1500
```

#### 安全に変換する

```python
def safe_int(text, default=0):
    """文字列を安全に整数に変換"""
    try:
        # 数字以外を削除
        numbers = re.sub(r"[^\d]", "", text)
        return int(numbers) if numbers else default
    except ValueError:
        return default

# 使用例
print(safe_int("¥1,500"))    # 1500
print(safe_int("価格未定"))   # 0
print(safe_int("abc"))       # 0
```

### 日付の処理

#### datetime で日付を扱う

```python
from datetime import datetime

# 文字列から日付オブジェクトを作成
date = datetime.strptime("2024-01-15", "%Y-%m-%d")
print(date)  # 2024-01-15 00:00:00

# 日付オブジェクトから文字列を作成
date_str = date.strftime("%Y年%m月%d日")
print(date_str)  # "2024年01月15日"
```

#### strptime と strftime の違い

| メソッド | 説明 | 入力例 | 出力例 |
|---------|------|------|------|
| `strptime` | 文字列を日付型として解析する | `"2024-01-15"` | datetime オブジェクト |
| `strftime` | 日付型を文字列として出力する | datetime オブジェクト | `"2024-01-15"` |

**日付型とは**: datetimeの関数によって日付に関する様々な演算ができるデータ構造です。日付のデータを解析（parse）できるように変換するため **strp**time という名前になっています。

**文字列とは**: 既にこのカリキュラムで取り扱っている、文字の集まりです。人間が見やすい形になっているデータ構造です。日付型のデータを人間の読みやすいフォーマット（format）に変換するため **strf**time という名前になっています。

#### フォーマット指定子

| 指定子 | 意味 | 例 |
|--------|------|-----|
| `%Y` | 4桁の年 | 2024 |
| `%y` | 2桁の年 | 24 |
| `%m` | 2桁の月（01-12） | 01 |
| `%d` | 2桁の日（01-31） | 15 |
| `%H` | 時（00-23） | 14 |
| `%M` | 分（00-59） | 30 |
| `%S` | 秒（00-59） | 45 |

#### 【応用】dateutil を使った柔軟な日付解析

`dateutil` ライブラリを使うと、様々な形式の日付を自動で解析できます。

```python
import re
from datetime import datetime
from dateutil.parser import parse

# 様々な形式を自動認識（英語・数字表記）
date1 = parse("2024/01/15")
date3 = parse("15-01-2024", dayfirst=True)
date4 = parse("Jan 15, 2024")

# 日本語形式は dateutil が対応していないため正規表現で変換
jp_match = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日", "2024年1月15日")
y, m, d = jp_match.groups()
date2 = datetime(int(y), int(m), int(d))

# すべて同じ日付になる
print(date1.strftime("%Y-%m-%d"))  # 2024-01-15
print(date2.strftime("%Y-%m-%d"))  # 2024-01-15
```

---

## 練習問題

### 問題1：基本的な文字列クリーニング

以下のデータから余分な空白や文字を削除してください。

```python
texts = [
    "  Python入門  ",
    "データ分析\n",
    "  スクレイピング講座  \n\n",
]

# すべてクリーンなテキストに変換
# 期待される結果: ["Python入門", "データ分析", "スクレイピング講座"]
```

**考え方のヒント:**

- `.strip()` で前後の空白・改行を削除できる
- リスト内包表記を使うと全要素を一括で処理できる

---

### 問題2：正規表現で数字を抽出

以下のテキストから数字だけを抽出してください。

```python
texts = [
    "在庫：残り5個",
    "価格は¥1,500です",
    "評価: 4.5/5.0",
]

# 各テキストから数字を抽出
# 期待される結果: ["5", "1500", "4.5/5.0"] など
```

**考え方のヒント:**

- `re.sub()` で数字以外を削除する方法：不要な文字を空文字に置換する
- `re.findall()` で数字を抽出する方法：`r"\d+"` で整数、`r"\d+\.?\d*"` で小数にも対応
- どちらの方法でも構わない

---

### 問題3：価格データを数値に変換

以下の価格データを数値に変換してください。

※問題2と違い、文字列ではなく数値で出力すること

```python
prices = [
    "¥1,500",
    "2,800円",
    "$29.99",
    "Price: €15.50",
    "無料",
]

# すべて数値に変換（無料は0とする）
# 期待される結果: [1500, 2800, 29.99, 15.50, 0]
```

**考え方のヒント:**

1. `re.findall(r"\d+\.?\d*", price)` で数字とピリオドだけを抽出する
2. 結果が空のリストの場合（「無料」など）は 0 を返す
3. 結果が複数の場合（カンマ区切りの `"1,500"` など）は `"".join()` で結合してから `float()` で変換する

---

### 問題4：日付フォーマットの統一

以下の様々な形式の日付を、すべて `"YYYY-MM-DD"` 形式に変換してください。

```python
dates = [
    "2024/01/15",
    "2024年1月15日",
    "15-01-2024",
    "Jan 15, 2024",
]

# すべて "2024-01-15" 形式に変換
```

**考え方のヒント:**

- `dateutil.parser.parse()` は英語・数字の形式を自動認識してくれる
- `strftime("%Y-%m-%d")` で統一フォーマットに変換する
- `"15-01-2024"` のような「日-月-年」形式は `dayfirst=True` オプションが必要
- `"2024年1月15日"` のような日本語形式は `re.match()` で年月日を抽出して `datetime()` で変換する

---

### 問題5：スクレイピングデータの総合整形

Books to Scrape から取得した以下のような「汚い」データを整形してください。

```python
books_data = [
    {
        "title": "  A Light in the Attic  ",
        "price": "£51.77",
        "rating": "Three",
        "availability": "In stock (22 available)",
    },
    {
        "title": "Tipping the Velvet",
        "price": "£53.74",
        "rating": "One",
        "availability": "In stock (20 available)",
    },
]

# 整形後のデータ:
# {
#     "title": "A Light in the Attic",  # 空白削除
#     "price": 51.77,                    # 数値
#     "rating": 3,                       # 数値
#     "stock": 22,                       # 在庫数を数値で
# }
```

**考え方のヒント:**

1. `title`: `.strip()` で空白削除
2. `price`: `"£"` を `replace()` で削除して `float()` で変換
3. `rating`: `rating_map` の辞書を使って数値に変換
4. `availability`: `re.findall(r"\d+", ...)` で数字を抽出して `int()` で変換
5. for ループで各 book を処理し、新しい辞書を `clean_books` に追加

---

## 検索キーワード

| 知りたいこと | 検索キーワード |
|-------------|---------------|
| 正規表現の基本 | `Python 正規表現 入門` |
| 数字だけ抽出 | `Python 正規表現 数字 抽出` |
| 日付の変換 | `Python datetime strptime` |
| dateutil の使い方 | `Python dateutil parser` |
| 文字列から数値 | `Python 文字列 数値 変換` |
| カンマ区切りの数字 | `Python カンマ 削除 数値変換` |

---

## 困ったときは

### 「ValueError: invalid literal for int()」

文字列に数字以外の文字が含まれています。

```python
# エラーになる例
price = int("¥1,500")  # ValueError

# 正しい方法
price_text = "¥1,500"
price_text = price_text.replace("¥", "").replace(",", "")
price = int(price_text)  # 1500
```

### 「正規表現が分からない」

まずは基本的なパターンから始めてください。

```python
import re

# 数字以外を削除
re.sub(r"[^\d]", "", text)

# 数字だけを抽出
re.findall(r"\d+", text)

# 小数を含む数字を抽出
re.findall(r"\d+\.?\d*", text)
```

詳しくは「Python 正規表現 チートシート」で検索してください。

### 「日付の解析に失敗する」

`dateutil.parser` を使うと、多くの形式を自動認識できます。

```python
import re
from datetime import datetime
from dateutil.parser import parse

# 英語・数字の形式は dateutil で対応
date = parse("2024/01/15")
date = parse("Jan 15, 2024")

# 日本語形式（"2024年1月15日"）は正規表現で変換
jp_match = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日", "2024年1月15日")
y, m, d = jp_match.groups()
date = datetime(int(y), int(m), int(d))
```

### 「空の文字列を数値に変換できない」

空の文字列は数値に変換できません。事前にチェックしてください。

```python
# エラーになる例
text = ""
number = int(text)  # ValueError

# 正しい方法
text = ""
if text:
    number = int(text)
else:
    number = 0

# または
number = int(text) if text else 0
```

---

## 確認事項

- 文字列の前後の空白を削除できた
- replace() で文字を置換できた
- 正規表現で数字を抽出できた
- 価格データを数値に変換できた
- 日付を統一フォーマットに変換できた
- datetime の strptime と strftime の違いがわかった
- スクレイピングで取得したデータを整形できた

---

## データ整形のベストプラクティス

### 1. できるだけ早い段階で整形する

```python
# 良い例: 取得直後に整形
for book in soup.select(".book"):
    price_text = book.select_one(".price").text
    price = float(price_text.replace("£", ""))  # すぐ整形
    books.append({"price": price})

# 悪い例: 後でまとめて整形（ミスしやすい）
for book in soup.select(".book"):
    price_text = book.select_one(".price").text
    books.append({"price": price_text})  # 文字列のまま

# 後でここで整形処理を行う
```

### 2. 関数にまとめる

```python
def clean_price(price_text):
    """価格テキストを数値に変換"""
    numbers = re.findall(r"\d+\.?\d*", price_text)
    return float(numbers[0]) if numbers else 0.0

# 使う
price = clean_price("¥1,500")
```

### 3. エラー処理を忘れない

```python
try:
    price = float(price_text.replace("£", ""))
except (ValueError, AttributeError):
    price = 0.0
```

---

**次回は「データの保存」です。CSVファイル・JSONファイル・pandasを使って、スクレイピングで取得したデータを保存・活用する方法を学びます。**
