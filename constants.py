# constants.py

# --- ファイル設定 ---
DATA_FILE = 'dictionary_data.json'

# --- GUI デザイン設定 ---
FONT_SIZE = 14
BG_COLOR = 'black'
FG_COLOR = 'lime green'
FONT = ('Consolas', FONT_SIZE)

# --- 辞書フィールドの定義 ---
# 並び替えや検索で利用可能なキーと、GUI表示名のマッピング
DICTIONARY_FIELDS = {
    "term": "単語 (term)",
    "pronunciation": "発音 (pronunciation)",
    "definition": "意味・定義 (definition)",
    "part_of_speech": "品詞 (part_of_speech)",
    "example": "使用例 (example)"
}