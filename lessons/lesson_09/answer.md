# 第9回：データ整形とクリーニング【解答・解説】

## 📝 問題1の解答：基本的な文字列クリーニング

```python
texts = [
    "  Python入門  ",
    "データ分析\n",
    "  スクレイピング講座  \n\n",
]

# for ループ
clean_texts = []
for text in texts:
    clean_texts.append(text.strip())

print(clean_texts)
# ['Python入門', 'データ分析', 'スクレイピング講座']

# 【別解】リスト内包表記（推奨）
clean_texts = [text.strip() for text in texts]
print(clean_texts)
```

### なぜこう書くの？

```python
# .strip() = 前後の空白・タブ・改行を削除
text = "  こんにちは  \n"
text.strip()  # → "こんにちは"

# リスト内包表記 = リストを1行で処理
[text.strip() for text in texts]
# ↓ 展開すると
result = []
for text in texts:
    result.append(text.strip())
```

**💡 格言**: とにかく余分な情報がついた文字列には `text.strip()`！

スクレイピングで取得したテキストには、前後に余分な空白や改行が含まれていることがほとんどです。データの比較やクリーニングの第1ステップは、常に `.strip()` で周囲の空白を削除することが大切です。

### 【＋α】strip() のバリエーション

```python
text = "  こんにちは  "

# strip() = 両端の空白を削除
text.strip()   # → "こんにちは"

# lstrip() = 左側（先頭）だけ
text.lstrip()  # → "こんにちは  "

# rstrip() = 右側（末尾）だけ
text.rstrip()  # → "  こんにちは"
```

---

## 📝 問題2の解答：正規表現で数字を抽出

```python
import re

texts = [
    "在庫：残り5個",
    "価格は¥1,500です",
    "評価: 4.5/5.0",
]

# re.sub() で数字以外を削除
for text in texts:
    numbers = re.sub(r"[^\d./]", "", text)
    print(f"{text} → {numbers}")

# 出力:
# 在庫：残り5個 → 5
# 価格は¥1,500です → 1500
# 評価: 4.5/5.0 → 4.5/5.0

# 【別解】re.findall() で数字を抽出
for text in texts:
    numbers = re.findall(r"\d+\.?\d*", text)
    print(f"{text} → {numbers}")

# 出力:
# 在庫：残り5個 → ['5']
# 価格は¥1,500です → ['1', '500']
# 評価: 4.5/5.0 → ['4.5', '5.0']
```

### なぜこう書くの？

```python
# re.sub(パターン, 置換文字, 対象文字列)
re.sub(r"[^\d./]", "", "価格¥1,500")
#      ↑数字・ピリオド・スラッシュ以外
#                 ↑空文字に置換（削除）

# [^\d./] の意味
# [   ] = 文字クラス
# ^     = 否定（〜以外）
# \d    = 数字（0-9）
# .     = ピリオド
# /     = スラッシュ
# → 「数字・ピリオド・スラッシュ以外」

# re.findall(パターン, 対象文字列)
re.findall(r"\d+\.?\d*", text)
# \d+  = 1つ以上の数字
# \.?  = ピリオドが0個または1個
# \d*  = 0個以上の数字
# → 「12.34」のような小数を抽出
```

### 正規表現パターンの比較

| パターン | マッチする例 | マッチしない例 |
|---------|-------------|---------------|
| `\d+` | `"123"`, `"5"` | `"12.34"` |
| `\d+\.?\d*` | `"123"`, `"12.34"` | - |
| `[0-9]+` | `"123"` | `"12.34"` |
| `[\d,]+` | `"1,500"` | - |

---

## 📝 問題3の解答：価格データを数値に変換

