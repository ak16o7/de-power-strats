# Backtest-Report: B (Long-only)

Testzeitraum 2026-01-01 bis 2026-10-23 (296 Tage), Walk-Forward des Engines, 10 MW je Viertelstunde, Kosten 1,5 €/MWh Round Trip, Exit ID-AEP. Stand 2026-10-25.

| | **B: Long-only** | A: Engine | immer long |
|---|---:|---:|---:|
| Netto-PnL € | +146 486 | +132 052 | +202 181 |
| Volumen MWh | 23 682 | 36 228 | 71 030 |
| €/MWh | +6,19 | +3,65 | +2,85 |
| Sharpe p. a. (täglich) | 2,78 | 1,94 | 1,95 |
| t (HAC, täglich) | 2,40 | 1,71 | 1,46 |
| Max. Drawdown € | -22 980 | -67 316 | -129 624 |
| Schlechtester Tag € | -19 300 | -30 795 | -48 138 |
| Break-even-Slippage €/MWh | 7,2 | 4,7 | 3,9 |
| Spread gekappt ±200 €/MWh: PnL € (t) | +74 679 (2,22) | +131 153 (2,90) | +13 030 (0,14) |
| Spread gekappt ±100 €/MWh: PnL € (t) | +33 442 (1,14) | +101 258 (2,69) | -73 636 (-0,96) |
| ohne die 10 besten Tage € | +12 648 | -12 530 | -20 890 |
| die 10 besten Viertelstunden € | +60 622 | +60 622 | +77 833 |
| Sharpe 1. / 2. Hälfte | 0,00 / 4,38 | 0,38 / 2,82 | 0,30 / 3,60 |
| Monate im Plus | 5 von 10 | 6 von 10 | 7 von 10 |

- **Zerlegung:** A = B + A's Shorts. Die Shorts allein: -14 434 € auf 12 545 MWh (t -0,27).
- **B gegen A:** +49 €/Tag; bei gleichem Risiko t = 1,01; Sharpe-Differenz +0,84, Block-Bootstrap P(Sharpe B > A) = 0,80, 90-%-Intervall [-0,72; 2,37].
- **B gegen A, Spread gekappt ±200 €/MWh:** bei gleichem Risiko t = -1,26, P(Sharpe B > A) = 0,11.
- **B gegen immer long:** bei gleichem Risiko t = 0,76; P(Sharpe B > immer long) = 0,81, 90-%-Intervall [-0,75; 2,27].

**Lesart**

- Ungekappt hat B die höhere Sharpe (2,78 gegen 1,94), mit gekapptem Spread A (3,41 gegen 2,27). B gewinnt also über die Spike-Flanke, A über die normalen Viertelstunden. Welche Sicht gilt, hängt davon ab, ob die Spike-Preise des ID-AEP tatsächlich erzielbar sind.
- Konzentration: Ohne seine 10 besten Tage bleiben von B +12 648 € (9 % des Gewinns). Das Profil ist rechtsschief: viele kleine Verlusttage, wenige große Gewinntage.
- Die unbedingte Long-Prämie (immer long: Sharpe 1,95, gekappt ±200: +13 030 €) ist fast vollständig Spike-Prämie. B filtert sie mit den Prognosen des Engines: gekappt ±200 bleibt B bei +74 679 €.

![PnL](pnl.png)

**Robustheit von B**

| Variante | PnL € | Sharpe | t | t gekappt ±200 |
|---|---:|---:|---:|---:|
| feste Schwelle 2 €/MWh | +127 606 | 1,80 | 1,49 | 1,52 |
| feste Schwelle 5 €/MWh | +122 304 | 1,99 | 1,68 | 1,78 |
| feste Schwelle 10 €/MWh | +118 746 | 2,66 | 2,25 | 2,43 |
| B, Seeds 5–9 | +105 779 | 1,59 | 1,35 | 1,46 |
| A, Seeds 5–9 | +84 079 | 1,07 | 0,96 | 2,33 |

<sub>Engine 74ec0b4, Dataset-Revision 6a64f66, Code ac20b35. Alle Zahlen in [reports/REPORT.md](reports/REPORT.md) und `reports/backtest.json`.</sub>

## Monate

| Monat | B € | A € | immer long € | Schwelle des Engines €/MWh |
|---|---:|---:|---:|---:|
| 2026-01 | -156 | -6 817 | +90 106 | 30 |
| 2026-02 | -569 | -569 | -13 658 | 30 |
| 2026-03 | -1 817 | +12 086 | -25 538 | 20 |
| 2026-04 | -2 458 | -2 106 | -49 881 | 10 |
| 2026-05 | +14 783 | +16 954 | +22 249 | 10 |
| 2026-06 | +29 068 | +28 564 | +30 469 | 2 |
| 2026-07 | +17 203 | +33 696 | +1 952 | 5 |
| 2026-08 | +41 575 | +16 966 | +95 796 | 5 |
| 2026-09 | +60 926 | +64 514 | +47 698 | 2 |
| 2026-10 | -12 069 | -31 236 | +2 989 | 2 |

## Der Spread

Alle 37 248 Viertelstunden von 2025-10-01 bis 2026-10-24:

