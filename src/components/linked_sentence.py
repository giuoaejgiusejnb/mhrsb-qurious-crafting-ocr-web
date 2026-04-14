import asyncio
import flet as ft
import subprocess
import os
import platform

class LinkedSentence(ft.Row):
    def __init__(self, parts: list):
        """
        parts: 
            - str: 通常のテキスト
            - tuple (ラベル, アクション): 
                アクションが文字列ならURL/パスとして開く。
                アクションが関数ならそのまま実行する。
        """
        super().__init__()
        self.tight = True
        self.spacing = 2
        self.vertical_alignment = ft.CrossAxisAlignment.CENTER
        
        self.controls = []
        for part in parts:
            if isinstance(part, str):
                self.controls.append(ft.Text(part))
            elif isinstance(part, tuple):
                label, action = part
                
                # 文字列（URLやパス）か、関数（コールバック）かを自動判別
                if isinstance(action, str):
                    # 文字列ならクラスメソッドを呼ぶようにラップする
                    # ※引数 u=action とすることでループ内での値の固定を行う
                    on_click_func = lambda e, u=action: LinkedSentence.open_content(e, u)
                else:
                    on_click_func = action

                self.controls.append(
                    ft.TextButton(
                        content=ft.Text(label, color=ft.Colors.BLUE, weight=ft.FontWeight.W_500),
                        style=ft.ButtonStyle(padding=0),
                        on_click=on_click_func
                    )
                )

    @staticmethod
    def open_content(e, path_or_url):
        """URLまたはフォルダパスをOS標準のアプリで開く"""
        try:
            if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
                LinkedSentence.open_url(e, path_or_url)
            else:
                LinkedSentence.open_explorer(e, path_or_url)
        except Exception as e:
            e.page.show_dialog(ft.SnackBar(ft.Text(f"内容を開く際にエラーが発生しました: {e}")))

    @staticmethod
    # エクスプローラーでパスを開く関数
    def open_explorer(e, path):
        if not path or not os.path.exists(path):
            e.page.show_dialog(ft.SnackBar(ft.Text("パスが存在しません")))
            return

        pf = platform.system()
        normalized_path = os.path.normpath(path)

        if pf == "Windows":
            # Windows: エクスプローラーで開く
            subprocess.run(['explorer', normalized_path])
        elif pf == "Darwin":
            # macOS: Finderで開く
            subprocess.run(["open", normalized_path])
        else:
            # Linuxなど: デフォルトのファイルマネージャーで開く
            subprocess.run(["xdg-open", normalized_path])

    @staticmethod
    # URLをブラウザで開く関数
    def open_url(e, url):
        if not url:
            e.page.show_dialog(ft.SnackBar(ft.Text("URLが設定されていません")))
            return
        #URLをブラウザで開く
        try:
            asyncio.create_task(ft.UrlLauncher().launch_url(url))
        except Exception as ex:
            e.page.show_dialog(ft.SnackBar(ft.Text(f"URLを開く際にエラーが発生しました: {ex}")))
