import firebase_admin
import json
import os
from firebase_admin import credentials
from google.cloud import firestore
from google.oauth2 import service_account

class FirebaseDB:
    def __init__(self):
        cert_json = os.getenv("FIREBASE_KEY")

        if cert_json:
            info = json.loads(cert_json)
            cred = credentials.Certificate(info)
        else:
            test_path = r"C:\flet-app-web-files\flet-app-mhrsb-ocr-firebase-adminsdk-fbsvc-358310d152.json"
            cred = credentials.Certificate(test_path)
            with open(test_path) as f:
                info = json.load(f)

        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        google_cred = service_account.Credentials.from_service_account_info(info)
        
        self.db = firestore.AsyncClient(
            project=info.get("project_id"),
            credentials=google_cred
        )
        
    async def close(self):
        if self.db:
            await self.db.close()