import flet as ft
from constants import HOME

@ft.component
def SettingsView(page: ft.Page, set_route: callable) -> ft.Column:
    return ft.Column(
        controls=[
            ft.Button("ホームへ", on_click=lambda _: set_route(HOME)),
            ft.Text("準備中")
        ],
    )