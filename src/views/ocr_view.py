# 画像認識ページのコンポーネント


from functools import partial

import flet as ft

from components import (
    DetailDialog,
    LoadingScreen,
    MountTrigger,
    SettingsRunOCRDialog,
    get_open_colab_sentence,
)
from constants import ANDROID_UNCOMPRESSED_APP_DOWNLOAD_URL, LATEST_BAT_DOWNLOAD_URL
from models.app_state import TypedPage
from repositories import UserSettings


@ft.component
def OCRView(page: TypedPage) -> ft.Control:
    user_id = page.app_state.user_id
    user_repo = page.app_state.repos.user_settings_repo

    is_loading, set_is_loading = ft.use_state(True)  # 初期化処理が終わったかどうか
    user_settings_ref: ft.Ref[UserSettings | None] = ft.use_ref(
        None
    )  # ユーザー設定データの参照を保持するためのref

    async def init_settings_view():
        # ユーザー設定の取得
        user_settings_ref.current = await user_repo.fetch(user_id)
        set_is_loading(False)

    if is_loading:
        return MountTrigger(
            content=LoadingScreen(msg="ユーザー設定を読み込み中"),
            on_mount=init_settings_view,
        )

    settings_name, set_settings_name = ft.use_state(
        user_settings_ref.current.last_selected_settings_name
    )
    input_zip_file, set_input_zip_file = ft.use_state(
        user_settings_ref.current.last_selected_input_zip_file
    )

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
                    weight=ft.FontWeight.BOLD,
                ),
                width=1000,
            )

    # --- 画像認識したい画像フォルダをdriveにアップロードするよう促す文とその名前を入力させるフィールドを定義 ---
    input_zip_file_field_label = """画像認識したい画像フォルダをzipファイルにまとめて，Google Driveのフォルダにアップロードしてください．
    アップロード出来たら，zipファイルの名前を記入してください．
    """

    async def save_input_zip_file(e: ft.ControlEvent):
        await user_repo.update(
            user_id=user_id,
            settings=UserSettings(last_selected_input_zip_file=e.control.value),
        )

    # zipファイル名を入力させるフィールド
    input_zip_file_field = ft.TextField(
        label="zipファイル名",
        suffix=".zip",
        value=input_zip_file,
        on_change=lambda e: set_input_zip_file(e.control.value),
        on_blur=save_input_zip_file,
        expand=True,
    )

    # osごとに無圧縮する方法を表示するダイアログ

    # 各OSごとのデータを定義
    os_settings = {
        "windows": {
            "title": "windows版の説明",
            "url": LATEST_BAT_DOWNLOAD_URL,
            "desc": "ダウンロードしたら、練成画像フォルダをbatファイルにドラッグしてください．",
            "link_text": "この部分をクリックしてbatファイルをダウンロードしてください．",
        },
        "android": {
            "title": "Android版の説明",
            "url": ANDROID_UNCOMPRESSED_APP_DOWNLOAD_URL,
            "desc": (
                "まず，練成画像をsdカードから本体ストレージに移動してください．\n"
                "次に，アプリを起動し、練成画像を映した場所に移動します．\n"
                "画面右下の「＋」ボタンをタップします．\n"
                "「新しいアーカイブ（フォルダのアイコン）」を選びます．\n"
                "設定画面が表示されたら、以下のように設定します．\n"
                "・アーカイブ形式：zip を選択\n"
                "・圧縮レベル：リストから「無圧縮」（または Store）を選択\n"
                "「OK」をタップして完了です．"
            ),
            "link_text": "ここからZArchiverをダウンロードしてください．",
        },
        "ios": {
            "title": "iOS版の説明",
            "url": "",
            "desc": (
                "青いフォルダの形をした「ファイル」アプリを開いて、練成画像が入っているフォルダを長押し→"
                "「圧縮」を選択してください．（iOSの標準機能でzip化できます）"
            ),
            "link_text": "",
        },
    }

    # 親ダイアログ（各端末ごとの説明）のcontentを作成
    dlg_content = []

    for os_name, info in os_settings.items():
        # zip化するアプリをダウンロードする関数
        async def download_zip_app(e, url=info["url"]):
            if url:
                await ft.UrlLauncher().launch_url(url)
            else:
                page.show_dialog(
                    ft.AlertDialog(
                        title="ダウンロードリンクが設定されていません",
                        content=ft.Text(
                            "現在、このOSのzip化ツールは提供されていません。"
                        ),
                        actions=[ft.TextButton("閉じる", on_click=page.pop_dialog)],
                    )
                )

        # 各OS用の詳細ダイアログ
        sub_dlg = ft.AlertDialog(
            title=info["title"],
            content=ft.Column(
                controls=[
                    ft.TextButton(
                        info["link_text"],
                        on_click=download_zip_app,
                    )
                    if info["url"]
                    else ft.Container(),
                    ft.Text(info["desc"]),
                ],
                tight=True,
            ),
            actions=[ft.TextButton("閉じる", on_click=page.pop_dialog)],
        )

        # 親ダイアログに追加する行（OSごとの説明へのリンク）
        dlg_content.append(
            ft.TextButton(
                os_name, on_click=partial(lambda _, d: page.show_dialog(d), d=sub_dlg)
            )
        )

    # 親ダイアログを作成
    dlg_content.append(
        ft.Text(
            "ここに記載されている以外のやり方でzip化しても問題ありません．\nその場合は，無圧縮で大丈夫です．"
        )
    )
    dlg = ft.AlertDialog(
        title="各端末ごとの説明",
        content=ft.Column(controls=dlg_content, tight=True),
        actions=[ft.TextButton("閉じる", on_click=page.pop_dialog)],
    )

    # トリガーとなるリンク
    zip_instruction_text = ft.TextButton(
        "zip化のやり方", on_click=lambda _: page.show_dialog(dlg)
    )

    input_zip_file_controls = (
        input_zip_file_field_label,
        ft.ResponsiveRow(
            [
                ft.Container(
                    input_zip_file_field,
                    col={
                        ft.ResponsiveRowBreakpoint.XS: 12,  # スマホ画面では12カラム分（100%の幅）
                        ft.ResponsiveRowBreakpoint.MD: 6,  # タブレット画面では6カラム分（50%の幅）
                        ft.ResponsiveRowBreakpoint.LG: 6,  # PC画面では6カラム分（50%の幅）
                    },
                ),
                ft.Container(
                    zip_instruction_text,
                    col={
                        ft.ResponsiveRowBreakpoint.XS: 12,
                        ft.ResponsiveRowBreakpoint.MD: 6,
                        ft.ResponsiveRowBreakpoint.LG: 6,
                    },
                ),
            ]
        ),
    )

    # --- DBに保存してある設定名を選択し，その設定名を表示するコントロールを定義 ---

    settings_selection_row_label = "欲しいスキル設定を選択してください．"

    settings_selection_row = ft.ResponsiveRow(
        vertical_alignment=ft.CrossAxisAlignment.CENTER,  # 上下中央揃えにする
        controls=[
            ft.Button(
                content="欲しいスキル設定を選択してください",
                icon=ft.Icons.DOWNLOAD,
                on_click=lambda _: page.show_dialog(
                    SettingsRunOCRDialog(page=page, on_load=set_settings_name)
                ),
                col={
                    ft.ResponsiveRowBreakpoint.XS: 12,
                    ft.ResponsiveRowBreakpoint.MD: 8,
                    ft.ResponsiveRowBreakpoint.LG: 8,
                },
            ),
            ft.Text(
                settings_name,
                size=12,
                expand=True,
                col={
                    ft.ResponsiveRowBreakpoint.XS: 2,
                    ft.ResponsiveRowBreakpoint.MD: 1,
                    ft.ResponsiveRowBreakpoint.LG: 1,
                },
            ),
            ft.IconButton(
                tooltip="詳細を表示",
                icon=ft.Icons.INFO_OUTLINE,
                visible=(not settings_name == ""),
                on_click=lambda e: e.page.show_dialog(
                    DetailDialog(page=page, settings_name=settings_name)
                ),
                col={
                    ft.ResponsiveRowBreakpoint.XS: 2,
                    ft.ResponsiveRowBreakpoint.MD: 1,
                    ft.ResponsiveRowBreakpoint.LG: 1,
                },
            ),
        ],
    )

    settings_selection_controls = (settings_selection_row_label, settings_selection_row)

    # --- Colabを開いてGPUを有効にするよう促す文とボタンを定義 ---
    open_colab_sentence_label = "Google Colabで画像認識を実行してください．"

    open_colab_sentence = get_open_colab_sentence(
        page=page, settings_name=settings_name, input_zip_file=input_zip_file
    )

    open_colab_controls = (open_colab_sentence_label, open_colab_sentence)

    # --- UI配置 ---
    controls = []
    for label, control in [
        input_zip_file_controls,
        settings_selection_controls,
        open_colab_controls,
    ]:
        # ヘッダー追加
        controls.append(SectionHeader(text=label))
        # 内容を追加
        controls.append(
            ft.Container(
                content=control,
                width=500,
            )
        )

    content = ft.Column(
        controls=controls,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # 中身を中央へ
        scroll=ft.ScrollMode.ADAPTIVE,
        expand=True,
    )

    return ft.Column(
        controls=[
            ft.Container(
                content=content,
                alignment=ft.Alignment.CENTER,  # これで画面の真ん中にドスンと配置される
                expand=True,  # 画面全体を使う
            )
        ],
        expand=True,
    )
