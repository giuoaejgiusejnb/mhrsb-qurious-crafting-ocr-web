import flet as ft
from dataclasses import dataclass
from firebase_admin import firestore
from pyrebase.pyrebase import Auth
from collections.abc import Callable
from constants import (
    GUEST_USER_NAME,
    KEY_USER_NAME,
    HOME,
    LOGIN
)

@dataclass
class AppState:
    auth: Auth
    db: firestore.firestore.Client
    github_token: str
    is_logged_in: bool
    set_route: Callable[[str], None]
    user_name: str | None = None

    async def login(self, name: str) -> None:
        self.is_logged_in = True
        self.user_name = name
        await ft.SharedPreferences().set(KEY_USER_NAME, name)
        self.set_route(HOME)

    async def logout(self) -> None:
        self.is_logged_in = False
        self.user_name = None
        await ft.SharedPreferences().remove(KEY_USER_NAME)
        self.set_route(LOGIN)

    @property
    def is_authenticated(self) -> bool:
        return self.is_logged_in and self.user_name is not None

    @property
    def is_guest(self) -> bool:
        return (self.user_name == GUEST_USER_NAME)

# page.app_stateをAppState型だと認識するために定義
class TypedPage(ft.Page):
    app_state: AppState