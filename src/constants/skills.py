import json
from.paths import ALL_SKILLS_DATA_PATH

# ALL_SKILLS_DATAのキー
SKILL_DATA_KEY = "skill_data"

with open(ALL_SKILLS_DATA_PATH, "r", encoding="utf-8") as f:
    # スキルをコスト毎に管理した辞書
    SKILLS_DATA = json.load(f)[SKILL_DATA_KEY]

# 全スキルを収納したリスト
SKILL_MASTER_LIST = [skill for skills in SKILLS_DATA.values() for skill in skills]