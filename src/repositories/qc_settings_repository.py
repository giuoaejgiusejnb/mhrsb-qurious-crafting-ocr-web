from google.cloud.firestore import AsyncClient, AsyncWriteBatch
from pydantic import BaseModel, Field, ConfigDict
from constants import (
    COL_USERS,
    COL_DESIRED_SKILLS_SETTINGS,
    FIELD_SKILLS
)
from .base_repository import BaseRepository

# --- QC設定を格納するクラス ---
class QCSettings(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    skills: set[str] | None = Field(None, alias=FIELD_SKILLS)

# --- QC設定を扱うリポジトリ ---
class QCSettingsRepository(BaseRepository[QCSettings]):
    def __init__(self, db: AsyncClient):
        super().__init__(db=db, model_class=QCSettings)

    @classmethod
    def get_collection_path(cls, user_id: str) -> str:
        return f"{COL_USERS}/{user_id}/{COL_DESIRED_SKILLS_SETTINGS}"

    # QC設定を取得
    async def fetch(self, user_id: str, settings_name: str) -> QCSettings:
        return await self.get(
            collection_path=self.get_collection_path(user_id),
            document_id=settings_name
        )

    # ユーザーが保存しているQC設定の名前をすべて取得
    async def fetch_all_settings_names(self, user_id: str) -> list[str]:
        docs = await self.get_all(collection_path=self.get_collection_path(user_id))
        return [doc_id for doc_id, _ in docs]

    # QC設定を保存・更新
    async def update(self, user_id: str, settings_name:str, settings: QCSettings, batch: AsyncWriteBatch | None = None) -> None:
        # 更新時は未設定(unset)のものを除外し、設定したい差分だけをマージする
        data = settings.model_dump(by_alias=True, exclude_unset=True)
        await self.save(
            collection_path=self.get_collection_path(user_id),
            document_id=settings_name,
            data=data,
            merge=True,
            batch=batch
        )
        
    # QC設定を削除
    async def delete_settings(self, user_id: str, settings_name: str, batch: AsyncWriteBatch | None = None) -> None:
        await self.delete_doc(
            collection_path=self.get_collection_path(user_id),
            document_id=settings_name,
            batch=batch
        )