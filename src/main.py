# main.py - アプリのエントリーポイント
from datetime import datetime
import flet as ft
from zoneinfo import ZoneInfo
import flet.fastapi as flet_fastapi
from fastapi import FastAPI, Body
from views import Root
from constants import (
    ENDPOINT_QC_LOG,
    PL_KEY_QC_COUNT,
    PL_KEY_USER_ID,
)
from components import LoadingScreen
from services import (
    fb_auth,
    fb_db,
    shared_gist
)
from models.app_state import TypedPage
from repositories import (
    QCLogsRepository,
    QCStatsRepository,
    QCLogs,
    QCStats,
    UserSettingsRepository,
    UserSettings
)

app = FastAPI()
# main関数内で初期化するとユーザーごとにFirestoreに接続されるので外側に作る
async def main(page: ft.Page):
    page: TypedPage = page

    # 画面にロード中表示を出す
    page.add(LoadingScreen(msg="Gistデータを取得中..."))

    try:
        remaining_days, exp_str = await shared_gist.get_token_expiry_info()
    except Exception as e:
        page.show_dialog(ft.SnackBar(
            ft.Text(f"起動エラー：{e}"),
            persist=True,
            action="ok",
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=ft.Margin.only(bottom=300, left=20, right=20)
            )
        )
    else:
        # ロード画面消去
        page.clean()

        # スクロールバーの定義
        page.theme = ft.Theme(
            scrollbar_theme=ft.ScrollbarTheme(
                track_color={ # バーが通る道の部分の色
                    ft.ControlState.HOVERED: ft.Colors.BLUE_GREY_50, # マウスを乗せた時の色
                    ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT, # 通常時の色
                },
                thumb_color={ # 動くバーの部分の色
                    ft.ControlState.HOVERED: ft.Colors.BLUE_GREY_400,
                    ft.ControlState.DEFAULT: ft.Colors.BLUE_GREY_200,
                },
                thickness=10,        # バーの太さ（デフォルトは短い）
                radius=5,            # 角の丸み
                main_axis_margin=5,
                cross_axis_margin=5,
                interactive=True,    # ドラッグ可能にする
            )
        )

        # ページ遷移
        page.render(
            lambda: Root(
                page=page,
                auth=fb_auth,
                db=fb_db.db,
                shared_gist=shared_gist,
                remaining_days=remaining_days,
                exp_str=exp_str
            )
        )

@app.post(ENDPOINT_QC_LOG)
async def receive_data(payload: dict = Body(...)):
    jst = ZoneInfo("Asia/Tokyo")
    executed_at: datetime = datetime.now(jst)
    year_month = executed_at.strftime("%Y-%m")

    user_id = payload.get(PL_KEY_USER_ID)
    qc_count = payload.get(PL_KEY_QC_COUNT)

    if user_id is None or qc_count is None:
        return False

    db = fb_db.db
    batch = db.batch()
    qc_logs_repo = QCLogsRepository(db)
    qc_stats_repo = QCStatsRepository(db)
    user_repo = UserSettingsRepository(db)

    await qc_logs_repo.update(
        user_id=user_id,
        logs=QCLogs(executed_at=executed_at, qc_count=qc_count),
        batch=batch
    )
    await qc_stats_repo.update(user_id=user_id,
                        year_month=year_month,
                        stats=QCStats(monthly_count=qc_count, qc_last_executed_at=executed_at),
                        batch=batch
    )
    await user_repo.update(user_id=user_id, settings=UserSettings(total_qc_count=qc_count), batch=batch)

    await batch.commit()

    return True

@app.get("/health")
def health():
    return {"status": "ok"}

app.mount("/", flet_fastapi.app(main))

# flet run されたときに実行（この場合，fastapiは無効になる）
if __name__ == "__main__": 
    ft.run(main)