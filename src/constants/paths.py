# パスをまとめるモジュール

import os

# srcフォルダのパス
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# すべてのスキルが書かれたJSONファイルへのパス
ALL_SKILLS_DATA_PATH  = os.path.join(BASE_DIR, "assets", "all_skills.json")

# OCRを行うipynbファイルへのパス
OCR_NOTEBOOK_PATH = os.path.join(BASE_DIR, "assets", "qurious_crafting.ipynb")
