# 第22回：アンチスクレイピング対策

## 今回のゴール

- Webサイトがボット（自動プログラム）をどのように検知しているかを理解する
- **User-Agent を変更して、スクレイピングプログラムを「人間のブラウザ」に見せる技術を習得する**
- その他のアンチスクレイピング対策（待機時間、Session など）に対応する方法を学ぶ
- 倫理的・法的観点からスクレイピングを判断できるようになる

## 所要時間：90分

---

## 導入：なぜスクレイピングが弾かれるのか

スクレイピングプログラムを実行しているとき、突然アクセスが遮断されたり、正しくない内容が返ってきたりすることがあります。これは、Webサイト側が「ボット（自動プログラム）によるアクセス」を検知して対処しているためです。

なぜサイト側はボットを弾くのでしょうか。主な理由は次の通りです。

- **サーバーへの負荷**: ボットは人間より圧倒的に速くアクセスするため、サーバーに過大な負荷がかかる
- **データの保護**: 苦労して作ったコンテンツを大量に収集されるのを防ぐ
- **不正利用の防止**: ログイン情報の総当たり攻撃など悪意のあるアクセスを防ぐ

サイト側の検知手法と、スクレイピング側の対処法は次のように対応しています。

| サイト側の検知手法       | 判断基準                 | スクレイピング側の対処           |
| ------------------------ | ------------------------ | -------------------------------- |
| User-Agent チェック      | ブラウザかどうか         | ブラウザの User-Agent を設定する |
| リクエスト間隔の監視     | 短時間に大量アクセス     | 待機時間を入れる                 |
| IP アドレスの監視        | 同一IPからの連続アクセス | アクセス頻度を下げる             |
| Cookie・セッションの確認 | 正規のセッションがあるか | Session を使う                   |
| JavaScript の実行確認    | JSを実行しているか       | Selenium を使う                  |

これらの対処法の中で、**最も基本的で重要なのが User-Agent の変更**です。

User-Agent を適切に設定するだけで、スクレイピングプログラムがまるで人間のブラウザからのアクセスに見えるようになります。このレッスンでは User-Agent を軸に、ボット検知を回避する技術を習得します。

その上で、以下の2つの要素も組み合わせることで、さらに「人間らしい」アクセスが実現できます：

- **ボット検知を回避する技術**（User-Agent、ヘッダー設定）：自分がボットであることを隠す
- **サーバーに負荷をかけない技術**（待機時間、アクセス頻度の調整）：サーバーのダメージを防ぐ

**ただし、これらの対処法の大半はあくまで「ボット検知を回避する」ためのものです。** User-Agent やヘッダー設定は偽装技術であり、自分がボットであることを隠すための手段です。サイトの利用規約でスクレイピングが禁止されている場合は、技術的に可能であっても行ってはいけません。

重要な倫理的原則は：**どれだけ技術的に巧妙に隠しても、サーバーのルール（robots.txt、利用規約）に従わない限り、スクレイピングを行うべきではない**ということです。人の家に上がるときはそのお家のルールに従うように、スクレイピングをするときもサーバーを利用する上でのルールに従う必要があります。

---

## ハンズオン：リクエストヘッダーを確認してみよう

**ヘッダーについて：** HTTPリクエストの「ヘッダー」は、HTMLの `<header>` タグのことではなく、Webブラウザやスクレイピングプログラムがサーバーに送る「付加情報」です。「どのブラウザからのアクセスか」「どの言語に対応しているか」などの情報をサーバーに伝えます。

その中で最も重要なのが **User-Agent** で、サーバーはこれを見て「どんなクライアント（ブラウザ？Pythonスクリプト？）からのアクセスか」を判定します。自分のプログラムがどのようなヘッダーを送っているか確認しましょう。`httpbin.org` はリクエストの詳細を返してくれる便利なテストサービスです。

```python
import requests

# ヘッダーなしのリクエスト
response = requests.get("https://httpbin.org/headers")
print("ヘッダーなし:")
print(response.json())
```

実行すると、`"User-Agent": "python-requests/2.x.x"` のように表示されます。サイト側からは「Pythonスクリプトからのアクセス」とすぐに識別できます。

次に、ブラウザと同様のヘッダーを設定してみます。

```python
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

response = requests.get("https://httpbin.org/headers", headers=headers)
print("ヘッダーあり:")
print(response.json())
```

`User-Agent` がブラウザのものに変わっていることが確認できます。

---

## 解説

### User-Agent とは

User-Agent とは、HTTPリクエストに含まれる「このリクエストを送ってきたのは何者か」を示す情報です。ブラウザ、スマートフォン、Pythonスクリプトなど、アクセス元の種類をサーバーに伝えます。

```text
python-requests/2.31.0             ← Pythonスクリプトと丸わかり
Mozilla/5.0 (Windows NT 10.0; ...) ← 通常のブラウザと同じ見た目
```

