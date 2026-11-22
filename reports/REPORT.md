# Backtest-Report: B (Long-only)

Testzeitraum 2026-01-01 bis 2026-11-20 (324 Tage), Walk-Forward des Engines, 10 MW je Viertelstunde, Kosten 1,5 €/MWh Round Trip, Exit ID-AEP. Stand 2026-11-22.

| | **B: Long-only** | A: Engine | immer long |
|---|---:|---:|---:|
| Netto-PnL € | +181 537 | +152 275 | +224 318 |
| Volumen MWh | 25 100 | 38 322 | 77 760 |
| €/MWh | +7,23 | +3,97 | +2,88 |
| Sharpe p. a. (täglich) | 2,99 | 2,02 | 1,96 |
| t (HAC, täglich) | 2,72 | 1,95 | 1,55 |
| Max. Drawdown € | -25 264 | -67 736 | -129 624 |
| Schlechtester Tag € | -19 604 | -31 934 | -48 138 |
| Break-even-Slippage €/MWh | 8,2 | 5,0 | 3,9 |
| Spread gekappt ±200 €/MWh: PnL € (t) | +99 661 (2,70) | +137 765 (3,05) | +29 952 (0,30) |
| Spread gekappt ±100 €/MWh: PnL € (t) | +54 577 (1,71) | +106 126 (2,77) | -67 571 (-0,79) |
| ohne die 10 besten Tage € | +27 664 | -8 630 | +1 247 |
| die 10 besten Viertelstunden € | +62 240 | +62 240 | +77 833 |
| Sharpe 1. / 2. Hälfte | 0,32 / 4,56 | 1,06 / 2,66 | 0,17 / 3,63 |
| Monate im Plus | 6 von 11 | 6 von 11 | 7 von 11 |

- **Zerlegung:** A = B + A's Shorts. Die Shorts allein: -29 262 € auf 13 222 MWh (t -0,57).
- **B gegen A:** +90 €/Tag; bei gleichem Risiko t = 1,31; Sharpe-Differenz +0,97, Block-Bootstrap P(Sharpe B > A) = 0,86, 90-%-Intervall [-0,42; 2,34].
- **B gegen A, Spread gekappt ±200 €/MWh:** bei gleichem Risiko t = -0,77, P(Sharpe B > A) = 0,21.
- **B gegen immer long:** bei gleichem Risiko t = 0,99; P(Sharpe B > immer long) = 0,88, 90-%-Intervall [-0,42; 2,42].

**Lesart**

- Ungekappt hat B die höhere Sharpe (2,99 gegen 2,02), mit gekapptem Spread A (3,22 gegen 2,61). B gewinnt also über die Spike-Flanke, A über die normalen Viertelstunden. Welche Sicht gilt, hängt davon ab, ob die Spike-Preise des ID-AEP tatsächlich erzielbar sind.
- Konzentration: Ohne seine 10 besten Tage bleiben von B +27 664 € (15 % des Gewinns). Das Profil ist rechtsschief: viele kleine Verlusttage, wenige große Gewinntage.
- Die unbedingte Long-Prämie (immer long: Sharpe 1,96, gekappt ±200: +29 952 €) ist fast vollständig Spike-Prämie. B filtert sie mit den Prognosen des Engines: gekappt ±200 bleibt B bei +99 661 €.

![PnL](pnl.png)

**Robustheit von B**

| Variante | PnL € | Sharpe | t | t gekappt ±200 |
|---|---:|---:|---:|---:|
| feste Schwelle 2 €/MWh | +154 161 | 2,01 | 1,76 | 1,95 |
| feste Schwelle 5 €/MWh | +148 397 | 2,18 | 1,94 | 2,15 |
| feste Schwelle 10 €/MWh | +131 842 | 2,67 | 2,45 | 2,64 |
| B, Seeds 5–9 | +160 873 | 2,93 | 2,75 | 2,74 |
| A, Seeds 5–9 | +152 737 | 2,17 | 2,08 | 3,63 |

<sub>Engine 74ec0b4, Dataset-Revision 8eabc65, Code db29be3. Alle Zahlen in [reports/REPORT.md](reports/REPORT.md) und `reports/backtest.json`.</sub>

## Monate

| Monat | B € | A € | immer long € | Schwelle des Engines €/MWh |
|---|---:|---:|---:|---:|
| 2026-01 | -220 | -5 366 | +90 106 | 30 |
| 2026-02 | -796 | -796 | -13 658 | 30 |
| 2026-03 | -2 269 | +9 533 | -25 538 | 20 |
| 2026-04 | -2 887 | -1 510 | -49 881 | 10 |
| 2026-05 | +13 428 | +13 802 | +22 249 | 10 |
| 2026-06 | +26 028 | +29 684 | +30 469 | 5 |
| 2026-07 | +19 324 | +34 996 | +1 952 | 2 |
| 2026-08 | +56 912 | +22 776 | +95 796 | 2 |
| 2026-09 | +60 949 | +63 897 | +47 698 | 5 |
| 2026-10 | +11 068 | -11 099 | +29 425 | 2 |
| 2026-11 | +0 | -3 644 | -4 298 | 30 |

## Der Spread

Alle 39 940 Viertelstunden von 2025-10-01 bis 2026-11-21:

