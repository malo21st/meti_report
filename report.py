# app.py　委託調査報告書（経済産業省）検索アプリ
import streamlit as st
import requests
import pandas as pd
import sqlite3

DB = "report.db"

@st.cache(allow_output_mutation=True)
def get_connection():
    return sqlite3.connect(DB, check_same_thread=False)

conn = get_connection()

def get_sql(name, key_word):
    if name == "報告書":
        lst_kw = ["report LIKE '%{}%'".format(kw) for kw in  key_word.split()]
    elif name == "委託先":
        lst_kw = ["auther LIKE '%{}%'".format(kw) for kw in  key_word.split()]
    SQL = "SELECT * FROM master WHERE " + " AND ".join(lst_kw)
    df = pd.read_sql(SQL, conn)
    json_data = df.to_json(orient='records')
    return json_data

def get_report(name, key_word):
    if key_word == "":
        data = '[{"msg" : "キーワードを入れて下さい。"}]'
    elif "%" in key_word:
        data = '[{"msg" : "キーワードに「％」は使えません。"}]'
    else:
        try:
            data = get_sql(name, key_word) #.json()
        except:
            data = '[{"msg" : "エラーが発生しました。"}]'
    if data == "[]":
        data = '[{"msg" : "該当する報告書はありません。"}]'
    df_out = pd.read_json(data)
    return df_out

st.title("委託調査報告書(経済産業省)検索サービス")

col1, col2 = st.beta_columns((1,4))
with col1:
    name = st.radio("項　目：", ("報告書", "委託先"))
with col2:
    key_word = st.text_input("キーワード：", value='')
    
df_report = get_report(name, key_word)
df_report = df_report.tail(20)

HEADER = '| 管理番号 | 　報　告　書　名 | 委託先 | 報告書 | データ |\n|:-:|:--|:-:|:-:|:-:|\n'

if df_report.columns[0] == "msg":
    st.markdown(df_report["msg"].values[0])
else:
    result = HEADER
    for i, r in df_report[::-1].iterrows():
        if r[8] == "":
            line = "|{}|{}|{}|[●]({})||\n".format(str(r[2]).zfill(6), r[3], r[4], r[7])
        else:
            line = "|{}|{}|{}|[●]({})|[●]({})|\n".format(str(r[2]).zfill(6), r[3], r[4], r[7], r[8])
        result += line
    st.markdown(result)
    
