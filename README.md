# MHR:SB Qurious Crafting OCR Web

モンスターハンターライズ：サンブレイク（MHR:SB）の「傀異錬成（Qurious Crafting）」の結果をOCRで読み取るFlet Webアプリです。

## 🚀 デモ

[アプリを開く (Demo)](https://flet-app-mhrsb-ocr.fly.dev/)
- **テスト用ユーザー名:** `aaaa`
- **テスト用パスワード:** `123456`

---

## 💾 テストデータのダウンロード

OCRの検証に使用できるテスト用のスクリーンショット画像一式です。

- **[テスト用画像をダウンロードする（20MB）](https://github.com/giuoaejgiusejnb/mhrsb-qurious-crafting-ocr-web/raw/refs/heads/main/tests/data/ocr_test.zip)**

---

## ✨ 機能

- 📸 **画像OCR読み取り:** スクリーンショットから傀異錬成の結果を自動認識
- 🎯 **ターゲットスキル判定:** 事前に選択した「欲しいスキル」が**少なくとも1つ含まれる画像のみ**を自動で判別して画面に出力
- 💻 **Web UI:** Fletによる直感的で軽量なWebインターフェース

---

## 🛠️ 使い方

1. **欲しいスキルの選択**: 画面上で狙っているスキルを事前に選択します。
2. **画像のアップロード**: 錬成結果のスクリーンショットをZIP化し、Google ドライブにアップロードします。
3. **自動判定・出力**: OCRで画像内のスキルを認識し、条件にマッチした「当たり画像」のみが画面に出力されます。

---

## 💻 実行方法（ローカル）

### 1. リポジトリをクローン
```bash
git clone https://github.com
cd mhrsb-qurious-crafting-ocr-web
```

### 2. 依存ライブラリのインストール
```bash
pip install -r requirements.txt
```

### 3. アプリの起動
```bash
flet run src/main.py
```

---

## 🧰 使用技術

- **Flet** (Python-based Flutter framework)
- **Python 3.x**
