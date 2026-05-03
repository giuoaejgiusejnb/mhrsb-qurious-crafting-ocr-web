from datetime import datetime, timezone
import httpx
import os
from typing import Any
from constants import GIST_URL

class Gist:
    def __init__(self):
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            test_path = r"C:\flet-app-web-files\github_token.txt"
            with open(test_path, "r", encoding="utf-8") as f:
                github_token = f.read().strip() 
                
        self.github_token = github_token
        self._client = None
        self.data = None        # JSON本文のキャッシュ
        self.headers = None     # ヘッダーのキャッシュ

    # 必要になったタイミングでクライアントを生成・返却する
    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient()
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()

    # 非同期でGistデータを取得し、ヘッダーをキャッシュする
    async def fetch_data(self) -> None:
        # キャッシュがあるなら何もしない
        if self.data is not None:
            return

        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json"
        }
        client = self._get_client()
        try:
            res = await client.get(GIST_URL, headers=headers)
            if res.status_code == 401:
                raise PermissionError("GitHubトークンが無効です。")
                
            res.raise_for_status() # 200番台以外なら例外を飛ばす
                
            # キャッシュを保存
            self.data = res.json()
            self.headers = res.headers
            return
        except Exception as e:
            raise e

    # gistの有効期限の残り日数を計算
    async def get_token_expiry_info(self) -> tuple[int, str]:
        await self.fetch_data()

        exp_str = self.headers.get("github-authentication-token-expiration")
        if exp_str is None:
            raise ValueError("有効期限の情報がヘッダーに見つかりませんでした。")

        exp_date = datetime.strptime(exp_str, "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        remaining_days = (exp_date - now).days
        
        return remaining_days, exp_str

    # ipynbファイルをアップロードする
    async def upload_ipynb(self, content: str, file_name:str) -> dict[str, Any]:
        await self.fetch_data()

        gist_id = "giuoaejgiusejnb"
        update_url = f"{GIST_URL}/{gist_id}"

        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json"
        }

        payload = {
            "public": True, 
            "files": {
                file_name: {
                    "content": content
                }
            }
        }

        client = self._get_client() # 既存のクライアントを再利用
        res = await client.post(GIST_URL, headers=headers, json=payload)
        res.raise_for_status() # 200番台以外なら例外を飛ばす

        # キャッシュを保存
        self.data = res.json()
        self.headers = res.headers
        
        return res.json()
