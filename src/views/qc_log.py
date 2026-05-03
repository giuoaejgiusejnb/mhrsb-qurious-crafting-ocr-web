# 練成履歴を表示するコンポーネント

import asyncio
import flet as ft
import calendar
from collections import defaultdict
from zoneinfo import ZoneInfo
from components import (
    LoadingScreen,
    MountTrigger
)
from models.app_state import TypedPage
from repositories import QCLogs

# TODO: レースコンディション（ui構築前にホームに戻ると，ホームに戻った後にこのページに自動的に戻ってしまう）
@ft.component
def QCLog(page: TypedPage) -> ft.Control:
    user_id = page.app_state.user_id
    user_repos = page.app_state.repos.user_settings_repo
    stats_repo = page.app_state.repos.qc_stats_repo
    logs_repo = page.app_state.repos.qc_logs_repo

    is_initialized, set_is_initialized = ft.use_state(False) # 初期化フラグ
    is_loading, set_is_loading = ft.use_state(True) # データロード中かどうか
    target_user_id_ref = ft.use_ref(user_id) # 現在表示しているユーザーIDの参照
    monthly_counts_ref = ft.use_ref([]) # 月ごとの練成回数のリストの参照
    target_year_month_idx_ref = ft.use_ref(0) # 現在表示している年月のインデックスの参照
    user_dropdown_ref = ft.use_ref(None) # ユーザー選択のドロップダウン
    total_stats_card_ref = ft.use_ref(None) # ユーザー総練成数を表示するカード
    logs_controls_ref = ft.use_ref([]) # 履歴を表示するコントロールの中身 

    # ---履歴部分のコントロール作成 ---
    async def create_logs_controls() -> None:
        set_is_loading(True)

        year_month = monthly_counts_ref.current[target_year_month_idx_ref.current][0]
        year, month = year_month.split("-")

        # 履歴の取得
        # TODO limitを制限して，ボタンを押したら残りを取得
        qc_logs = await logs_repo.get_recent_logs_by_month(target_user_id_ref.current, year_month, limit=1000)
        daily_data = defaultdict(list)
        daily_totals = defaultdict(int)

        for log in qc_logs:
            day_key = log.executed_at.astimezone(ZoneInfo("Asia/Tokyo")).strftime('%Y-%m-%d')
            daily_data[day_key].append(log)
            daily_totals[day_key] += log.qc_count

        # UIコントロールの組み立て
        new_controls = []

        # その月の合計練成数と平均を表示
        month_sum = monthly_counts_ref.current[target_year_month_idx_ref.current][1]
        daily_average_in_month = month_sum / calendar.monthrange(int(year), int(month))[1]
        new_controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Text(f"{year}年{month}月", weight=ft.FontWeight.BOLD, size=18, color="white"),
                    ft.Column([
                        ft.Text(f"月間計: {month_sum}", size=14, color="white"),
                        ft.Text(f"日平均(全日): {daily_average_in_month:.1f}", size=12, color="white"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.END),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=ft.Colors.BLUE_800,
                # スクロールバーに重なるので，右側の余白を少し追加
                padding=ft.Padding.only(left=10, top=10, bottom=10, right=30),
                expand=True
            )
        )

        for day, logs in daily_data.items():
            logs: list[QCLogs]
            day_sum = daily_totals[day]
            new_controls.append(ft.Text(f"{day}日 合計: {day_sum}", weight=ft.FontWeight.BOLD, bgcolor=ft.Colors.BLUE_GREY_200))
            for log in logs:
                new_controls.append(
                    ft.ListTile(
                        title=ft.Text(f"{log.created_at_str}の結果"),
                        subtitle=ft.Text(f"練成回数: {log.qc_count}"),
                        leading=ft.Icon(ft.Icons.HISTORY)
                    )
                )
            new_controls.append(ft.Divider(height=10, color=ft.Colors.BLUE))

        logs_controls_ref.current = new_controls
        set_is_loading(False)
        
    # --- 起動時の初期化関数（ドロップダウンを作成し，create_logs_controlsを実行） ---
    async def init_qc_view() -> None:
        if is_initialized: return # 既に初期化したならスキップ
        # --- ドロップダウンの作成 ---

        # 公開設定にしているユーザーとログインユーザーをドロップダウンに追加
        users_info = await user_repos.get_public_log_users()
        login_user_info =  (user_id, page.app_state.user_name)
        if not login_user_info in users_info:
            users_info.append(login_user_info)
        user_options = [
            ft.dropdown.Option(key=user_id, text=user_name)
            for user_id, user_name in users_info
        ]

        # どのユーザーの履歴を選択するかのドロップダウン
        user_dropdown_ref.current = ft.Dropdown(
                label="表示するユーザーを選択",
                value=user_id,
                options=user_options,
                on_select=on_user_change,
                width=300,
            )

        set_is_initialized(True) # 初期化開始を記録
        # 表示する履歴を作成
        await change_target_user(page.app_state.user_id)
    
    # --- 表示するユーザーを変更 ---
    async def change_target_user(uid:str) -> None:
        set_is_loading(True)
        target_user_id_ref.current = uid
        stats_data = await stats_repo.get_all_year_months(uid)
        monthly_counts_ref.current = [
            (year_month, stats.monthly_count) 
            for year_month, stats in stats_data
        ]
        # 総合計カードの追加
        user_settings = await user_repos.fetch(target_user_id_ref.current)
        total_stats_card_ref.current = TotalStatsCard(user_settings.total_qc_count)

        # 練成したことがあれば，それを取得して表示
        if monthly_counts_ref.current:
            target_year_month_idx_ref.current = 0
            
            await create_logs_controls()
        else:
            logs_controls_ref.current = []
            set_is_loading(False)

    async def on_user_change(e:ft.ControlEvent) -> None:
        await change_target_user(e.control.value)

    # --- 表示する月を決定するコントロール
    def MonthSelector():
        current_index = target_year_month_idx_ref.current
        year_months = monthly_counts_ref.current
        # ボタンの状態判定
        can_go_prev = current_index > 0
        can_go_next = current_index < len(year_months) - 1
        current_label = year_months[current_index][0] if year_months else "データなし"

        async def handle_month_change(new_index: int):
            target_year_month_idx_ref.current = new_index
            await create_logs_controls()

        return ft.Container(
            bgcolor=ft.Colors.BLUE_GREY_900,
            border_radius=10,
            padding=5,
            content=ft.Row([
                ft.IconButton(
                    icon=ft.Icons.CHEVRON_LEFT,
                    icon_color=ft.Colors.BLUE_200 if can_go_prev else ft.Colors.BLUE_GREY_700,
                    disabled=not can_go_prev,
                    on_click=lambda _: page.run_task(handle_month_change, current_index - 1),
                    tooltip="前の月へ"
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Text("表示月", size=20, color=ft.Colors.WHITE),
                        ft.Dropdown(
                            value=str(current_index),
                            options=[
                                ft.dropdown.Option(
                                    key=str(idx),
                                    text=item[0],
                                ) for idx, item in enumerate(monthly_counts_ref.current)
                            ],
                            border_color=ft.Colors.BLUE_400,
                            filled=True, 
                            bgcolor=ft.Colors.BLUE_200,
                            on_select=lambda e: page.run_task(handle_month_change, int(e.control.value))
                        )
                    ]),
                ),
                ft.IconButton(
                    icon=ft.Icons.CHEVRON_RIGHT,
                    icon_color=ft.Colors.BLUE_200 if can_go_next else ft.Colors.BLUE_GREY_700,
                    disabled=not can_go_next,
                    on_click=lambda _: page.run_task(handle_month_change, current_index + 1),
                    tooltip="次の月へ"
                ),
            ])
        )

    # --- UI ---
    # まだ初期化が始まっていない場合のみ MountTrigger を返す
    if not is_initialized:
        return MountTrigger(
            content=LoadingScreen(msg="初期化中..."), 
            on_mount=init_qc_view
        )

    # 読み込み中の表示
    if is_loading:
        return LoadingScreen(msg="練成履歴を読み込み中")
    else:
        return ft.Column(
            controls=[
                user_dropdown_ref.current, # ユーザードロップダウン
                total_stats_card_ref.current, # 総練成数カード
                MonthSelector(),
                # 履歴表示エリア（ここをスクロールさせる）
                ft.Column(
                    controls=logs_controls_ref.current, 
                    scroll=ft.ScrollMode.ALWAYS,
                    expand=True
                ) 
            ],
            expand=True
        )

class TotalStatsCard(ft.Container):
    def __init__(self, total:int):
        super().__init__()

        self.content = ft.Column([
            ft.Row(
                [
                    ft.Icon(ft.Icons.AUTO_AWESOME, color=ft.Colors.AMBER_400),
                    ft.Text("トータル練成実績", size=14, color=ft.Colors.BLUE_GREY_100),
                ],
                alignment=ft.MainAxisAlignment.CENTER),
            ft.Row(
                [
                    ft.Text(f"{total:,}", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text(" 回", size=30, color=ft.Colors.WHITE_70),
                ],
                alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.END),
            ])

        self.bgcolor=ft.Colors.BLUE_900
        self.padding=20
        self.border_radius=15
        self.margin=ft.Margin.only(bottom=20)
        self.shadow=ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
            offset=ft.Offset(0, 5),
        )


