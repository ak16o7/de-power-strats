# Backtest-Report: B (Long-only)

Testzeitraum 2026-01-01 bis 2026-10-14 (287 Tage), Walk-Forward des Engines, 10 MW je Viertelstunde, Kosten 1,5 €/MWh Round Trip, Exit ID-AEP. Stand 2026-10-15.

| | **B: Long-only** | A: Engine | immer long |
|---|---:|---:|---:|
| Netto-PnL € | +113 680 | +101 691 | +198 483 |
| Volumen MWh | 22 078 | 37 440 | 68 870 |
| €/MWh | +5,15 | +2,72 | +2,88 |
| Sharpe p. a. (täglich) | 2,19 | 1,56 | 1,95 |
| t (HAC, täglich) | 1,80 | 1,39 | 1,44 |
| Max. Drawdown € | -36 939 | -55 398 | -129 624 |
| Schlechtester Tag € | -29 759 | -30 716 | -48 138 |
| Break-even-Slippage €/MWh | 6,2 | 3,7 | 3,9 |
| Spread gekappt ±200 €/MWh: PnL € (t) | +60 174 (1,73) | +114 721 (2,77) | +10 208 (0,11) |
| Spread gekappt ±100 €/MWh: PnL € (t) | +27 584 (0,89) | +94 167 (2,54) | -74 007 (-0,97) |
| ohne die 10 besten Tage € | -3 338 | -21 228 | -24 589 |
| die 10 besten Viertelstunden € | +55 800 | +55 800 | +77 833 |
| Sharpe 1. / 2. Hälfte | -0,40 / 4,20 | -0,19 / 2,68 | 0,35 / 3,50 |
| Monate im Plus | 6 von 10 | 6 von 10 | 6 von 10 |

- **Zerlegung:** A = B + A's Shorts. Die Shorts allein: -11 989 € auf 15 362 MWh (t -0,23).
- **B gegen A:** +42 €/Tag; bei gleichem Risiko t = 0,71; Sharpe-Differenz +0,63, Block-Bootstrap P(Sharpe B > A) = 0,73, 90-%-Intervall [-0,94; 2,42].
- **B gegen A, Spread gekappt ±200 €/MWh:** bei gleichem Risiko t = -1,41, P(Sharpe B > A) = 0,08.
- **B gegen immer long:** bei gleichem Risiko t = 0,23; P(Sharpe B > immer long) = 0,63, 90-%-Intervall [-1,18; 1,83].

**Lesart**

- Ungekappt hat B die höhere Sharpe (2,19 gegen 1,56), mit gekapptem Spread A (3,27 gegen 1,96). B gewinnt also über die Spike-Flanke, A über die normalen Viertelstunden. Welche Sicht gilt, hängt davon ab, ob die Spike-Preise des ID-AEP tatsächlich erzielbar sind.
- Konzentration: Ohne seine 10 besten Tage liegt B bei -3 338 €: der ganze Gewinn stammt aus diesen Tagen. Das Profil ist rechtsschief: viele kleine Verlusttage, wenige große Gewinntage.
- Die unbedingte Long-Prämie (immer long: Sharpe 1,95, gekappt ±200: +10 208 €) ist fast vollständig Spike-Prämie. B filtert sie mit den Prognosen des Engines: gekappt ±200 bleibt B bei +60 174 €.

![PnL](pnl.png)

**Robustheit von B**

| Variante | PnL € | Sharpe | t | t gekappt ±200 |
|---|---:|---:|---:|---:|
| feste Schwelle 2 €/MWh | +150 523 | 2,33 | 1,91 | 1,85 |
| feste Schwelle 5 €/MWh | +133 148 | 2,47 | 2,06 | 1,99 |
| feste Schwelle 10 €/MWh | +104 490 | 3,09 | 2,64 | 1,89 |
| B, Seeds 5–9 | +130 773 | 3,03 | 2,62 | 1,78 |
| A, Seeds 5–9 | +95 980 | 1,61 | 1,40 | 2,52 |

<sub>Engine 74ec0b4, Dataset-Revision 0499790, Code eaf740d. Alle Zahlen in [reports/REPORT.md](reports/REPORT.md) und `reports/backtest.json`.</sub>

## Monate

| Monat | B € | A € | immer long € | Schwelle des Engines €/MWh |
|---|---:|---:|---:|---:|
| 2026-01 | -413 | -1 303 | +90 106 | 30 |
| 2026-02 | -2 411 | -2 411 | -13 658 | 30 |
| 2026-03 | +4 491 | +14 554 | -25 538 | 5 |
| 2026-04 | -16 975 | -9 926 | -49 881 | 5 |
| 2026-05 | +14 314 | +4 471 | +22 249 | 5 |
| 2026-06 | +20 480 | +19 206 | +30 469 | 5 |
| 2026-07 | +20 908 | +33 620 | +1 952 | 10 |
| 2026-08 | +43 860 | +24 401 | +95 796 | 5 |
| 2026-09 | +48 301 | +41 218 | +47 698 | 5 |
| 2026-10 | -18 875 | -22 140 | -709 | 2 |

## Der Spread

Alle 36 384 Viertelstunden von 2025-10-01 bis 2026-10-15:

| ID-AEP − DA | €/MWh |
|---|---:|
| Mittelwert | +3,42 |
| **Median** | **-1,26** |
| Mittelwert ohne die äußersten 5 % je Seite | -0,43 |
| Mittelwert der Viertelstunden mit \|Spread\| ≤ 100 €/MWh | -1,31 |
| Anteil Viertelstunden mit ID-AEP > DA | 47 % |
| Anteil des obersten 1 % an der Summe aller Spreads | **139 %** |

