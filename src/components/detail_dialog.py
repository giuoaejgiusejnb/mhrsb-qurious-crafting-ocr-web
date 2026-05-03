import flet as ft
from models.app_state import TypedPage
from .loading_screen import LoadingScreen

class DetailDialog(ft.AlertDialog):
    def __init__(self, page: TypedPage, settings_name: str):
        super().__init__()
        self.title=ft.Text(f"「{settings_name}」の詳細")
        self.settings_name = settings_name
        self.user_id = page.app_state.user_id
        self.settings_repo = page.app_state.repos.qc_settings_repo
        self.content = LoadingScreen()

    def did_mount(self):
        self.page.run_task(self.my_async_init)

    async def my_async_init(self):
        settings = await self.settings_repo.fetch(self.user_id, self.settings_name)
        skills = settings.skills

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
                        wrap=True,         # これで自動改行される
                        spacing=10,        # チップ同士の横の間隔
                        run_spacing=10,    # 改行された時の縦の間隔
                        scroll=ft.ScrollMode.ADAPTIVE,
                        expand=True
                    ),
                ],
                tight=True
            )

        else:
            self.content=ft.Text(f"{self.settings_name}は存在しません")

        self.actions=[ft.TextButton("閉じる", on_click=lambda e: e.page.pop_dialog())]
        
        self.page.update()