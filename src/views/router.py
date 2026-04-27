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
    DEFAULT_PAGE_TITLE,
    COL_USERS,
    COL_USER_SETTINGS,
    DOC_ID_CURRENT,
    FIELD_ALERT_DAYS,
    DEFAULT_ALERT_DAYS
)
from components import LoadingScreen
from models import (
    AppState,
    TypedPage
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
def Root(page: TypedPage, auth: Auth, db: firestore.firestore.Client, github_token: str, remaining_days: int, exp_str: str) -> ft.Control:
    is_loading, set_is_loading = ft.use_state(True)
    route, set_route = ft.use_state(HOME)

    # page.app_stateに登録
    if not hasattr(page, "app_state"):
        page.app_state = AppState(
            auth=auth,
            db=db,
            github_token=github_token,
            is_logged_in=False,
            set_route=set_route,
            user_name=""
        )

    async def initial_setup()-> None:
        # --- 前回のログインデータが残っているかチェック ---
        name = await ft.SharedPreferences().get(KEY_USER_NAME) # 前回のログインユーザー
        alert_threshold = DEFAULT_ALERT_DAYS # gist有効期限警告の閾値

        if name: # ログインデータが残っているならそのデータでログイン
            await page.app_state.login(name)
            # alert_thresholdを取得
            user_settings_ref = (
                db.collection(COL_USERS)
                .document(page.app_state.user_name)
                .collection(COL_USER_SETTINGS)
                .document(DOC_ID_CURRENT)
            )
            user_settings = user_settings_ref.get().to_dict() or {}
            alert_threshold = user_settings.get(FIELD_ALERT_DAYS, alert_threshold)
        
        # --- gistの有効期限が近づいていたら，警告表示 ---
        if remaining_days <= alert_threshold:
            expiration_warning_text = f"このwebアプリは{exp_str}に使用できなくなります．アプリ作成者に連絡して有効期限を延ばしてください"
            page.show_dialog(ft.SnackBar(
                ft.Text(expiration_warning_text),
                persist=True,
                action="ok",
                behavior=ft.SnackBarBehavior.FLOATING,
                margin=ft.Margin.only(bottom=300, left=20, right=20)
                )
            )

        # 初期化終了
        set_is_loading(False)

    # 初回起動時にのみ前回のログインチェックとgistの有効期限チェック
    ft.use_effect(initial_setup, [])
    # ログイン状態の確認が終わるまでは待機表示
    if is_loading:
        return LoadingScreen(msg="ログイン状態を確認中")

    # ログインしていないならログインページに移動
    if not page.app_state.is_authenticated and route != LOGIN:
        page.app_state.set_route(LOGIN)

    #--- UI構築 ---
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
    return ROUTES_MAP.get(route, NotFoundView)(page)

# ルートとView関数のマッピング
ROUTES_MAP = {
    HOME: HomeView,
    LOGIN: LoginView,
    ROUTE_OCR: OCRView,
    ROUTE_SKILLS_SETTINGS: SkillSettingsView,
    SETTINGS: SettingsView,
    ROUTE_QC_LOG: QCLog,
}