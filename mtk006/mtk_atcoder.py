# -*- coding: utf-8 -*-
import requests
import json
import time
import lxml
import html5lib
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import sys
import os
import plotly.express as px
import plotly.graph_objects as go

username = os.environ.get("ATC_USERNAME")
password = os.environ.get("ATC_PASS")

contest_id = "ahc020"
problem_id = "ahc020_a"

contest_start = datetime.datetime(2023, 6, 11, 15, 0, 0)
contest_end = datetime.datetime(2023, 6, 18, 19, 0, 0)

personal = {
    "sou31415": ["RuSwiftive", "Code Novices", 429, 0, 0],
    "Rillaboom2020": ["MM", "Code Novices", 1425, 0, 0],
    "ayatosuzuki": ["プリン", "Code Novices", 948, 0, 0],
    "jamuojisan": ["maeda", "summery bumblebee", 752, 915, 1574],
    "brthyyjp": ["brthyyjp", "summery bumblebee", 1714, 1253, 1640],
    "june193": ["六月", "summery bumblebee", 1020, 1316, 1669],
    "motoshira": ["motoshira", "summery bumblebee", 1395, 1344, 1794],
    "nephrologist": ["ねふ", "四代目バベルクライマーズ", 1566, 1420, 1795],
    "keroru": ["keroru", "四代目バベルクライマーズ", 1607, 1401, 1682],
    "fujikawahiroaki": ["fujikawahiroaki", "四代目バベルクライマーズ", 532, 1342, 1712],
    "2bit": ["2bit", "四代目バベルクライマーズ", 1196, 710, 1003],
    "michirakara": ["michirakara", "四代目バベルクライマーズ", 1164, 930, 1287],
    "PrussianBlue": ["PrussianBlue", "こたえはポンプ", 2118, 1398, 1876],
    "tabae326": ["tabae", "こたえはポンプ", 2014, 1705, 2128],
    "komori3": ["komori3", "こたえはポンプ", 1722, 2399, 2853],
    "ponjuice": ["ぽんじゅーす", "こたえはポンプ", 2132, 2063, 2413],
    "C7BMkOO7Qbmcwck7": ["EvbCFfp1XB", "こたえはポンプ", 1285, 2231, 2732],
    "r3yohei": ["ぱらぼろ", "運営", 662, 1327, 1583],
    "ainem": ["ainem", "運営", 941, 1441, 1801],
    "edomondo": ["えどもんど", "運営", 921, 1110, 1679],
}

personal = pd.DataFrame.from_dict(
    personal, orient="index", columns=["名前", "チーム名", "Aレート", "Hレート", "BestPerf"]
)

# User Agentの設定の設定
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4.1 Safari/605.1.15"
header = {"User-Agent": user_agent}

login_url = "https://atcoder.jp/login?continue=https%3A%2F%2Fatcoder.jp%2F"
session = requests.session()
response = session.get(login_url, headers=header)

# BeautifulSoupオブジェクト作成(token取得の為)
bs = BeautifulSoup(response.text, "html.parser")
# tokenの取得
csrf_token = bs.find(attrs={"name": "csrf_token"}).get("value")

login_data = {
    "username": username,
    "password": password,
    "csrf_token": csrf_token,
}

# cookieの取得
response_cookie = response.cookies

login = session.post(login_url, data=login_data, cookies=response_cookie)
time.sleep(2)  # 少し時間を置いてみる


def make_datetime(s: str) -> datetime:
    ymd, hms = s.split(" ")
    year, month, day = map(int, ymd.split("-"))
    hour, minute, second = hms.split(":")
    second = int(second.split("+")[0])

    res = datetime.datetime(
        year=year,
        month=month,
        day=day,
        hour=int(hour),
        minute=int(minute),
        second=int(second),
    )

    return res


records = {
    "name": [],
    "display_name": [],
    "team": [],
    "lang": [],
    "score": [],
    "submit": [],
    "elapsed_time": [],
    # "argo_rate": [],
    # "heuristic_rate": [],
    # "performance": []
}

submission_url = (
    "https://atcoder.jp/contests/"
    + contest_id
    + "/submissions?desc=true&f.LanguageName=&f.Status=AC&f.Task="
    + problem_id
    + "&f.User=&orderBy=created&page="
)
page = 1

not_in_record = set()

while True:
    submissions = session.get(submission_url + str(page))
    soup = BeautifulSoup(submissions.text, "html5lib")
    tr = soup.select("tbody > tr")
    if len(tr) == 0:
        break
    for row in tr:
        submit = make_datetime(row.contents[1].text)
        if contest_start < submit < contest_end:
            name = (
                row.contents[5].text.rstrip()
                if " " in row.contents[5].text
                else row.contents[5].text
            )
            lang = row.contents[7].text
            score = int(row.find(name="td", attrs={"class": "submission-score"}).text)
            elapsed_time = row.contents[14].text
            if name in personal.index:
                tname = personal.at[name, "チーム名"]
                dname = personal.at[name, "名前"]
                records["name"].append(name)
                records["display_name"].append(dname)
                records["team"].append(tname)
                records["lang"].append(lang)
                records["score"].append(score)
                records["submit"].append(submit)
                records["elapsed_time"].append(elapsed_time)
                # records["argo_rate"].append(a_rate)
                # records["heuristic_rate"].append(h_rate)
                # records["performance"].append(perf)
            else:
                not_in_record.add(name)
        elif submit < contest_start:
            break
    else:
        page += 1
        continue
    break

