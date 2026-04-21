import flet as ft
from firebase_admin import firestore
from .load_settings_dialog_base import LoadSettingsDialogBase
from constants import FIELD_SKILLS

class SettingsEditDialog(LoadSettingsDialogBase):
    def __init__(self, user_name: str, db: firestore.client, on_load: callable):
        super().__init__(user_name, db, on_load)

    def show_overwrite_confirm_dlg(self):
        self.settings_name = self.settings_selection_group.value
        self.overwrite_confirm_msg = f"{self.settings_name}を読み込みます．\n現在の選択は上書きされますがよろしいですか？"
        super().show_overwrite_confirm_dlg()

    def execute_load(self):
        # チェックボックス変更
        settings_doc = self.settings_ref.document(self.settings_name).get()
        settings_data = settings_doc.to_dict()
        new_skills = set(settings_data[FIELD_SKILLS])
        self.on_load(new_skills)

        # 二つのダイアログを消す
        self.page.pop_dialog()
        self.page.pop_dialog()

        # スナックバーを表示
        snack_bar = ft.SnackBar(
            content=ft.Text(f"「{self.settings_name}」を適用しました"),
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=ft.Margin.only(bottom=100, left=20, right=20),
        )
        self.page.show_dialog(snack_bar)