# Backtest-Report: B (Long-only)

Testzeitraum 2026-01-01 bis 2026-10-16 (289 Tage), Walk-Forward des Engines, 10 MW je Viertelstunde, Kosten 1,5 €/MWh Round Trip, Exit ID-AEP. Stand 2026-10-18.

| | **B: Long-only** | A: Engine | immer long |
|---|---:|---:|---:|
| Netto-PnL € | +121 018 | +83 973 | +202 751 |
| Volumen MWh | 22 802 | 36 208 | 69 350 |
| €/MWh | +5,31 | +2,32 | +2,92 |
| Sharpe p. a. (täglich) | 2,49 | 1,38 | 1,98 |
| t (HAC, täglich) | 2,12 | 1,19 | 1,47 |
| Max. Drawdown € | -38 866 | -65 434 | -129 624 |
| Schlechtester Tag € | -25 683 | -30 759 | -48 138 |
| Break-even-Slippage €/MWh | 6,3 | 3,3 | 3,9 |
| Spread gekappt ±200 €/MWh: PnL € (t) | +72 723 (2,32) | +110 371 (2,84) | +14 476 (0,16) |
| Spread gekappt ±100 €/MWh: PnL € (t) | +39 992 (1,46) | +92 809 (2,82) | -69 855 (-0,91) |
| ohne die 10 besten Tage € | +8 277 | -26 711 | -20 321 |
| die 10 besten Viertelstunden € | +50 397 | +56 217 | +77 833 |
| Sharpe 1. / 2. Hälfte | -0,39 / 4,85 | 0,45 / 1,93 | 0,25 / 3,68 |
| Monate im Plus | 5 von 10 | 7 von 10 | 7 von 10 |

- **Zerlegung:** A = B + A's Shorts. Die Shorts allein: -37 045 € auf 13 405 MWh (t -0,64).
- **B gegen A:** +128 €/Tag; bei gleichem Risiko t = 1,07; Sharpe-Differenz +1,11, Block-Bootstrap P(Sharpe B > A) = 0,82, 90-%-Intervall [-0,85; 3,18].
- **B gegen A, Spread gekappt ±200 €/MWh:** bei gleichem Risiko t = -0,92, P(Sharpe B > A) = 0,17.
- **B gegen immer long:** bei gleichem Risiko t = 0,47; P(Sharpe B > immer long) = 0,72, 90-%-Intervall [-0,93; 2,09].

**Lesart**

- Ungekappt hat B die höhere Sharpe (2,49 gegen 1,38), mit gekapptem Spread A (3,22 gegen 2,38). B gewinnt also über die Spike-Flanke, A über die normalen Viertelstunden. Welche Sicht gilt, hängt davon ab, ob die Spike-Preise des ID-AEP tatsächlich erzielbar sind.
- Konzentration: Ohne seine 10 besten Tage bleiben von B +8 277 € (7 % des Gewinns). Das Profil ist rechtsschief: viele kleine Verlusttage, wenige große Gewinntage.
- Die unbedingte Long-Prämie (immer long: Sharpe 1,98, gekappt ±200: +14 476 €) ist fast vollständig Spike-Prämie. B filtert sie mit den Prognosen des Engines: gekappt ±200 bleibt B bei +72 723 €.

![PnL](pnl.png)

**Robustheit von B**

| Variante | PnL € | Sharpe | t | t gekappt ±200 |
|---|---:|---:|---:|---:|
| feste Schwelle 2 €/MWh | +137 211 | 2,45 | 2,03 | 1,83 |
| feste Schwelle 5 €/MWh | +155 789 | 3,26 | 2,81 | 2,07 |
| feste Schwelle 10 €/MWh | +128 020 | 3,42 | 2,97 | 2,46 |
| B, Seeds 5–9 | +151 814 | 3,27 | 2,70 | 2,09 |
| A, Seeds 5–9 | +94 907 | 1,50 | 1,32 | 2,79 |

<sub>Engine 74ec0b4, Dataset-Revision 5904e27, Code 32b50d1. Alle Zahlen in [reports/REPORT.md](reports/REPORT.md) und `reports/backtest.json`.</sub>

## Monate

| Monat | B € | A € | immer long € | Schwelle des Engines €/MWh |
|---|---:|---:|---:|---:|
| 2026-01 | -302 | -3 222 | +90 106 | 30 |
| 2026-02 | -963 | -963 | -13 658 | 30 |
| 2026-03 | -774 | +12 105 | -25 538 | 15 |
| 2026-04 | -13 349 | +2 253 | -49 881 | 2 |
| 2026-05 | +17 549 | +5 462 | +22 249 | 2 |
| 2026-06 | +22 899 | +11 478 | +30 469 | 2 |
| 2026-07 | +24 553 | +34 271 | +1 952 | 10 |
| 2026-08 | +39 818 | +16 523 | +95 796 | 5 |
| 2026-09 | +38 628 | +28 674 | +47 698 | 10 |
| 2026-10 | -7 042 | -22 609 | +3 559 | 2 |

## Der Spread

Alle 36 576 Viertelstunden von 2025-10-01 bis 2026-10-17:

| ID-AEP − DA | €/MWh |
|---|---:|
| Mittelwert | +3,46 |
| **Median** | **-1,21** |
| Mittelwert ohne die äußersten 5 % je Seite | -0,37 |
| Mittelwert der Viertelstunden mit \|Spread\| ≤ 100 €/MWh | -1,25 |
| Anteil Viertelstunden mit ID-AEP > DA | 48 % |
| Anteil des obersten 1 % an der Summe aller Spreads | **138 %** |