```python
import re

prices = [
    "¥1,500",
    "2,800円",
    "$29.99",
    "Price: €15.50",
    "無料",
]

# 関数を作る
def extract_price(text):
    """価格テキストから数値を抽出"""
    # 数字とピリオドを抽出
    numbers = re.findall(r"\d+\.?\d*", text)

    # 「if numbers:」は「リストに要素があるか」をチェック
    # re.findall() は数字が見つからないと空のリスト [] を返す
    # 空のリストに対して numbers[0] でアクセスするとエラー（IndexError）になるため、
    # 事前にチェックしてエラーを避ける（プログラマー的な安全な書き方）
    if numbers:
        # カンマで区切られた数字を結合
        # ["1", "500"] → "1500"
        price_str = "".join(numbers)
        return float(price_str)
    else:
        # 数字がない場合は 0
        return 0.0

# すべての価格を変換
price_values = [extract_price(price) for price in prices]
print(price_values)
# [1500.0, 2800.0, 29.99, 15.5, 0.0]

# 詳しく表示
for original, value in zip(prices, price_values):
    print(f"{original:20s} → {value}")

# 出力:
# ¥1,500               → 1500.0
# 2,800円              → 2800.0
# $29.99               → 29.99
# Price: €15.50        → 15.5
# 無料                 → 0.0
```

### なぜこう書くの？

```python
# カンマ区切りの数字の処理
text = "¥1,500"
numbers = re.findall(r"\d+\.?\d*", text)
# → ['1', '500']

# カンマを含めて抽出する場合
numbers = re.findall(r"[\d,]+\.?\d*", text)
# → ['1,500']
# この場合、カンマを削除してから変換
price_str = numbers[0].replace(",", "")
price = float(price_str)

# または、数字だけを抽出して結合
numbers = re.findall(r"\d+", text)  # ['1', '500']
price_str = "".join(numbers)        # '1500'
price = float(price_str)            # 1500.0
```

**💡 if numbers: の意味**: `re.findall()` で数字が見つからない場合、空のリスト `[]` が返されます。`if numbers:` は「リストに要素があるか」をチェックしています。このチェックがないと、「無料」のような数字がない文字列に対して `numbers[0]` でエラーが発生します（IndexError）。このように、「プログラマー的」に事前にエラーの可能性をチェックして対応する方法を覚えておくと、より堅牢なコードが書けます。

### 処理の流れ（図解）

```
"¥1,500"
  ↓ re.findall(r"\d+\.?\d*", "¥1,500")
['1', '500']
  ↓ "".join(['1', '500'])
'1500'
  ↓ float('1500')
1500.0

"$29.99"
  ↓ re.findall(r"\d+\.?\d*", "$29.99")
['29.99']
  ↓ "".join(['29.99'])
'29.99'
  ↓ float('29.99')
29.99

"無料"
  ↓ re.findall(r"\d+\.?\d*", "無料")
[]
  ↓ if numbers: float("".join(numbers)) else: 0.0
0.0
```

---

## 📝 問題4の解答：日付フォーマットの統一

```python
import re
from datetime import datetime
from dateutil.parser import parse

dates = [
    "2024/01/15",
    "2024年1月15日",
    "15-01-2024",
    "Jan 15, 2024",
]

formatted_dates = []

for date_str in dates:
    # 日本語の日付形式（例: "2024年1月15日"）は dateutil が対応していないため正規表現で変換
    jp_match = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日", date_str)
    if jp_match:
        y, m, d = jp_match.groups()
        date_obj = datetime(int(y), int(m), int(d))
    else:
        # 日本語以外の形式は dateutil で自動解析（dayfirst=True で "15-01-2024" に対応）
        date_obj = parse(date_str, dayfirst=True)

    # 統一フォーマットに変換
    formatted = date_obj.strftime("%Y-%m-%d")
    formatted_dates.append(formatted)

    print(f"{date_str:20s} → {formatted}")

# 出力:
# 2024/01/15           → 2024-01-15
# 2024年1月15日        → 2024-01-15
# 15-01-2024           → 2024-01-15
# Jan 15, 2024         → 2024-01-15

print(formatted_dates)
# ['2024-01-15', '2024-01-15', '2024-01-15', '2024-01-15']
```

### なぜこう書くの？

