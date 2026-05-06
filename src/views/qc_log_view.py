import calendar
from collections import defaultdict
from dataclasses import dataclass
from zoneinfo import ZoneInfo

import flet as ft

from components import LoadingScreen, MountTrigger
from models.app_state import TypedPage
from repositories import QCLogs, QCStats, RepositoryManager


@ft.observable
@dataclass
class QCLogStore:
    repos: RepositoryManager | None = None
    target_uid: str | None = None  # 履歴を表示するユーザーID
    total: int | None = None  # 履歴を表示するユーザーの総連整数
    # 履歴を表示するユーザーの月ごとのQCStats
    # [(year_month, qc_stats), ...]の形式
    monthly_qc_stats: list[tuple[str, QCStats]] | None = None
    # 履歴を表示する月 = monthly_qc_stats[target_ym_idx][0]
    target_ym_idx: int | None = None
    # 表示する履歴
    target_logs: list[QCLogs] | None = None
    # 表示する履歴のキャッシュ
    # {"year_month":[qc_logs, ...], ...}の形式
    _logs_cache: dict[str, list[QCLogs]] | None = None
    # データ読み込み中
    is_loading: bool = True

    async def change_target_user(self, new_uid: str) -> None:
        self.is_loading = True
        self._logs_cache = {}  # キャッシュクリア

        self.monthly_qc_stats = await self.repos.qc_stats_repo.get_all_year_months(
            new_uid
        )
        user_settings = await self.repos.user_settings_repo.fetch(new_uid)

        self.total = user_settings.total_qc_count
        self.target_uid = new_uid
        await self.change_target_ym(0)

    async def change_target_ym(self, new_ym_idx: int) -> None:
        self.is_loading = True
        new_year_month = self.monthly_qc_stats[new_ym_idx][0]

        cache = self._logs_cache.get(new_year_month)  # キャッシュを取得
        if cache is not None:  # キャッシュがあればそれを使う
            self.target_logs = cache
        else:  # ないならDBから読み込んで，キャッシュ保存
            self.target_logs = await self.repos.qc_logs_repo.get_recent_logs_by_month(
                user_id=self.target_uid,
                year_month=new_year_month,
                limit=10000,  # TODO limit指定して，少しづつ表示する形式に
            )
            self._logs_cache[new_year_month] = self.target_logs

        self.target_ym_idx = new_ym_idx
        self.is_loading = False


@ft.component
def QCLogView(page: TypedPage) -> ft.Control:
    qc_log_store = ft.use_memo(lambda: QCLogStore(), [])
    # 初期化が終わったかどうか
    is_initialized, set_is_initialized = ft.use_state(False)
    # ログを表示するユーザーの(usr_id, user_name)のリスト
    users_info, set_users_info = ft.use_state([])

    # --- 起動時の初期化関数（ドロップダウンオプションを作成） ---
    async def init_qc_view() -> None:
        if is_initialized:
            return  # 既に初期化したならスキップ

        initial_uid = page.app_state.user_id
        initial_uname = page.app_state.user_name
        repos = page.app_state.repos

        # 公開設定にしているユーザーとログインユーザーをドロップダウンに追加
        users_info = await repos.user_settings_repo.get_public_log_users()
        login_user_info = (initial_uid, initial_uname)
        if login_user_info not in users_info:
            users_info.append(login_user_info)

        qc_log_store.repos = repos
        set_users_info(users_info)
        set_is_initialized(True)  # 初期化終了

    # --- UI ---
    # まだ初期化が始まっていない場合のみ MountTrigger を返す
    if not is_initialized:
        return MountTrigger(
            content=LoadingScreen(msg="初期化中..."), on_mount=init_qc_view
        )

    # --- どのユーザーの履歴を選択するかのドロップダウン ---
    @ft.component
    def UserDropdown(users_info: list[tuple[str, str]]) -> ft.Control:
        user_options = [
            ft.dropdown.Option(key=user_id, text=user_name)
            for user_id, user_name in users_info
        ]

        return ft.Dropdown(
            label="履歴を表示するユーザーを選択",
            options=user_options,
            on_select=lambda e: e.page.run_task(
                qc_log_store.change_target_user, e.control.value
            ),
            width=300,
        )

    return ft.Column(
        controls=[UserDropdown(users_info=users_info), MainContent(state=qc_log_store)],
        expand=True,
    )


@ft.component
def MainContent(state: QCLogStore) -> ft.Control:
    # 表示するユーザーを選択していないなら何も表示しない
    if state.target_uid is None:
        return ft.Container()
    # ロード中ならロード画面を表示
    if state.is_loading:
        return LoadingScreen()
    else:
        return ft.Column(
            controls=[
                TotalStatsCard(state=state),
                MonthSelector(state=state),
                LogControls(state=state),
            ],
            expand=True,
        )


