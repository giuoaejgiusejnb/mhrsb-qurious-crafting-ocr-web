# ルーティングと認証状態の管理を行うコンポーネント

import flet as ft
from firebase_admin import firestore
from pyrebase.pyrebase import Auth
from constants import (
    HOME,
    ROUTE_OCR,
    ROUTE_SKILLS_SETTINGS,
    LOGIN,
    ROUTE_QC_LOG,
    SETTINGS,
    KEY_USER_NAME,
    PAGE_TITLES,
    UI_TITLES,
    DEFAULT_UI_TITLE,
    DEFAULT_PAGE_TITLE
)
from views import (
    HomeView,
    LoginView,
    SkillSettingsView,
    SettingsView,
    OCRView,
    QCLog,
    NotFoundView
)

@ft.component
def Root(page: ft.Page, auth: Auth, db: firestore.client, github_token: str) -> ft.Column:
    # ユーザーネーム (None: 確認中, "": 未ログイン, それ以外の文字列: ログイン済み)
    user_name, set_user_name = ft.use_state(None)
    route, set_route = ft.use_state(HOME)

    async def check_login()-> None:
        name = await ft.SharedPreferences().get(KEY_USER_NAME)
        set_user_name(name if name else "")

    ft.use_effect(check_login, [])
    # ログイン状態の確認が終わるまでは待機表示
    if user_name is None:
        return ft.Column([ft.ProgressRing()])

    page.route = route
    page.title  = PAGE_TITLES.get(route, DEFAULT_PAGE_TITLE)
    page.appbar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            tooltip="ホームへ戻る",
            on_click=lambda _: set_route(HOME),
            disabled= (route == HOME)
        ),
        leading_width=40,
        title=UI_TITLES.get(route, DEFAULT_UI_TITLE),
        center_title=True,
        bgcolor=ft.Colors.BLUE_GREY_400,
    )

    if not user_name:  # ログインしていない場合はログイン画面へ
        set_route(LOGIN)
        return LoginView(page, set_route, set_user_name, auth, db)
    else:
        if page.route == HOME:
            return HomeView(page, set_route, set_user_name, user_name)
        elif page.route == SETTINGS:
            return SettingsView(page, set_route, user_name, db)
        elif page.route == ROUTE_SKILLS_SETTINGS:
            return SkillSettingsView(page, set_route, user_name, db)
        elif page.route == ROUTE_OCR:
            return OCRView(page, set_route, user_name, db, github_token)
        elif page.route == ROUTE_QC_LOG:
            # ft.Containerで包まないとQCLog内のft.use_effectが動かない
            # 理由はわからん！！！！！！！
            return ft.Container(content=QCLog(page, set_route, user_name, db), expand=True)
        # ルートにマッチしない場合は404ページを表示
        else:
            return NotFoundView()
