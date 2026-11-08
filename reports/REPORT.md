# Backtest-Report: B (Long-only)

Testzeitraum 2026-01-01 bis 2026-11-06 (310 Tage), Walk-Forward des Engines, 10 MW je Viertelstunde, Kosten 1,5 €/MWh Round Trip, Exit ID-AEP. Stand 2026-11-08.

| | **B: Long-only** | A: Engine | immer long |
|---|---:|---:|---:|
| Netto-PnL € | +167 138 | +166 849 | +243 809 |
| Volumen MWh | 25 140 | 38 720 | 74 400 |
| €/MWh | +6,65 | +4,31 | +3,28 |
| Sharpe p. a. (täglich) | 3,02 | 2,39 | 2,22 |
| t (HAC, täglich) | 2,75 | 2,26 | 1,74 |
| Max. Drawdown € | -23 563 | -67 590 | -129 624 |
| Schlechtester Tag € | -19 759 | -31 591 | -48 138 |
| Break-even-Slippage €/MWh | 7,7 | 5,3 | 4,3 |
| Spread gekappt ±200 €/MWh: PnL € (t) | +97 197 (2,70) | +159 428 (3,69) | +53 709 (0,57) |
| Spread gekappt ±100 €/MWh: PnL € (t) | +52 392 (1,64) | +123 921 (3,39) | -39 749 (-0,49) |
| ohne die 10 besten Tage € | +29 422 | +24 262 | +20 738 |
| die 10 besten Viertelstunden € | +56 610 | +56 610 | +77 833 |
| Sharpe 1. / 2. Hälfte | 0,43 / 4,60 | 1,23 / 3,17 | 0,22 / 4,14 |
| Monate im Plus | 6 von 11 | 7 von 11 | 8 von 11 |

- **Zerlegung:** A = B + A's Shorts. Die Shorts allein: -289 € auf 13 580 MWh (t -0,01).
- **B gegen A:** +1 €/Tag; bei gleichem Risiko t = 0,79; Sharpe-Differenz +0,63, Block-Bootstrap P(Sharpe B > A) = 0,72, 90-%-Intervall [-0,99; 2,14].
- **B gegen A, Spread gekappt ±200 €/MWh:** bei gleichem Risiko t = -1,55, P(Sharpe B > A) = 0,05.
- **B gegen immer long:** bei gleichem Risiko t = 0,78; P(Sharpe B > immer long) = 0,82, 90-%-Intervall [-0,66; 2,12].

**Lesart**

- Ungekappt hat B die höhere Sharpe (3,02 gegen 2,39), mit gekapptem Spread A (3,89 gegen 2,60). B gewinnt also über die Spike-Flanke, A über die normalen Viertelstunden. Welche Sicht gilt, hängt davon ab, ob die Spike-Preise des ID-AEP tatsächlich erzielbar sind.
- Konzentration: Ohne seine 10 besten Tage bleiben von B +29 422 € (18 % des Gewinns). Das Profil ist rechtsschief: viele kleine Verlusttage, wenige große Gewinntage.
- Die unbedingte Long-Prämie (immer long: Sharpe 2,22, gekappt ±200: +53 709 €) ist fast vollständig Spike-Prämie. B filtert sie mit den Prognosen des Engines: gekappt ±200 bleibt B bei +97 197 €.

![PnL](pnl.png)

**Robustheit von B**

| Variante | PnL € | Sharpe | t | t gekappt ±200 |
|---|---:|---:|---:|---:|
| feste Schwelle 2 €/MWh | +157 187 | 2,14 | 1,83 | 2,10 |
| feste Schwelle 5 €/MWh | +142 196 | 2,23 | 1,96 | 2,25 |
| feste Schwelle 10 €/MWh | +128 827 | 2,77 | 2,51 | 2,86 |
| B, Seeds 5–9 | +150 908 | 2,06 | 1,81 | 2,20 |
| A, Seeds 5–9 | +121 016 | 1,44 | 1,34 | 2,96 |

<sub>Engine 74ec0b4, Dataset-Revision 8b30c0b, Code ed7ce99. Alle Zahlen in [reports/REPORT.md](reports/REPORT.md) und `reports/backtest.json`.</sub>

## Monate

| Monat | B € | A € | immer long € | Schwelle des Engines €/MWh |
|---|---:|---:|---:|---:|
| 2026-01 | -267 | -4 988 | +90 106 | 30 |
| 2026-02 | -796 | -796 | -13 658 | 30 |
| 2026-03 | -336 | +13 173 | -25 538 | 15 |
| 2026-04 | -3 194 | -2 288 | -49 881 | 10 |
| 2026-05 | +15 342 | +16 870 | +22 249 | 10 |
| 2026-06 | +27 802 | +37 588 | +30 469 | 5 |
| 2026-07 | +17 608 | +33 093 | +1 952 | 2 |
| 2026-08 | +41 190 | +18 464 | +95 796 | 5 |
| 2026-09 | +60 162 | +67 542 | +47 698 | 2 |
| 2026-10 | +9 627 | -13 131 | +29 425 | 2 |
| 2026-11 | +0 | +1 322 | +15 193 | 30 |

## Der Spread

Alle 38 596 Viertelstunden von 2025-10-01 bis 2026-11-07:

