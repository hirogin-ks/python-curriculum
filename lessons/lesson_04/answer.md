# 第4回：Python基礎（後編）【解答・解説】

## 📝 問題1の解答：平均を返す関数

```python
def average(a, b):
    result = (a + b) / 2
    return result

# テスト
print(average(10, 20))  # 15.0
print(average(3, 7))    # 5.0
```

### もっと短く書くと

```python
def average(a, b):
    return (a + b) / 2
```

### なぜこう書くの？

```python
# 足して2で割る = 平均
(a + b) / 2

# return で結果を返す
# これがないと None になる
return (a + b) / 2
```

---

## 📝 問題2の解答：最大値を返す関数

```python
def find_max(numbers):
    # 最初は1番目の値を「一番大きい」とする
    max_value = numbers[0]
    
    # 最初から順番に全部見ていく
    for num in numbers:
        if num > max_value:
            # 今見てる値の方が大きければ更新
            max_value = num
    
    return max_value

# テスト
print(find_max([3, 1, 4, 1, 5, 9, 2, 6]))  # 9
```

### 処理の流れ（図で説明）

```
リスト: [3, 1, 4, 1, 5, 9, 2, 6]

最初: max_value = 3

3 > 3 ? → No
1 > 3 ? → No
4 > 3 ? → Yes! → max_value = 4
1 > 4 ? → No
5 > 4 ? → Yes! → max_value = 5
9 > 5 ? → Yes! → max_value = 9
2 > 9 ? → No
6 > 9 ? → No

結果: max_value = 9
```

---

## 📝 問題3の解答：ファイル操作

```python
# 1. 書き込み
with open("shopping.txt", "w", encoding="utf-8") as f:
    f.write("買い物リスト:\n")
    f.write("- りんご\n")
    f.write("- バナナ\n")
    f.write("- 牛乳\n")

# 2. 読み込み
with open("shopping.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)
```

### 出力結果

```
買い物リスト:
- りんご
- バナナ
- 牛乳
```

### なぜこう書くの？

```python
# "w" = write（書き込み）モード
# ファイルがなければ作る、あれば上書き
open("shopping.txt", "w")

# "r" = read（読み込み）モード
open("shopping.txt", "r")

# \n = 改行
f.write("りんご\n")  # りんご の後で改行

# encoding="utf-8" = 日本語が文字化けしないおまじない
```

---

## 📝 問題4の解答：安全な割り算

### 方法1: if で事前チェック

```python
def safe_divide(a, b):
    if b == 0:
        return None
    return a / b

print(safe_divide(10, 2))   # 5.0
print(safe_divide(10, 0))   # None
```

### 方法2: try-except

```python
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None

print(safe_divide(10, 2))   # 5.0
print(safe_divide(10, 0))   # None
```

### どっちがいい？

- **方法1**: シンプルでわかりやすい
- **方法2**: 特定の例外だけを捕まえられる（必要なら対象を増やせる）

今回はどちらでもOK！

---

## 📝 問題5の解答：商品データを辞書で

```python
def create_product(name, price):
    """商品を辞書で作る"""
    return {"name": name, "price": price}

def get_product_info(product):
    """「商品名: ○○円」という文字列を返す"""
    return f"{product['name']}: {product['price']}円"

# テスト
apple = create_product("りんご", 150)
print(apple)  # {'name': 'りんご', 'price': 150}
print(get_product_info(apple))  # りんご: 150円
```

### なぜこう書くの？

```python
# 関数の引数がそのまま辞書の値になる
def create_product(name, price):
    return {"name": name, "price": price}
    #        ↑キー   ↑引数で受け取った値

# f-string の中で辞書の値を使う
# 注意: 外側が " なら内側は ' を使う
f"{product['name']}"
```

---

## 💡 今回のポイントまとめ

### 関数の基本形

```python
def 関数名(引数1, 引数2):
    # 処理
    return 結果
```

### ファイル操作の基本形

```python
# 書き込み
with open("ファイル名", "w", encoding="utf-8") as f:
    f.write("内容")

# 読み込み
with open("ファイル名", "r", encoding="utf-8") as f:
    content = f.read()
```

### エラー処理の基本形

```python
try:
    # エラーが起きるかもしれない処理
except エラーの種類:
    # エラーが起きたときの処理
```

---

## 🔍 よくある間違い

### ❌ return を忘れる

```python
def add(a, b):
    result = a + b
    # return がない！

x = add(1, 2)
print(x)  # None になる
```

### ❌ インデントがおかしい

```python
def greet(name):
print(f"Hello, {name}")  # ← インデントがない！
```

### ❌ ファイルモードを間違える

```python
# 読むつもりが書いてしまった
with open("data.txt", "w") as f:  # w は書き込み！
    content = f.read()  # エラー
```

---

**次回は「HTTP通信の基礎」です！**
