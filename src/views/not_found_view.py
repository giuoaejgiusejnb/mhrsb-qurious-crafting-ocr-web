import flet as ft
from models import TypedPage

# --- ページが見つからなかったときのコンポーネント ---
@ft.component
def NotFoundView(page: TypedPage) -> ft.Control:

    return ft.Column([
        ft.Text("404 - ページが見つかりません", size=40, color="red", weight=ft.FontWeight.BOLD),
        ft.Text("お探しのページは削除されたか、URLが間違っている可能性があります。"),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)