import flet as ft
from constants import(
    COL_USERS,
    COL_DESIRED_SKILLS_SETTINGS,
    FIELD_SKILLS
)
from firebase_admin import firestore

class SaveSettingsDialog(ft.AlertDialog):
    def __init__(self, user_name: str, db: firestore.client, selected_skills: set[str]) -> None:
        super().__init__()

        self.title = ft.Text("欲しいスキル設定保存")
        self.selected_skills = selected_skills
        self.settings_ref = (
            db.collection(COL_USERS)
            .document(user_name)
            .collection(COL_DESIRED_SKILLS_SETTINGS)
        )

        # --- 設定のデフォルト名を選択 ---
        # 設定のデフォルトの名前を設定1にする
        default_settings_id = 1
        # 設定1がすでに存在するなら，存在しなくなるまで末尾の数字を足していく
        docs = self.settings_ref.stream()
        setting_names = [doc.id for doc in docs]
        settings_name = f"設定{default_settings_id}"
        while settings_name in setting_names:
            default_settings_id += 1
            settings_name = f"設定{default_settings_id}"

        # テキストボックスをプロパティとして保持（後で値を取り出すため）
        name_input = ft.TextField(
            label="設定の名前",
            value=f"設定{str(default_settings_id)}",
            autofocus=True # ダイアログが開いた時にすぐ入力できる
        )
        
        self.content = ft.Column([
            ft.Text("設定名を入力してください"),
            name_input
        ], tight=True)
        self.actions = [
            ft.TextButton("キャンセル", on_click=lambda e: e.page.pop_dialog()),
            ft.TextButton(
                "保存", 
                on_click=lambda _: self.save_desired_skills_settings(
                    settings_name=name_input.value,
                )
            )
        ]

    def save_desired_skills_settings(self, settings_name: str) -> None:
        docs = self.settings_ref.stream()
        setting_names = [doc.id for doc in docs]
        if settings_name in setting_names:
            # 上書き確認ダイアログ (B)
            overwrite_dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("確認"),
                content=ft.Text("この設定名は既に存在しますが、上書きしますか？"),
                actions=[
                    ft.TextButton("キャンセル", on_click=lambda _: self.page.pop_dialog()),
                    ft.TextButton(
                        "保存",
                        on_click=lambda _: self.execute_save(
                            settings_name=settings_name,
                            overwrite_mode=True
                        )
                    )
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.show_dialog(overwrite_dlg)
        else:
            self.execute_save(settings_name=settings_name)

    def execute_save(self, settings_name: str, overwrite_mode: bool = False) -> None:
        # チェックがついている(value=True)スキルだけを抽出
        # 設定をsettings_dataに追加し，jsonファイルに書き込む
        self.settings_ref.document(settings_name).set({
            FIELD_SKILLS: self.selected_skills
        }, merge=True)

        self.page.pop_dialog() # 保存ダイアログを閉じる
        if overwrite_mode:
            self.page.pop_dialog() # 上書き確認ダイアログも閉じる
        
        #スナックバー表示とページ更新
        snack_bar = ft.SnackBar(
            content=ft.Text("保存しました！"),
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=ft.Margin.only(bottom=100, left=20, right=20),
        )
        self.page.show_dialog(snack_bar)
