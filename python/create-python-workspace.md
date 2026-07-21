# Python ワークスペース案内

このページは、カリキュラムの問題を解くための `python/lessonXX/` ワークスペース案内です。

## 使い方

1. `lessons/lesson_XX/exercise.md` で問題文を確認します。
2. 対応する `python/lessonXX/` を開きます。
3. 問題ごとに用意された `.py` を編集して実行します。
4. 前の問題に戻りたくなったら、同じ lesson 内の別ファイルを開けばOKです。

## ディレクトリ構成

```text
lessons/
  lesson_02/
    exercise.md

python/
  lesson02/
    01.py
    02.py
    03.py
```

## ダウンロード

- [python ワークスペースの zip をダウンロード](./python-workspace.zip)

GitHub 上ではこのリンクから zip を取得できます。
ダウンロードした zip を展開したら、このリポジトリ内の `python/lessonXX/` を編集してください。

## 仮想環境の作り方

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows の場合は次のようにします。

```powershell
.venv\Scripts\activate
```

## モジュールの入れ方

`requirements.txt` があるので、必要なモジュールはまとめて入れられます。

```bash
pip install -r requirements.txt
```

## よく使う確認

```bash
python --version
pip --version
```

`lesson02` は環境確認用のファイルが入っています。最初にここから動作確認すると進めやすいです。