| ID-AEP − DA | €/MWh |
|---|---:|
| Mittelwert | +3,78 |
| **Median** | **-1,08** |
| Mittelwert ohne die äußersten 5 % je Seite | -0,01 |
| Mittelwert der Viertelstunden mit \|Spread\| ≤ 100 €/MWh | -0,98 |
| Anteil Viertelstunden mit ID-AEP > DA | 48 % |
| Anteil des obersten 1 % an der Summe aller Spreads | **122 %** |

Spikes über +200 €/MWh: 307 Viertelstunden an 100 Tagen; unter −200 €/MWh: 69. Sie häufen sich in den Rampenstunden (Grafik unten).

| Stunde | Mittelwert | Median | Spikes > +200 | Spikes < −200 |
|---:|---:|---:|---:|---:|
| 0 | +3,9 | +0,0 | 2 | 0 |
| 1 | +5,0 | +1,2 | 3 | 0 |
| 2 | +3,8 | +0,4 | 3 | 0 |
| 3 | +4,3 | +0,5 | 2 | 0 |
| 4 | +2,8 | +0,4 | 0 | 0 |
| 5 | +0,5 | -0,7 | 0 | 0 |
| 6 | -1,8 | -2,7 | 1 | 0 |
| 7 | +1,3 | -2,1 | 11 | 2 |
| 8 | +7,1 | -3,3 | 19 | 1 |
| 9 | +6,4 | +0,2 | 14 | 0 |
| 10 | +12,9 | +2,3 | 28 | 0 |
| 11 | +10,4 | +0,6 | 15 | 3 |
| 12 | +7,4 | +0,6 | 14 | 3 |
| 13 | +4,2 | +0,4 | 8 | 5 |
| 14 | -1,0 | +1,0 | 5 | 4 |
| 15 | -1,0 | -0,7 | 4 | 4 |
| 16 | -4,3 | -3,0 | 4 | 2 |
| 17 | -2,5 | -5,6 | 19 | 3 |
| 18 | -1,4 | -9,0 | 18 | 4 |
| 19 | +1,3 | -10,4 | 39 | 20 |
| 20 | +9,0 | -5,9 | 36 | 8 |
| 21 | +11,2 | -3,3 | 40 | 7 |
| 22 | +7,9 | -2,0 | 15 | 3 |
| 23 | +3,4 | -0,3 | 7 | 0 |

## Alle Kennzahlen je Bein

```json
{
 "B": {
  "days": 310,
  "days_traded": 241,
  "quarter_hours_traded": 10056,
  "mwh": 25140.0,
  "net_eur": 167138.0,
  "gross_eur": 204848.0,
  "costs_eur": 37710.0,
  "eur_per_mwh": 6.65,
  "hit_rate": 0.468,
  "sharpe_daily_ann": 3.02,
  "t_daily_hac": 2.75,
  "max_drawdown_eur": -23563.0,
  "worst_day_eur": -19759.0,
  "best_day_eur": 22514.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": 29422.0,
  "top_qh_net_eur": 56610.0,
  "break_even_slippage_eur_mwh": 7.65,
  "sharpe_first_half": 0.43,
  "sharpe_second_half": 4.6,
  "positive_months": 6,
  "months": 11
 },
 "A": {
  "days": 310,
  "days_traded": 267,
  "quarter_hours_traded": 15488,
  "mwh": 38720.0,
  "net_eur": 166849.0,
  "gross_eur": 224929.0,
  "costs_eur": 58080.0,
  "eur_per_mwh": 4.31,
  "hit_rate": 0.507,
  "sharpe_daily_ann": 2.39,
  "t_daily_hac": 2.26,
  "max_drawdown_eur": -67590.0,
  "worst_day_eur": -31591.0,
  "best_day_eur": 24752.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": 24262.0,
  "top_qh_net_eur": 56610.0,
  "break_even_slippage_eur_mwh": 5.31,
  "sharpe_first_half": 1.23,
  "sharpe_second_half": 3.17,
  "positive_months": 7,
  "months": 11
 },
 "A_short": {
  "days": 310,
  "days_traded": 231,
  "quarter_hours_traded": 5432,
  "mwh": 13580.0,
  "net_eur": -289.0,
  "gross_eur": 20081.0,
  "costs_eur": 20370.0,
  "eur_per_mwh": -0.02,
  "hit_rate": 0.579,
  "sharpe_daily_ann": -0.01,
  "t_daily_hac": -0.01,
  "max_drawdown_eur": -68139.0,
  "worst_day_eur": -30829.0,
  "best_day_eur": 13894.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": -62800.0,
  "top_qh_net_eur": 10182.0,
  "break_even_slippage_eur_mwh": 0.98,
  "sharpe_first_half": 1.46,
  "sharpe_second_half": -0.55,
  "positive_months": 7,
  "months": 11
 },
 "always_long": {
  "days": 310,
  "days_traded": 310,
  "quarter_hours_traded": 29760,
  "mwh": 74400.0,
  "net_eur": 243809.0,
  "gross_eur": 355409.0,
  "costs_eur": 111600.0,
  "eur_per_mwh": 3.28,
  "hit_rate": 0.447,
  "sharpe_daily_ann": 2.22,
  "t_daily_hac": 1.74,
  "max_drawdown_eur": -129624.0,
  "worst_day_eur": -48138.0,
  "best_day_eur": 30229.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": 20738.0,
  "top_qh_net_eur": 77833.0,
  "break_even_slippage_eur_mwh": 4.28,
  "sharpe_first_half": 0.22,
  "sharpe_second_half": 4.14,
  "positive_months": 8,
  "months": 11
 }
}
```
