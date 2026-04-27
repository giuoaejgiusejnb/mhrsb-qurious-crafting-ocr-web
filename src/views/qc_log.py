# 練成履歴を表示するコンポーネント

import asyncio
import flet as ft
import calendar
import pytz
from collections import defaultdict
from firebase_admin import firestore
from constants import (
    COL_QC_LOGS,
    COL_USERS,
    COL_USER_SETTINGS,
    DOC_ID_CURRENT,
    FIELD_QC_COUNT,
    FIELD_EXECUTED_AT,
    FIELD_CREATED_AT_STR,
    FIELD_IS_QC_LOG_PUBLIC
)
from components import (
    LoadingScreen,
    MountTrigger
)
from models import TypedPage

@ft.component
def QCLog(page: TypedPage) -> ft.Control:
    user_name = page.app_state.user_name
    db = page.app_state.db

    target_user_ref = ft.use_ref(user_name)
    logs_user_options_ref = ft.use_ref([])
    logs_controls_ref = ft.use_ref([])
    is_loading, set_is_loading = ft.use_state(True)

    # Fletのコントロール（部品）作成はメインスレッド（UIスレッド）で行うのが安全．
    # 別スレッドで部品を作ろうとすると、たまに描画エラーの原因になることがあるため、
    # 重いデータ計算が終わってから、UIをサッと作るのがよい
    # ．．．らしい

    # --- データ取得・集計処理 ---
    async def fetch_data() -> None:
        set_is_loading(True)
        # 重い処理（Firestore通信 + 集計）を別スレッドで実行
        def process() -> None:
            # 履歴の取得と集集計
            qc_log_docs = (
                db.collection(COL_USERS)
                .document(target_user_ref.current)
                .collection(COL_QC_LOGS)
                .order_by(FIELD_EXECUTED_AT, direction=firestore.Query.DESCENDING)
                .stream()
            )

            all_total_qc = 0
            monthly_totals = defaultdict(int)
            daily_totals = defaultdict(lambda: defaultdict(int))
            monthly_data = defaultdict(lambda: defaultdict(list))

            for doc in qc_log_docs:
                data = doc.to_dict()
                jst = pytz.timezone('Asia/Tokyo')
                dt = data.get(FIELD_EXECUTED_AT).astimezone(jst)
                count = data.get(FIELD_QC_COUNT, 0)

                if dt:
                    month_key = dt.strftime('%Y-%m')
                    day_key = dt.strftime('%d')
                    monthly_data[month_key][day_key].append(data)
                    all_total_qc += count
                    monthly_totals[month_key] += count
                    daily_totals[month_key][day_key] += count
            
            return all_total_qc, monthly_totals, daily_totals, monthly_data

        # 実行
        total, m_totals, d_totals, m_data = await asyncio.to_thread(process)

        # UIコントロールの組み立て
        new_controls = []
        
        # 総合計カードの追加
        new_controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.AUTO_AWESOME, color=ft.Colors.AMBER_400),
                        ft.Text("トータル練成実績", size=14, color=ft.Colors.BLUE_GREY_100),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([
                        ft.Text(f"{total:,}", size=40, weight="bold", color=ft.Colors.WHITE),
                        ft.Text(" 回", size=30, color=ft.Colors.WHITE_70),
                    ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.END),
                ]),
                bgcolor=ft.Colors.BLUE_900,
                padding=20,
                border_radius=15,
                margin=ft.Margin.only(bottom=20),
                shadow=ft.BoxShadow(
                    blur_radius=10,
                    color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                    offset=ft.Offset(0, 5),
                ),
            )
        )

        # 月ごとの組み立て
        for month, daily_data in m_data.items():
            year_int, month_int = map(int, month.split("-"))
            days_in_month = calendar.monthrange(year_int, month_int)[1]
            month_sum = m_totals[month]
            daily_average_in_month = month_sum / days_in_month if days_in_month > 0 else 0
            
            new_controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"{month}月", weight="bold", size=18, color="white"),
                        ft.Column([
                            ft.Text(f"月間計: {month_sum}", size=14, color="white"),
                            ft.Text(f"日平均(全日): {daily_average_in_month:.1f}", size=12, color="white"),
                        ], horizontal_alignment=ft.CrossAxisAlignment.END),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=ft.Colors.BLUE_800,
                    padding=10,
                    expand=True
                )
            )

            for day, logs in daily_data.items():
                day_sum = d_totals[month][day]
                new_controls.append(ft.Text(f"{day}日 合計: {day_sum}", weight="bold", bgcolor=ft.Colors.BLUE_GREY_200))
                for log in logs:
                    new_controls.append(
                        ft.ListTile(
                            title=ft.Text(f"{log.get(FIELD_CREATED_AT_STR)}の結果"),
                            subtitle=ft.Text(f"練成回数: {log.get(FIELD_QC_COUNT)}"),
                            leading=ft.Icon(ft.Icons.HISTORY)
                        )
                    )
                new_controls.append(ft.Divider(height=10, color=ft.Colors.BLUE))

        logs_controls_ref.current = new_controls
        set_is_loading(False)
        
    # 起動時の初期化関数
    async def init_qc_view() -> None:
        # --- ドロップダウンの作成 ---
        users_list = []
        for doc in db.collection(COL_USERS).stream():
            user_settings = (
                db.collection(COL_USERS)
                .document(doc.id)
                .collection(COL_USER_SETTINGS)
                .document(DOC_ID_CURRENT)
                .get().to_dict() or {}
            )
            # 自分自身の履歴と，履歴を一般公開しているユーザーの履歴を表示
            if doc.id == user_name or user_settings.get(FIELD_IS_QC_LOG_PUBLIC, True):
                users_list.append(ft.dropdown.Option(doc.id))
                
        logs_user_options_ref.current = users_list
        
        # --- 表示する履歴を作成 ---
        await fetch_data()
        
    async def change_target_user(e:ft.ControlEvent) -> None:
        target_user_ref.current = e.control.value
        await fetch_data()

    # --- UI ---
    if is_loading: # logs_controlsを作っている段階なら，ロード画面を表示
        return MountTrigger(content=LoadingScreen(msg="練成履歴を読み込み中"), on_mount=init_qc_view)
    else:
        return ft.Column(
            controls=[
                # どのユーザーの履歴を選択するかのドロップダウン
                ft.Dropdown(
                    label="表示するユーザーを選択",
                    value=target_user_ref.current,
                    options=logs_user_options_ref.current,
                    on_select=change_target_user,
                    width=300,
                ),
                # 履歴表示エリア（ここをスクロールさせる）
                ft.Column(
                    controls=logs_controls_ref.current, 
                    scroll=ft.ScrollMode.ALWAYS,
                    expand=True
                ) 
            ],
            expand=True
        )
