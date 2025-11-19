# gui_search_dictionary.py
import json 
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from constants import DATA_FILE, FONT_SIZE, BG_COLOR, FG_COLOR, FONT, DICTIONARY_FIELDS
# load_data はここでは使用せず、ファイル選択機能を残すため
# load_data_from_file_dialog と load_data_default を分ける

# グローバル変数として読み込んだ全データを保持
loaded_data = []
loaded_filepath = "" # 読み込んだファイルのパスを保持

# ウィジェットをグローバルで保持
result_text = None
search_entry = None
# search_scope_combo の代わりに search_scope_var を使用
search_scope_var = None 
confirm_text = None 

# --- 共通関数 ---
def update_confirmation_box(message, tag='normal'):
    """確認ボックスの内容を更新します。"""
    global confirm_text
    if confirm_text:
        confirm_text.config(state=tk.NORMAL)
        confirm_text.delete(1.0, tk.END)
        confirm_text.insert(tk.END, message, tag)
        confirm_text.config(state=tk.DISABLED)

# --- データ操作ロジック ---

def _load_data_logic(filepath, silent=False):
    """データ読み込みのコアロジック。"""
    global loaded_data, loaded_filepath
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        loaded_filepath = filepath
        if not silent:
            # confirm_text は setup_gui() で定義済み
            update_confirmation_box(
                f"✅ データが正常に読み込まれました。\nファイル: {os.path.basename(filepath)}\n項目数: {len(loaded_data)}件", 
                'success'
            )
        
        # 読み込み後、全データを結果表示エリアに出力
        search_and_display()
        return True
        
    except FileNotFoundError:
        if not silent:
            update_confirmation_box("❌ エラー: ファイルが見つかりません。", 'error')
        loaded_data = []
        loaded_filepath = ""
    except json.JSONDecodeError:
        if not silent:
            update_confirmation_box("❌ エラー: JSONファイルの形式が正しくありません。", 'error')
        loaded_data = []
        loaded_filepath = ""
    except Exception as e:
        if not silent:
            update_confirmation_box(f"❌ 予期せぬエラーが発生しました: {e}", 'error')
        loaded_data = []
        loaded_filepath = ""
    
    display_results([])
    return False

def load_data_default():
    """デフォルトのDATA_FILEからデータを読み込みを試みます。"""
    if os.path.exists(DATA_FILE):
        _load_data_logic(DATA_FILE, silent=True)
        if loaded_data:
            update_confirmation_box(
                f"✅ 起動時にデフォルトファイルが読み込まれました。\nファイル: {DATA_FILE}\n項目数: {len(loaded_data)}件", 
                'success'
            )
    else:
        # confirm_text は setup_gui() で定義済み
        update_confirmation_box(f"「データ読み込み」ボタンを押して、辞書データファイルを選択してください。（デフォルトファイル: {DATA_FILE} が見つかりませんでした）", 'normal')


def load_data_from_file_dialog():
    """ファイル選択ダイアログを表示し、JSONファイルを読み込みます。"""
    
    initialdir = os.path.dirname(loaded_filepath) if loaded_filepath else os.getcwd()

    filepath = filedialog.askopenfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        title="辞書データファイルを選択してください",
        initialdir=initialdir
    )
    
    if not filepath:
        update_confirmation_box("📂 ファイルの選択がキャンセルされました。", 'info')
        return

    _load_data_logic(filepath)


def search_and_display(event=None):
    """検索ボックスの入力と検索ジャンルに基づいてデータをフィルタリングし、結果を表示します。"""
    global search_scope_var # OptionMenuの変数を使用
    
    if not loaded_data:
        display_results([])
        return
        
    search_term = search_entry.get().lower().strip()
    # OptionMenu の StringVar から値を取得
    selected_scope_display = search_scope_var.get()
    
    # 検索ジャンルとデータキーのマッピング 
    scope_map = {v: k for k, v in DICTIONARY_FIELDS.items()} # DICTIONARY_FIELDSを反転
    
    if selected_scope_display == "全項目":
        search_keys = list(DICTIONARY_FIELDS.keys())
    else:
        search_keys = [scope_map.get(selected_scope_display)]

    # 検索キーワードがない場合は、全データを表示
    if not search_term:
        display_results(loaded_data)
        return
    
    results = []
    
    # フィルタリング検索
    for entry in loaded_data:
        # search_keys のNoneチェックを追加
        if not search_keys or search_keys[0] is None: 
             continue 

        found = False
        # 選択された検索キーのみをチェック
        for key in search_keys:
            if search_term in str(entry.get(key, '')).lower(): # str()で安全性を高める
                results.append(entry)
                found = True
                break
            
    display_results(results, search_term)


def display_results(results, search_term=""):
    """指定されたデータを結果表示エリアに整形して出力します。"""
    # result_text は setup_gui() で定義済みのため、AttributeErrorは発生しない
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    
    if not loaded_data and not results:
        result_text.insert(tk.END, "データを読み込んでください。", 'info')
    elif not results and search_term:
        result_text.insert(tk.END, f"キーワード「{search_term}」に一致する項目は見つかりませんでした。", 'info')
    elif not results and not search_term and loaded_data:
         result_text.insert(tk.END, "キーワードを入力するか、全項目が表示されています。", 'info')
    elif not results and not search_term and not loaded_data:
         result_text.insert(tk.END, "データが読み込まれていません。", 'info')
    else:
        # ヘッダー表示
        header_text = f"--- 表示項目数: {len(results)}件 (全{len(loaded_data)}件中) ---\n\n"
        
        result_text.insert(tk.END, header_text, 'header')
        
        # 各項目の整形出力
        for i, result in enumerate(results, 1):
            result_text.insert(tk.END, f"[{i}] 単語: {result.get('term', 'N/A')}\n", 'term')
            result_text.insert(tk.END, f"  発音: {result.get('pronunciation', 'N/A')}\n")
            result_text.insert(tk.END, f"  意味・定義: {result.get('definition', 'N/A')}\n")
            result_text.insert(tk.END, f"  品詞: {result.get('part_of_speech', 'N/A')}\n")
            result_text.insert(tk.END, f"  使用例: {result.get('example', 'N/A')}\n\n")

    result_text.config(state=tk.DISABLED)

