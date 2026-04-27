# ユーザー設定を変更するコンポーネント

import flet as ft
from firebase_admin import firestore
from constants import (
    COL_USERS,
    COL_USER_SETTINGS,
    DOC_ID_CURRENT,
    FIELD_IS_QC_LOG_PUBLIC
)
from models import TypedPage

@ft.component
def SettingsView(page: TypedPage) -> ft.Control:
    user_name = page.app_state.user_name
    db = page.app_state.db

    user_settings_ref = (
        db.collection(COL_USERS)
        .document(user_name)
        .collection(COL_USER_SETTINGS)
        .document(DOC_ID_CURRENT)
    )
    user_settings = user_settings_ref.get().to_dict() or {}

    # --- 練成履歴を一般公開するかどうかの設定を変更するコントロールの定義 ---
    def on_change_share(e: ft.ControlEvent):
        user_settings_ref.set(
            {FIELD_IS_QC_LOG_PUBLIC: e.control.value}, 
            merge=True
        )

    share_toggle = ft.Switch(
        label="練成履歴を他の人にも公開する",
        on_change=on_change_share,
        value=user_settings.get(FIELD_IS_QC_LOG_PUBLIC, True)
    )
    # --- 練成履歴を一般公開するかどうかの設定を変更するコントロールの定義おわり ---

    return ft.Column(
        controls=[
            share_toggle
        ],
    )