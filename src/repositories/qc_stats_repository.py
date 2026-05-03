from datetime import datetime
from google.cloud.firestore import (
    AsyncClient,
    Increment,
    AsyncWriteBatch
)
from pydantic import BaseModel, Field, ConfigDict
from constants import (
    COL_USERS,
    COL_QC_STATS,
    FIELD_QC_LAST_EXECUTED_AT,
    FIELD_QC_MONTHLY_COUNT,
)
from .base_repository import BaseRepository

class QCStats(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    last_executed_at: datetime | None = Field(None, alias=FIELD_QC_LAST_EXECUTED_AT)
    monthly_count: int = Field(0, alias=FIELD_QC_MONTHLY_COUNT)

class QCStatsRepository(BaseRepository[QCStats]):
    def __init__(self, db: AsyncClient):
        super().__init__(db=db, model_class=QCStats)

    @classmethod
    def get_collection_path(cls, user_id: str) -> str:
        return f"{COL_USERS}/{user_id}/{COL_QC_STATS}"

    async def fetch(self, user_id: str, year_month: str) -> QCStats:
        return await self.get(
            collection_path=self.get_collection_path(user_id),
            document_id=year_month
        )

    async def get_all_year_months(self, user_id: str) -> list[tuple[str, QCStats]]:
        return await self.get_all(
            collection_path=self.get_collection_path(user_id),
            order_by_field="__name__",
            descending=True
        )

    async def update(self, user_id: str, year_month: str, stats: QCStats, batch: AsyncWriteBatch | None = None) -> None:
        data = stats.model_dump(by_alias=True, exclude_unset=True)
        data[FIELD_QC_MONTHLY_COUNT] = Increment(stats.monthly_count)

        await self.save(
            collection_path=self.get_collection_path(user_id),
            document_id=year_month,
            data=data,
            merge=True,
            batch=batch
        )   