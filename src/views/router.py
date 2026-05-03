# ルーティングと認証状態の管理を行うコンポーネント

import flet as ft
from google.cloud.firestore import AsyncClient
from constants import (
    HOME,
    ROUTE_SKILLS_SETTINGS,
    LOGIN,
    ROUTE_OCR,
    SETTINGS,
    ROUTE_QC_LOG,
    KEY_USER_NAME,
    KEY_USER_ID,
    PAGE_TITLES,
    UI_TITLES,
    DEFAULT_ALERT_DAYS,
    DEFAULT_PAGE_TITLE,
    DEFAULT_UI_TITLE
)
from components import LoadingScreen
from models.app_state import (
    AppState,
    TypedPage
)
from services import (
    FirebaseAuth,
    Gist
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
def Root(page: TypedPage, auth: FirebaseAuth, db: AsyncClient, shared_gist: Gist, remaining_days: int, exp_str: str) -> ft.Control:
    is_loading, set_is_loading = ft.use_state(True)
    route, set_route = ft.use_state(HOME)

    # page.app_stateに登録
    if not hasattr(page, "app_state"):
        page.app_state = AppState(
            auth=auth,
            db=db,
            shared_gist=shared_gist,
            is_logged_in=False,
            set_route=set_route,
            user_name=""
        )
        page.on_disconnect = page.app_state.close_all

    async def initial_setup()-> None:
        #--- 前回のログインデータが残っているかチェック ---
        uid = await ft.SharedPreferences().get(KEY_USER_ID) # 前回のログインユーザーID
        name = await ft.SharedPreferences().get(KEY_USER_NAME) # 前回のログインユーザー名
        alert_threshold = DEFAULT_ALERT_DAYS # gist有効期限警告の閾値

        if name and uid: # ログインデータが残っているならそのデータでログイン
            await page.app_state.login(uid, name)
            # alert_thresholdを取得
            settings = await page.app_state.repos.user_settings_repo.fetch(uid)
            alert_threshold = settings.alert_days
        
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

    try:
        return ROUTES_MAP.get(route, NotFoundView)(page)
    except Exception as e:
        return ft.Text(f"Error loading view for route '{route}': {e}")

# ルートとView関数のマッピング
ROUTES_MAP = {
    HOME: HomeView,
    LOGIN: LoginView,
    ROUTE_OCR: OCRView,
    ROUTE_SKILLS_SETTINGS: SkillSettingsView,
    SETTINGS: SettingsView,
    ROUTE_QC_LOG: QCLog,
}