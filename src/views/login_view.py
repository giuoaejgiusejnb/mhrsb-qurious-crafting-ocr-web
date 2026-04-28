# login_view.py
import base64
import flet as ft
from firebase_admin import firestore
from pyrebase.pyrebase import Auth
from constants import (
    DOC_ID_CURRENT,
    COL_USERS,
    COL_USER_SETTINGS,
    FIELD_USER_ACTIVE,
    FIELD_IS_QC_LOG_PUBLIC,
    FIELD_ALERT_DAYS,
    GUEST_USER_NAME,
    GUEST_PASSWORD,
    DEFAULT_ALERT_DAYS,
    DEFAULT_IS_QC_LOG_PUBLIC
)
from models import TypedPage

@ft.component
def LoginView(page: TypedPage) -> ft.Control:
    name_input, set_name_input = ft.use_state("")
    password, set_password = ft.use_state("")
    error_str, set_error_str = ft.use_state("")
    user_name_field = ft.TextField(
        label="ユーザー名",
        width=300,
        value=name_input,
        on_change=lambda e: set_name_input(e.control.value)
    )
    password_field = ft.TextField(
        label="パスワード",
        password=True,
        can_reveal_password=True,
        width=300,
        value=password,
        on_change=lambda e: set_password(e.control.value)
    )
    error_text = ft.Text(error_str, color="red")
    auth = page.app_state.auth
    db = page.app_state.db

    async def login(name: str, pwd: str)-> None:
        encoded_name = base64.urlsafe_b64encode(name.encode()).decode().rstrip("=")
        dummy_email = f"{encoded_name}@mhrsb-app.internal"
            
        try:
            # ユーザーログイン実行
            user = auth.sign_in_with_email_and_password(dummy_email, pwd)
            await page.app_state.login(name=name)
        except:
            set_error_str("ログインに失敗しました。メールアドレスとパスワードを確認してください。")

    async def login_click(e: ft.ControlEvent) -> None:
        await login(name_input, password)

    async def guest_login_click (e: ft.ControlEvent) -> None:
        await login(GUEST_USER_NAME, GUEST_PASSWORD)

    async def register_click(e: ft.ControlEvent)-> None:
        if not name_input:
            set_error_str("ユーザー名を入力してください")
            return
        if not password:
            set_error_str("パスワードを入力してください")
            return
        if len(password) < 6:
            set_error_str("パスワードは6文字以上である必要があります")
            return

        encoded_name = base64.urlsafe_b64encode(name_input.encode()).decode().rstrip("=")
        dummy_email = f"{encoded_name}@mhrsb-app.internal"
        try:
            # Firebase Authenticationにユーザーを登録
            user = auth.create_user_with_email_and_password(dummy_email, password)
            # firestoreにユーザーを登録（ドキュメントにフィールドが存在しないと，.stream()で取得できない）
            db.collection(COL_USERS).document(name_input).set({FIELD_USER_ACTIVE: True})
            # 練成履歴公開可の初期設定を設定
            db.collection(COL_USERS).document(name_input).collection(COL_USER_SETTINGS).document(DOC_ID_CURRENT).set(
                {FIELD_IS_QC_LOG_PUBLIC: DEFAULT_IS_QC_LOG_PUBLIC},
                merge=True
            )
            # gist有効期限警告の初期設定を設定
            db.collection(COL_USERS).document(name_input).collection(COL_USER_SETTINGS).document(DOC_ID_CURRENT).set(
                {FIELD_ALERT_DAYS: DEFAULT_ALERT_DAYS},
                merge=True
            )
        except Exception as ex:
            # すでに登録されている場合やパスワードが短い場合などにエラー
            set_error_str(f"登録失敗: {ex}")
            return

        # 登録成功後、そのままログイン状態にしてダッシュボードへ
        await login(name_input, password)

    return ft.Column([
        ft.Text("ログイン画面", size=30, weight=ft.FontWeight.BOLD),
        user_name_field, password_field,
        ft.Button("ログイン", on_click=login_click),
        ft.Button("ゲストでログイン", on_click=guest_login_click ),
        ft.Button("新規登録", on_click=register_click, bgcolor="green", color="white"),
        error_text
    ],)