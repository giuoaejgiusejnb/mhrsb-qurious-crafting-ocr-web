from __future__ import annotations
from google.cloud.firestore import (
    AsyncDocumentReference,
    AsyncWriteBatch,
    AsyncClient,
    Increment
)
from google.cloud.firestore_v1.base_query import FieldFilter
from pydantic import BaseModel, Field, ConfigDict
from constants import (
    COL_USERS,
    COL_USERNAME_MAP,
    DEFAULT_ALERT_DAYS,
    DEFAULT_IS_QC_LOG_PUBLIC,
    FIELD_USER_NAME,
    FIELD_SKILLS_SETTINGS_NAME,
    FIELD_INPUT_ZIP_FILE,
    FIELD_EMAIL,
    FIELD_TOTAL_QC_COUNT,
    FIELD_ALERT_DAYS,
    FIELD_IS_QC_LOG_PUBLIC,
    FIELD_MAP_EMAIL
)
from .base_repository import BaseRepository

# --- ユーザー設定を格納するクラス ---
class UserSettings(BaseModel):
    model_config = ConfigDict(populate_by_name=True) 
    user_name: str | None = Field(None, alias=FIELD_USER_NAME)
    last_selected_settings_name: str | None = Field(None, alias=FIELD_SKILLS_SETTINGS_NAME)
    last_selected_input_zip_file: str | None = Field(None, alias=FIELD_INPUT_ZIP_FILE)
    email: str | None = Field(None, alias=FIELD_EMAIL)
    total_qc_count: int = Field(0, alias=FIELD_TOTAL_QC_COUNT)
    alert_days: int = Field(DEFAULT_ALERT_DAYS, alias=FIELD_ALERT_DAYS)
    is_qc_log_public: bool = Field(DEFAULT_IS_QC_LOG_PUBLIC, alias=FIELD_IS_QC_LOG_PUBLIC)

# --- ユーザー設定を扱うリポジトリ ---
class UserSettingsRepository(BaseRepository[UserSettings]):
    def __init__(self, db: AsyncClient):
        super().__init__(db=db, model_class=UserSettings)

    # ユーザー設定を取得
    async def fetch(self, user_id: str) -> UserSettings:
        return await self.get(collection_path=COL_USERS, document_id=user_id)

    # ユーザー設定を保存・更新
    async def update(self, user_id: str, settings: UserSettings, batch: AsyncWriteBatch | None = None) -> None:
        # 更新時は未設定(unset)のものを除外し、設定したい差分だけをマージする
        data = settings.model_dump(by_alias=True, exclude_unset=True)
        data[FIELD_TOTAL_QC_COUNT] = Increment(settings.total_qc_count)

        await self.save(
            collection_path=COL_USERS,
            document_id=user_id,
            data=data,
            merge=True,
            batch=batch
        )

    # ユーザー設定の初期値をバッチ処理に追加
    def add_initial_data_to_batch(
            self, 
            batch: AsyncWriteBatch, 
            user_id: str, 
            user_name: str, 
            email: str
        ) -> AsyncDocumentReference:
        user_ref = self._get_doc_ref(collection_path=COL_USERS, document_id=user_id)
        save_data = UserSettings(email=email, user_name=user_name).model_dump(by_alias=True, exclude_none=True)

        batch.set(user_ref, save_data)
        return user_ref
    
    # is_qc_log_publicがTrueのユーザーのリストを取得
    async def get_public_log_users(self):
        users_ref = self.db.collection(COL_USERS)
        query = users_ref.where(filter=FieldFilter(FIELD_IS_QC_LOG_PUBLIC, '==', True))
    
        results = await self._fetch_and_validate(query, UserSettings)
        return [(u[0] ,u[1].user_name) for u in results]

    # --- ユーザー名からメールを引く (ログイン用) ---
    async def get_email_by_name(self, user_name: str) -> str | None:
        if user_name == "":
            return None
        doc_ref = self.db.collection(COL_USERNAME_MAP).document(user_name)
        doc = await doc_ref.get()
        if doc.exists:
            return doc.to_dict().get(FIELD_MAP_EMAIL)
        return None

    # --- ユーザー名が既に使用されているかチェック ---
    async def is_username_taken(self, user_name: str) -> bool:
        if user_name == "":
            return False
        doc_ref = self.db.collection(COL_USERNAME_MAP).document(user_name)
        doc = await doc_ref.get()
        return doc.exists

    # --- 新規登録時のマッピング追加 (バッチ用) ---
    def add_username_map_to_batch(
            self, 
            batch: AsyncWriteBatch, 
            user_name: str, 
            email: str
        ) -> None:
        map_ref = self.db.collection(COL_USERNAME_MAP).document(user_name)
        batch.set(map_ref, {FIELD_MAP_EMAIL: email})
        
    # --- ユーザー名変更 (アトミックなバッチ処理) ---
    async def rename_user(self, old_name: str, new_name: str, user_id: str):
        email = await self.get_email_by_name(old_name)

        batch = self.db.batch()
        
        # 旧名のマッピング削除
        batch.delete(self.db.collection(COL_USERNAME_MAP).document(old_name))
        
        # 新名のマッピング作成
        batch.set(self.db.collection(COL_USERNAME_MAP).document(new_name), {FIELD_MAP_EMAIL: email})
        
        # usersコレクション内の表示名も更新
        user_ref = self._get_doc_ref(collection_path=COL_USERS, document_id=user_id)
        batch.update(user_ref, {FIELD_USER_NAME: new_name})
        await batch.commit()