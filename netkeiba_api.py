# 2つの変数の和を計算する自作関数
def my_sum(x, y):
    z = x + y
    return z


# 2つの変数の差を計算する自作関数
def my_dif(x, y):
    z = x - y
    return z


#%%
import pandas as pd

# %%
id = 202206050811
raw_tables = pd.read_html(f"https://db.netkeiba.com/race/{id}/")

# %%
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

# %%
払い戻し1
pd.concat([払い戻し1, 払い戻し2])


#%%
def get_race(id: int):
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


# %%
# get_race(202001020405)


#%%
raw_tables = pd.read_html(f"https://db.netkeiba.com/horse/2018105027/")

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
dict(zip(tablekeys, raw_tables))
# tables = dict(zip(tablekeys, raw_tables))
# tables["払い戻し"] = pd.concat([tables.pop("払い戻し1"), tables.pop("払い戻し2")])
