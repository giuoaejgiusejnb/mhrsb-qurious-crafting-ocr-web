from pydantic import BaseModel
from google.cloud.firestore import (
    AsyncDocumentReference,
    AsyncClient,
    AsyncWriteBatch,
    Query
)
from typing import (
    TypeVar,
    Generic,
    Dict,
    Any
)

T = TypeVar("T", bound=BaseModel)

class BaseRepository(Generic[T]):
    def __init__(self, db: AsyncClient, model_class: type[T]):
        self.db = db
        self.model_class = model_class

    # コレクションやドキュメントパスのバリデーション
    @classmethod
    def _validate_path_segments(self, path: str) -> None:
        segments = path.split("/")
    
        if not all(segments):
            raise ValueError(f"Path contains empty segments: '{path}'")

    # ドキュメントのrefを得る
    def _get_doc_ref(self, collection_path: str, document_id: str) -> AsyncDocumentReference:
        self._validate_path_segments(f"{collection_path}/{document_id}")

        return self.db.collection(collection_path).document(document_id)

    # コレクションのrefを得る
    def _get_col_ref(self, collection_path: str) -> AsyncDocumentReference:
        self._validate_path_segments(collection_path)

        return self.db.collection(collection_path)

    # 指定した単一ドキュメントのフィールドを得る
    async def get(self, collection_path: str, document_id: str) -> T:
        doc_ref = self._get_doc_ref(collection_path, document_id)
        doc = await doc_ref.get()
        # ドキュメントが存在しない場合は、空の辞書を渡してデフォルト値でインスタンス化
        data = doc.to_dict() if doc.exists else {}
        return self.model_class.model_validate(data)

    # クエリを実行し、結果を指定されたPydanticモデルでパースしたものとドキュメントIDを，リストで返す
    async def _fetch_and_validate(self, query, model_class: type[T]) -> list[tuple[str, T]]:
        results = []
        async for doc in query.stream():
            results.append((doc.id, model_class.model_validate(doc.to_dict())))
        return results

    # 指定したコレクションパス内の全ドキュメントを取得する
    async def get_all(self, collection_path: str, order_by_field: str | None = None, descending: bool = False) -> list[tuple[str, T]]:
        col_ref = self._get_col_ref(collection_path)
        query = col_ref

        # ソート条件が指定されていれば order_by を追加
        if order_by_field:
            direction = Query.DESCENDING if descending else Query.ASCENDING
            query = query.order_by(order_by_field, direction=direction)

        return await self._fetch_and_validate(query=query, model_class=self.model_class)

    # 指定した単一ドキュメントのフィールドを保存する
    # increment したいときは，dataの中に increment(n) を入れる
    async def save(
        self, 
        collection_path: str, 
        document_id: str, 
        data: Dict[str, Any], 
        merge: bool = True,
        batch: AsyncWriteBatch | None = None
    ) -> None:
        doc_ref = self._get_doc_ref(collection_path, document_id)

        if batch is not None:
            batch.set(doc_ref, data, merge=merge)
        else:
            await doc_ref.set(data, merge=merge)

    # 指定したコレクションにランダムなIDのドキュメントを生成し，それにフィールド保存
    # 生成したランダムIDを返す
    async def add(
        self, 
        collection_path: str, 
        data: Dict[str, Any],
        batch: AsyncWriteBatch | None = None
    ) -> str:
        collection_ref = self._get_col_ref(collection_path)
        doc_ref = collection_ref.document()
        if batch is not None:
            batch.set(doc_ref, data)
        else:
            await doc_ref.set(data)
        return doc_ref.id

    # 指定したドキュメントを削除する
    async def delete_doc(self, collection_path: str, document_id: str, batch: AsyncWriteBatch | None = None) -> None:
        doc_ref = self._get_doc_ref(collection_path, document_id)
        if batch is not None:
            batch.delete(doc_ref)
        else:
            await doc_ref.delete()