from repositories import RepositoryManager

class AuthService:
    def __init__(self, repos:RepositoryManager):
        self.db = repos.db
        self.user_repo = repos.user_settings_repo

    # ユーザー新規登録時のDB初期化
    async def register_new_user(self, user_id: str, user_name:str, email: str):
        # 今後，別リポジトリを使った初期値追加を行うかもしれないので，いったんバッチ化
        batch = self.db.batch()

        # ユーザー基本情報の追加
        self.user_repo.add_initial_data_to_batch(user_id=user_id, user_name=user_name, email=email, batch=batch)
        # username_mapにユーザーネームとemail追加
        self.user_repo.add_username_map_to_batch(batch=batch, user_name=user_name, email=email)

        # 全てを確定させる
        await batch.commit()
