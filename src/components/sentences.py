import flet as ft
from firebase_admin import firestore
import nbformat
import requests
import re
from constants import (
    OCR_NOTEBOOK_PATH,
    APP_NAME,
    ENDPOINT_QC_LOG,
    SKILL_MASTER_LIST,
    GIST_URL,
    FIELD_SKILLS
)
from .linked_sentence import LinkedSentence

def get_open_colab_sentence(user_name: str, github_token: str, settings_ref: firestore.CollectionReference, settings_name: str, input_zip_file: str):
    if settings_name:
        data = (
            settings_ref
            .document(settings_name)
            .get().to_dict() or {}
        )
    else:
        # Firestoreのルールで、ドキュメントIDを指定する場所に空文字が入ると
        # パスが /documents/users/aaaaaa/desired_skills_settings/
        # のように末尾がスラッシュで終わってしまい、「ドキュメント名が不正です（400 Error）」とエラーが出る
        data = {}
    desired_skills = data.get(FIELD_SKILLS)

    async def open_in_colab(e):
        if desired_skills is None or input_zip_file == "":
            e.page.show_dialog(
                ft.SnackBar(
                    ft.Text("欲しいスキル設定か画像zipファイルの名前が設定されていません．"),
                    behavior=ft.SnackBarBehavior.FLOATING,
                    margin=ft.Margin.only(bottom=100, left=20, right=20)
                )
            )
            return

        # colabの変数の値を書き換える
        updata_vars = {
            "user_name": user_name,
            "fly_url": f"https://{APP_NAME}.fly.dev{ENDPOINT_QC_LOG}",
            "skill_master_list": SKILL_MASTER_LIST,
            "desired_skills": desired_skills,
            "input_zip_file": input_zip_file#.zipも
        }
        with open(OCR_NOTEBOOK_PATH, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)

        for var_name, new_value in updata_vars.items():
            pattern = rf"^{var_name}\s*=.*"
            replacement = f"{var_name} = {repr(new_value)}"

            nb.cells[1].source = re.sub(pattern, replacement, nb.cells[1].source, flags=re.MULTILINE)

        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json"
        }

        gist_filename = "temp_modified"
        payload = {
            "public": True, 
            "files": {
                gist_filename: {
                    "content": nbformat.writes(nb)
                }
            }
        }

        res = requests.post(GIST_URL, headers=headers, json=payload)

        # Colabで開く
        if res.status_code == 201:
            res_data = res.json()
            gist_id = res_data["id"]
            gist_username = res_data["owner"]["login"]

            # Colabで開くためのURLを組み立て
            # 形式: https://google.com<username>/<gist_id>
            # usernameは省略してもIDが合っていればリダイレクトされます

            # Colab 用の URL を生成
            colab_url = f"https://colab.research.google.com/gist/{gist_username}/{gist_id}/{gist_filename}"
            await ft.UrlLauncher().launch_url(colab_url)

    def open_how_to_enable_gpu_dialog(e):
        e.page.show_dialog(ft.AlertDialog(
            title=ft.Text("GPUを有効にする方法"),
            content=ft.Column(
                controls=[
                    ft.Text("（（スマホの場合は≡を押して，）Google Colabのメニューから，ランタイム > ランタイムのタイプを変更 を選択してください"),
                    ft.Text("ハードウェアアクセラレータのところでGPUを選択して保存をクリックしてください"),
                ],
                tight=True,
            ),
            actions=[ft.TextButton("閉じる", on_click=lambda e: e.page.pop_dialog())]
        ))

    def open_how_to_run_cells_dialog(e):
        e.page.show_dialog(ft.AlertDialog(
            title=ft.Text("すべてのセルを実行する方法"),
            content=ft.Column(
                controls=[
                    ft.Text("（（スマホの場合は≡を押して，）Google Colabのメニューから，ランタイム > すべてのセルを実行 を選択してください"),
                    ft.Text("あとはしばらく待つだけです。"),
                ],
                tight=True,
            ),
            actions=[ft.TextButton("閉じる", on_click=lambda e: e.page.pop_dialog())]
        ))

    open_colab_sentence = LinkedSentence([
        ("これをクリック", open_in_colab),
        "して",
        ("GPUを有効", open_how_to_enable_gpu_dialog),
        "にしてから",
        ("すべてのセルを実行", open_how_to_run_cells_dialog),
        "してください．",
        "10分ほど経ったら一番下のところに結果が出ます",
    ])
    open_colab_sentence.scroll=ft.ScrollMode.ADAPTIVE
    open_colab_sentence.expand=True

    return open_colab_sentence