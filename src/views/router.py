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
    APP_NAME,
    KEY_USER_NAME
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
    page.title  = page.route.lstrip("/") + f" ({APP_NAME})"

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
            return QCLog(page, set_route, user_name, db)
        # ルートにマッチしない場合は404ページを表示
        else:
            return NotFoundView(page, set_route) 
