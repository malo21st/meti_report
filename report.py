# app.py　委託調査報告書（経済産業省）検索アプリ
import streamlit as st
import pandas as pd
import sqlite3

DB = "report.db"

LIMIT = 50 # １度に表示するデータの数
SORT = -1  # -1：登録が新しい順，1：登録が古い順

@st.cache(allow_output_mutation=True)
def get_connection():
    return sqlite3.connect(DB, check_same_thread=False)

conn = get_connection()

def get_sql(name, key_word):
    if name == "報告書名":
        lst_kw = ["report LIKE '%{}%'".format(kw) for kw in  key_word.split()]
    elif name == "委託先":
        lst_kw = ["auther LIKE '%{}%'".format(kw) for kw in  key_word.split()]
    SQL = "SELECT * FROM master WHERE " + " AND ".join(lst_kw)
    df_sql = pd.read_sql(SQL, conn)
    return df_sql

def get_report(name, key_word):
    if key_word == "":
        msg, data = "項目を選択して、キーワードを入力して下さい。", 0
    elif "%" in key_word:
        msg, data = "キーワードに「％」は使えません。", -3
    else:
        try:
            data = get_sql(name, key_word)
            if len(data) > LIMIT:
                msg = "該当した報告書 {}件 から、登録の新しい {}件 を表示しました。".format(len(data), LIMIT)
            else:
                msg = "該当した報告書は、{}件 です。".format(len(data))
        except:
            msg, data = "エラーが発生しました。", -2
        if data.empty:
            msg, data = "該当する報告書はありません。", -1
    return msg, data

# タイトル
st.title("委託調査報告書 (経済産業省) 検索サービス")

# 項目とキーワードの入力
col1, col2 = st.beta_columns((1,5.5))
with col1:
    name = st.radio("項　目：", ("報告書名", "委託先"))
with col2:
    key_word = st.text_input("キーワード：", value='')
    
# 検索
msg, data = get_report(name, key_word)

# 検索結果（メッセージと表）
st.markdown(msg)

HEADER = '| 管理No. | 　報　告　書　名 | 委託先 | 報告書 | デ｜タ |\n|:-:|:--|:-:|:-:|:-:|\n'
if isinstance(data, pd.core.frame.DataFrame):
    result = HEADER
    df_report = data.tail(LIMIT)[::SORT]
    for _, r in df_report.iterrows():
        if r[8] == "":
            row = "|{}|{}|{}|[●]({})||\n".format(str(r[2]).zfill(6), r[3], r[4], r[7])
        else:
            row = "|{}|{}|{}|[●]({})|[●]({})|\n".format(str(r[2]).zfill(6), r[3], r[4], r[7], r[8])
        result += row
    st.markdown(result)
    
# 出典
st.markdown("出典：[委託調査報告書（METI/経済産業省）](https://www.meti.go.jp/topic/data/e90622aj.html)")    
