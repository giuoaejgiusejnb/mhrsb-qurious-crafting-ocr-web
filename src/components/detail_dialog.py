import flet as ft
from firebase_admin import firestore
from constants import FIELD_SKILLS

class DetailDialog(ft.AlertDialog):
    def __init__(self, settings_name: str, settings_ref: firestore.CollectionReference, **kwargs):
        super().__init__(**kwargs)
        self.title=ft.Text(f"「{settings_name}」の詳細")
        data = (
            settings_ref
            .document(settings_name)
            .get().to_dict() or {}
        )
        skills = data.get(FIELD_SKILLS)

        if skills is not None: # 指定した設定が存在するとき
            self.content = ft.Column(
                controls=[
                    # ラベル部分
                    ft.Text("スキル一覧：", weight=ft.FontWeight.BOLD, size=16),
                    # チップを横に並べる（入り切らない場合は自動改行）
                    ft.Row(
                        controls=[
                            ft.Chip(
                                label=ft.Text(skill),
                                leading=ft.Icon(ft.Icons.CHECK, size=16),
                                bgcolor=ft.Colors.BLUE_100,
                                on_click=lambda _: None # これを設定しないと色が変更できない
                            ) for skill in skills
                        ],
                        wrap=True,         # これで自動改行されます
                        spacing=10,        # チップ同士の横の間隔
                        run_spacing=10,    # 改行された時の縦の間隔
                        scroll=ft.ScrollMode.ADAPTIVE,
                        expand=True
                    ),
                ],
                tight=True
            )

        else:
            self.content=ft.Text(f"{settings_name}は存在しません")

        self.actions=[ft.TextButton("閉じる", on_click=lambda e: e.page.pop_dialog())]