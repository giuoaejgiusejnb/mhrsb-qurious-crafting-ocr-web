from .app import (
    APP_NAME,
    KEY_USER_NAME,
    ENDPOINT_QC_LOG,
    GUEST_PASSWORD,
    GUEST_USER_NAME
)
from .colab_constants import (
    PL_KEY_USER_NAME,
    PL_KEY_QC_COUNT
)
from .db_keys import (
    COL_USERS,
    COL_DESIRED_SKILLS_SETTINGS,
    COL_QC_LOGS,
    COL_PREV_OCR_SETTINGS,
    DOC_ID_CURRENT,
    FIELD_SKILLS,
    FIELD_SKILLS_SETTINGS_NAME,
    FIELD_INPUT_ZIP_FILE,
    FIELD_EXECUTED_AT,
    FIELD_QC_COUNT,
    FIELD_CREATED_AT_STR,
    FIELD_USER_ACTIVE
)
from .paths import (
    BASE_DIR,
    OCR_NOTEBOOK_PATH
)
from .routes import (
    LOGIN,
    ROUTE_OCR,
    ROUTE_SKILLS_SETTINGS,
    ROUTE_QC_LOG ,
    SETTINGS,
    HOME
)
from .skills import (
    SKILL_MASTER_LIST,
    SKILLS_DATA
)
from .urls import GIST_URL