# MHR:SB Qurious Crafting OCR Web

モンスターハンターライズ：サンブレイク（MHR:SB）の「傀異錬成（Qurious Crafting）」の結果をOCRで読み取るFlet Webアプリです。

## 機能
- スクリーンショット画像からのOCR読み取り
- 錬成結果のデータ化
- FletによるWebインターフェース

## 実行方法（ローカル）

1. **リポジトリをクローン**
   ```bash
   git clone https://github.com
   cd mhrsb-qurious-crafting-ocr-web

2. **依存ライブラリのインストール**
    ```bash
    pip install -r requirements.txt

3. **アプリの起動**
    ```bash
    flet run src/main.py

## 使用技術
Flet (Python-based Flutter framework)
Python 3.x