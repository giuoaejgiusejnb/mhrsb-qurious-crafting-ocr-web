# スキル設定ページのコンポーネント

import flet as ft
import json
from firebase_admin import firestore
from functools import partial
from constants import (
    HOME,
    SKILLS_DATA
)
from components import (
    SaveSettingsDialog,
    SettingsEditDialog,
)

# --- 欲しいスキル設定ページのコンポーネント ---
@ft.component
def SkillSettingsView(page : ft.Page, set_route: callable, user_name: str, db: firestore.client) -> ft.Column:
    selected_skills, set_selected_skills = ft.use_state(set())

    # 保存ボタンを押したときの処理（保存ダイアログを表示）
    def show_save_settings_dialog(e):
        dialog = SaveSettingsDialog(user_name=user_name, db=db, selected_skills=selected_skills)
        page.show_dialog(dialog)

    # 読み込みボタンを押したときの処理（読み込みダイアログを表示）
    def show_load_settings_dialog(e):
        dialog = SettingsEditDialog(user_name=user_name, db=db, on_load=set_selected_skills)
        page.show_dialog(dialog)

    # スキルのチェックがオンオフされるごとに，selected_skillsも更新
    def toggle_skill(e, skill_name):
        is_checked = e.control.value
    
        if is_checked:
            selected_skills.add(skill_name)
        else:
            selected_skills.discard(skill_name)

    # データを元にUI要素を生成
    content_list = [ft.Text("スキル選択（翔と蝕はどちらも選択しないかどちらも選択するかを推奨）", size=25, weight="bold")]
    for cost, skills in SKILLS_DATA.items():
        # セクションの見出し（コスト）
        content_list.append(
            ft.Text(cost, size=20, weight="bold", color=ft.Colors.BLUE_ACCENT)
        )
        # チェックボックス
        checkboxes = []
        for skill in skills:
            checkboxes.append(ft.Checkbox(
                value=skill in selected_skills,
                label=skill, 
                col={"xs": 6, "sm": 4, "md": 3},
                on_change=partial(toggle_skill, skill_name=skill)
            ))
        content_list.append(ft.ResponsiveRow(
            controls=checkboxes,
            spacing=10,        # 横の間隔
            run_spacing=10,    # 縦の間隔（改行時）
            alignment=ft.MainAxisAlignment.START
            ))
        # セクション間の余白
        content_list.append(ft.Divider(height=10, color=ft.Colors.BLUE))
    skill_form_controls = (
        ft.Column(
            controls=content_list,
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True
        )
    )

    # 読み込みボタン，保存ボタンの定義
    action_buttons = []
    # 読み込みボタン
    action_buttons.append(
        ft.Row(
            controls=[
                ft.Button(
                    "設定を読み込む", 
                    icon=ft.Icons.DOWNLOAD,
                    on_click=show_load_settings_dialog
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER 
        )
    )
    # 削除ボタン
    action_buttons.append(
        ft.Row(
            controls=[
                ft.Button(
                    "保存する", 
                    icon=ft.Icons.SAVE,
                    on_click=show_save_settings_dialog
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER 
        )
    )

    return ft.Column(
        controls=[
            ft.Row(action_buttons, alignment=ft.MainAxisAlignment.CENTER),
            skill_form_controls
        ],
        expand=True
    )