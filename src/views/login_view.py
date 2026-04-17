# login_view.py
import base64
import flet as ft
from firebase_admin import firestore
from pyrebase.pyrebase import Auth
from constants import (
    HOME,
    KEY_USER_NAME,
    DOC_ID_CURRENT,
    COL_USERS,
    COL_USER_SETTINGS,
    FIELD_USER_ACTIVE,
    FIELD_IS_QC_LOG_PUBLIC,
    GUEST_USER_NAME,
    GUEST_PASSWORD
)
@ft.component
def LoginView(page: ft.Page, set_route: callable, set_user_name: callable, auth: Auth,  db: firestore.client) -> ft.Column:
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

    async def login(name: str, pwd: str)-> None:
        encoded_name = base64.urlsafe_b64encode(name.encode()).decode().rstrip("=")
        dummy_email = f"{encoded_name}@mhrsb-app.internal"
            
        try:
            # ユーザーログイン実行
            user = auth.sign_in_with_email_and_password(dummy_email, pwd)
            await ft.SharedPreferences().set(KEY_USER_NAME, name)
            set_user_name(name)
            set_route(HOME)
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
            # 練成履歴公開可の初期設定をtrueに設定
            db.collection(COL_USERS).document(name_input).collection(COL_USER_SETTINGS).document(DOC_ID_CURRENT).set(
                {FIELD_IS_QC_LOG_PUBLIC: True})
        except Exception as ex:
            # すでに登録されている場合やパスワードが短い場合などにエラー
            set_error_str(f"登録失敗: {ex}")

        # 登録成功後、そのままログイン状態にしてダッシュボードへ
        await login(name_input, password)

    return ft.Column([
        ft.Text("ログイン画面", size=30, weight="bold"),
        user_name_field, password_field,
        ft.Button("ログイン", on_click=login_click),
        ft.Button("ゲストでログイン", on_click=guest_login_click ),
        ft.Button("新規登録", on_click=register_click, bgcolor="green", color="white"),
        error_text
    ],)