import flet as ft
from constants.routes import HOME

# --- ページが見つからなかったときのコンポーネント ---
@ft.component
def NotFoundView(page :ft.Page, set_route: callable) -> ft.Column:
    return ft.Column([
        ft.Text("404 - ページが見つかりません", size=40, color="red", weight="bold"),
        ft.Text("お探しのページは削除されたか、URLが間違っている可能性があります。"),
        ft.Button("ホームに戻る", on_click=lambda _: set_route(HOME)),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)