# ログインを行うコンポーネント

import uuid
import flet as ft
from components import (
    create_password_field,
    PW_FIELD_WIDTH,
    use_status_text
)
from constants import (
    GUEST_USER_NAME,
    GUEST_PASSWORD,
    FIREBASE_ERR_MSGS
)
from models.app_state import TypedPage
from services import (
    PasswordValidator,
    AuthService
)

@ft.component
def LoginView(page: TypedPage) -> ft.Control:
    auth = page.app_state.auth
    user_repo = page.app_state.repos.user_settings_repo
    
    # 再描画時に消えないようにメモ
    user_name_field = ft.use_memo(
        lambda: ft.TextField(label="ユーザー名", width=PW_FIELD_WIDTH),
        []
    )
    password_field = ft.use_memo(
        create_password_field,
        []
    )
    # ログインや新規登録失敗時に表示するメッセージ
    login_status_control, set_login_status = use_status_text()

    async def login(name: str, pwd: str)-> None:
        set_login_status("ログイン処理中...", ft.Colors.GREEN)
        email = await user_repo.get_email_by_name(name)
        if email is None:
            set_login_status("ユーザー名が間違えています", ft.Colors.RED)
            return

        try:
            user = await page.app_state.auth.login(email=email, password=pwd)
            await page.app_state.login(uid=user.uid)
        except Exception as e:
            set_login_status(FIREBASE_ERR_MSGS.get(str(e), f"エラー：{e}"), ft.Colors.RED)

    async def login_click(e: ft.ControlEvent) -> None:
        await login(user_name_field.value, password_field.value)

    async def guest_login_click (e: ft.ControlEvent) -> None:
        await login(GUEST_USER_NAME, GUEST_PASSWORD)

    async def register_click(e: ft.ControlEvent)-> None:
        set_login_status("新規登録中...", ft.Colors.GREEN)
        user_name = user_name_field.value
        if user_name == "":
            set_login_status("ユーザー名を入力してください", ft.Colors.RED)
            return
        password = password_field.value
        res = PasswordValidator().check(password)
        if not res.is_valid:
            set_login_status(res.join_errors(), ft.Colors.RED)
            return

        fixed_id = uuid.uuid4().hex
        dummy_email = f"{fixed_id}@mhrsb-app.internal"
        is_username_taken = await user_repo.is_username_taken(user_name)
        if is_username_taken:
            set_login_status("そのユーザー名は既に存在しています", ft.Colors.RED)
            return

        try:
            user = await auth.register(dummy_email, password)
            uid = user.uid
            await AuthService(page.app_state.repos).register_new_user(uid, user_name, dummy_email)
        except Exception as ex:
        # すでに登録されている場合やパスワードが短い場合などにエラー
            set_login_status(FIREBASE_ERR_MSGS.get(str(ex), f"エラー：{ex}"), ft.Colors.RED)
        else:
            # 登録成功後、そのままログイン状態にしてダッシュボードへ
            await page.app_state.login(uid)

    return ft.Column([
        ft.Text("ログイン画面", size=30, weight=ft.FontWeight.BOLD),
        user_name_field, password_field,
        ft.Button("ログイン", on_click=login_click),
        ft.Button("ゲストでログイン", on_click=guest_login_click ),
        ft.Button("新規登録", on_click=register_click, bgcolor="green", color="white"),
        login_status_control
    ],)