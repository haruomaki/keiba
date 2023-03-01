#%%
import requests
from requests_cache import CachedSession
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from time import time, sleep

session = CachedSession()
delay = 10
last_fetched = 0


# キャッシュが無い場合、最低delay秒間の間を空けてダウンロードしてくる
def fetch_url(url):
    if not session.cache.has_url(url):
        print("キャッシュがありません")

        global last_fetched
        now = time()
        rest = delay - (now - last_fetched)
        if rest > 0:
            print("スリープ: %f秒" % rest)
            sleep(rest)

        last_fetched = time()

    return session.get(url)


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
# fetch_race(202001020405)


# #%%
# raw_tables = pd.read_html(f"https://db.netkeiba.com/horse/2018105027/")

# # NOTE: 「レース分析」と「注目馬 レース後の短評」が無いレースもあるが，その場合も今のところ問題無く動く
# tablekeys = [
#     "適性レビュー",  # FIXME: NaNのみ
#     "基本データ",
#     "血統",
#     "受賞歴",
#     "競走成績",
#     "みんなの適性レビュー",  # FIXME: NaNのみ
#     "netkeibaレーティング",
# ]
# dict(zip(tablekeys, raw_tables))
# # tables = dict(zip(tablekeys, raw_tables))
# # tables["払い戻し"] = pd.concat([tables.pop("払い戻し1"), tables.pop("払い戻し2")])


#%%
def replace_nbsp(s):
    return s.replace("\xa0", " ")  # &nbsp;


# 参考: https://qiita.com/go_honn/items/ec96c2246229e4ee2ea6#コードまとめ
def parse_table(table):
    rows = table.find_all("tr")

    mat = []  # 二次元リスト
    for row in rows:
        cells = row.find_all(("th", "td"))

        # <br>と"\n"をスペースに変換する https://stackoverflow.com/a/48628074
        line = [cell.get_text(" ", strip=True) for cell in cells]
        mat.append(line)

    # 先頭行にデータが無い(＝ヘッダ行である)場合，そこは行名と解釈する
    if not rows[0].find("td"):
        df = pd.DataFrame(mat[1:], columns=mat[0])
    else:
        df = pd.DataFrame(mat)

    return df


def get_race(id):
    url = f"https://db.netkeiba.com/race/{id}/"
    page = fetch_url(url)

    soup = BeautifulSoup(page.content, "html.parser")
    mainblock = soup.find("div", id="main")
    tables = soup.find_all("table")

    dfs = {
        "概要": pd.DataFrame(
            data=[
                id,
                mainblock.find("h1").text,
                replace_nbsp(mainblock.find("diary_snap_cut").span.text),
                replace_nbsp(mainblock.find("p", class_="smalltxt").text),
            ],
        )
    }

    for table in tables:
        k = table["summary"]  # tableタグのsummary属性をキーとする
        df = parse_table(table)
        if k in dfs:
            # summary属性が重複した場合はDataFrameを結合していく
            dfs[k] = pd.concat([dfs[k], df])
        else:
            dfs[k] = df

    # 列名の修正
    dfs["レース結果"].columns = [c.replace(" ", "") for c in dfs["レース結果"].columns]

    return dfs


id = 202206050811
id = 202205040911
dfs = get_race(id)


#%%
# ファイルに保存
dir = Path("data/%d" % dfs["概要"].iloc[0])
dir.mkdir(parents=True, exist_ok=True)
for (name, df) in dfs.items():
    df.to_csv(f"{dir}/{name}.csv", index=False)


#%%
id = 202206050811
url = f"https://db.netkeiba.com/race/{id}/"
page = requests.get(url)  # TODO: ダウンロード済みのキャッシュを用いる

soup = BeautifulSoup(page.content, "html.parser")
tables = soup.find_all("table")

# %%
mainblock = soup.find("div", id="main")

# %%
mainblock.find("h1").get_text()
clean(mainblock.find("diary_snap_cut").span.text)
clean(mainblock.find("p", class_="smalltxt").text)


#%%
session = requests_cache.CachedSession()
print(session.cache.urls)
