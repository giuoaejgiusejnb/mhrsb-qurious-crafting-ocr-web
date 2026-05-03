import flet as ft
from dataclasses import dataclass, field
from collections.abc import Callable
from google.cloud.firestore import AsyncClient
from constants import (
    GUEST_USER_NAME,
    KEY_USER_NAME,
    KEY_USER_ID,
    HOME,
    LOGIN
)
from repositories import RepositoryManager, UserSettings
from services import FirebaseAuth, Gist

@dataclass
class AppState:
    # --- 状態 ---
    auth: FirebaseAuth
    db: AsyncClient
    shared_gist: Gist
    is_logged_in: bool
    set_route: Callable[[str], None]
    user_id: str | None = None
    user_name: str | None = None
    
    # --- リポジトリ ---
    repos: RepositoryManager = field(init=False)

    def __post_init__(self):
        self.repos = RepositoryManager(self.db)

    async def login(self, uid:str, name: str) -> None:
        self.is_logged_in = True
        self.user_id = uid
        self.user_name = name
        await ft.SharedPreferences().set(KEY_USER_NAME, name)
        await ft.SharedPreferences().set(KEY_USER_ID, uid)
        self.set_route(HOME)

    async def logout(self) -> None:
        self.is_logged_in = False
        self.user_name = None
        self.user_id = None
        await ft.SharedPreferences().remove(KEY_USER_ID)
        await ft.SharedPreferences().remove(KEY_USER_NAME)
        self.set_route(LOGIN)

    @property
    def is_authenticated(self) -> bool:
        return self.is_logged_in and self.user_name is not None

    @property
    def is_guest(self) -> bool:
        return (self.user_name == GUEST_USER_NAME)

    async def change_name(self, name: str):
        # DBも更新
        await self.repos.user_settings_repo.rename_user(
            old_name=self.user_name,
            new_name=name,
            user_id=self.user_id
        )
        #メモリ上のデータを更新
        self.user_name = name
        # 永続化（SharedPreference）
        await ft.SharedPreferences().set(KEY_USER_NAME, name)

    # すべての接続を安全に終了する
    async def close_all(self):
        await self.auth.close()
        await self.db.close()
        await self.shared_gist.close()

# page.app_stateをAppState型だと認識するために定義
class TypedPage(ft.Page):
    app_state: AppState