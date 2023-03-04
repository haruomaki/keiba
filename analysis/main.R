library(tidyverse)
library(patchwork)

df <- read_csv("data/df.csv")


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
        labs(subtitle = str_c(k, "番人気")) +
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
ggsave("figure/人気の的中率.pdf", pp, device = cairo_pdf)
