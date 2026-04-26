from .app import APP_NAME
# ルート定数をまとめたファイル

HOME = "/home"
LOGIN = "/login"
ROUTE_OCR = "/ocr-images"
ROUTE_SKILLS_SETTINGS = "/desired-skills-settings"
ROUTE_QC_LOG = "/qc-log"
SETTINGS = "/settings"

# --- page.title用 (ブラウザタブ / 英語) ---
PAGE_TITLES = {
    HOME: f"Home | {APP_NAME}",
    LOGIN: f"Login | {APP_NAME}",
    ROUTE_OCR: f"OCR | {APP_NAME}",
    ROUTE_SKILLS_SETTINGS: f"Skills Settings | {APP_NAME}",
    ROUTE_QC_LOG: f"QC Log | {APP_NAME}",
    SETTINGS: f"Settings | {APP_NAME}",
}
DEFAULT_PAGE_TITLE = f"Unknown | {APP_NAME}" # PAGE_TITLESのキーにrouteが含まれていない場合のタイトル

# --- AppBar用 (画面表示 / 日本語) ---
UI_TITLES = {
    HOME: "ホーム",
    LOGIN: "ログイン",
    ROUTE_OCR: "OCR画像処理",
    ROUTE_SKILLS_SETTINGS: "欲しいスキル設定",
    ROUTE_QC_LOG: "QCログ確認",
    SETTINGS: "設定",
}
DEFAULT_UI_TITLE = "名称未設定" # UI_TITLESのキーにrouteが含まれていない場合のタイトル
