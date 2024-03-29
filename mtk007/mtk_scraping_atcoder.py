# -*- coding: utf-8 -*-
"""mtk_scraping_atcoder.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ApSfP_JFrjngOGClDirDGrzAi7KiKUUq
"""

import requests
import json
import time
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import sys
import os

username = os.environ.get("ATC_USERNAME ")
password = os.environ.get("ATC_PASS ")

contest_id = "ahc003"
problem_id = "ahc003_a"

contest_start = datetime.datetime(2023, 9, 30, 12, 0, 0)
contest_end = datetime.datetime(2023, 10, 8, 19, 0, 0)

personal = {
    "r3yohei": ["ぱらぼろ", "運営", 703, 1373, 1583],
    "TGSR": ["troche", "バベル・アルトマン", 1309, 1358, 1852],
    "keroru": ["keroru", "チーム1", 1607, 1507, 1765],
    "edomondo": ["えどもんど", "運営", 920, 1352, 1679],
    "tebanya": ["てば", "チーム1", 1227, 283, 870],
    "Comavius": ["こま(@comavius)", "648feb86", 1313, 1660, 2395],
    "fujikawahiroaki": ["fujikawahiroaki", "バベル・アルトマン", 598, 1384, 1712],
    "brthyyjp": ["brthyyjp", "チーム1", 1702, 1357, 1640],
    "komori3": ["komori3", "バベル・アルトマン", 1847, 2412, 2853],
    "udon1206": ["udon1206", "648feb86", 2106, 2054, 2292],
    "motoshira": ["motoshira", "チーム1", 1528, 1383, 1794],
    "tabae326": ["tabae", "648feb86", 1929, 1868, 2142],
    "nephrologist": ["ねふ", "バベル・アルトマン", 1591, 1433, 1795],
    "hiroyuk1": ["hiro1729", "チーム1", 1206, 1126, 1599],
}

"""
for name in personal.keys():
  url = "https://atcoder.jp/users/" + name + "/history/json"
  json = requests.session().get(url).json()
  argo_rate = 0
  for data in json:
    ymd, hms_ = data["EndTime"].split("T")
    y,m,d = map(int,ymd.split("-"))
    h,min,sec = map(int,hms_.split("+")[0].split(":"))
    end_time = datetime.datetime(y,m,d,h,min,sec)
    if end_time > contest_start:
      break
    argo_rate = data["NewRating"]

  url = "https://atcoder.jp/users/" + name + "/history/json?contestType=heuristic"
  json = requests.session().get(url).json()
  heur_rate = 0
  heur_highest_perf = 0
  for data in json:
    ymd, hms_ = data["EndTime"].split("T")
    y,m,d = map(int,ymd.split("-"))
    h,min,sec = map(int,hms_.split("+")[0].split(":"))
    end_time = datetime.datetime(y,m,d,h,min,sec)
    if end_time > contest_start:
      break
    heur_rate = data["NewRating"]
    heur_highest_perf = max(heur_highest_perf, data["NewRating"])
  personal[name] += [argo_rate, heur_rate, heur_highest_perf]
"""

df = pd.DataFrame.from_dict(
    personal, orient="index", columns=["名前", "チーム名", "Aレート", "Hレート", "BestPerf"]
)
df.to_csv("personal_info.csv")

personal = pd.read_csv("personal_info.csv", index_col=0)
personal.head()

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
                records["name"].append(name)
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

# if not_in_record: print("バチャ期間中に提出があったが、参加者に登録されていない：", not_in_record)

df = pd.DataFrame(data=records)
df

df.to_csv("submissions.csv")
