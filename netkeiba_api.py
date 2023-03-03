#%%
from requests_cache import CachedSession
from bs4 import BeautifulSoup
import pandas as pd
from time import time, sleep
from dataclasses import dataclass

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


#%%
def replace_nbsp(s):
    return s.replace("\xa0", " ")  # &nbsp;


@dataclass
class Cellinfo:
    pos: int
    rowspan: int
    colspan: int
    value: str


# 参考: https://qiita.com/go_honn/items/ec96c2246229e4ee2ea6#コードまとめ
# アイデア: https://rooter.jp/web-crawling/parse-connected-table/
def parse_table(table, separator=""):
    rows = table.find_all("tr")

    mat = []  # 二次元リスト
    current_line_info = []
    next_line_info = []
    for row in rows:
        cells = row.find_all(("th", "td"))
        line = []
        x = 0

        def extend_line(cellinfo: Cellinfo):
            nonlocal line, x
            rs = cellinfo.rowspan
            cs = cellinfo.colspan
            if rs >= 2:
                cellinfo.rowspan = rs - 1
                next_line_info.append(cellinfo)
            for _ in range(cs):
                line.append(cellinfo.value)
                x += 1

        while current_line_info or cells:
            if current_line_info and current_line_info[0].pos == x:
                extend_line(current_line_info.pop(0))
            else:
                cell = cells.pop(0)
                cellinfo = Cellinfo(
                    x,
                    int(cell["rowspan"]) if "rowspan" in cell.attrs else 1,
                    int(cell["colspan"]) if "colspan" in cell.attrs else 1,
                    cell.get_text(separator, strip=True),
                    # separatorについて https://stackoverflow.com/a/48628074
                )
                extend_line(cellinfo)

        mat.append(line)
        current_line_info = next_line_info
        next_line_info = []

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
        df = parse_table(table, " " if k == "払い戻し" else "")  # 「払い戻し」の表だけは改行を保持
        if k in dfs:
            # summary属性が重複した場合はDataFrameを結合していく
            dfs[k] = pd.concat([dfs[k], df])
        else:
            dfs[k] = df

    return dfs


#%% テスト
soup = BeautifulSoup(open("test/ttt.html"), "html.parser")
parse_table(soup)


# %%
def get_horse(id):
    url = f"https://db.netkeiba.com/horse/{id}/"
    page = fetch_url(url)

    soup = BeautifulSoup(page.content, "html.parser")
    tables = soup.find_all("table")

    dfs = {table["summary"]: parse_table(table) for table in tables}

    return dfs


#%%
def get_search_result(url):
    page = fetch_url(url)
    soup = BeautifulSoup(page.content, "html.parser")
    headline = soup.find("div", class_="cate_bar").h2
    table = soup.find("table", summary="レース検索結果")

    # 検索条件を抽出
    query = headline.text[:-5]

    # レース名のハイパーリンクからレースIDを取得
    rows = table.find_all("tr")
    ids = [row.find_all("td")[4].a["href"][6:18] for row in rows[1:]]

    # 表をパースして冒頭にID列追加
    df = parse_table(table)
    df.insert(0, "レースID", ids)

    # 次のページが存在する場合、URLを取得して再帰的に実行
    # NOTE: 再帰だと無駄＆重いかも。for文もアリ
    nextbutton = soup.find("a", title="次")
    if nextbutton:
        next_url = nextbutton["href"]
        rest_df = get_search_result(next_url)[1]
        return (query, pd.concat([df, rest_df]).reset_index(drop=True))
    else:
        return (query, df)


#%%
# url = f"https://db.netkeiba.com/?pid=race_list&word=&start_year=2020&start_mon=none&end_year=2020&end_mon=none&kyori_min=&kyori_max=&sort=date&list=100&page=196"
# url = f"https://db.netkeiba.com/?pid=race_list&word=&start_year=2020&start_mon=none&end_year=2020&end_mon=none&kyori_min=&kyori_max=&sort=date&list=100&page=1"
url = "https://db.netkeiba.com/?pid=race_list&word=&start_year=2020&start_mon=none&end_year=2020&end_mon=none&grade%5B%5D=1&kyori_min=&kyori_max=&sort=date&list=100"
(query, df) = get_search_result(url)
df.to_csv(f"data/{query}.csv", index=False)


#%%
url = "https://db.netkeiba.com/?pid=race_list&word=&start_year=2020&start_mon=none&end_year=2020&end_mon=none&grade%5B%5D=1&kyori_min=&kyori_max=&sort=date&list=100"
page = fetch_url(url)
soup = BeautifulSoup(page.content, "html.parser")
table = soup.find("table", summary="レース検索結果")

rows = table.find_all("tr")
ids = [row.find_all("td")[4].a["href"][6:18] for row in rows[1:]]
df["レースID"] = ids
