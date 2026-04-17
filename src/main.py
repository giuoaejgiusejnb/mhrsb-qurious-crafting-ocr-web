# main.py - アプリのエントリーポイント

import warnings
# python_jwt に関する DeprecationWarning を無視する
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pyrebase")

from datetime import datetime, timezone
import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase
import os
import pytz
import json
import httpx
import flet.fastapi as flet_fastapi
from fastapi import FastAPI, Body
from views import Root
from constants import (
    ENDPOINT_QC_LOG,
    COL_USERS,
    COL_QC_LOGS,
    FIELD_EXECUTED_AT,
    FIELD_QC_COUNT,
    FIELD_CREATED_AT_STR,
    PL_KEY_QC_COUNT,
    PL_KEY_USER_NAME,
    GIST_URL
)
app = FastAPI()

async def main(page: ft.Page):
    # ロード画面
    loading_screen = ft.Column(
        controls=[
            ft.ProgressRing(),
            ft.Text("Gistデータを取得中...", size=20)
        ]
    )
    
    # 画面にロード中表示を出す
    page.add(loading_screen)

    # --- Firebase Admin SDK (サーバー権限) の初期化 ---
    if not firebase_admin._apps:
        cert_json = os.getenv("FIREBASE_KEY")
        if cert_json:
            cred = credentials.Certificate(json.loads(cert_json))
        else:
            test_path = r"C:\flet-app-web-files\flet-app-mhrsb-ocr-firebase-adminsdk-fbsvc-358310d152.json"
            cred = credentials.Certificate(test_path)
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    # --- Pyrebase (ユーザーログイン用) の設定 ---
    config_json = os.getenv("FIREBASE_CLIENT_CONFIG")
    if config_json:
        # Fly.io環境: 環境変数から辞書に変換
        config = json.loads(config_json)
    else:
        # ローカル環境: ローカルファイルから読み込み
        client_config_path = r"C:\flet-app-web-files\firebase_client_config.json"
        with open(client_config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()

    # gistの設定
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        test_path = r"C:\flet-app-web-files\github_token.txt"
        with open(test_path, "r", encoding="utf-8") as f:
            github_token = f.read()

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }

    async with httpx.AsyncClient() as client:
        res = await client.get(GIST_URL, headers=headers)
    if res.status_code == 401:
        page.add(ft.Text("トークンの有効期限が切れているか，無効なトークンです．アプリ作成者に連絡してください"))
        return
    elif res.status_code != 200:
        page.add(ft.Text(f"エラーが発生しました．  res.status_code:{res.status_code}"))
        return

    exp_str = res.headers.get("github-authentication-token-expiration")
    exp_date = datetime.strptime(exp_str, "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
            
    # 残り日数を計算
    remaining_days = (exp_date - now).days
    if remaining_days <= 30:
        expiration_warning_text = f"このwebアプリは{exp_str}に使用できなくなります．アプリ作成者に連絡して有効期限を延ばしてください"
        page.show_dialog(ft.SnackBar(
            ft.Text(expiration_warning_text),
            persist=True,
            action="ok",
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=ft.Margin.only(bottom=300, left=20, right=20)
            )
        )

    page.clean()
    page.render(lambda: Root(page, auth, db, github_token))

@app.post(ENDPOINT_QC_LOG)
async def receive_data(payload: dict = Body(...)):
    jst = pytz.timezone('Asia/Tokyo')
    executed_at = datetime.now(jst)

    user_name = payload.get(PL_KEY_USER_NAME)
    qc_count = payload.get(PL_KEY_QC_COUNT)
    db = firestore.client()

    if user_name is None or qc_count is None:
        return False

    qc_data = {
        FIELD_EXECUTED_AT: executed_at,
        FIELD_QC_COUNT: qc_count,
        FIELD_CREATED_AT_STR: executed_at.strftime('%Y-%m-%d %H:%M:%S') 
    }

    db.collection(COL_USERS).document(user_name).collection(COL_QC_LOGS).add(qc_data)

    return True

@app.get("/health")
def health():
    return {"status": "ok"}

app.mount("/", flet_fastapi.app(main))

# flet run されたときに実行（この場合，fastapiは無効になる）
if __name__ == "__main__": 
    ft.run(main)