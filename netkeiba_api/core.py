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
# get_race(202001020405)


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