Spikes über +200 €/MWh: 294 Viertelstunden an 94 Tagen; unter −200 €/MWh: 69. Sie häufen sich in den Rampenstunden (Grafik unten).

| Stunde | Mittelwert | Median | Spikes > +200 | Spikes < −200 |
|---:|---:|---:|---:|---:|
| 0 | +3,4 | -0,3 | 2 | 0 |
| 1 | +4,9 | +1,2 | 3 | 0 |
| 2 | +3,7 | +0,4 | 3 | 0 |
| 3 | +4,3 | +0,6 | 2 | 0 |
| 4 | +2,7 | +0,4 | 0 | 0 |
| 5 | +0,6 | -0,7 | 0 | 0 |
| 6 | -2,1 | -2,7 | 1 | 0 |
| 7 | +1,5 | -2,1 | 11 | 2 |
| 8 | +7,3 | -3,4 | 19 | 1 |
| 9 | +6,1 | +0,2 | 12 | 0 |
| 10 | +12,8 | +2,3 | 25 | 0 |
| 11 | +10,5 | +0,5 | 15 | 3 |
| 12 | +7,2 | +0,5 | 14 | 3 |
| 13 | +3,2 | +0,1 | 7 | 5 |
| 14 | -2,6 | +0,6 | 5 | 4 |
| 15 | -2,4 | -1,1 | 4 | 4 |
| 16 | -5,5 | -3,4 | 4 | 2 |
| 17 | -3,1 | -6,0 | 17 | 3 |
| 18 | -1,8 | -9,1 | 18 | 4 |
| 19 | +1,3 | -10,3 | 36 | 20 |
| 20 | +8,8 | -6,3 | 35 | 8 |
| 21 | +10,8 | -4,0 | 39 | 7 |
| 22 | +7,8 | -1,8 | 15 | 3 |
| 23 | +3,3 | -0,2 | 7 | 0 |

## Alle Kennzahlen je Bein

```json
{
 "B": {
  "days": 289,
  "days_traded": 224,
  "quarter_hours_traded": 9121,
  "mwh": 22802.5,
  "net_eur": 121018.0,
  "gross_eur": 155222.0,
  "costs_eur": 34204.0,
  "eur_per_mwh": 5.31,
  "hit_rate": 0.471,
  "sharpe_daily_ann": 2.49,
  "t_daily_hac": 2.12,
  "max_drawdown_eur": -38866.0,
  "worst_day_eur": -25683.0,
  "best_day_eur": 21731.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": 8277.0,
  "top_qh_net_eur": 50397.0,
  "break_even_slippage_eur_mwh": 6.31,
  "sharpe_first_half": -0.39,
  "sharpe_second_half": 4.85,
  "positive_months": 5,
  "months": 10
 },
 "A": {
  "days": 289,
  "days_traded": 247,
  "quarter_hours_traded": 14483,
  "mwh": 36207.5,
  "net_eur": 83973.0,
  "gross_eur": 138284.0,
  "costs_eur": 54311.0,
  "eur_per_mwh": 2.32,
  "hit_rate": 0.509,
  "sharpe_daily_ann": 1.38,
  "t_daily_hac": 1.19,
  "max_drawdown_eur": -65434.0,
  "worst_day_eur": -30759.0,
  "best_day_eur": 20518.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": -26711.0,
  "top_qh_net_eur": 56217.0,
  "break_even_slippage_eur_mwh": 3.32,
  "sharpe_first_half": 0.45,
  "sharpe_second_half": 1.93,
  "positive_months": 7,
  "months": 10
 },
 "A_short": {
  "days": 289,
  "days_traded": 214,
  "quarter_hours_traded": 5362,
  "mwh": 13405.0,
  "net_eur": -37045.0,
  "gross_eur": -16938.0,
  "costs_eur": 20108.0,
  "eur_per_mwh": -2.76,
  "hit_rate": 0.572,
  "sharpe_daily_ann": -0.77,
  "t_daily_hac": -0.64,
  "max_drawdown_eur": -70992.0,
  "worst_day_eur": -30880.0,
  "best_day_eur": 11388.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": -100419.0,
  "top_qh_net_eur": 19488.0,
  "break_even_slippage_eur_mwh": -1.76,
  "sharpe_first_half": 1.03,
  "sharpe_second_half": -1.75,
  "positive_months": 3,
  "months": 10
 },
 "always_long": {
  "days": 289,
  "days_traded": 289,
  "quarter_hours_traded": 27740,
  "mwh": 69350.0,
  "net_eur": 202751.0,
  "gross_eur": 306776.0,
  "costs_eur": 104025.0,
  "eur_per_mwh": 2.92,
  "hit_rate": 0.443,
  "sharpe_daily_ann": 1.98,
  "t_daily_hac": 1.47,
  "max_drawdown_eur": -129624.0,
  "worst_day_eur": -48138.0,
  "best_day_eur": 30229.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": -20321.0,
  "top_qh_net_eur": 77833.0,
  "break_even_slippage_eur_mwh": 3.92,
  "sharpe_first_half": 0.25,
  "sharpe_second_half": 3.68,
  "positive_months": 7,
  "months": 10
 }
}
```