# --- GUIの構築とデザイン設定 ---

def setup_gui():
    
    global search_entry, result_text, search_scope_var, confirm_text
    
    root = tk.Tk()
    root.title("辞書検索アプリケーション")
    
    root.configure(bg=BG_COLOR)
    
    # ttkスタイル設定（OptionMenuでは使用しないが、Entry/Textの見た目統一のためttkのベーススタイルは残す）
    style = ttk.Style()
    style.theme_use('clam')
    
    # ウィジェットの共通スタイル設定
    label_style = {'bg': BG_COLOR, 'fg': FG_COLOR, 'font': FONT}
    entry_style = {'bg': 'gray15', 'fg': FG_COLOR, 'insertbackground': FG_COLOR, 'font': FONT, 'relief': tk.SOLID, 'bd': 1}
    button_style = {'bg': 'darkgreen', 'fg': FG_COLOR, 'font': FONT, 'activebackground': 'green', 'activeforeground': 'white', 'relief': tk.RAISED, 'bd': 2}
    text_area_style = {'bg': 'gray15', 'fg': FG_COLOR, 'font': FONT, 'relief': tk.SUNKEN, 'bd': 2, 'insertbackground': FG_COLOR}
    
    # ★ OptionMenu 用の追加スタイル
    option_menu_style = {
        'bg': 'gray15',          # ボタンの背景色
        'fg': FG_COLOR,          # ボタンの文字色
        'font': FONT,
        'activebackground': 'darkgreen', # クリック時の背景色
        'activeforeground': 'white',    # クリック時の文字色
        'indicatoron': 0,        # ドロップダウンインジケータを非表示にする
        'width': 20,
        'relief': tk.SOLID,
        'bd': 1
    }
    
    main_frame = tk.Frame(root, bg=BG_COLOR, padx=10, pady=10)
    main_frame.pack(expand=True, fill=tk.BOTH)

    # 1. データ読み込みボタン
    load_button = tk.Button(main_frame, text="📂 データ読み込み (ファイル選択)", command=load_data_from_file_dialog, **button_style)
    load_button.pack(pady=(0, 10), fill=tk.X)

    # 2. 検索コントロールフレーム (OptionMenuとEntryを配置)
    control_frame = tk.Frame(main_frame, bg=BG_COLOR)
    control_frame.pack(pady=5, fill=tk.X)
    
    tk.Label(control_frame, text="🔍 検索ジャンル:", **label_style).pack(side=tk.LEFT, padx=(0, 5))

    # --- 検索ジャンル OptionMenu (ttk.Comboboxから変更) ---
    search_scopes = ["全項目"] + list(DICTIONARY_FIELDS.values())
    search_scope_var = tk.StringVar(root)
    search_scope_var.set(search_scopes[0]) # 初期値

    # OptionMenuの作成
    search_menu = tk.OptionMenu(control_frame, search_scope_var, *search_scopes, command=search_and_display)
    search_menu.config(**option_menu_style)
    
    # ★ ドロップダウンメニュー自体の見た目を設定
    menu = root.nametowidget(search_menu.menuname)
    menu.config(
        bg='gray15',             # ドロップダウンメニューの背景
        fg='lime green',         # ドロップダウンメニューの文字色
        font=FONT,
        activebackground='darkgreen', # 選択肢にマウスオーバーしたときの背景色
        activeforeground='white'      # 選択肢にマウスオーバーしたときの文字色
    )
    
    search_menu.pack(side=tk.LEFT, padx=(0, 10))

    # 検索入力ボックス
    search_entry = tk.Entry(control_frame, width=30, **entry_style)
    search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
    search_entry.bind('<KeyRelease>', search_and_display)

    # --- 確認ボックスの追加 (ロードメッセージ用) --- 
    tk.Label(main_frame, text="--- 状況 / メッセージ ---", **label_style).pack(pady=(10, 0), anchor='w')
    
    # confirm_text を定義
    confirm_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=3, 
                                            bg='gray15', fg='lime green', font=('Consolas', 12), 
                                            relief=tk.SUNKEN, bd=2, insertbackground='lime green', state=tk.DISABLED)
    confirm_text.pack(pady=5, fill=tk.X)
    
    # テキストの色付け設定 (確認ボックス用)
    confirm_text.tag_config('error', foreground='red')
    confirm_text.tag_config('info', foreground='gray')
    confirm_text.tag_config('success', foreground=FG_COLOR, font=(FONT[0], FONT_SIZE, 'bold'))
    
    
    # 3. 検索結果表示エリア
    tk.Label(main_frame, text="--- データ一覧 / 検索結果 ---", **label_style).pack(pady=(10, 0), anchor='w')
    
    # result_text を定義
    result_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=70, height=15, 
                                            state=tk.DISABLED, **text_area_style)
    result_text.pack(pady=10, fill=tk.BOTH, expand=True)

    # テキストの色付け設定 (結果表示エリア用)
    result_text.tag_config('header', foreground='yellow', font=(FONT[0], FONT[1], 'bold'))
    result_text.tag_config('term', foreground='light coral', font=(FONT[0], FONT[1], 'bold'))
    
    # 全てのウィジェット定義後に load_data_default() を呼び出す
    load_data_default() 

    root.mainloop()

if __name__ == "__main__":
    setup_gui()