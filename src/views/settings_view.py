# ユーザー設定を変更するコンポーネント

import flet as ft
from models.app_state import TypedPage
from repositories import UserSettings
from components import LoadingScreen, MountTrigger, create_password_field
from services import PasswordValidator
from constants import FIREBASE_ERR_MSGS
from components import use_status_text

@ft.component
def SettingsView(page: TypedPage) -> ft.Control:
    user_id = page.app_state.user_id
    auth = page.app_state.auth
    user_repo = page.app_state.repos.user_settings_repo

    is_loading, set_is_loading = ft.use_state(True) # 初期化処理が終わったかどうか
    email_ref = ft.use_ref(None) # emailを保持するためのref
    user_settings_ref = ft.use_ref(None) # ユーザー設定データの参照を保持するためのref

    async def init_settings_view():
        # ユーザー設定の取得
        user_settings_ref.current = await user_repo.fetch(user_id)
        email_ref.current = user_settings_ref.current.email
        set_is_loading(False)

    if is_loading: # controlsを作っている段階なら，ロード画面を表示
        return MountTrigger(content=LoadingScreen(msg="ユーザー設定を読み込み中"), on_mount=init_settings_view)
    else:
        # 各設定のラベル
        class SettingLabel(ft.Text):
            def __init__(self, value):
                super().__init__(
                    value=value,
                    size=20,
                    weight=ft.FontWeight.BOLD,
                )

        # --- 練成履歴を一般公開するかどうかの設定を変更するコントロールの定義 ---
        async def on_change_share(e: ft.ControlEvent):
            await user_repo.update(
                user_id=user_id,
                settings=UserSettings(is_qc_log_public=e.control.value)
            )

        share_toggle = ft.Column([
            SettingLabel("練成履歴公開設定"),
            ft.Switch(
                label="練成履歴を他の人にも公開する",
                on_change=on_change_share,
                value=user_settings_ref.current.is_qc_log_public
            )
        ])

        # --- gist有効期限警告の閾値を変更するコントロールの定義 ---
        initial_threshold = user_settings_ref.current.alert_days
        current_threshold, set_current_threshold = ft.use_state(initial_threshold)

        # スライダーの指を離した時に実行される保存処理
        async def auto_save_threshold(e):
            new_value = int(e.control.value)
        
            await user_repo.update(
                user_id=user_id,
                settings=UserSettings(alert_days=new_value)
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
        
        #--- ユーザー名変更を行うコントロールの定義 ---
        
        name_status_control, set_name_status = use_status_text()
        # 再描画時に消えないようにメモ
        name_field = ft.use_memo(
            lambda:  ft.TextField(label="新しいユーザーネーム", value=user_settings_ref.current.user_name),
            []
        )

        async def on_name_submit(e):
            if not name_field.value.strip(): return # 名前が入力されていないなら何もしない
            set_name_status("名前を変更中...", ft.Colors.BLUE)
            is_user_name_taken = await user_repo.is_username_taken(name_field.value)
            if is_user_name_taken:
                set_name_status("その名前は既に使われています", ft.Colors.RED)
                return

            try:
                await page.app_state.change_name(name_field.value)
            except Exception as e:
                set_name_status(f"名前の変更に失敗しました。{e}", ft.Colors.RED )
            else:
                set_name_status("名前が正常に変更されました。", ft.Colors.GREEN)

        name_change_button = ft.Button("名前を変更", on_click=on_name_submit)
        name_change_section = ft.Column(
            controls=[
                SettingLabel("ユーザーネーム変更"),
                name_field,
                name_change_button,
                name_status_control
            ],
        )

        #--- パスワード変更を行うコントロールの定義 ---

        pw_status_control, set_pw_status = use_status_text()
        can_submit_pw_change, set_can_submit_pw_change = ft.use_state(True) # パスワード更新ボタンが押せるかどうか
        current_pw_text, set_curernt_pw_text = ft.use_state("")
        new_pw_text, set_new_pw_text = ft.use_state("")

        current_pw_field = create_password_field(
            label="今のパスワード",
            value=current_pw_text,
            on_change=lambda e: set_curernt_pw_text(e.control.value))
        new_pw_field = create_password_field(
            label="新しいパスワード",
            value=new_pw_text,
            on_change=lambda e: set_new_pw_text(e.control.value))

        # パスワード変更を行う関数
        async def on_change_posword_click(e: ft.ControlEvent):
            set_can_submit_pw_change(False)
            set_pw_status("パスワード変更処理中...", ft.Colors.BLUE)
            page.pop_dialog()

            try:
                user = await auth.reauthenticate_and_change_password(
                    email=email_ref.current,
                    current_password=current_pw_field.value,
                    new_password=new_pw_field.value
                )

                # 入力欄をクリア
                set_curernt_pw_text("")
                set_new_pw_text("")
                set_pw_status("パスワードが正常に変更できました．", ft.Colors.GREEN)
            except Exception as err:
                set_pw_status(FIREBASE_ERR_MSGS.get(str(err), f"エラー：{err}"), ft.Colors.RED)
            finally:
                set_can_submit_pw_change(True)

        # パスワード変更確認ダイアログ
        confirm_change_pw_dialog = ft.AlertDialog(
            title=ft.Text("パスワードの変更"),
            content=ft.Column(
                ft.Text("パスワードを変更しますが，よろしいですか？")
            ),
            actions=[
                ft.TextButton("キャンセル", on_click=lambda _: page.pop_dialog()),
                ft.TextButton("変更する", on_click=on_change_posword_click)
            ],
        )

        # パスワードバリデーションチェックと，パスワード変更確認ダイアログ表示
        def show_confirm_change_pw_dialog(e: ft.ControlEvent):
            res = PasswordValidator().check(new_pw_field.value)
            if not res.is_valid:
                set_pw_status(res.join_errors(), ft.Colors.RED)
            else:
                set_pw_status("", None)
                page.show_dialog(confirm_change_pw_dialog)

        # パスワード変更ボタン
        change_password_button = ft.Button(
            "パスワードを更新",
            on_click=show_confirm_change_pw_dialog,
            disabled=not can_submit_pw_change
        )    

        # パスワード変更カラム
        pw_change_section = ft.Column(
            controls=[
                SettingLabel("パスワード変更"),
                current_pw_field,
                ft.Container(
                    content=ft.Divider(height=1, color=ft.Colors.BLUE),
                    width=current_pw_field.width
                ),
                new_pw_field,
                change_password_button,
                pw_status_control,
            ],
        )

        # --- Uiを表示 ---
        settings_items  = [share_toggle, alert_days_slider, name_change_section, pw_change_section]
        controls = []
        # 項目の間にだけ Divider を入れる
        for item in settings_items:
            controls.append(item)
            controls.append(ft.Divider(height=30, color=ft.Colors.RED))

        return ft.Column(
            controls=controls,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )