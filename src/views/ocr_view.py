# 画像認識ページのコンポーネント

import flet as ft
from firebase_admin import firestore
from components import(
    get_open_colab_sentence,
    SettingsRunOCRDialog,
    DetailDialog
)
from constants import (
    COL_USERS,
    COL_PREV_OCR_SETTINGS,
    COL_DESIRED_SKILLS_SETTINGS,
    DOC_ID_CURRENT,
    FIELD_SKILLS_SETTINGS_NAME,
    FIELD_INPUT_ZIP_FILE
)
from models import TypedPage

@ft.component
def OCRView(page: TypedPage) -> ft.Control:
    user_name = page.app_state.user_name
    db = page.app_state.db
    github_token = page.app_state.github_token

    data = (db.collection(COL_USERS)
    .document(user_name)
    .collection(COL_PREV_OCR_SETTINGS)
    .document(DOC_ID_CURRENT)
    .get().to_dict()) or {}
    previous_settings_name = data.get(FIELD_SKILLS_SETTINGS_NAME, "")
    previous_input_zip_file = data.get(FIELD_INPUT_ZIP_FILE, "")
    settings_name, set_settings_name = ft.use_state(previous_settings_name)
    input_zip_file, set_input_zip_file = ft.use_state(previous_input_zip_file)

    # --- 見出しのクラスを定義 ---
    class SectionHeader(ft.Container):
        # 見出し番号
        _counter = 0

        def __init__(self, text: str):
            # 呼び出されるたびにカウントを＋1
            SectionHeader._counter += 1

            super().__init__(
                content=ft.Text(
                    f"{SectionHeader._counter}. {text}",
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),
                width=1000
            )

    # --- 画像認識したい画像フォルダをdriveにアップロードするよう促す文とその名前を入力させるフィールドを定義 ---
    input_zip_file_field_label =  """画像認識したい画像フォルダをzipファイルにまとめて，Google Driveのフォルダにアップロードしてください．
    アップロード出来たら，zipファイルの名前を記入してください．
    """

    def save_input_zip_file(e: ft.ControlEvent):
        ocr_settings_doc_ref = (
            db.collection(COL_USERS)
            .document(user_name)
            .collection(COL_PREV_OCR_SETTINGS)
            .document(DOC_ID_CURRENT)
        )
        ocr_settings_doc_ref.set({
            FIELD_INPUT_ZIP_FILE: e.control.value
        }, merge=True)

    input_zip_file_field = ft.TextField(
        label="zipファイル名",
        suffix=".zip",
        width=300,
        value=input_zip_file,
        on_change=lambda e: set_input_zip_file(e.control.value),
        on_blur=save_input_zip_file
    )

    input_zip_file_controls = (input_zip_file_field_label, input_zip_file_field)

    # --- DBに保存してある設定名を選択し，その設定名を表示するコントロールを定義 ---
    settings_selection_row_label =  "欲しいスキル設定を選択してください．"

    settings_ref = (
        db.collection(COL_USERS)
        .document(user_name)
        .collection(COL_DESIRED_SKILLS_SETTINGS)
    )
    settings_selection_row = ft.Row(
        controls=[
            ft.Button(
                content="欲しいスキル設定を選択してください",
                icon=ft.Icons.DOWNLOAD,
                on_click=lambda _: page.show_dialog(SettingsRunOCRDialog(user_name=user_name, db=db, on_load=set_settings_name))
                ),
            ft.Text(settings_name, size=12),
            ft.IconButton(
                tooltip="詳細を表示",
                icon=ft.Icons.INFO_OUTLINE,
                visible=(not settings_name == ""),
                on_click=lambda e: e.page.show_dialog(DetailDialog(settings_name=settings_name, settings_ref=settings_ref))
            )
        ],
        scroll=ft.ScrollMode.ADAPTIVE,
        expand=True
    )

    settings_selection_controls = (settings_selection_row_label, settings_selection_row)

    # --- Colabを開いてGPUを有効にするよう促す文とボタンを定義 ---
    open_colab_sentence_label = "Google Colabで画像認識を実行してください．"

    open_colab_sentence = get_open_colab_sentence(user_name, github_token, settings_ref, settings_name, input_zip_file)

    open_colab_controls = (open_colab_sentence_label, open_colab_sentence)

    # --- UI配置 ---
    controls = []
    print(222)
    for label, control in [input_zip_file_controls, settings_selection_controls, open_colab_controls]:
        controls.append(SectionHeader(text=label))
        controls.append(control)

    content = ft.Column(
        controls=controls,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, # 中身を中央へ
        scroll=ft.ScrollMode.ADAPTIVE,
        expand=True
    )

    return ft.Column(
        controls=[
            ft.Container(
                content=content,
                alignment=ft.Alignment.CENTER, # これで画面の真ん中にドスンと配置される
                expand=True, # 画面全体を使う
            )
        ],
        expand=True
    )