Spikes über +200 €/MWh: 294 Viertelstunden an 94 Tagen; unter −200 €/MWh: 69. Sie häufen sich in den Rampenstunden (Grafik unten).

| Stunde | Mittelwert | Median | Spikes > +200 | Spikes < −200 |
|---:|---:|---:|---:|---:|
| 0 | +3,4 | -0,3 | 2 | 0 |
| 1 | +4,8 | +1,1 | 3 | 0 |
| 2 | +3,6 | +0,3 | 3 | 0 |
| 3 | +4,2 | +0,5 | 2 | 0 |
| 4 | +2,6 | +0,2 | 0 | 0 |
| 5 | +0,5 | -0,7 | 0 | 0 |
| 6 | -2,2 | -2,8 | 1 | 0 |
| 7 | +1,5 | -2,2 | 11 | 2 |
| 8 | +7,3 | -3,4 | 19 | 1 |
| 9 | +6,2 | +0,2 | 12 | 0 |
| 10 | +13,1 | +2,5 | 25 | 0 |
| 11 | +10,9 | +0,7 | 15 | 3 |
| 12 | +7,2 | +0,5 | 14 | 3 |
| 13 | +3,1 | +0,1 | 7 | 5 |
| 14 | -2,7 | +0,6 | 5 | 4 |
| 15 | -2,1 | -1,1 | 4 | 4 |
| 16 | -5,6 | -3,5 | 4 | 2 |
| 17 | -3,3 | -6,2 | 17 | 3 |
| 18 | -1,8 | -9,1 | 18 | 4 |
| 19 | +1,3 | -10,3 | 36 | 20 |
| 20 | +8,8 | -6,4 | 35 | 8 |
| 21 | +10,6 | -4,2 | 39 | 7 |
| 22 | +7,6 | -2,0 | 15 | 3 |
| 23 | +3,2 | -0,2 | 7 | 0 |

## Alle Kennzahlen je Bein

```json
{
 "B": {
  "days": 287,
  "days_traded": 234,
  "quarter_hours_traded": 8831,
  "mwh": 22077.5,
  "net_eur": 113680.0,
  "gross_eur": 146796.0,
  "costs_eur": 33116.0,
  "eur_per_mwh": 5.15,
  "hit_rate": 0.461,
  "sharpe_daily_ann": 2.19,
  "t_daily_hac": 1.8,
  "max_drawdown_eur": -36939.0,
  "worst_day_eur": -29759.0,
  "best_day_eur": 19702.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": -3338.0,
  "top_qh_net_eur": 55800.0,
  "break_even_slippage_eur_mwh": 6.15,
  "sharpe_first_half": -0.4,
  "sharpe_second_half": 4.2,
  "positive_months": 6,
  "months": 10
 },
 "A": {
  "days": 287,
  "days_traded": 242,
  "quarter_hours_traded": 14976,
  "mwh": 37440.0,
  "net_eur": 101691.0,
  "gross_eur": 157851.0,
  "costs_eur": 56160.0,
  "eur_per_mwh": 2.72,
  "hit_rate": 0.508,
  "sharpe_daily_ann": 1.56,
  "t_daily_hac": 1.39,
  "max_drawdown_eur": -55398.0,
  "worst_day_eur": -30716.0,
  "best_day_eur": 21688.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": -21228.0,
  "top_qh_net_eur": 55800.0,
  "break_even_slippage_eur_mwh": 3.72,
  "sharpe_first_half": -0.19,
  "sharpe_second_half": 2.68,
  "positive_months": 6,
  "months": 10
 },
 "A_short": {
  "days": 287,
  "days_traded": 216,
  "quarter_hours_traded": 6145,
  "mwh": 15362.5,
  "net_eur": -11989.0,
  "gross_eur": 11055.0,
  "costs_eur": 23044.0,
  "eur_per_mwh": -0.78,
  "hit_rate": 0.575,
  "sharpe_daily_ann": -0.27,
  "t_daily_hac": -0.23,
  "max_drawdown_eur": -48863.0,
  "worst_day_eur": -30836.0,
  "best_day_eur": 9521.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": -74922.0,
  "top_qh_net_eur": 10182.0,
  "break_even_slippage_eur_mwh": 0.22,
  "sharpe_first_half": 0.31,
  "sharpe_second_half": -0.57,
  "positive_months": 3,
  "months": 10
 },
 "always_long": {
  "days": 287,
  "days_traded": 287,
  "quarter_hours_traded": 27548,
  "mwh": 68870.0,
  "net_eur": 198483.0,
  "gross_eur": 301788.0,
  "costs_eur": 103305.0,
  "eur_per_mwh": 2.88,
  "hit_rate": 0.441,
  "sharpe_daily_ann": 1.95,
  "t_daily_hac": 1.44,
  "max_drawdown_eur": -129624.0,
  "worst_day_eur": -48138.0,
  "best_day_eur": 30229.0,
  "missing_exit_qh": 0,
  "missing_da_qh": 0,
  "without_best_days_eur": -24589.0,
  "top_qh_net_eur": 77833.0,
  "break_even_slippage_eur_mwh": 3.88,
  "sharpe_first_half": 0.35,
  "sharpe_second_half": 3.5,
  "positive_months": 6,
  "months": 10
 }
}
```
