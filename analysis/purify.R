library(tidyverse)


df_search_result <- read_csv("data/search/期間[2022年〜2022年]、競馬場[札幌、函館、福島、新潟、東京、中山、中京、京都、阪神、小倉]、クラス[G1、G2、G3].csv")
df_search_result


ids <- df_search_result[["レースID"]]
dfs <- list()
for (id in ids) {
    fname <- str_c("data/race/", id, "/レース結果.csv")
    df <- read_csv(fname, progress = FALSE, show_col_types = FALSE)
    df["着順"] <- as.double(df$着順) # 「中」「除」をNAに
    df["通過"] <- as.character(df$通過)
    df["単勝"] <- as.double(df$単勝) # 「...」などをNAに
    df["レースID"] <- id
    dfs <- c(dfs, list(df))
}
df <- bind_rows(dfs) |>
    mutate(着順 = factor(着順)) |>
    select(レースID, everything())

df
# df |> View()

write_csv(df, "data/df.csv")
