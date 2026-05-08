# 第3回：Python基礎（前編）【解答・解説】

## 📝 問題1の解答：リストの操作

```python
# 1. リストを作る
languages = ["Python", "Java", "JavaScript"]
print(languages)  # ['Python', 'Java', 'JavaScript']

# 2. "Ruby" を末尾に追加
languages.append("Ruby")
print(languages)  # ['Python', 'Java', 'JavaScript', 'Ruby']

# 3. "Java" を削除
languages.remove("Java")
print(languages)  # ['Python', 'JavaScript', 'Ruby']

# 4. リストの長さを表示
print(len(languages))  # 3
```

### なぜこう書くの？

```python
# append = 「追加する」という意味
# リストの最後に追加される
languages.append("Ruby")

# remove = 「取り除く」という意味
# 指定した値を削除する
languages.remove("Java")

# len = length（長さ）の略
# リストの要素数を返す
len(languages)
```

---

## 📝 問題2の解答：辞書の操作

```python
# 辞書を作る
book = {
    "title": "Python入門",
    "author": "山田太郎",
    "price": 2500
}

# 1. タイトルを表示
print(book["title"])  # Python入門

# 2. "pages": 300 を追加
book["pages"] = 300
print(book)
# {'title': 'Python入門', 'author': '山田太郎', 'price': 2500, 'pages': 300}

# 3. 価格を 2800 に変更
book["price"] = 2800
print(book["price"])  # 2800
```

### なぜこう書くの？

```python
# 辞書の値を取り出す
# 辞書["キー"] で、そのキーの値が取れる
book["title"]  # → "Python入門"

# 辞書に追加する
# 新しいキーを指定して値を入れる
book["pages"] = 300

# 辞書の値を変更する
# 既存のキーを指定して新しい値を入れる
# （追加と同じ書き方！）
book["price"] = 2800
```

**ポイント: 追加も変更も `辞書["キー"] = 値` で同じ！**

---

## 📝 問題3の解答：リストの辞書

```python
# 商品データ（辞書のリスト）
products = [
    {"name": "りんご", "price": 150},
    {"name": "バナナ", "price": 100},
    {"name": "牛乳", "price": 200}
]

# 1. 全商品の名前を表示
print("--- 商品一覧 ---")
for product in products:
    print(product["name"])

# 出力:
# りんご
# バナナ
# 牛乳

# 2. 合計金額を計算
total = 0
for product in products:
    total = total + product["price"]
    # 省略形: total += product["price"]

print(f"合計: {total}円")  # 合計: 450円
```

### なぜこう書くの？（図で説明）

```
products = [
    {"name": "りんご", "price": 150},  ← これが product（1周目）
    {"name": "バナナ", "price": 100},  ← これが product（2周目）
    {"name": "牛乳", "price": 200}     ← これが product（3周目）
]

for product in products:
    # product は辞書なので、["name"] で名前が取れる
    print(product["name"])
```

### 合計の計算（図で説明）

```
最初: total = 0

1周目: total = 0 + 150 = 150
2周目: total = 150 + 100 = 250
3周目: total = 250 + 200 = 450

最後: total = 450
```

---

## 📝 問題4の解答：BMI判定

```python
# 1. データを用意
height = 170  # cm
weight = 65   # kg

# 2. 身長をメートルに変換
height_m = height / 100  # 1.7

# 3. BMIを計算
bmi = weight / (height_m ** 2)
# ** は「○乗」。height_m ** 2 は「height_m の2乗」

print(f"BMI: {bmi:.1f}")  # BMI: 22.5
# :.1f は「小数点以下1桁」という意味

# 4. 判定
if bmi < 18.5:
    print("やせ型")
elif bmi < 25:
    print("標準")
else:
    print("肥満")

# 出力: 標準
```

### なぜこう書くの？

```python
# ** は「累乗（るいじょう）」
# 2 ** 3 = 2の3乗 = 8
# height_m ** 2 = height_m × height_m

# elif は「else if」の略
# 「そうじゃなくて、もし〜なら」という意味
if bmi < 18.5:
    # 18.5未満
elif bmi < 25:
    # 18.5以上 かつ 25未満
else:
    # 25以上
```

---

## 📝 問題5の解答：ループで集計

```python
scores = [
    {"name": "田中", "score": 85},
    {"name": "佐藤", "score": 72},
    {"name": "鈴木", "score": 90},
    {"name": "高橋", "score": 65}
]

print("80点以上の人:")
for person in scores:
    if person["score"] >= 80:
        print(f"  {person['name']}: {person['score']}点")

# 出力:
# 80点以上の人:
#   田中: 85点
#   鈴木: 90点
```

### なぜこう書くの？（処理の流れ）

```
1周目: person = {"name": "田中", "score": 85}
       85 >= 80 → True → 表示する

2周目: person = {"name": "佐藤", "score": 72}
       72 >= 80 → False → 表示しない

3周目: person = {"name": "鈴木", "score": 90}
       90 >= 80 → True → 表示する

4周目: person = {"name": "高橋", "score": 65}
       65 >= 80 → False → 表示しない
```

---

## 💡 今回のポイントまとめ

### リストと辞書の使い分け

| こんなとき | 使うもの | 例 |
|-----------|---------|-----|
| 順番に並べたい | リスト | `["A", "B", "C"]` |
| 名前をつけて管理したい | 辞書 | `{"name": "田中"}` |
| 複数の「もの」を管理 | 辞書のリスト | `[{...}, {...}]` |

### よく使うコード

```python
# リストに追加
list.append(値)

# 辞書の値を取得
dict["キー"]

# 辞書に追加・変更
dict["キー"] = 値

# リストをループ
for item in list:
    print(item)

# 条件分岐
if 条件:
    処理1
elif 条件2:
    処理2
else:
    処理3
```

---

## 🔍 もっと知りたい人向け

### 検索キーワード

- `Python リスト内包表記` - リストをもっと短く書く方法
- `Python 辞書 get` - キーがなくてもエラーにならない方法
- `Python enumerate` - ループで番号も一緒に取得

---

**次回は「Python基礎（後編）」です！**
