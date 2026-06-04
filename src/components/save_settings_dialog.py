import asyncio

import flet as ft

from models.app_state import TypedPage
from repositories.qc_settings_repository import QCSettings

from .loading_screen import LoadingScreen


class SaveSettingsDialog(ft.AlertDialog):
    def __init__(self, page: TypedPage, selected_skills: set[str]) -> None:
        super().__init__()

        self.title = ft.Text("欲しいスキル設定保存")
        self.selected_skills = selected_skills
        self.user_id = page.app_state.user_id
        self.settings_repo = page.app_state.repos.qc_settings_repo
        self.content = LoadingScreen()

    def did_mount(self):
        self.page.run_task(self.my_async_init)

    async def my_async_init(self):
        # --- 設定のデフォルト名を選択 ---
        # 設定のデフォルトの名前を設定1にする
        default_settings_id = 1
        # 設定1がすでに存在するなら，存在しなくなるまで末尾の数字を足していく
        self.settings_names = await self.settings_repo.fetch_all_settings_names(
            user_id=self.user_id
        )
        settings_name = f"設定{default_settings_id}"
        while settings_name in self.settings_names:
            default_settings_id += 1
            settings_name = f"設定{default_settings_id}"

        # テキストボックスをプロパティとして保持（後で値を取り出すため）
        self.name_input = ft.TextField(
            label="設定の名前",
            value=f"設定{str(default_settings_id)}",
            autofocus=True,  # ダイアログが開いた時にすぐ入力できる
        )

        self.content = ft.Column(
            [ft.Text("設定名を入力してください"), self.name_input], tight=True
        )
        self.actions = [
            ft.TextButton("キャンセル", on_click=lambda e: e.page.pop_dialog()),
            ft.TextButton("保存", on_click=self.save_desired_skills_settings),
        ]

        self.page.update()

    async def save_desired_skills_settings(self, e) -> None:
        settings_name = self.name_input.value
        if settings_name == "":
            # 設定名が空のときは保存せずに警告を表示
            self.page.show_dialog(
                ft.AlertDialog(
                    content=ft.Text("設定名が入力されていません"),
                    actions=[
                        ft.TextButton("OK", on_click=lambda _: self.page.pop_dialog())
                    ],
                )
            )
            return

        if settings_name in self.settings_names:
            # 上書き確認ダイアログ
            overwrite_dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("確認"),
                content=ft.Text("この設定名は既に存在しますが、上書きしますか？"),
                actions=[
                    ft.TextButton(
                        "キャンセル", on_click=lambda _: self.page.pop_dialog()
                    ),
                    ft.TextButton(
                        "保存",
                        on_click=lambda _: self.page.run_task(
                            self.execute_save, settings_name, True
                        ),
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.show_dialog(overwrite_dlg)
        else:
            await self.execute_save(settings_name=settings_name)

    async def execute_save(
        self, settings_name: str, overwrite_mode: bool = False
    ) -> None:
        # チェックがついている(value=True)スキルだけを抽出
        # 設定をsettings_dataに追加し，jsonファイルに書き込む
        await self.settings_repo.update(
            user_id=self.user_id,
            settings_name=settings_name,
            settings=QCSettings(skills=self.selected_skills),
        )

        self.page.pop_dialog()  # 保存ダイアログを閉じる
        if overwrite_mode:
            # Web版におけるダイアログ連続pop時の挙動バグを回避するためのウェイト
            await asyncio.sleep(0.1)
            self.page.pop_dialog()  # 上書き確認ダイアログも閉じる

        # スナックバー表示とページ更新
        snack_bar = ft.SnackBar(
            content=ft.Text("保存しました！"),
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=ft.Margin.only(bottom=100, left=20, right=20),
        )
        self.page.show_dialog(snack_bar)
