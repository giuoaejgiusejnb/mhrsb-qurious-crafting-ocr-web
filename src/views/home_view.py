# ホームページのコンポーネント

import flet as ft
from constants import(
    SETTINGS,
    ROUTE_SKILLS_SETTINGS,
    ROUTE_OCR,
    ROUTE_QC_LOG,
)
from models import TypedPage

@ft.component
def HomeView(page: TypedPage) -> ft.Control:
    async def logout_click(e: ft.ControlEvent):
        await page.app_state.logout()

    user_name = page.app_state.user_name
    is_guest = page.app_state.is_guest
    set_route = page.app_state.set_route

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