if not_in_record:
    print("バチャ期間中に提出があったが、参加者に登録されていない：", not_in_record)

df = pd.DataFrame(data=records)
df.columns = ["名前", "表示名", "チーム名", "言語", "スコア", "提出日時", "実行時間"]

df_individual = df.loc[df.groupby("名前")["スコア"].idxmax()]
df_individual = df_individual.drop(columns=["言語", "提出日時", "実行時間"])
df_individual.sort_values("スコア", ascending=False, inplace=True)
df_individual.reset_index(inplace=True, drop=True)
df_individual["順位"] = range(1, len(df_individual) + 1)
df_individual = df_individual.reindex(columns=["順位", "名前", "チーム名", "スコア"])
df_individual.head()

"""## チームランキング"""

df_team = df.loc[df.groupby("チーム名")["スコア"].idxmax()]
df_team = df_team.drop(columns=["言語", "提出日時", "実行時間"])
df_team = df_team.reindex(columns=["チーム名", "名前", "スコア"])
df_team.sort_values("スコア", ascending=False, inplace=True)
df_team.reset_index(inplace=True, drop=True)
df_team["順位"] = range(1, len(df_team) + 1)
df_team = df_team.reindex(columns=["順位", "チーム名", "名前", "スコア"])
df_team.head()

"""# グラフ作成

1.   縦軸：スコア、横軸：時間の折れ線グラフ（個人）
2.   縦軸：スコア、横軸：時間の折れ線グラフ（チーム）
3.   言語ごとのランキング
4.   スコアとレートの相関関係（アルゴ、ヒューリスティック）



"""

df_line_indv = df.sort_values("提出日時", ascending=True)
df_line_indv["スコア"] = df_line_indv.groupby("名前")["スコア"].cummax()

fig_individual = px.line(df_line_indv, x="提出日時", y="スコア", color="名前")
fig_individual.show()

df_line_team = df.sort_values("提出日時", ascending=True)
df_line_team["スコア"] = df_line_team.groupby("チーム名")["スコア"].cummax()

fig_team = px.line(df_line_team, x="提出日時", y="スコア", color="チーム名")
fig_team.show()

df_lang = (
    df.replace("C++ (GCC 9.2.1)", "C++")
    .replace("C++ (Clang 10.0.0)", "C++")
    .replace("C++14", "C++")
    .replace("C# (.NET Core 3.1.201)", "C#")
    .replace("PyPy3 (7.3.0)", "Python")
    .replace("Python (3.8.2)", "Python")
    .replace("Rust (1.42.0)", "Rust")
    .replace("Crystal (0.33.0)", "Crystal")
    .replace("D (DMD 2.091.0)", "D")
    .replace("D (LDC 1.20.1)", "D")
    .replace("Common Lisp (SBCL 2.0.3)", "Common Lisp")
    .replace("Java (OpenJDK 11.0.6)", "Java")
)
df_lang = df_lang.loc[df_lang.groupby("名前")["スコア"].idxmax()]

fig_lang = px.box(df_lang, x="言語", y="スコア", points="all")
fig_lang.show()

"""df_rate = df.loc[df.groupby("名前")["スコア"].idxmax()]

layout = go.Layout(
    xaxis = dict(title="レート", range = [0,3001], dtick=500),   # rangeで範囲、dtick で区間幅
    yaxis = dict(title="スコア（対数）"))

fig_rate = go.Figure(layout = layout)
fig_rate.add_trace(go.Scatter(x = df_rate["アルゴレート"],
                              y = df_rate["スコア"],
                              mode = "markers",
                              name = "アルゴ"))
fig_rate.add_trace(go.Scatter(x = df_rate["ヒューリスティックレート"],
                              y = df_rate["スコア"],
                              mode = "markers",
                              name = "ヒューリスティック"))
fig_rate.update_yaxes(type="log")
fig_rate.show()

## HTMLで書き出し
"""

fig_individual.write_html("docs/mtk006/line_individual.html")
fig_team.write_html("docs/mtk006/line_team.html")
# fig_lang.write_html("docs/mtk006/box_lang.html")
# fig_rate.write_html("docs/mtk006/scatter_rate.html")

table_individual = df_individual.to_html(
    border=0,
    classes=["table", "table-striped", "table-hover"],
    index=False,
    justify="left",
)

table_team = df_team.to_html(
    border=0,
    classes=["table", "table-striped", "table-hover"],
    index=False,
    justify="left",
)

filepath = "docs/mtk006/mtk006.html"
soup = BeautifulSoup(open(filepath), "html.parser")
for i, table in enumerate(soup.select(".card-body table")):
    if i == 0:
        table.replace_with(table_team)
    elif i == 0:
        table.replace_with(table_individual)

with open(filepath, mode="w") as f:
    f.write(str(soup))
