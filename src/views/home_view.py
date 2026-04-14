# ホームページのコンポーネント

import flet as ft
from constants import(
    SETTINGS,
    KEY_USER_NAME,
    ROUTE_SKILLS_SETTINGS,
    ROUTE_OCR,
    ROUTE_QC_LOG,
    GUEST_USER_NAME
)

@ft.component
def HomeView(page: ft.Page, set_route: callable, set_user_name: callable, user_name: str) -> ft.Column:
    async def logout_click(e: ft.ControlEvent):
        await ft.SharedPreferences().remove(KEY_USER_NAME)
        set_user_name("")

    is_guest = user_name == GUEST_USER_NAME
    return ft.Column(
        controls=[
            ft.Text(f"こんにちは、 {user_name} さん"),
            ft.Button("画像認識を行う", on_click=lambda _: set_route(ROUTE_OCR), disabled=is_guest),
            ft.Button("欲しいスキル設定", on_click=lambda _: set_route(ROUTE_SKILLS_SETTINGS), disabled=is_guest),
            ft.Button("練成履歴", on_click=lambda _: set_route(ROUTE_QC_LOG)),
            ft.Button("設定へ", on_click=lambda _: set_route(SETTINGS), disabled=is_guest),
            ft.Button("ログアウト", on_click=logout_click),
        ],
    )