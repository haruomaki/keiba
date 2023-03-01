#%%
import netkeiba_api as nk
from pathlib import Path


#%%
id = 202206050811  # 有馬記念
id = 202205040911  # 天皇賞
dfs = nk.get_race(id)


#%%
# ファイルに保存
dir = Path("data/%d" % dfs["概要"].iloc[0])
dir.mkdir(parents=True, exist_ok=True)
for (name, df) in dfs.items():
    df.to_csv(f"{dir}/{name}.csv", index=False)
