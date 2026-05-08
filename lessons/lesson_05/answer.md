# 第5回：HTTP通信の基礎【解答・解説】

## 📝 requestsの基本 コードの説明

```python
import requests                        # requestsパッケージをインポートする

response = requests.get("https://example.com")  # GETリクエストを送り、レスポンスを受取る

print(response.status_code)  # レスポンスオブジェクトの「status_code」属性を参照して出力
print(response.text)         # レスポンスオブジェクトの「text」属性（HTML本文）を参照して出力
```

`response.status_code` や `response.text` のように「`.`」を使ってオブジェクトのデータにアクセスする書き方は、これPython中最初の登場です。詳しくは次回以降に出てきますが、今は「データを取り出す書き方」として覚えておいてください。

---

## 📝 問題1の解答

```python
import requests

response = requests.get("https://httpbin.org/get")

print(f"ステータス: {response.status_code}")
print(f"本文:\n{response.text}")
```

---

## 📝 問題2の解答

コードを実行してテキストが表示されれば正解です。

**発展：JSON形式で見る**

`response.json()` を使うと、レスポンスを辞書形式で取り出せるため、送ったパラメータだけをスッキリ確認できます。

```python
import requests

params = {"name": "太郎", "age": 25}
response = requests.get("https://httpbin.org/get", params=params)

# response.json() でJSON形式で見やすく
data = response.json()
print(data["args"])  # {'name': '太郎', 'age': '25'}
```

### なぜこう書くの？

`params` を渡すと、URLの後ろに `?name=太郎&age=25` が自動でつきます。自分でURLを組み立てなくて済むので便利です。

---

## 📝 問題3の解答

```python
import requests

def fetch_url(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"エラー: ステータス {response.status_code}")
            return None
    except Exception as e:
        print(f"エラー: {e}")
        return None

# テスト（200）
html_200 = fetch_url("https://httpbin.org/status/200")
print("200:", "取得成功" if html_200 is not None else "取得失敗")

# テスト（404）
html_404 = fetch_url("https://httpbin.org/status/404")
print("404:", "取得成功" if html_404 is not None else "取得失敗")
```

---

## 📝 問題4の解答

コードを実行して `タイムアウトしました` と表示されれば正解です。

---

## 💡 ポイント

`timeout` は待ち時間の上限です。指定した秒数待ってもサーバーが応答しない場合、そこで諦めます。

```python
requests.get(url, timeout=10)
```

---

**次回は「HTML解析入門」です！**
