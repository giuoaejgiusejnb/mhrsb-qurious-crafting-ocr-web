# ログインを行うコンポーネント

import uuid
import flet as ft
from components import (
    create_password_field,
    PW_FIELD_WIDTH
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
    # TODO エラーではなく，ステータスメッセージ（ログイン中など）を追加
    error_str, set_error_str = ft.use_state("")

    error_text = ft.Text(error_str, color="red")

    async def login(name: str, pwd: str)-> None:
        email = await user_repo.get_email_by_name(name)
        if email is None:
            set_error_str("ユーザー名が間違えています")
            return

        try:
            user = await page.app_state.auth.login(email=email, password=pwd)
            await page.app_state.login(uid=user.uid, name=name)
        except Exception as e:
            set_error_str(FIREBASE_ERR_MSGS.get(str(e), f"エラー：{e}"))

    async def login_click(e: ft.ControlEvent) -> None:
        await login(user_name_field.value, password_field.value)

    async def guest_login_click (e: ft.ControlEvent) -> None:
        await login(GUEST_USER_NAME, GUEST_PASSWORD)

    async def register_click(e: ft.ControlEvent)-> None:
        user_name = user_name_field.value
        if user_name == "":
            set_error_str("ユーザー名を入力してください")
            return
        password = password_field.value
        res = PasswordValidator().check(password)
        if not res.is_valid:
            set_error_str(res.join_errors())
            return

        fixed_id = uuid.uuid4().hex
        dummy_email = f"{fixed_id}@mhrsb-app.internal"
        is_username_taken = await user_repo.is_username_taken(user_name)
        if is_username_taken:
            set_error_str("そのユーザー名は既に存在しています")
            return

        try:
            user = await auth.register(dummy_email, password)
            uid = user.uid
            await AuthService(page.app_state.repos).register_new_user(uid, user_name, dummy_email)
        except Exception as ex:
        # すでに登録されている場合やパスワードが短い場合などにエラー
            set_error_str(FIREBASE_ERR_MSGS.get(str(ex), f"エラー：{ex}"))
        else:
            # 登録成功後、そのままログイン状態にしてダッシュボードへ
            await page.app_state.login(uid, user_name)

    return ft.Column([
        ft.Text("ログイン画面", size=30, weight=ft.FontWeight.BOLD),
        user_name_field, password_field,
        ft.Button("ログイン", on_click=login_click),
        ft.Button("ゲストでログイン", on_click=guest_login_click ),
        ft.Button("新規登録", on_click=register_click, bgcolor="green", color="white"),
        error_text
    ],)