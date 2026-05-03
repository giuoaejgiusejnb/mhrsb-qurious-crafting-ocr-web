import flet as ft
from functools import partial
from .detail_dialog import DetailDialog
from models.app_state import TypedPage
from .loading_screen import LoadingScreen

class LoadSettingsDialogBase(ft.AlertDialog):
    def __init__(self, page: TypedPage, on_load: callable, is_delete_button_visible=True, needs_overwrite_confirm=True):
        super().__init__()

        self.title = ft.Text("設定読み込み")
        self.overwrite_confirm_msg = "上書きしても構いませんか？"
        self.needs_overwrite_confirm = needs_overwrite_confirm
        self.on_load = on_load
        self.is_delete_button_visible = is_delete_button_visible
        self.user_id = page.app_state.user_id
        self.settings_repo = page.app_state.repos.qc_settings_repo
        self.user_settings_repo = page.app_state.repos.user_settings_repo
        self.content = LoadingScreen()

    def did_mount(self):
        self.page.run_task(self.my_async_init)

    async def my_async_init(self):
        # ラジオボタンの選択肢を格納するリスト
        radio_options = []

        setting_names = await self.settings_repo.fetch_all_settings_names(self.page.app_state.user_id)
        for settings_name in setting_names:
        # 設定名、詳細ボタンを横に並べるRowを作成
        # ラジオボタン本体（ft.Radio）をRowに組み込む
            row = ft.Row(
                controls=[
                    # ラジオボタン（valueには設定名を指定）
                    ft.Radio(value=settings_name, label=settings_name), 
                
                    # 右寄せにするためのスペーサー
                    ft.Container(expand=True), 
                
                    # 詳細ボタン
                    ft.IconButton(
                        tooltip="詳細を表示",
                        icon=ft.Icons.INFO_OUTLINE,
                        # こうしないとクロージャの仕様（遅延評価）で，settings_nameがループの最後のものに固定される
                        on_click=partial(lambda settings_name, page, e
                                        : e.page.show_dialog(DetailDialog(page, settings_name)),
                                        settings_name, self.page)
                    ),

                    # 削除ボタン（is_delete_button_visibleがTrueのときのみ表示）
                    ft.IconButton(
                        tooltip="削除する",
                        icon=ft.Icons.DELETE,
                        visible=self.is_delete_button_visible,
                        on_click=partial(self.show_deltete_confirm_dlg, settings_name=settings_name)
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
            )
            # 各行をリストに追加
            radio_options.append(ft.Container(content=row, padding=ft.Padding.symmetric(vertical=2), data=settings_name))

        # 全体をRadioGroupで包む
        self.settings_selection_group = ft.RadioGroup(
            content=ft.Column(radio_options, scroll=ft.ScrollMode.AUTO),
            on_change=lambda _: (
                setattr(self.load_button, "disabled", False), # 選択されたら無効化を解除
                self.update() # ダイアログを再描画)
            )
        )

        self.content = ft.Column(controls=[self.settings_selection_group], tight=True)
        self.load_button = ft.Button(
            "選んだ設定を読み込む",
            on_click=self.show_overwrite_confirm_dlg,
            disabled=True
        )
        self.actions = [
                ft.TextButton("戻る", on_click=lambda _: self.page.pop_dialog()),
                self.load_button
            ]
        
        self.page.update()

    async def show_overwrite_confirm_dlg(self, e):
        if not self.needs_overwrite_confirm:
            await self.execute_load()
            return

        overwrite_confirm_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("確認"),
            content=ft.Text(self.overwrite_confirm_msg),
            actions=[
                ft.TextButton("キャンセル", on_click=lambda _: self.page.pop_dialog()),
                ft.TextButton(
                    "読み込む",
                    on_click=self.execute_load,
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(overwrite_confirm_dlg)
    
    async def execute_load(self, e=None):
        pass

    def show_deltete_confirm_dlg(self, e, settings_name):
        delete_confirm_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("確認"),
            content=ft.Text(f"{settings_name}を削除しますがよろしいですか？"),
            actions=[
                ft.TextButton("キャンセル", on_click=lambda _: self.page.pop_dialog()),
                ft.TextButton(
                    "削除する",
                    on_click=lambda _: self.page.run_task(self.execute_delete, settings_name)
                    )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(delete_confirm_dlg)

    async def execute_delete(self, settings_name):
        await self.settings_repo.delete_settings(self.page.app_state.user_id, settings_name)
        # 読み込みダイアログに変更を反映させる
        # UIのリスト(Columnのcontrols)から削除するContainerを探す
        target_container = None
        for control in self.settings_selection_group.content.controls:
            if control.data == settings_name:
                target_container = control
                break

        if target_container:
            # UIから削除
            self.settings_selection_group.content.controls.remove(target_container)
            # もし削除したものが現在選択中だったら選択を解除
            if self.settings_selection_group.value == settings_name:
                self.settings_selection_group.value = None
                self.load_button.disabled = True

        # 確認ダイアログを消す
        self.page.pop_dialog()

        self.page.update()
