#%%
import netkeiba_api as nk


#%%
id = 202206050811  # 有馬記念
# id = 202205040911  # 天皇賞
dfs = nk.get_race(id)


#%% 馬情報
id = 2002100877  # ヴァーミリアン
dfs = nk.get_horse(id)


#%% レースの検索
url = "https://db.netkeiba.com/?pid=race_list&word=&start_year=2022&start_mon=none&end_year=2022&end_mon=none&jyo%5B%5D=01&jyo%5B%5D=02&jyo%5B%5D=03&jyo%5B%5D=04&jyo%5B%5D=05&jyo%5B%5D=06&jyo%5B%5D=07&jyo%5B%5D=08&jyo%5B%5D=09&jyo%5B%5D=10&grade%5B%5D=1&grade%5B%5D=2&grade%5B%5D=3&kyori_min=&kyori_max=&sort=date&list=100"
(query, df_search_result) = nk.get_search_result(url)


#%% 検索結果の各レースの情報を取得
for i, id in enumerate(df_search_result["レースID"]):
    id = int(id)
    print(f"[{i}/{len(df_search_result)}] get_race: {id}")
    nk.get_race(id)


#%%
# # n番人気が本当にn着になったかどうか調べる
# id = 202206050911
# df = nk.get_race(id)["レース結果"]
# # def was_exact(n):

nk.get_race(202206050710)
