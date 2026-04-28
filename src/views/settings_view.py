# ユーザー設定を変更するコンポーネント

import flet as ft
from firebase_admin import firestore
from constants import (
    COL_USERS,
    COL_USER_SETTINGS,
    DOC_ID_CURRENT,
    FIELD_IS_QC_LOG_PUBLIC,
    FIELD_ALERT_DAYS,
    DEFAULT_IS_QC_LOG_PUBLIC,
    DEFAULT_ALERT_DAYS
)
from models import TypedPage

@ft.component
def SettingsView(page: TypedPage) -> ft.Control:
    user_name = page.app_state.user_name
    db = page.app_state.db

    # 各設定のラベル
    class SettingLabel(ft.Text):
        def __init__(self, value):
            super().__init__(
                value=value,
                size=20,
                weight=ft.FontWeight.BOLD,
            )

    # --- ユーザー設定の読み込み ---
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

    share_toggle = ft.Column([
        SettingLabel("練成履歴公開設定"),
        ft.Switch(
            label="練成履歴を他の人にも公開する",
            on_change=on_change_share,
            value=user_settings.get(FIELD_IS_QC_LOG_PUBLIC, DEFAULT_IS_QC_LOG_PUBLIC)
        )
    ])

    # --- gist有効期限警告の閾値を変更するコントロールの定義 ---
    initial_threshold = user_settings.get(FIELD_ALERT_DAYS, DEFAULT_ALERT_DAYS)
    current_threshold, set_current_threshold = ft.use_state(initial_threshold)

    # スライダーの指を離した時に実行される保存処理
    async def auto_save_threshold(e):
        new_value = int(e.control.value)
        
        user_settings_ref.set(
            {FIELD_ALERT_DAYS: new_value},
            merge=True
        )
        
    alert_days_slider = ft.Column([
        SettingLabel("通知設定"),
        ft.Container(
            content=ft.Column([
                ft.Text(f"期限切れの警告を開始する日数: {current_threshold}日前", color=ft.Colors.RED),
                ft.Slider(
                    min=0,
                    max=90,
                    divisions=18, # 5日刻み
                    value=current_threshold,
                    label="{value}日前",
                    on_change=lambda e: set_current_threshold(int(e.control.value)),
                    on_change_end=auto_save_threshold 
                ),
                ft.Text("※0にすると警告を表示しません", size=12, color=ft.Colors.GREY_400),
            ]),
            padding=20,
            bgcolor=ft.Colors.BLUE_GREY_900,
            border_radius=10
        )
    ])

    # --- Uiを表示 ---
    settings_items  = [share_toggle, alert_days_slider]
    # 項目の間にだけ Divider を入れる
    controls = []
    for item in settings_items:
        controls.append(item)
        controls.append(ft.Divider(height=30, color=ft.Colors.RED))

    return ft.Column(
        controls=controls
    )