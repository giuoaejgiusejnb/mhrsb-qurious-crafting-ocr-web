import flet as ft
from typing import Callable

PW_FIELD_WIDTH = 300

def create_password_field(label:str = "パスワード", value:str = "", on_change:Callable | None = None) -> ft.TextField:
    password_field = ft.TextField(
        label=label,
        value=value,
        password=True,
        can_reveal_password=True,
        width=PW_FIELD_WIDTH,
        on_change=on_change
    )
    
    return password_field