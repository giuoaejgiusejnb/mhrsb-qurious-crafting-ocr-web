import flet as ft
from constants import(
    COL_USERS,
    COL_DESIRED_SKILLS_SETTINGS,
    FIELD_SKILLS
)
from firebase_admin import firestore

class SaveSettingsDialog(ft.AlertDialog):
    def __init__(self, checkbox_refs: list[ft.Ref[ft.Checkbox]], user_name: str, db: firestore.client):
        super().__init__()

        self.title = ft.Text("欲しいスキル設定保存")

        # 設定のデフォルトの名前を設定1にする
        default_settings_id = 1
        # 設定1がすでに存在するなら，存在しなくなるまで末尾の数字を足していく
        settings_ref = (
            db.collection(COL_USERS)
            .document(user_name)
            .collection(COL_DESIRED_SKILLS_SETTINGS)
        )
        docs = settings_ref.stream()
        setting_names = [doc.id for doc in docs]
        settings_name = f"設定{default_settings_id}"
        while settings_name in setting_names:
            default_settings_id += 1
            settings_name = f"設定{default_settings_id}"

        # テキストボックスをプロパティとして保持（後で値を取り出すため）
        self.name_input = ft.TextField(
            label="設定の名前",
            value=f"設定{str(default_settings_id)}",
            autofocus=True # ダイアログが開いた時にすぐ入力できる
        )
        
        self.content = ft.Column([
            ft.Text("設定名を入力してください"),
            self.name_input, # 配置
        ], tight=True)
        self.actions = [
            ft.TextButton("キャンセル", on_click=lambda e: e.page.pop_dialog()),
            ft.TextButton(
                "保存", 
                on_click=lambda _: self.save_desired_skills_settings(
                    checkbox_refs=checkbox_refs, 
                    settings_name=self.name_input.value,
                    settings_data=settings_ref
                )
            )
        ]

    def save_desired_skills_settings(self, checkbox_refs, settings_name, settings_data):
        docs = settings_data.stream()
        setting_names = [doc.id for doc in docs]
        if settings_name in setting_names:
            # 上書き確認ダイアログ (B)
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("確認"),
                content=ft.Text("この設定名は既に存在しますが、上書きしますか？"),
                actions=[
                    # 修正：ここでのキャンセルは「dlg (B)」を閉じるだけにする
                    ft.TextButton("キャンセル", on_click=lambda _: (setattr(dlg, "open", False), self.page.update())),
                    ft.TextButton(
                        "保存",
                        on_click=lambda _: self.execute_save(
                            checkbox_refs=checkbox_refs,
                            settings_name=settings_name,
                            settings_data=settings_data,
                            dlg=dlg
                        )
                    )
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.show_dialog(dlg)
        else:
            self.execute_save(checkbox_refs=checkbox_refs, settings_name=settings_name, settings_data=settings_data)

    def execute_save(self, checkbox_refs, settings_name, settings_data, dlg=None):
        # チェックがついている(value=True)スキルだけを抽出
        selected = [
            ref.current.label 
            for ref in checkbox_refs 
            if ref.current.value
        ]
        # 設定をsettings_dataに追加し，jsonファイルに書き込む
        settings_data.document(settings_name).set({
            FIELD_SKILLS: selected
        }, merge=True)

        self.page.pop_dialog() # 保存ダイアログを閉じる
        if dlg:
            self.page.pop_dialog() # 上書き確認ダイアログも閉じる
        
        #スナックバー表示とページ更新
        snack_bar = ft.SnackBar(
            content=ft.Text("保存しました！"),
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=ft.Margin.only(bottom=100, left=20, right=20),
        )
        self.page.show_dialog(snack_bar)