```python
# dateutil.parser.parse() = 柔軟な日付解析
from dateutil.parser import parse

# 様々な形式を自動認識（英語・数字表記）
parse("2024/01/15")     # datetime(2024, 1, 15, 0, 0)
# ※ "2024年1月15日" のような日本語形式は dateutil が対応していないため、
# 正規表現で変換してから datetime() で作成する

# dayfirst=True オプション
# "15-01-2024" を「日-月-年」として解釈
parse("15-01-2024", dayfirst=True)  # 2024-01-15
parse("15-01-2024", dayfirst=False) # 2024-03-15（間違い）

# strftime() = datetime → 文字列
date_obj.strftime("%Y-%m-%d")  # "2024-01-15"
date_obj.strftime("%Y年%m月%d日")  # "2024年01月15日"
```

### datetime の基本的な使い方

```python
from datetime import datetime

# 現在時刻を取得
now = datetime.now()
print(now)  # 2024-01-15 14:30:45.123456

# 文字列から datetime に変換（strptime）
date = datetime.strptime("2024-01-15", "%Y-%m-%d")

# datetime から文字列に変換（strftime）
date_str = date.strftime("%Y年%m月%d日")
print(date_str)  # "2024年01月15日"
```

### フォーマット指定子まとめ

| 指定子 | 意味 | 例 |
|--------|------|-----|
| `%Y` | 4桁の年 | 2024 |
| `%m` | 2桁の月 | 01 |
| `%d` | 2桁の日 | 15 |
| `%H` | 時（24時間） | 14 |
| `%I` | 時（12時間） | 02 |
| `%M` | 分 | 30 |
| `%S` | 秒 | 45 |
| `%p` | AM/PM | PM |

---

## 📝 問題5の解答：スクレイピングデータの総合整形

```python
import re

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

# 評価を数値に変換するマップ
rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}

# データを整形
clean_books = []

for book in books_data:
    # タイトル: 前後の空白を削除
    title = book["title"].strip()

    # 価格: £を削除して数値に変換
    price = float(book["price"].replace("£", ""))

    # 評価: 文字列から数値に変換
    rating = rating_map.get(book["rating"], 0)

    # 在庫: 正規表現で数字を抽出
    stock_numbers = re.findall(r"\d+", book["availability"])
    stock = int(stock_numbers[0]) if stock_numbers else 0

    # 整形したデータを辞書にまとめる
    clean_book = {
        "title": title,
        "price": price,
        "rating": rating,
        "stock": stock,
    }

    clean_books.append(clean_book)

# 結果を表示
for book in clean_books:
    print(book)

# 出力:
# {'title': 'A Light in the Attic', 'price': 51.77, 'rating': 3, 'stock': 22}
# {'title': 'Tipping the Velvet', 'price': 53.74, 'rating': 1, 'stock': 20}
```

### 関数化したバージョン（推奨）

```python
import re

def clean_book_data(book):
    """書籍データを整形"""
    rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    availability_numbers = re.findall(r"\d+", book["availability"])

    return {
        "title": book["title"].strip(),
        "price": float(book["price"].replace("£", "")),
        "rating": rating_map.get(book["rating"], 0),
        "stock": int(availability_numbers[0]) if availability_numbers else 0,
    }

# 使う
clean_books = [clean_book_data(book) for book in books_data]
```

### なぜこう書くの？

```python
# .strip() = 前後の空白削除
"  A Light in the Attic  ".strip()
# → "A Light in the Attic"

# .replace() + float() = 価格を数値に
"£51.77".replace("£", "")  # → "51.77"
float("51.77")              # → 51.77

# rating_map.get() = 安全に変換
rating_map.get("Three", 0)  # → 3
rating_map.get("Unknown", 0)  # → 0（エラーにならない）

# re.findall() で数字を抽出
re.findall(r"\d+", "In stock (22 available)")
# → ['22']
# [0] で最初の要素を取得
```

### 処理の流れ（1冊目の例）

```
元データ:
{
  "title": "  A Light in the Attic  ",
  "price": "£51.77",
  "rating": "Three",
  "availability": "In stock (22 available)"
}

↓ 整形

title:
  "  A Light in the Attic  "
  → .strip()
  → "A Light in the Attic"

price:
  "£51.77"
  → .replace("£", "")
  → "51.77"
  → float()
  → 51.77

rating:
  "Three"
  → rating_map.get("Three", 0)
  → 3

stock:
  "In stock (22 available)"
  → re.findall(r"\d+", "In stock (22 available)")
  → ['22']
  → [0]
  → '22'
  → int()
  → 22

↓ 結果

{
  "title": "A Light in the Attic",
  "price": 51.77,
  "rating": 3,
  "stock": 22
}
```

