from __future__ import annotations
from dataclasses import dataclass
import os
import json
import httpx

# --- 認証データのクラス ---
@dataclass
class AuthResponse:
    uid: str
    email: str
    id_token: str

    @classmethod
    def from_dict(cls, data: dict) -> AuthResponse:
        # APIのレスポンス（辞書）から、必要な分だけ抜き出してクラスを作る
        return cls(
            uid=data.get("localId"),
            email=data.get("email"),
            id_token=data.get("idToken")
        )

# ---認証データを扱うクラス ---
class FirebaseAuth:
    def __init__(self):
        config_json = os.getenv("FIREBASE_CLIENT_CONFIG")
        if config_json:
            config = json.loads(config_json)
        else:
            client_config_path = r"C:\flet-app-web-files\firebase_client_config.json"
            with open(client_config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

        self.api_key = config.get("apiKey")
        self.base_url = "https://identitytoolkit.googleapis.com/v1/accounts"
        self._client = None

    # 必要になったタイミングでクライアントを生成・返却する
    def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient()
        return self._client

    # アプリ終了時に呼び出して接続を閉じる
    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # 内部共通リクエストメソッド
    async def _send_request(self, endpoint: str, payload: dict) -> AuthResponse:
        client = self.get_client()
        url = f"{self.base_url}:{endpoint}?key={self.api_key}"

        try:
            res = await client.post(url, json=payload)
            data = res.json()
            
            if res.status_code != 200:
                error_code = data.get("error", {}).get("message", "UNKNOWN_ERROR")
                raise ValueError(error_code) 
            
            return AuthResponse.from_dict(data)
        except httpx.RequestError as exc:
            raise ConnectionError(f"通信エラーが発生しました: {exc}")

    async def login(self, email: str, password: str) -> AuthResponse:
        payload = {"email": email, "password": password, "returnSecureToken": True}
        return await self._send_request("signInWithPassword", payload)

    async def register(self, email: str, password: str) -> AuthResponse:
        payload = {"email": email, "password": password, "returnSecureToken": True}
        return await self._send_request("signUp", payload)

    # id_tokenはログイン時に渡されるトークン
    async def change_password(self, id_token: str, new_password: str) -> AuthResponse:
        payload = {"idToken": id_token, "password": new_password,"returnSecureToken": True}
        return await self._send_request("update", payload)

    # 現在のパスワードで再ログインし、成功したら新しいパスワードに更新
    async def reauthenticate_and_change_password(self, email: str, current_password: str, new_password: str) -> AuthResponse:
        # 現在の認証情報でログイン
        auth_data = await self.login(email, current_password)
        id_token = auth_data.id_token

        # 取得したトークンを使ってパスワードを更新
        return await self.change_password(id_token, new_password)