# 総連整数を表示するカード
@ft.component
def TotalStatsCard(state: QCLogStore) -> ft.Control:
    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.AUTO_AWESOME, color=ft.Colors.AMBER_400),
                        ft.Text(
                            "トータル練成実績", size=14, color=ft.Colors.BLUE_GREY_100
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        ft.Text(
                            f"{state.total:,}",
                            size=40,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                        ft.Text(" 回", size=30, color=ft.Colors.WHITE_70),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                ),
            ]
        ),
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


# --- 表示する月を決定するコントロール
@ft.component
def MonthSelector(state: QCLogStore) -> ft.Control:
    current_index = state.target_ym_idx
    year_months = [t[0] for t in state.monthly_qc_stats]
    # ボタンの状態判定
    can_go_prev = current_index > 0
    can_go_next = current_index < len(year_months) - 1

    return ft.Container(
        bgcolor=ft.Colors.BLUE_GREY_900,
        border_radius=10,
        padding=5,
        content=ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.CHEVRON_LEFT,
                    icon_color=ft.Colors.BLUE_200
                    if can_go_prev
                    else ft.Colors.BLUE_GREY_700,
                    disabled=not can_go_prev,
                    on_click=lambda e: e.page.run_task(
                        state.change_target_ym, current_index - 1
                    ),
                    tooltip="前の月へ",
                ),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text("表示月", size=20, color=ft.Colors.WHITE),
                            ft.Dropdown(
                                value=str(current_index),
                                options=[
                                    ft.dropdown.Option(
                                        key=str(idx),
                                        text=item,
                                    )
                                    for idx, item in enumerate(year_months)
                                ],
                                border_color=ft.Colors.BLUE_400,
                                filled=True,
                                bgcolor=ft.Colors.BLUE_200,
                                on_select=lambda e: e.page.run_task(
                                    state.change_target_ym, int(e.control.value)
                                ),
                            ),
                        ]
                    ),
                ),
                ft.IconButton(
                    icon=ft.Icons.CHEVRON_RIGHT,
                    icon_color=ft.Colors.BLUE_200
                    if can_go_next
                    else ft.Colors.BLUE_GREY_700,
                    disabled=not can_go_next,
                    on_click=lambda e: e.page.run_task(
                        state.change_target_ym, current_index + 1
                    ),
                    tooltip="次の月へ",
                ),
            ]
        ),
    )


# ---履歴部分のコントロール作成 ---
@ft.component
def LogControls(state: QCLogStore) -> ft.Control:
    month_data = state.monthly_qc_stats[state.target_ym_idx]
    year_month = month_data[0]
    year, month = year_month.split("-")
    month_sum = month_data[1].monthly_count
    daily_average_in_month = month_sum / calendar.monthrange(int(year), int(month))[1]

    # 返り値のコントロール
    controls = []

    # その月の合計練成数と平均を表示
    controls.append(
        ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        f"{year}年{month}月",
                        weight=ft.FontWeight.BOLD,
                        size=18,
                        color="white",
                    ),
                    ft.Column(
                        [
                            ft.Text(f"月間計: {month_sum}", size=14, color="white"),
                            ft.Text(
                                f"日平均(全日): {daily_average_in_month:.1f}",
                                size=12,
                                color="white",
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=ft.Colors.BLUE_800,
            # スクロールバーに重なるので，右側の余白を少し追加
            padding=ft.Padding.only(left=10, top=10, bottom=10, right=30),
            expand=True,
        )
    )

    # 日ごとにログと総練成数が格納されている辞書を作成
    daily_data = defaultdict(list)
    daily_totals = defaultdict(int)

    # 日ごとにログと総練成数をまとめる
    for log in state.target_logs:
        day_key = log.executed_at.astimezone(ZoneInfo("Asia/Tokyo")).strftime(
            "%Y-%m-%d"
        )
        daily_data[day_key].append(log)
        daily_totals[day_key] += log.qc_count

    # 日ごとに表示
    for day, logs in daily_data.items():
        day_sum = daily_totals[day]
        controls.append(
            ft.Text(
                f"{day}日 合計: {day_sum}",
                weight=ft.FontWeight.BOLD,
                bgcolor=ft.Colors.BLUE_GREY_200,
            )
        )
        for log in logs:
            controls.append(
                ft.ListTile(
                    title=ft.Text(f"{log.created_at_str}の結果"),
                    subtitle=ft.Text(f"練成回数: {log.qc_count}"),
                    leading=ft.Icon(ft.Icons.HISTORY),
                )
            )
        # 日ごとにセクションを区切るため，青い水平線を追加
        controls.append(ft.Divider(height=10, color=ft.Colors.BLUE))

    return ft.ListView(controls=controls, expand=True, spacing=0)
