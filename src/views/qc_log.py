import flet as ft
import calendar
from collections import defaultdict
from firebase_admin import firestore
from constants import (
    HOME,
    COL_QC_LOGS,
    COL_USERS,
    FIELD_QC_COUNT,
    FIELD_EXECUTED_AT,
    FIELD_CREATED_AT_STR
)

@ft.component
def QCLog(page: ft.Page, set_route: callable, user_name: str, db: firestore.client) -> ft.Column:
    # 履歴を表示するユーザー
    target_user, set_target_user = ft.use_state(user_name)

    # target_userを選択するドロップダウン
    dropdown = ft.Dropdown(
        label="表示するユーザーを選択",
        value= target_user,
        on_select=lambda _: set_target_user(dropdown.value),
        width=300,
    )

    # dropdownにユーザーを追加
    for doc in db.collection(COL_USERS).stream():
        dropdown.options.append(ft.dropdown.Option(doc.id))

    # 履歴が表示されるコントロール
    qc_logs_list = ft.ListView(
        expand=True, 
        spacing=10, 
        padding=20,
    )
    # 履歴の辞書
    qc_log_docs = (
        db.collection(COL_USERS)
        .document(target_user)
        .collection(COL_QC_LOGS)
        .order_by(FIELD_EXECUTED_AT, direction=firestore.Query.DESCENDING)
        .stream()
    )

    # 各階層の合計を保存する変数・辞書
    all_total_qc = 0
    monthly_totals = defaultdict(int)        # {"2024-05": 500}
    daily_totals = defaultdict(lambda: defaultdict(int)) # {"2024-05": {"14": 100}}
    # 月・日ごとにログ（辞書データ）をリスト形式で格納する
    # 構造例: {"2024-05": {"14": [{"count": 10, ...}, {"count": 20, ...}], "15": [...]}}
    monthly_data = defaultdict(lambda: defaultdict(list))

    # monthly_dataを作成
    for doc in qc_log_docs:
        data = doc.to_dict()
        dt = data.get(FIELD_EXECUTED_AT)
        count = data.get(FIELD_QC_COUNT, 0)

        if dt:
            # datetimeオブジェクトから「2023-10」のようなキーを作成
            month_key = dt.strftime('%Y-%m')
            day_key = dt.strftime('%d')
            monthly_data[month_key][day_key].append(data)
            
            # 各階層に加算
            all_total_qc += count
            monthly_totals[month_key] += count
            daily_totals[month_key][day_key] += count

    # --- 表示部分 ---

    # 総合計を表示するリッチなカード
    qc_logs_list.controls.append(
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.AUTO_AWESOME, color=ft.Colors.AMBER_400),
                    ft.Text("トータル練成実績", size=14, color=ft.Colors.BLUE_GREY_100),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([
                    ft.Text(f"{all_total_qc:,}", size=40, weight="bold", color=ft.Colors.WHITE),
                    ft.Container(
                        content=ft.Text(" 回", size=30, color=ft.Colors.WHITE_70),
                        margin=ft.Margin.only(bottom=5) 
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.END),
            ], spacing=5),
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


    # 月ごとに表示
    for month, daily_data in monthly_data.items():
        year_str, month_str = month.split("-")
        year_int = int(year_str)
        month_int = int(month_str)

        # その月が何日まであるか取得 (例: 5月なら31)
        # calendar.monthrange は (最初の曜日のインデックス, 日数) を返すので [1] を取る
        days_in_month = calendar.monthrange(year_int, month_int)[1]

        # 日平均を計算（やっていない日も含めた平均）
        month_sum = monthly_totals[month]
        daily_average_in_month = month_sum / days_in_month if days_in_month > 0 else 0

        # 月ごとのヘッダーを追加
        qc_logs_list.controls.append(
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

        # 日ごとに表示
        # 日ごとのヘッダーを追加
        for day, logs in daily_data.items():
            day_sum = daily_totals[month][day]
            qc_logs_list.controls.append(
                ft.Container(
                    content=ft.Text(f"{day}日 合計: {day_sum}", weight="bold", size=18),
                    bgcolor=ft.Colors.BLUE_GREY_50,
                    padding=10,
                    border_radius=5,
                )
            )

            # 日ごとの履歴を表示
            for log in logs:
                qc_logs_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(f"{log.get(FIELD_CREATED_AT_STR)}の結果"),
                        subtitle=ft.Text(f"練成回数: {log.get(FIELD_QC_COUNT)}"),
                        leading=ft.Icon(ft.Icons.HISTORY),
                    )
                )

            # 日ごとに余白を入れる
            qc_logs_list.controls.append(ft.Divider(height=10, color=ft.Colors.BLUE))

    return ft.Column(
        controls=[
            ft.Button("ホームに戻る", on_click=lambda _: set_route(HOME)),
            dropdown,
            qc_logs_list
        ],
        expand=True
    )