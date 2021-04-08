# report.py　委託調査報告書（経済産業省）検索アプリ
import streamlit as st
import pandas as pd
import sqlite3
    
DB = "report.db"

LIMIT = 50 # 一度に表示する出力結果の数
SORT = "DESC" # "DESC"：登録が新しい順，""：登録が古い順
DIC_ITEM = {"報告書名":"report", "委託先":"auther"}
DF_EMPTY = pd.DataFrame() # 空のデータフレーム

# RDBとのコネクションを確立
@st.cache(allow_output_mutation=True)
def get_connection():
    return sqlite3.connect(DB, check_same_thread=False)
conn = get_connection()

# RDBをSQLで検索、検索結果を返す（空白で複数キーワード検索可能）
def get_sql(item: str, key_word: str):
    lst_kw = [f"report LIKE '%{ DIC_ITEM[item] }%'" for kw in key_word.split()]
    SQL = "SELECT * FROM master WHERE " + " AND ".join(lst_kw) + "ORDER BY id " + SORT
    df_sql = pd.read_sql(SQL, conn)
    return df_sql

# 項目名とキーワードで検索し、メッセージと検索結果を返す
def get_report(item: str, key_word: str):
    if key_word == "":
        msg, df_data = "項目を選択して、キーワードを入力して下さい。", DF_EMPTY
    elif "%" in key_word:
        msg, df_data = "キーワードに「％」は使えません。", DF_EMPTY
    else:
        try:
            df_data = get_sql(item, key_word)
            if len(df_data) > LIMIT:
                msg = f"該当した報告書 { len(df_data) }件 から、登録の新しい { LIMIT }件 を表示しました。"
            else:
                msg = f"該当した報告書は、{ len(df_data) }件 です。"
        except:
            msg, df_data = "エラーが発生しました。", DF_EMPTY
        if df_data.empty:
            msg, df_data = "該当する報告書はありません。", DF_EMPTY
    return msg, df_data

#【表示】タイトル
st.title("委託調査報告書 (経済産業省) 検索サービス")

#【入力】項目とキーワード
col1, col2 = st.beta_columns((1, 5.5))
with col1:
    item = st.radio("項　目：", tuple(DIC_ITEM))
with col2:
    key_word = st.text_input("キーワード：", value='')
    
#【処理】検索
msg, df_data = get_report(item, key_word)

#【出力】検索結果
## メッセージ
st.markdown(f"**{ msg }**")
## 表　df_dataのカラム名
## 'id', 'fy', 'fy_jp', 'num', 'report', 'auther', 'dept', 'capa', 'pdf', 'data', 'pdf_YN', 'data_YN'
if df_data.size: # 0：検索結果がない場合，1以上：検索結果がある場合
    result = '| 管理No. | 　報　告　書　名 | 委託先 | 報告書 | デ｜タ |\n|:-:|:--|:-:|:-:|:-:|\n'
    df_report = df_data.head(LIMIT) # 出力数の制限
    for _, r in df_report.iterrows():
        # 「管理No.（num）」「報告書名（report）」「委託先（auther）」列の処理
        row = f"|{ r['num'].zfill(6) }|{ r['report'] }|{ r['auther'] }|"
        #「報告書（pdf）」列の処理
        if (r['pdf'] != ""):
            if r['pdf_YN']: # リンクあり
                row += f"[●]({ r['pdf'] })|"
            else: # リンクなし
                row += f"[×]({ r['pdf'] })|"
        else: # 報告書（pdf）なし
                row += "|"
        #「データ（data）」列の処理
        if (r['data'] != ""):
            if r['data_YN']: # リンクあり
                row += f"[●]({ r['data'] })|\n"
            else: # リンクなし
                row += f"[×]({ r['data'] })|\n"
        else: # dataなし
            row += "|\n"    
        result += row
    #【出力】検索結果
    st.markdown(result)
    st.markdown("【凡例】●：リンク，×：リンク切れ")
    
#【表示】出典
st.markdown("出典：[委託調査報告書（METI/経済産業省）](https://www.meti.go.jp/topic/data/e90622aj.html)")
