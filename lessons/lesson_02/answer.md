# 第2回：環境構築【解答・解説】

## 📝 問題1の解答

```python
>>> print("Hello, Scraping!")
Hello, Scraping!

>>> 1 + 1
2

>>> exit()
```

### なぜこうなる？

- `>>>` は「入力してね」という合図
- `print()` は画面に文字を出す命令
- `1 + 1` は計算。Python は電卓としても使える
- `exit()` で終了

---

## 📝 問題2の解答

### hello.py の答え

```python
print("=" * 40)
print("スクレイピングコースへようこそ")
print("=" * 40)

name = "あなたの名前"
print(f"こんにちは、{name}さん")
```

### 実行結果

```
========================================
スクレイピングコースへようこそ
========================================
こんにちは、あなたの名前さん
```

### このコードのポイント

- `"=" * 40` で「=」を40回繰り返す
- 文字列に `*` 数字を使うと繰り返し表示できます
- f-stringで変数を埋め込む: `f"テキスト {変数}"`

---

## 📝 問題3の解答

### check.py の答え

```python
libraries = ["requests", "bs4", "selenium", "pandas"]

for lib in libraries:
    try:
        __import__(lib)
        print(f"✅ {lib}: OK")
    except ImportError:
        print(f"❌ {lib}: NG")
```

### 実行結果（すべてインストール済みの場合）

```
✅ requests: OK
✅ bs4: OK
✅ selenium: OK
✅ pandas: OK
```

### このコードのポイント

- `__import__()` で動的にライブラリをインポート可能か確認
- try-exceptでImportErrorを処理（ライブラリがない場合の例外処理）
- リストをループで処理することで、複数のライブラリを一括確認
- 仮想環境が正しく有効になっていることが重要

---

## 💡 今回のポイントまとめ

### 仮想環境のコマンド

| やりたいこと | コマンド |
|-------------|---------|
| 作る | `python -m venv .venv` |
| 有効にする (Win) | `.\.venv\Scripts\Activate.ps1` |
| 有効にする (Mac) | `source .venv/bin/activate` |
| 終わる | `deactivate` |

### pip のコマンド

| やりたいこと | コマンド |
|-------------|---------|
| インストール | `pip install ライブラリ名` |
| 一括インストール | `pip install -r requirements.txt` |
| 一覧表示 | `pip list` |
| アンインストール | `pip uninstall ライブラリ名` |

---

## 🔍 よくあるエラーと対処法

### エラー1: 「python が見つからない」

```
'python' は、内部コマンドまたは...
```

**対処法:**
- Windows: Python を再インストール（Add to PATH にチェック）
- Mac: `python3` と打つ

### エラー2: 「スクリプトの実行が無効」

```
このシステムではスクリプトの実行が無効になっている...
```

**対処法:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### エラー3: 「ModuleNotFoundError」

```
ModuleNotFoundError: No module named 'requests'
```

**対処法:**
```bash
pip install requests
```

---

**次回は「Python基礎（前編）」です！**
