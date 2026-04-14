from firebase_admin import firestore
from constants import (
    COL_USERS,
    COL_PREV_OCR_SETTINGS,
    DOC_ID_CURRENT,
    FIELD_SKILLS_SETTINGS_NAME
    )
from .load_settings_dialog_base import LoadSettingsDialogBase

class SettingsRunOCRDialog(LoadSettingsDialogBase):
    def __init__(self, user_name: str, db: firestore.client, on_load: callable):
        super().__init__(user_name, db, on_load, is_delete_button_visible=False, needs_overwrite_confirm=False)
        self.ocr_settings_doc_ref =(
            db.collection(COL_USERS)
            .document(user_name)
            .collection(COL_PREV_OCR_SETTINGS)
            .document(DOC_ID_CURRENT)
        )

    def show_overwrite_confirm_dlg(self):
        self.settings_name = self.settings_selection_group.value
        self.overwrite_confirm_msg = f"{self.settings_name}を読み込みます．"
        super().show_overwrite_confirm_dlg()

    def execute_load(self):
        self.on_load(self.settings_name)

        self.ocr_settings_doc_ref.set({
            FIELD_SKILLS_SETTINGS_NAME: self.settings_name
        }, merge=True)

        self.open = False
        
        self.page.update()