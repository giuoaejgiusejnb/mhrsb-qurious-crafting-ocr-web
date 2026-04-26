import flet as ft
from constants.routes import HOME

# --- ページが見つからなかったときのコンポーネント ---
@ft.component
def NotFoundView() -> ft.Column:
    return ft.Column([
        ft.Text("404 - ページが見つかりません", size=40, color="red", weight="bold"),
        ft.Text("お探しのページは削除されたか、URLが間違っている可能性があります。"),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)