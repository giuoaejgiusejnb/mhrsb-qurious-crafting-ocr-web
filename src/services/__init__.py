from .firebase_auth import FirebaseAuth
from .firebase_db import FirebaseDB
from .gist import Gist
from .password_validator import PasswordValidator
from .auth_service import AuthService

shared_gist = Gist()
fb_auth = FirebaseAuth()
fb_db = FirebaseDB()