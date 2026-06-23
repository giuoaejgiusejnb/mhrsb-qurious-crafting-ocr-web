import re

import flet as ft
import httpx
import nbformat

from components.status_text import use_status_text
from constants import (
    APP_NAME,
    ENDPOINT_QC_LOG,
    OCR_NOTEBOOK_PATH,
    SKILL_MASTER_LIST,
)
from models.app_state import TypedPage


def get_open_colab_sentence(page: TypedPage, settings_name: str, input_zip_file: str):
    user_id = page.app_state.user_id
    qc_settings_repo = page.app_state.repos.qc_settings_repo

    colab_url, set_colab_url = ft.use_state("")
    url_status_control, set_url_status = use_status_text()

    async def create_colab_url(e):
        set_url_status("Colab用URLを作成中...", "blue")
        set_colab_url("")
        if settings_name == "" or input_zip_file == "":
            set_url_status(
                "欲しいスキル設定か画像zipファイルの名前が設定されていません", "red"
            )
            return

        qc_settings = await qc_settings_repo.fetch(
            user_id=user_id, settings_name=settings_name
        )
        desired_skills = qc_settings.skills

        # colabの変数の値を書き換える
        updata_vars = {
            "user_id": user_id,
            "fly_url": f"https://{APP_NAME}.fly.dev{ENDPOINT_QC_LOG}",
            "skill_master_list": SKILL_MASTER_LIST,
            "desired_skills": desired_skills,
            "input_zip_file": input_zip_file,
        }
        with open(OCR_NOTEBOOK_PATH, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)

        # ノートブックの全セルから特定のコメントを探す
        target_tag = "# SETTINGS_HERE"
        target_cell = None

        for cell in nb.cells:
            # コードセルであり、かつソースコード内にタグが含まれているか
            if cell.cell_type == "code" and target_tag in cell.source:
                target_cell = cell
                break

        if target_cell:
            # 見つかったセルの内容を置換
            for var_name, new_value in updata_vars.items():
                pattern = rf"^{var_name}\s*=.*"
                replacement = f"{var_name} = {repr(new_value)}"

                target_cell.source = re.sub(
                    pattern, replacement, target_cell.source, flags=re.MULTILINE
                )

        gist_filename = "temp_modified"
        try:
            res_data = await page.app_state.shared_gist.upload_ipynb(
                content=nbformat.writes(nb), file_name=gist_filename
            )
            gist_id = res_data["id"]
            gist_username = res_data["owner"]["login"]
        except httpx.HTTPStatusError as ex:
            set_url_status(
                f"Gistへのアップロードに失敗しました: {ex.response.status_code} {ex.response.text}",
                "red",
            )
            return
        else:
            # TODO ユーザーごとにgistを一個作って，消さないようにする？
            # Colab 用の URL を生成
            url = f"https://colab.research.google.com/gist/{gist_username}/{gist_id}/{gist_filename}"
            set_colab_url(url)
            set_url_status("Colab用URLを作成しました", "green")

    def open_how_to_enable_gpu_dialog(e):
        e.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("GPUを有効にする方法"),
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "（（スマホの場合は≡を押して，）Google Colabのメニューから，ランタイム > ランタイムのタイプを変更 を選択してください"
                        ),
                        ft.Text(
                            "ハードウェアアクセラレータのところでGPUを選択して保存をクリックしてください"
                        ),
                    ],
                    tight=True,
                ),
                actions=[
                    ft.TextButton("閉じる", on_click=lambda e: e.page.pop_dialog())
                ],
            )
        )

    def open_how_to_run_cells_dialog(e):
        e.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("すべてのセルを実行する方法"),
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "（（スマホの場合は≡を押して，）Google Colabのメニューから，ランタイム > すべてのセルを実行 を選択してください"
                        ),
                        ft.Text("あとはしばらく待つだけです。"),
                    ],
                    tight=True,
                ),
                actions=[
                    ft.TextButton("閉じる", on_click=lambda e: e.page.pop_dialog())
                ],
            )
        )

    open_colab_sentence = ft.Row(
        [
            ft.TextButton(
                "GPUを有効",
                on_click=open_how_to_enable_gpu_dialog,
                style=ft.ButtonStyle(padding=0),
            ),
            ft.Text("にしてから"),
            ft.TextButton(
                "すべてのセルを実行",
                on_click=open_how_to_run_cells_dialog,
                style=ft.ButtonStyle(padding=0),
            ),
            ft.Text("してください．"),
        ],
        wrap=True,
        spacing=0,
    )
    create_url_button = ft.Button("urlを作成", on_click=create_colab_url)

    return ft.Column(
        controls=[  # gistは1ユーザーごとに一個持つようにする？そうすると消さなくてよい
            ft.Text(
                "url作成ボタンを押すと出てくるurlにアクセスしてください（urlは一時間で削除されます）．"
            ),
            open_colab_sentence,
            ft.Text("10分ほど経ったら一番下のところに結果が出ます．"),
            create_url_button,
            url_status_control,
            ft.TextButton(colab_url, url=colab_url, visible=(colab_url != "")),
        ]
    )
