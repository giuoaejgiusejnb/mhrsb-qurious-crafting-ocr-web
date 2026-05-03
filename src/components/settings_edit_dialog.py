import flet as ft
from .load_settings_dialog_base import LoadSettingsDialogBase
from constants import FIELD_SKILLS
from models.app_state import TypedPage

class SettingsEditDialog(LoadSettingsDialogBase):
    def __init__(self, page: TypedPage, on_load: callable):
        super().__init__(page=page, on_load=on_load)

    async def show_overwrite_confirm_dlg(self, e):
        settings_name = self.settings_selection_group.value
        self.overwrite_confirm_msg = f"{settings_name}を読み込みます．\n現在の選択は上書きされますがよろしいですか？"
        await super().show_overwrite_confirm_dlg(e)

    async def execute_load(self):
        # チェックボックス変更
        settings_name = self.settings_selection_group.value
        settings_data = await self.settings_repo.fetch(self.user_id, settings_name)
        new_skills = settings_data.skills
        self.on_load(new_skills)

        # 二つのダイアログを消す
        self.page.pop_dialog()
        self.page.pop_dialog()

        # スナックバーを表示
        snack_bar = ft.SnackBar(
            content=ft.Text(f"「{settings_name}」を適用しました"),
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=ft.Margin.only(bottom=100, left=20, right=20),
        )
        self.page.show_dialog(snack_bar)