| ID-AEP − DA | €/MWh |
|---|---:|
| Mittelwert | +3,42 |
| **Median** | **-1,21** |
| Mittelwert ohne die äußersten 5 % je Seite | -0,38 |
| Mittelwert der Viertelstunden mit \|Spread\| ≤ 100 €/MWh | -1,27 |
| Anteil Viertelstunden mit ID-AEP > DA | 48 % |
| Anteil des obersten 1 % an der Summe aller Spreads | **138 %** |

Spikes über +200 €/MWh: 300 Viertelstunden an 97 Tagen; unter −200 €/MWh: 69. Sie häufen sich in den Rampenstunden (Grafik unten).

| Stunde | Mittelwert | Median | Spikes > +200 | Spikes < −200 |
|---:|---:|---:|---:|---:|
| 0 | +3,5 | -0,2 | 2 | 0 |
| 1 | +4,9 | +1,3 | 3 | 0 |
| 2 | +3,6 | +0,4 | 3 | 0 |
| 3 | +4,2 | +0,5 | 2 | 0 |
| 4 | +2,6 | +0,4 | 0 | 0 |
| 5 | +0,6 | -0,6 | 0 | 0 |
| 6 | -2,2 | -2,8 | 1 | 0 |
| 7 | +1,2 | -2,4 | 11 | 2 |
| 8 | +7,3 | -3,4 | 19 | 1 |
| 9 | +6,4 | +0,2 | 13 | 0 |
| 10 | +12,7 | +2,2 | 27 | 0 |
| 11 | +10,2 | +0,5 | 15 | 3 |
| 12 | +7,2 | +0,5 | 14 | 3 |
| 13 | +3,4 | +0,2 | 7 | 5 |
| 14 | -2,3 | +0,8 | 5 | 4 |
| 15 | -2,3 | -1,1 | 4 | 4 |
| 16 | -5,5 | -3,4 | 4 | 2 |
| 17 | -3,0 | -6,0 | 18 | 3 |
| 18 | -1,9 | -9,2 | 18 | 4 |
| 19 | +1,5 | -10,3 | 38 | 20 |
| 20 | +8,6 | -6,4 | 35 | 8 |
| 21 | +10,7 | -4,0 | 39 | 7 |
| 22 | +7,5 | -2,0 | 15 | 3 |
| 23 | +3,1 | -0,3 | 7 | 0 |

## Alle Kennzahlen je Bein

```json
{
 "B": {
  "days": 296,
  "days_traded": 224,
  "quarter_hours_traded": 9473,
  "mwh": 23682.5,
  "net_eur": 146486.0,
  "gross_eur": 182009.0,
  "costs_eur": 35524.0,
  "eur_per_mwh": 6.19,
  "hit_rate": 0.465,
  "sharpe_daily_ann": 2.78,
  "t_daily_hac": 2.4,
  "max_drawdown_eur": -22980.0,
  "worst_day_eur": -19300.0,
  "best_day_eur": 22779.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": 12648.0,
  "top_qh_net_eur": 60622.0,
  "break_even_slippage_eur_mwh": 7.19,
  "sharpe_first_half": 0.0,
  "sharpe_second_half": 4.38,
  "positive_months": 5,
  "months": 10
 },
 "A": {
  "days": 296,
  "days_traded": 250,
  "quarter_hours_traded": 14491,
  "mwh": 36227.5,
  "net_eur": 132052.0,
  "gross_eur": 186393.0,
  "costs_eur": 54341.0,
  "eur_per_mwh": 3.65,
  "hit_rate": 0.506,
  "sharpe_daily_ann": 1.94,
  "t_daily_hac": 1.71,
  "max_drawdown_eur": -67316.0,
  "worst_day_eur": -30795.0,
  "best_day_eur": 24976.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": -12530.0,
  "top_qh_net_eur": 60622.0,
  "break_even_slippage_eur_mwh": 4.65,
  "sharpe_first_half": 0.38,
  "sharpe_second_half": 2.82,
  "positive_months": 6,
  "months": 10
 },
 "A_short": {
  "days": 296,
  "days_traded": 209,
  "quarter_hours_traded": 5018,
  "mwh": 12545.0,
  "net_eur": -14434.0,
  "gross_eur": 4383.0,
  "costs_eur": 18818.0,
  "eur_per_mwh": -1.15,
  "hit_rate": 0.583,
  "sharpe_daily_ann": -0.31,
  "t_daily_hac": -0.27,
  "max_drawdown_eur": -64276.0,
  "worst_day_eur": -30836.0,
  "best_day_eur": 13821.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": -78378.0,
  "top_qh_net_eur": 10182.0,
  "break_even_slippage_eur_mwh": -0.15,
  "sharpe_first_half": 0.6,
  "sharpe_second_half": -0.69,
  "positive_months": 5,
  "months": 10
 },
 "always_long": {
  "days": 296,
  "days_traded": 296,
  "quarter_hours_traded": 28412,
  "mwh": 71030.0,
  "net_eur": 202181.0,
  "gross_eur": 308726.0,
  "costs_eur": 106545.0,
  "eur_per_mwh": 2.85,
  "hit_rate": 0.443,
  "sharpe_daily_ann": 1.95,
  "t_daily_hac": 1.46,
  "max_drawdown_eur": -129624.0,
  "worst_day_eur": -48138.0,
  "best_day_eur": 30229.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": -20890.0,
  "top_qh_net_eur": 77833.0,
  "break_even_slippage_eur_mwh": 3.85,
  "sharpe_first_half": 0.3,
  "sharpe_second_half": 3.6,
  "positive_months": 7,
  "months": 10
 }
}
```
