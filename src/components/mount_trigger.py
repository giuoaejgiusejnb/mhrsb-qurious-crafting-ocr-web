import flet as ft
from typing import Callable, Awaitable

# ft.use_effectがなぜか使えないのでこれでdid_mountを使う
class MountTrigger(ft.Container):
    def __init__(
            self, 
            content: ft.Control, 
            on_mount: Callable[[], Awaitable[None]]
    ):
        super().__init__()
        self.content = content
        self.on_mount = on_mount
        self.expand = True

    # Fletの設計上，did_mount は同期関数として定義されることが決まっている
    # なので，did_mount は普通の def（同期関数）で書かなければならない
    # よって，async を外して page.run_task(self.on_mount) を使う
    def did_mount(self):
        # ページがマウントされたら、渡された非同期関数をタスクとして実行
        self.page.run_task(self.on_mount)