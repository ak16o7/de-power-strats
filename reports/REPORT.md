# Backtest-Report: B (Long-only)

Testzeitraum 2026-01-01 bis 2026-10-15 (288 Tage), Walk-Forward des Engines, 10 MW je Viertelstunde, Kosten 1,5 €/MWh Round Trip, Exit ID-AEP. Stand 2026-10-17.

| | **B: Long-only** | A: Engine | immer long |
|---|---:|---:|---:|
| Netto-PnL € | +121 015 | +84 089 | +202 644 |
| Volumen MWh | 22 570 | 35 970 | 69 110 |
| €/MWh | +5,36 | +2,34 | +2,93 |
| Sharpe p. a. (täglich) | 2,50 | 1,39 | 1,98 |
| t (HAC, täglich) | 2,12 | 1,19 | 1,47 |
| Max. Drawdown € | -38 866 | -65 434 | -129 624 |
| Schlechtester Tag € | -25 683 | -30 759 | -48 138 |
| Break-even-Slippage €/MWh | 6,4 | 3,3 | 3,9 |
| Spread gekappt ±200 €/MWh: PnL € (t) | +72 720 (2,32) | +110 487 (2,84) | +14 369 (0,16) |
| Spread gekappt ±100 €/MWh: PnL € (t) | +39 988 (1,46) | +92 924 (2,82) | -69 962 (-0,91) |
| ohne die 10 besten Tage € | +8 274 | -26 596 | -20 428 |
| die 10 besten Viertelstunden € | +50 397 | +56 217 | +77 833 |
| Sharpe 1. / 2. Hälfte | -0,39 / 4,87 | 0,45 / 1,94 | 0,25 / 3,69 |
| Monate im Plus | 5 von 10 | 7 von 10 | 7 von 10 |

- **Zerlegung:** A = B + A's Shorts. Die Shorts allein: -36 926 € auf 13 400 MWh (t -0,64).
- **B gegen A:** +128 €/Tag; bei gleichem Risiko t = 1,07; Sharpe-Differenz +1,11, Block-Bootstrap P(Sharpe B > A) = 0,81, 90-%-Intervall [-0,83; 3,20].
- **B gegen A, Spread gekappt ±200 €/MWh:** bei gleichem Risiko t = -0,93, P(Sharpe B > A) = 0,17.
- **B gegen immer long:** bei gleichem Risiko t = 0,47; P(Sharpe B > immer long) = 0,73, 90-%-Intervall [-0,92; 2,12].

**Lesart**

- Ungekappt hat B die höhere Sharpe (2,50 gegen 1,39), mit gekapptem Spread A (3,23 gegen 2,38). B gewinnt also über die Spike-Flanke, A über die normalen Viertelstunden. Welche Sicht gilt, hängt davon ab, ob die Spike-Preise des ID-AEP tatsächlich erzielbar sind.
- Konzentration: Ohne seine 10 besten Tage bleiben von B +8 274 € (7 % des Gewinns). Das Profil ist rechtsschief: viele kleine Verlusttage, wenige große Gewinntage.
- Die unbedingte Long-Prämie (immer long: Sharpe 1,98, gekappt ±200: +14 369 €) ist fast vollständig Spike-Prämie. B filtert sie mit den Prognosen des Engines: gekappt ±200 bleibt B bei +72 720 €.

![PnL](pnl.png)

**Robustheit von B**

| Variante | PnL € | Sharpe | t | t gekappt ±200 |
|---|---:|---:|---:|---:|
| feste Schwelle 2 €/MWh | +137 208 | 2,45 | 2,03 | 1,83 |
| feste Schwelle 5 €/MWh | +155 770 | 3,26 | 2,81 | 2,07 |
| feste Schwelle 10 €/MWh | +127 741 | 3,42 | 2,96 | 2,45 |
| B, Seeds 5–9 | +151 810 | 3,27 | 2,70 | 2,09 |
| A, Seeds 5–9 | +95 023 | 1,51 | 1,33 | 2,79 |

<sub>Engine 74ec0b4, Dataset-Revision 042ba74, Code a2e6f74. Alle Zahlen in [reports/REPORT.md](reports/REPORT.md) und `reports/backtest.json`.</sub>

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
| 2026-10 | -7 045 | -22 493 | +3 452 | 2 |

## Der Spread

Alle 36 480 Viertelstunden von 2025-10-01 bis 2026-10-16:

| ID-AEP − DA | €/MWh |
|---|---:|
| Mittelwert | +3,46 |
| **Median** | **-1,22** |
| Mittelwert ohne die äußersten 5 % je Seite | -0,38 |
| Mittelwert der Viertelstunden mit \|Spread\| ≤ 100 €/MWh | -1,26 |
| Anteil Viertelstunden mit ID-AEP > DA | 48 % |
| Anteil des obersten 1 % an der Summe aller Spreads | **138 %** |

Spikes über +200 €/MWh: 294 Viertelstunden an 94 Tagen; unter −200 €/MWh: 69. Sie häufen sich in den Rampenstunden (Grafik unten).