---

## 💡 今回のポイントまとめ

### 文字列クリーニング

```python
# 前後の空白削除
text.strip()

# 文字を置換
text.replace("古い", "新しい")

# 連続する空白を1つに
" ".join(text.split())
```

### 正規表現

```python
import re

# 置換（削除）
re.sub(r"[^\d]", "", text)  # 数字以外を削除

# 抽出
re.findall(r"\d+", text)          # 整数
re.findall(r"\d+\.?\d*", text)    # 小数を含む
```

### 数値変換

```python
# 整数
int("123")

# 小数
float("12.34")

# エラー回避
int(text) if text else 0
```

### 日付処理

```python
from datetime import datetime
from dateutil.parser import parse

# 柔軟な解析
date = parse("2024年1月15日")

# フォーマット変換
date.strftime("%Y-%m-%d")  # "2024-01-15"
```

---

## 🔍 よくある間違い

### ❌ strip() を忘れる

```python
# 間違い
title = "  Python入門  "
if title == "Python入門":  # False（空白があるため）
    print("一致")

# 正しい
title = "  Python入門  ".strip()
if title == "Python入門":  # True
    print("一致")
```

---

### ❌ 数値変換前にクリーニングを忘れる

```python
# 間違い
price = int("¥1,500")  # ValueError

# 正しい
price_text = "¥1,500"
price_text = price_text.replace("¥", "").replace(",", "")
price = int(price_text)  # 1500
```

---

### ❌ 正規表現のエスケープを忘れる

```python
# 間違い（. は任意の1文字）
re.findall(r"\d+.\d+", text)  # "12x34" もマッチしてしまう

# 正しい（\. でエスケープ）
re.findall(r"\d+\.\d+", text)  # "12.34" のみマッチ
```

---

### ❌ リストが空の場合を考慮しない

```python
# 間違い
numbers = re.findall(r"\d+", "無料")
price = int(numbers[0])  # IndexError（リストが空）

# 正しい
numbers = re.findall(r"\d+", "無料")
price = int(numbers[0]) if numbers else 0
```

---

## 🔧 実践的なテクニック

### 1. データ整形を関数化

```python
def clean_price(text):
    """価格を数値に変換"""
    numbers = re.findall(r"\d+\.?\d*", text)
    if numbers:
        return float("".join(numbers))
    return 0.0

def clean_date(text):
    """日付を YYYY-MM-DD 形式に変換"""
    try:
        date = parse(text, dayfirst=True)
        return date.strftime("%Y-%m-%d")
    except:
        return None

# 使う
price = clean_price("¥1,500")
date = clean_date("2024年1月15日")
```

### 2. パイプライン処理

```python
def clean_text(text):
    """テキストを段階的にクリーニング"""
    # 1. 前後の空白削除
    text = text.strip()

    # 2. 改行をスペースに
    text = text.replace("\n", " ")

    # 3. 連続する空白を1つに
    text = " ".join(text.split())

    return text

# 使う
clean = clean_text("  こんにちは\n世界  ")
print(clean)  # "こんにちは 世界"
```

### 3. 一括変換

```python
# 複数のデータを一括で整形
def clean_all_books(books):
    """すべての書籍データを整形"""
    return [clean_book_data(book) for book in books]

clean_books = clean_all_books(raw_books)
```

---

## 🎓 さらに学びたい人向け

### 正規表現のテストツール

- [Regex101](https://regex101.com/) - 正規表現をオンラインでテストできる
- Python の `re` モジュールを選択して使う

### pandas を使ったデータ整形

```python
import pandas as pd

# DataFrame に変換
df = pd.DataFrame(books_data)

# 一括で整形
df['price'] = df['price'].str.replace('£', '').astype(float)
df['title'] = df['title'].str.strip()
```

---

**次回は「データの保存」です！**
