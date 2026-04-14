import flet as ft
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
    target_user, set_target_user = ft.use_state(user_name)

    dropdown = ft.Dropdown(
        label="表示するユーザーを選択",
        value= target_user,
        on_select=lambda _: set_target_user(dropdown.value),
        width=300,
    )

    # dropdownにユーザーを追加
    for doc in db.collection(COL_USERS).stream():
        dropdown.options.append(ft.dropdown.Option(doc.id))

    qc_logs_colum = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    qc_log_docs = (
        db.collection(COL_USERS)
        .document(target_user)
        .collection(COL_QC_LOGS)
        .order_by(FIELD_EXECUTED_AT, direction=firestore.Query.DESCENDING)
        .stream()
    )

    # 月ごとにデータを格納する辞書を用意
    monthly_data = defaultdict(list)

    for doc in qc_log_docs:
        data = doc.to_dict()
        dt = data.get(FIELD_EXECUTED_AT)
    
        if dt:
            # datetimeオブジェクトから「2023-10」のようなキーを作成
            month_key = dt.strftime('%Y-%m')
            monthly_data[month_key].append(data)

    # 月ごとに表示
    for month, logs in monthly_data.items():
        # 月ごとのヘッダーを追加
        qc_logs_colum.controls.append(
            ft.Container(
                content=ft.Text(month, weight="bold", size=18),
                bgcolor=ft.Colors.OUTLINE,
                padding=10,
                border_radius=5
            )
        )

        # その月のデータを追加
        for log in logs:
            qc_logs_colum.controls.append(
                ft.ListTile(
                    title=ft.Text(f"{log.get(FIELD_CREATED_AT_STR)}の結果"),
                    subtitle=ft.Text(f"練成回数: {log.get(FIELD_QC_COUNT)}"),
                    leading=ft.Icon(ft.Icons.HISTORY),
                )
            )

    return ft.Column(
        controls=[
            ft.Button("ホームに戻る", on_click=lambda _: set_route(HOME)),
            dropdown,
            qc_logs_colum
        ],
        expand=True
    )