| Stunde | Mittelwert | Median | Spikes > +200 | Spikes < −200 |
|---:|---:|---:|---:|---:|
| 0 | +3,4 | -0,3 | 2 | 0 |
| 1 | +4,8 | +1,2 | 3 | 0 |
| 2 | +3,7 | +0,3 | 3 | 0 |
| 3 | +4,3 | +0,5 | 2 | 0 |
| 4 | +2,7 | +0,3 | 0 | 0 |
| 5 | +0,6 | -0,7 | 0 | 0 |
| 6 | -2,1 | -2,8 | 1 | 0 |
| 7 | +1,5 | -2,1 | 11 | 2 |
| 8 | +7,4 | -3,4 | 19 | 1 |
| 9 | +6,3 | +0,3 | 12 | 0 |
| 10 | +13,0 | +2,4 | 25 | 0 |
| 11 | +10,7 | +0,5 | 15 | 3 |
| 12 | +7,1 | +0,5 | 14 | 3 |
| 13 | +3,1 | +0,1 | 7 | 5 |
| 14 | -2,6 | +0,6 | 5 | 4 |
| 15 | -2,4 | -1,2 | 4 | 4 |
| 16 | -5,6 | -3,5 | 4 | 2 |
| 17 | -3,2 | -6,1 | 17 | 3 |
| 18 | -1,8 | -9,1 | 18 | 4 |
| 19 | +1,4 | -10,1 | 36 | 20 |
| 20 | +8,9 | -6,2 | 35 | 8 |
| 21 | +10,8 | -4,0 | 39 | 7 |
| 22 | +7,8 | -2,0 | 15 | 3 |
| 23 | +3,4 | -0,2 | 7 | 0 |

## Alle Kennzahlen je Bein

```json
{
 "B": {
  "days": 288,
  "days_traded": 223,
  "quarter_hours_traded": 9028,
  "mwh": 22570.0,
  "net_eur": 121015.0,
  "gross_eur": 154870.0,
  "costs_eur": 33855.0,
  "eur_per_mwh": 5.36,
  "hit_rate": 0.47,
  "sharpe_daily_ann": 2.5,
  "t_daily_hac": 2.12,
  "max_drawdown_eur": -38866.0,
  "worst_day_eur": -25683.0,
  "best_day_eur": 21731.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": 8274.0,
  "top_qh_net_eur": 50397.0,
  "break_even_slippage_eur_mwh": 6.36,
  "sharpe_first_half": -0.39,
  "sharpe_second_half": 4.87,
  "positive_months": 5,
  "months": 10
 },
 "A": {
  "days": 288,
  "days_traded": 246,
  "quarter_hours_traded": 14388,
  "mwh": 35970.0,
  "net_eur": 84089.0,
  "gross_eur": 138044.0,
  "costs_eur": 53955.0,
  "eur_per_mwh": 2.34,
  "hit_rate": 0.508,
  "sharpe_daily_ann": 1.39,
  "t_daily_hac": 1.19,
  "max_drawdown_eur": -65434.0,
  "worst_day_eur": -30759.0,
  "best_day_eur": 20518.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": -26596.0,
  "top_qh_net_eur": 56217.0,
  "break_even_slippage_eur_mwh": 3.34,
  "sharpe_first_half": 0.45,
  "sharpe_second_half": 1.94,
  "positive_months": 7,
  "months": 10
 },
 "A_short": {
  "days": 288,
  "days_traded": 213,
  "quarter_hours_traded": 5360,
  "mwh": 13400.0,
  "net_eur": -36926.0,
  "gross_eur": -16826.0,
  "costs_eur": 20100.0,
  "eur_per_mwh": -2.76,
  "hit_rate": 0.572,
  "sharpe_daily_ann": -0.77,
  "t_daily_hac": -0.64,
  "max_drawdown_eur": -70992.0,
  "worst_day_eur": -30880.0,
  "best_day_eur": 11388.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": -100300.0,
  "top_qh_net_eur": 19488.0,
  "break_even_slippage_eur_mwh": -1.76,
  "sharpe_first_half": 1.03,
  "sharpe_second_half": -1.75,
  "positive_months": 3,
  "months": 10
 },
 "always_long": {
  "days": 288,
  "days_traded": 288,
  "quarter_hours_traded": 27644,
  "mwh": 69110.0,
  "net_eur": 202644.0,
  "gross_eur": 306309.0,
  "costs_eur": 103665.0,
  "eur_per_mwh": 2.93,
  "hit_rate": 0.442,
  "sharpe_daily_ann": 1.98,
  "t_daily_hac": 1.47,
  "max_drawdown_eur": -129624.0,
  "worst_day_eur": -48138.0,
  "best_day_eur": 30229.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": -20428.0,
  "top_qh_net_eur": 77833.0,
  "break_even_slippage_eur_mwh": 3.93,
  "sharpe_first_half": 0.25,
  "sharpe_second_half": 3.69,
  "positive_months": 7,
  "months": 10
 }
}
```
