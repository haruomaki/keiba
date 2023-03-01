#%%
import pandas as pd


#%%
def fetch_race(id: int):
    raw_tables = pd.read_html(f"https://db.netkeiba.com/race/{id}/")

    # NOTE: 「レース分析」と「注目馬 レース後の短評」が無いレースもあるが，その場合も今のところ問題無く動く
    tablekeys = [
        "結果/払戻",
        "払い戻し1",
        "払い戻し2",
        "馬場情報",
        "コーナー通過順位",
        "ラップタイム",
        "レース分析",
        "注目馬 レース後の短評",
    ]
    tables = dict(zip(tablekeys, raw_tables))
    tables["払い戻し"] = pd.concat([tables.pop("払い戻し1"), tables.pop("払い戻し2")])

    return tables


# https://walkintheforest.net/r-keiba-scraping/#参考
sites = ["札幌", "函館", "福島", "新潟", "東京", "中山", "中京", "京都", "阪神", "小倉"]


def get_id(年: int, 回: int, 場所: str, 日目: int, レース: int):
    id = "%d%02d%02d%02d%02d" % (年, sites.index(場所) + 1, 回, 日目, レース)
    return int(id)


def get_raceinfo(id: int):
    id = str(id)
    年 = int(id[0:4])
    回 = int(id[6:8])
    場所 = sites[int(id[4:6]) - 1]
    日目 = int(id[8:10])
    レース = int(id[10:12])
    return (年, 回, 場所, 日目, レース)


# %%
fetch_race(202001020405)


#%%
raw_tables = pd.read_html(f"https://db.netkeiba.com/horse/2018105027/")

# NOTE: 「レース分析」と「注目馬 レース後の短評」が無いレースもあるが，その場合も今のところ問題無く動く
tablekeys = [
    "適性レビュー",  # FIXME: NaNのみ
    "基本データ",
    "血統",
    "受賞歴",
    "競走成績",
    "みんなの適性レビュー",  # FIXME: NaNのみ
    "netkeibaレーティング",
]
dict(zip(tablekeys, raw_tables))
# tables = dict(zip(tablekeys, raw_tables))
# tables["払い戻し"] = pd.concat([tables.pop("払い戻し1"), tables.pop("払い戻し2")])


#%%
import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd

# url = "https://en.wikipedia.org/wiki/Transistor_count"
# page = requests.get(url)
id = 202206050811
url = f"https://db.netkeiba.com/race/{id}/"
page = requests.get(url)

soup = BeautifulSoup(page.content, "html.parser")
# table = soup.find("table", {"class": "wikitable"}).tbody
tables = soup.find_all("table")


# def replace


#%%
# 参考: https://qiita.com/go_honn/items/ec96c2246229e4ee2ea6#コードまとめ
def parse_table(table):
    rows = table.find_all("tr")

    df = pd.DataFrame()

    for row in rows:
        cells = row.find_all(("th", "td"))

        # <br>と"\n"をスペースに変換する https://stackoverflow.com/a/48628074
        values = [cell.get_text(" ").replace("\n", " ") for cell in cells]
        df = df.append(pd.Series(values), ignore_index=True)
        # values = []
        # for cell in cells:
        #     # cell.br.replace_with("\n")
        #     values.append(cell.get_text(" "))
        # df = df.append(pd.Series(values), ignore_index=True)

    # 先頭行にデータが無い(＝ヘッダ行である)場合，そこは行名と解釈する
    if not rows[0].find("td"):
        df.columns = df.iloc[0]
        df.drop(0, inplace=True)

    return df


dfs = {}
for table in tables:
    dfkey = table["summary"]
    df = parse_table(table)
    # df = pd.read_html(table.prettify())[0]
    dfs |= {dfkey: df}


#%%
# ファイルに保存
for (name, df) in dfs.items():
    df.to_csv(f"{name}.csv", index=False)

#%%
tables[0]["summary"]