多くのサイトは `python-requests` という文字列を含む User-Agent を持つリクエストをブロックまたは制限し、ボットを検知します。ブラウザの User-Agent に変更することで、このボット検知を回避できることがあります。これは「自分がボットであることを隠す」ための技術であることに注意してください。

### よく使う User-Agent

```python
# Windows + Chrome
USER_AGENTS = {
    "chrome_windows": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    # Mac + Safari
    "safari_mac": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.1 Safari/605.1.15"
    ),
    # iPhone + Safari
    "safari_iphone": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.1 Mobile/15E148 Safari/604.1"
    ),
}
```

### 複数の User-Agent をランダムに使う

同じ User-Agent を使い続けると、それ自体がパターンとして検知される場合があります。複数の User-Agent をランダムに切り替えることで、より自然なアクセスに近づけられます。

```python
import random
import requests

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 ...",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ...",
]

def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "ja,en-US;q=0.9",
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    }

url = "https://httpbin.org/get"
response = requests.get(url, headers=get_random_headers())
```

### ランダムな待機時間

人間のブラウジングは、ページを読んだり考えたりするため、アクセス間隔が一定ではありません。スクレイピングでも `random.uniform()` でランダムな待機時間を入れると、より自然な動作に近づけられます。

```python
import time
import random

def wait_politely(min_sec=1.0, max_sec=3.0):
    """ランダムな時間待機する"""
    wait = random.uniform(min_sec, max_sec)
    time.sleep(wait)
```

待機時間の目安：

| アクセス先                             | 推奨待機時間       |
| -------------------------------------- | ------------------ |
| 一般的なWebサイト                      | 1〜3秒             |
| 高負荷なサービス・API                  | 3〜10秒            |
| robots.txt に Crawl-delay の指定がある | 指定された秒数以上 |

### Session に共通ヘッダーを設定する

`Session` に一度設定すれば、以降のすべてのリクエストに自動的に付与されます。

```python
import requests

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Accept-Language": "ja,en-US;q=0.9",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Referer": "https://www.google.com/",  # 検索エンジンからのアクセスに見せる
})
```

### Referer ヘッダーとは

`Referer` は「どのページからリンクをたどってきたか」を示すヘッダーです。直接URLを打ち込んでアクセスするとき（例：スクレイピングプログラム）は `Referer` がありませんが、ブラウザで普通にリンクをクリックするときは自動的に付きます。

`Referer` を設定することで、外部サイトからリンクをたどってきたように見せることができます。ただし、送る `Referer` は実際にリンクが存在するページのURLにするのが自然です。

### 倫理的・法的な観点からの注意

**最も重要な原則：ブラウザと同じように、サーバーに過大な負荷（ダメージ）を与えない利用方法をすること。**

人の家に上がるときはそのお家のルールに従い礼儀正しく振る舞うように、スクレイピングをするときもサーバーを利用する上でのルールに従って礼儀正しく利用してください。

技術的にアンチスクレイピング対策を回避できたとしても、以下の点を必ず確認してください。

**具体的に確認すること：**

1. **robots.txt** を確認し、`Disallow` に指定されたパスにはアクセスしない
2. **利用規約** を確認し、スクレイピングを禁止していないか確認する
3. **著作権** のあるコンテンツを無断で公開・販売しない
4. サーバーに過大な負荷をかけない（短時間の大量アクセスをしない）

スクレイピングは技術的には可能であっても、以下のルールを守らない限り行うべきではありません。技術と倫理は別です。

---

## 練習問題

### 問題1：ヘッダーなしとありを比較する

`python/lesson22/01_headers_compare.py` に回答を書いてください。

以下のコードを完成させて、ヘッダーの有無でレスポンスがどう変わるかを確認してください。

```python
import requests

url = "https://httpbin.org/headers"

# ① ヘッダーなし
response_plain = requests.get(url)
print("ヘッダーなし User-Agent:")
print(response_plain.json()["headers"].get("User-Agent"))

# ② ヘッダーあり（ブラウザのものを設定する）
headers = {
    # ここにヘッダーを追加する
}
response_with_headers = requests.get(url, headers=headers)
print("ヘッダーあり User-Agent:")
print(response_with_headers.json()["headers"].get("User-Agent"))
```

さらに、`https://httpbin.org/get` にアクセスして、送信されたすべてのヘッダーを表示してみてください。

**考え方:**

```
1. headers 辞書に "User-Agent" を追加する
2. "Accept-Language" と "Accept" も追加してみる
3. response.json()["headers"] でヘッダー全体が確認できる
```

---

### 問題2：ランダム待機付きのスクレイパーを作る

`python/lesson22/02_random_wait_scraper.py` に回答を書いてください。

以下の条件を満たすスクレイパーを実装してください。

```
条件:
- Session を使う
- User-Agent はランダムに選ぶ（最低3種類用意する）
- リクエストのたびに 1〜3 秒のランダムな待機を入れる
- 5つの URL に順番にアクセスして結果を表示する

URL リスト:
urls = [
    "https://httpbin.org/get",
    "https://httpbin.org/user-agent",
    "https://httpbin.org/headers",
    "https://httpbin.org/get",
    "https://httpbin.org/user-agent",
]
```

