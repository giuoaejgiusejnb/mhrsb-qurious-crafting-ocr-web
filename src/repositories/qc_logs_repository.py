from __future__ import annotations
from google.cloud.firestore import AsyncClient, AsyncWriteBatch
from google.cloud.firestore_v1.base_query import FieldFilter
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    model_validator
)
from datetime import datetime
from constants import (
    COL_USERS,
    FIELD_CREATED_AT_STR,
    FIELD_EXECUTED_AT,
    FIELD_QC_COUNT,
    FIELD_YEAR_MONTH,
    COL_QC_LOGS
)
from .base_repository import BaseRepository

# --- QC履歴を格納するクラス ---
class QCLogs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    executed_at: datetime | None = Field(None, alias=FIELD_EXECUTED_AT)
    created_at_str: str | None = Field(None, alias=FIELD_CREATED_AT_STR)
    year_month : str | None = Field(None, alias=FIELD_YEAR_MONTH)
    qc_count: int | None = Field(None, alias=FIELD_QC_COUNT)
    
    @model_validator(mode='after')
    def derive_fields_from_executed_at(self) -> 'QCLogs':
        if self.executed_at:
            # datetimeから "2023-11-24 10:21:56" 形式を生成
            if not self.created_at_str:
                self.created_at_str = self.executed_at.strftime("%Y-%m-%d %H:%M:%S")
            
            # datetimeから "2023-11" 形式を生成
            if not self.year_month:
                self.year_month = self.executed_at.strftime("%Y-%m")
        return self

# --- QC履歴を扱うリポジトリ ---
class QCLogsRepository(BaseRepository[QCLogs]):
    def __init__(self, db: AsyncClient):
        super().__init__(db=db, model_class=QCLogs)

    @classmethod
    def get_collection_path(cls, user_id: str) -> str:
        collection_path = f"{COL_USERS}/{user_id}/{COL_QC_LOGS}"
        cls._validate_path_segments(collection_path)
        return collection_path

    # QC履歴を取得
    async def get_recent_logs_by_month(self, user_id: str, year_month: str, limit: int = 10) -> list[QCLogs]:
        query = (
            self.db.collection(self.get_collection_path(user_id))
            .where(filter=FieldFilter(FIELD_YEAR_MONTH, "==", year_month))
            .order_by(FIELD_CREATED_AT_STR, direction="DESCENDING")
            .limit(limit)
        )

        results = await self._fetch_and_validate(query, QCLogs)
        return [t[1] for t in results]

    # QC履歴を保存・更新
    async def update(self, user_id: str, logs:QCLogs, batch: AsyncWriteBatch | None = None) -> None:
        data = logs.model_dump(by_alias=True)
        await self.add(
            collection_path=self.get_collection_path(user_id=user_id),
            data=data,
            batch=batch
        )