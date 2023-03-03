library(tidyverse)


df_search_result <- read_csv("data/search/期間[2022年〜2022年]、競馬場[札幌、函館、福島、新潟、東京、中山、中京、京都、阪神、小倉]、クラス[G1、G2、G3].csv")
df_search_result


ids <- df_search_result[["レースID"]]
dfs <- list()
for (id in ids[1:10]) {
    fname <- str_c("data/race/", id, "/レース結果.csv")
    df <- read_csv(fname, progress = FALSE, col_types = "cddccdctcccdddccccccc")
    # df <- df |>
    #     mutate(着順 = if_else(着順 == "中", "-1", 着順))|>
    #     mutate(着順 = as.double(着順))
    df <- df |> add_column(レースID = as.character(id), .before = "着順")
    dfs <- c(dfs, list(df))
}
df <- bind_rows(dfs)

df$着順

bind_cols(dfs)
inner_join(dfs)

dfs[[3]] |> colnames()
bind_rows(list(df1, df2, df2))

df1 <- dfs[[1]]
df2 <- dfs[[2]]
df3 <- dfs[[3]]
bind_rows(df2, df3)
