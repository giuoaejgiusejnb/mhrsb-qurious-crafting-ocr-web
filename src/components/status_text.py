import flet as ft

# ステータス表示用のコントロールと更新関数を提供するカスタムフック

def use_status_text():
    status_text, set_status_text = ft.use_state("")
    status_color, set_status_color = ft.use_state(None)

    # テキストと色を同時に更新するヘルパー関数
    def set_status(text: str, color: str = None):
        set_status_text(text)
        set_status_color(color)

    # 描画用のTextコントロール
    status_control = ft.Text(value=status_text, color=status_color)

    return status_control, set_status