| ID-AEP − DA | €/MWh |
|---|---:|
| Mittelwert | +3,51 |
| **Median** | **-1,18** |
| Mittelwert ohne die äußersten 5 % je Seite | -0,21 |
| Mittelwert der Viertelstunden mit \|Spread\| ≤ 100 €/MWh | -1,16 |
| Anteil Viertelstunden mit ID-AEP > DA | 48 % |
| Anteil des obersten 1 % an der Summe aller Spreads | **131 %** |

Spikes über +200 €/MWh: 322 Viertelstunden an 104 Tagen; unter −200 €/MWh: 69. Sie häufen sich in den Rampenstunden (Grafik unten).

| Stunde | Mittelwert | Median | Spikes > +200 | Spikes < −200 |
|---:|---:|---:|---:|---:|
| 0 | +3,6 | -0,3 | 2 | 0 |
| 1 | +4,5 | +0,8 | 3 | 0 |
| 2 | +3,3 | -0,0 | 3 | 0 |
| 3 | +4,0 | +0,5 | 2 | 0 |
| 4 | +2,7 | +0,4 | 0 | 0 |
| 5 | +0,7 | -0,5 | 0 | 0 |
| 6 | -1,6 | -2,7 | 1 | 0 |
| 7 | +1,0 | -2,5 | 11 | 2 |
| 8 | +7,1 | -3,5 | 22 | 1 |
| 9 | +5,6 | -0,0 | 14 | 0 |
| 10 | +12,1 | +1,8 | 28 | 0 |
| 11 | +9,5 | +0,4 | 15 | 3 |
| 12 | +7,0 | +0,6 | 14 | 3 |
| 13 | +3,9 | +0,3 | 8 | 5 |
| 14 | -0,7 | +1,0 | 9 | 4 |
| 15 | -0,4 | -0,7 | 8 | 4 |
| 16 | -4,5 | -3,1 | 5 | 2 |
| 17 | -3,0 | -6,1 | 21 | 3 |
| 18 | -2,0 | -9,1 | 18 | 4 |
| 19 | +1,1 | -10,4 | 40 | 20 |
| 20 | +8,3 | -6,0 | 36 | 8 |
| 21 | +10,9 | -3,1 | 40 | 7 |
| 22 | +7,8 | -1,5 | 15 | 3 |
| 23 | +3,4 | -0,2 | 7 | 0 |

## Alle Kennzahlen je Bein

```json
{
 "B": {
  "days": 324,
  "days_traded": 233,
  "quarter_hours_traded": 10040,
  "mwh": 25100.0,
  "net_eur": 181537.0,
  "gross_eur": 219187.0,
  "costs_eur": 37650.0,
  "eur_per_mwh": 7.23,
  "hit_rate": 0.47,
  "sharpe_daily_ann": 2.99,
  "t_daily_hac": 2.72,
  "max_drawdown_eur": -25264.0,
  "worst_day_eur": -19604.0,
  "best_day_eur": 24305.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": 27664.0,
  "top_qh_net_eur": 62240.0,
  "break_even_slippage_eur_mwh": 8.23,
  "sharpe_first_half": 0.32,
  "sharpe_second_half": 4.56,
  "positive_months": 6,
  "months": 11
 },
 "A": {
  "days": 324,
  "days_traded": 268,
  "quarter_hours_traded": 15329,
  "mwh": 38322.5,
  "net_eur": 152275.0,
  "gross_eur": 209759.0,
  "costs_eur": 57484.0,
  "eur_per_mwh": 3.97,
  "hit_rate": 0.505,
  "sharpe_daily_ann": 2.02,
  "t_daily_hac": 1.95,
  "max_drawdown_eur": -67736.0,
  "worst_day_eur": -31934.0,
  "best_day_eur": 25872.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": -8630.0,
  "top_qh_net_eur": 62240.0,
  "break_even_slippage_eur_mwh": 4.97,
  "sharpe_first_half": 1.06,
  "sharpe_second_half": 2.66,
  "positive_months": 6,
  "months": 11
 },
 "A_short": {
  "days": 324,
  "days_traded": 235,
  "quarter_hours_traded": 5289,
  "mwh": 13222.5,
  "net_eur": -29262.0,
  "gross_eur": -9428.0,
  "costs_eur": 19834.0,
  "eur_per_mwh": -2.21,
  "hit_rate": 0.569,
  "sharpe_daily_ann": -0.61,
  "t_daily_hac": -0.57,
  "max_drawdown_eur": -69206.0,
  "worst_day_eur": -31260.0,
  "best_day_eur": 13892.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": -88177.0,
  "top_qh_net_eur": 10182.0,
  "break_even_slippage_eur_mwh": -1.21,
  "sharpe_first_half": 1.36,
  "sharpe_second_half": -1.41,
  "positive_months": 6,
  "months": 11
 },
 "always_long": {
  "days": 324,
  "days_traded": 324,
  "quarter_hours_traded": 31104,
  "mwh": 77760.0,
  "net_eur": 224318.0,
  "gross_eur": 340958.0,
  "costs_eur": 116640.0,
  "eur_per_mwh": 2.88,
  "hit_rate": 0.445,
  "sharpe_daily_ann": 1.96,
  "t_daily_hac": 1.55,
  "max_drawdown_eur": -129624.0,
  "worst_day_eur": -48138.0,
  "best_day_eur": 30229.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": 1247.0,
  "top_qh_net_eur": 77833.0,
  "break_even_slippage_eur_mwh": 3.88,
  "sharpe_first_half": 0.17,
  "sharpe_second_half": 3.63,
  "positive_months": 7,
  "months": 11
 }
}
```
