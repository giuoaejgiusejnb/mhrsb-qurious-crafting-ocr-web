from .load_settings_dialog_base import LoadSettingsDialogBase
from models.app_state import TypedPage
from repositories import UserSettings

class SettingsRunOCRDialog(LoadSettingsDialogBase):
    def __init__(self, page: TypedPage, on_load: callable):
        super().__init__(page, on_load, is_delete_button_visible=False, needs_overwrite_confirm=False)

    async def show_overwrite_confirm_dlg(self, e):
        settings_name = self.settings_selection_group.value
        self.overwrite_confirm_msg = f"{settings_name}を読み込みます．"
        await super().show_overwrite_confirm_dlg(e)

    async def execute_load(self, e=None):
        settings_name = self.settings_selection_group.value
        self.on_load(settings_name)

        await self.user_settings_repo.update(
            user_id=self.user_id,
            settings=UserSettings(last_selected_settings_name=settings_name)
        )

        self.page.pop_dialog() # ダイアログを消す