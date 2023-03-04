library(tidyverse)
library(patchwork)


df_search_result <- read_csv("data/search/期間[2022年〜2022年]、競馬場[札幌、函館、福島、新潟、東京、中山、中京、京都、阪神、小倉]、クラス[G1、G2、G3].csv")
df_search_result


ids <- df_search_result[["レースID"]]
dfs <- list()
for (id in ids) {
    fname <- str_c("data/race/", id, "/レース結果.csv")
    df <- read_csv(fname, progress = FALSE, show_col_types = FALSE)
    suppressWarnings(df["着順"] <- as.double(df$着順)) # 「中」「除」をNAに
    df["通過"] <- as.character(df$通過)
    suppressWarnings(df["単勝"] <- as.double(df$単勝))
    df["レースID"] <- id
    dfs <- c(dfs, list(df))
}
df <- bind_rows(dfs) |>
    mutate(着順 = factor(着順)) |>
    select(レースID, everything())

df
# df |> View()

arrival_hist <- function(k) {
    df_freq <- df |>
        select(人気, 着順) |>
        filter(人気 == k) |>
        drop_na() |>
        count(着順, name = "頻度") |>
        mutate(
            相対度数 = 頻度 / sum(頻度),
            fill = (着順 == k),
            label = if_else(fill, sprintf("%.1f%%", 相対度数 * 100), ""),
        )
    df_freq
    ggplot(df_freq, aes(着順, 頻度, fill = fill, label = label)) +
        geom_bar(stat = "identity") +
        labs(title = str_c(k, "番人気")) +
        scale_fill_manual(values = c("TRUE" = "tomato", "FALSE" = "gray")) +
        geom_text(hjust = -0.3, vjust = 1.5) +
        theme(
            # text = element_text(family = "Noto Sans CJK JP"),
            text = element_text(family = "メイリオ"),
            panel.grid = element_blank(),
            legend.position = "none"
        )
}
# arrival_hist(1)
plist <- map(1:6, arrival_hist)
pp <- wrap_plots(plist, ncol = 2, nrow = 3, byrow = FALSE)
ggsave("figure/人気の的中率.svg", pp, width = 20, height = 20, units = "cm")
ggsave("figure/人気の的中率.pdf", pp, height = 20, width = 20, units = "cm", device = cairo_pdf)
