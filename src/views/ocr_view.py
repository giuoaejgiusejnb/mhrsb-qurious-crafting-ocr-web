# 画像認識ページのコンポーネント

import flet as ft
from components import(
    get_open_colab_sentence,
    SettingsRunOCRDialog,
    DetailDialog
)
from models.app_state import TypedPage
from components import MountTrigger, LoadingScreen
from repositories import UserSettings

@ft.component
def OCRView(page: TypedPage) -> ft.Control:
    user_id = page.app_state.user_id
    user_repo = page.app_state.repos.user_settings_repo

    is_loading, set_is_loading = ft.use_state(True) # 初期化処理が終わったかどうか
    user_settings_ref: ft.Ref[UserSettings | None] = ft.use_ref(None)  # ユーザー設定データの参照を保持するためのref

    async def init_settings_view():
        # ユーザー設定の取得
        user_settings_ref.current = await user_repo.fetch(user_id)
        set_is_loading(False)

    if is_loading:
        return MountTrigger(content=LoadingScreen(msg="ユーザー設定を読み込み中"), on_mount=init_settings_view)

    settings_name, set_settings_name = ft.use_state(user_settings_ref.current.last_selected_settings_name)
    input_zip_file, set_input_zip_file = ft.use_state(user_settings_ref.current.last_selected_input_zip_file)


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

    async def save_input_zip_file(e: ft.ControlEvent):
        await user_repo.update(user_id=user_id, settings=UserSettings(last_selected_input_zip_file=e.control.value))

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

    settings_selection_row = ft.Row(
        controls=[
            ft.Button(
                content="欲しいスキル設定を選択してください",
                icon=ft.Icons.DOWNLOAD,
                on_click=lambda _: page.show_dialog(SettingsRunOCRDialog(page=page, on_load=set_settings_name))
                ),
            ft.Text(settings_name, size=12),
            ft.IconButton(
                tooltip="詳細を表示",
                icon=ft.Icons.INFO_OUTLINE,
                visible=(not settings_name == ""),
                on_click=lambda e: e.page.show_dialog(DetailDialog(page=page, settings_name=settings_name))
            )
        ],
        scroll=ft.ScrollMode.ADAPTIVE,
        expand=True
    )

    settings_selection_controls = (settings_selection_row_label, settings_selection_row)

    # --- Colabを開いてGPUを有効にするよう促す文とボタンを定義 ---
    open_colab_sentence_label = "Google Colabで画像認識を実行してください．"

    open_colab_sentence = get_open_colab_sentence(page=page, settings_name=settings_name, input_zip_file=input_zip_file)

    open_colab_controls = (open_colab_sentence_label, open_colab_sentence)

    # --- UI配置 ---
    controls = []
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
