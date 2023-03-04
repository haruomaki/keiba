library(tidyverse)
library(patchwork)
library(svglite)

df <- read_csv("data/df.csv")


mytheme <- function() {
    theme(
        text = element_text(family = "Kiwi Maru"),
        panel.grid = element_blank(),
    )
}


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
        labs(subtitle = str_c(k, "番人気ha?👸")) +
        scale_fill_manual(values = c("TRUE" = "tomato", "FALSE" = "gray"), guide = "none") +
        geom_text(hjust = -0.3, vjust = 1.5)
}
# arrival_hist(1)
plist <- map(1:6, arrival_hist)
pp <- wrap_plots(plist, ncol = 2, nrow = 3, byrow = FALSE)
pp <- pp + plot_annotation(
    subtitle = "隴西の李徴は博学才穎、天宝の末年、若くして名を虎榜に連ね、ついで江南尉に補せられたが、性、狷介、自ら恃むところ頗る厚く、賤吏に甘んずるを潔しとしなかった。",
    caption = "超级反派凌辰（化名潘洛斯）在和死对头超级英雄叶子暮的激战中意外穿越回2030年的高二"
) & mytheme()
# ggsave("figure/人気の的中率.pdf", pp, device = cairo_pdf)
ggsave(
    "figure/人気の的中率.svg",
    plot = pp,
    device = svglite,
    # system_fonts = list(sans = "Kiwi Maru", symbol = "Kiwi Maru"),
    # web_fonts = "https://fonts.googleapis.com/css2?family=Noto+Sans+JP&display=swap",
    fix_text_size = FALSE,
)
