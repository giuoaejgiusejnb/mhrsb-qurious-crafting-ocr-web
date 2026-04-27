# ロード画面として使うクラス

import flet as ft

class LoadingScreen(ft.Container):
    def __init__(self, msg: str = "データを読み込み中...") -> None:
        super().__init__()
        
        self.alignment = ft.Alignment(0, 0)
        self.expand = True

        self.content = ft.Column(
            [
                ft.ProgressRing(width=100, height=100, stroke_width=10),
                ft.Text(msg, size=30),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True 
        )
