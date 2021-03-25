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

def get_sql(key_word):
    lst_kw = ["report LIKE '%{}%'".format(kw) for kw in  key_word.split()]
    SQL = "SELECT * FROM master WHERE " + " AND ".join(lst_kw)
    df = pd.read_sql(SQL, conn)
    json_data = df.to_json(orient='records')
    return json_data

def get_report(key_word):
    if key_word == "":
        data = '[{"msg" : "キーワードを入れて下さい。"}]'
    elif "%" in key_word:
        data = '[{"msg" : "キーワードに「％」は使えません。"}]'
    else:
        try:
            data = get_sql(key_word) #.json()
        except:
            data = '[{"msg" : "エラーが発生しました。"}]'
    if data == "[]":
        data = '[{"msg" : "該当する報告書はありません。"}]'
    df_out = pd.read_json(data)
    return df_out

st.title("委託調査報告書(経済産業省)検索サービス")

key_word = st.text_input("キーワード：", value='')
df_api = get_report(key_word)
df_api = df_api.tail(20)

HEADER = '| 管理番号 | 　　　報　告　書　名 | 報告書 | データ |\n|:-:|:--|:-:|:-:|\n'

if df_api.columns[0] == "msg":
    st.markdown(df_api["msg"].values[0])
else:
    result = HEADER
    for i, r in df_api[::-1].iterrows():
        if r[8] == "":
            line = "|{}|{}|[●]({})||\n".format(str(r[2]).zfill(6), r[3], r[7])
        else:
            line = "|{}|{}|[●]({})|[●]({})|\n".format(str(r[2]).zfill(6), r[3], r[7], r[8])
        result += line
    st.markdown(result)
    