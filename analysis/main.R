source("~/R/lib.R")

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
        scale_fill_manual(values = c("TRUE" = "tomato", "FALSE" = "gray"), guide = "none") +
        geom_text(hjust = -0.3, vjust = 1.5, family = myfont)
}

plist <- map(1:6, arrival_hist)
pp <- wrap_plots(plist, ncol = 2, nrow = 3, byrow = FALSE) +
    plot_annotation(
        subtitle = "期間[2022年〜2022年]\n競馬場[札幌、函館、福島、新潟、東京、中山、中京、京都、阪神、小倉]\nクラス[G1、G2、G3]"
    ) & mytheme()
pp

# ggsave("figure/人気の的中率.pdf", pp, device = cairo_pdf)
pp |> ggsave_svg("figure/人気の的中率.svg")
