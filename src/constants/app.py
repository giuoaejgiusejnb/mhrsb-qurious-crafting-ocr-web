# アプリの定数をまとめるファイル

APP_NAME = "flet-app-mhrsb-ocr" # アプリ名
KEY_USER_NAME = f"{APP_NAME}.user_name"  # ユーザー名を保存するキー
KEY_USER_ID = f"{APP_NAME}.user_id"  # ユーザーIDを保存するキー
ENDPOINT_QC_LOG = "/api/data"
GUEST_USER_NAME = "guest"
GUEST_PASSWORD = "111111"
FIREBASE_ERR_MSGS = { # ログインや新規登録失敗時に表示するメッセージ
    "INVALID_EMAIL": "ユーザー名を入力してください",
    "MISSING_PASSWORD": "パスワードを入力してください",
    "INVALID_LOGIN_CREDENTIALS": "パスワードまたはユーザー名が間違っています",
    "EMAIL_EXISTS": "このユーザー名は既に登録されています。",
    "WEAK_PASSWORD": "パスワードは6文字以上で設定してください。",
}