期待する出力例：

```
[1/5] https://httpbin.org/get → 200 (待機: 2.1秒)
[2/5] https://httpbin.org/user-agent → 200 (待機: 1.4秒)
...
```

**考え方:**

```
1. USER_AGENTS リストを定義する
2. Session を作り、リクエストのたびに random.choice でヘッダーを更新する
3. random.uniform(1.0, 3.0) で待機時間を計算して time.sleep する
4. enumerate で順番と URL を同時に取り出す
```

---

### 問題3：robots.txt チェック付きのスクレイパーを作る

`python/lesson22/03_robots_check.py` に回答を書いてください。

アクセスする前に robots.txt を確認し、アクセスが許可されているURLのみ処理するスクレイパーを作成してください。

```
条件:
- urllib.robotparser.RobotFileParser を使う
- 対象サイト: https://quotes.toscrape.com/
- スクレイパーの名前（User-Agent）: "MyCrawler"
- /login, /page/1/ など複数のパスを確認する
- アクセス可能なパスのみ実際に requests.get する
```

期待する出力例：

```
/login → アクセス許可
/page/1/ → アクセス許可
/admin/ → アクセス禁止（スキップ）
```

**考え方:**

```
1. RobotFileParser を作り、set_url(.../robots.txt) と read() で robots.txt をロードする
2. rp.can_fetch("MyCrawler", url) で True/False を取得する
3. True ならアクセス、False ならスキップ
```

---

### 問題4：問題2・3を組み合わせた礼儀正しいスクレイパーを作る

`python/lesson22/04_polite_scraper.py` に回答を書いてください。

以下の機能をすべて備えたスクレイパークラスを作成してください。

```
機能:
- robots.txt を確認してアクセス可否を判定する
- ブラウザと同様のヘッダーを設定する（User-Agent をランダムに選択）
- リクエストのたびに Crawl-delay または 1〜3秒の待機を入れる
  （robots.txt に Crawl-delay がある場合はその値を使う）
- エラーが起きたらスキップして次の URL に進む
- 成功・スキップの件数を最後に表示する
```

**考え方:**

```
1. __init__ で RobotFileParser と Session を初期化する
2. setup_robots(base_url) で robots.txt を読み込む
3. get_crawl_delay() で Crawl-delay を取得する（ない場合は None）
4. fetch(url) で robots.txt チェック → 待機 → リクエスト の順に処理する
5. run(urls) でURLリストを順番に処理し、結果を集計する
```

---

## 検索キーワード

| 知りたいこと               | 検索キーワード                                  |
| -------------------------- | ----------------------------------------------- |
| User-Agent の調べ方        | `自分のブラウザ User-Agent 確認`                |
| robots.txt の読み方        | `Python robotparser 使い方`                     |
| ブラウザのヘッダーを調べる | `Chrome 開発者ツール ネットワーク ヘッダー確認` |
| fake-useragent ライブラリ  | `Python fake-useragent 使い方`                  |
| スクレイピングの法律       | `スクレイピング 違法 日本 2024`                 |

---

## 困ったときは

### 「User-Agent を変えてもブロックされる」

User-Agent 以外のヘッダー（`Accept`・`Accept-Language`・`Referer` など）の設定が不足している可能性があります。ブラウザの開発者ツール（F12 → ネットワークタブ）でどのヘッダーが送られているか確認し、同じ内容を設定してみてください。

### 「待機時間を入れたのに 429 エラーが出る」

待機時間が短すぎるか、短時間に多くのリクエストを送りすぎています。`min_sec` と `max_sec` を長くしてみてください。また、`max_workers` を下げるか並列処理をやめて直列処理に戻すことも有効です。

### 「robots.txt を確認しているのに 403 になる」

robots.txt はあくまで「お願い」の文書であり、技術的なアクセス制限ではありません。robots.txt で許可されていても、サイト側が独自のファイアウォールで制限している場合はアクセスできません。無理に突破しようとせず、別の方法（公式 API など）を検討してください。

### 「requests と Selenium のどちらを使うべきかわからない」

まず `requests` で試してください。それでも正したいデータが取れない（JavaScriptで動的に生成されるコンテンツなど）場合に Selenium を検討します。`requests` の方が速く、サーバーへの負荷も小さいため、可能な限り `requests` を優先してください。

---

## 確認事項

- [ ] デフォルトの User-Agent が Python スクリプトと分かる文字列であることを確認した
- [ ] ブラウザの User-Agent をヘッダーに設定できた
- [ ] ランダムな待機時間を実装できた
- [ ] robots.txt を確認してアクセス可否を判定できた
- [ ] 礼儀正しいアクセスをするための設計ができた
- [ ] 倫理・法的観点から「やってよいか」を判断できた

---

**次回は「デバッグとテスト」です。loguruを使った見やすいログ出力、pytestを使ったテスト作成、スクレイピングコードの品質向上を学びます。**
