# de-power-strats

Handelsstrategien auf dem Spread-Modell von
[de-power-spread](https://github.com/ak16o7/de-power-spread) (im Folgenden: Engine).
Dieses Repo enthält **Strategie B, Long-only**: die Positionen des Engines unverändert,
jede Short-Position auf null. Backtest über den Walk-Forward des Engines, seit Oktober 2026
live mit öffentlichem, zeitgestempeltem Signal vor jeder Auktion.

Die Begründung ist eine Eigenschaft des Spreads, keine Verbesserung des Modells. Der ID-AEP
misst die letzten 500 MW vor Handelsschluss; dort entstehen Knappheitsspitzen fast nur nach
oben. Eine Short-Position verkauft diese Spitzen, ohne dafür eine Prämie zu bekommen, denn
die Prognose des Engines bildet die Spike-Flanke nicht ab.

## Hypothese

Der Spread ID-AEP − DA ist in der typischen Viertelstunde leicht negativ und im Mittel
positiv. Der Mittelwert stammt aus einem sehr kleinen Teil der Viertelstunden:

<!-- ANATOMY:START -->
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

<!-- ANATOMY:END -->

- **Mechanik:** In den Rampenstunden (Morgen, Abend) trifft knappe flexible Leistung auf den
  dünnsten Teil des Intraday-Handels kurz vor Gate Closure. Der ID-AEP bildet genau diesen
  Teil ab. Abwärtsspitzen gibt es auch (Solarüberschuss mittags), aber deutlich seltener und
  kleiner.
- **Was das für Shorts heißt:** Das Engine schätzt den Erwartungswert auf einem
  winsorisierten Ziel (1 %/99 %). Eine Short-Position mit wenigen €/MWh prognostiziertem Edge
  trägt deshalb ein Aufwärtsrisiko, das in der Prognose nicht enthalten ist und mit fester
  Größe von 10 MW voll durchschlägt.
- **Was B ist:** dieselbe Prognose, ein anderes Risikoprofil. Rechtsschief, viele kleine
  Verlusttage, wenige große Gewinntage. B ist keine bessere Prognose und kein Beleg für einen
  Edge; die Zahlen unten zeigen, wo B gewinnt und wo nicht.

## Definition

| | |
|---|---|
| Entscheidung | 11:00 Uhr D-1, vor der Day-Ahead-Auktion (SDAC, Gate Closure 12:00) |
| Position je Viertelstunde | B = max(A, 0), mit A ∈ {−1, 0, +1} × 10 MW aus dem Engine |
| Einstieg / Ausstieg | Day-Ahead-Preis / ID-AEP (Benchmark, nicht handelbar) |
| Kosten | 0,25 €/MWh je Leg + 1,0 €/MWh Slippage = 1,5 €/MWh Round Trip |
| Modell, Features, Schwelle | unverändert aus dem Engine (Submodul `engine`, fester Commit): Gradient Boosting, Mittel aus 5 Fits, monatlicher Walk-Forward, Schwelle monatlich auf 28 Validierungstagen gewählt |

Die Schwelle wählt das Engine für A; B übernimmt sie, ohne sie für sich neu zu optimieren.
Auf den Ergebnissen von B ist nichts gefittet. Die PnL-Funktion, der Verfügbarkeitsfilter
und der Data Guard sind die des Engines.

## Ergebnis

<!-- RESULTS:START -->
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

![PnL](reports/pnl.png)

**Robustheit von B**

| Variante | PnL € | Sharpe | t | t gekappt ±200 |
|---|---:|---:|---:|---:|
| feste Schwelle 2 €/MWh | +127 606 | 1,80 | 1,49 | 1,52 |
| feste Schwelle 5 €/MWh | +122 304 | 1,99 | 1,68 | 1,78 |
| feste Schwelle 10 €/MWh | +118 746 | 2,66 | 2,25 | 2,43 |
| B, Seeds 5–9 | +105 779 | 1,59 | 1,35 | 1,46 |
| A, Seeds 5–9 | +84 079 | 1,07 | 0,96 | 2,33 |

<sub>Engine 74ec0b4, Dataset-Revision 6a64f66, Code ac20b35. Alle Zahlen in [reports/REPORT.md](reports/REPORT.md) und `reports/backtest.json`.</sub>

<!-- RESULTS:END -->

Zerlegung: A = B + A's Shorts. „Immer long“ misst die unbedingte Long-Prämie des Spreads;
die gekappten Werte zeigen das Ergebnis ohne die Spike-Flanke.

## Einordnung und Grenzen

- **Kein Out-of-sample-Beleg.** Die Regel wurde nach der Analyse des Backtests von A
  festgelegt. Der Backtest von B zeigt, was die Regel auf diesen Daten getan hätte, beweist
  aber nichts. Belastbar ist erst der Live-Track-Record unten.
- **Abhängig von der Spike-Flanke.** Im Backtest bis Oktober 2026 war B ungekappt besser als
  A, mit gekapptem Spread nicht (Lesart oben). Ob die Spike-Preise des ID-AEP erzielbar sind, ist offen: Der Index ist nicht handelbar und
  misst die letzten 500 MW. Eine reale Ausführung über die letzten Handelsstunden (ID1/ID3)
  würde einen Teil davon nicht einfangen.
- **Konzentriert und regimeabhängig.** Ein großer Teil des PnL stammt aus wenigen Tagen. Die
  Long-Prämie war nicht in allen Monaten da; mehr Flexibilität im System (Batterien) kann
  Knappheitsspitzen dämpfen.
- **Nicht signifikant gegen A.** Im Backtest bis Oktober 2026 lag der gepaarte Vergleich gegen A
  unter t = 2.
- **Datenstand.** Die Wetterhistorie des Engines wird laufend um vollständige Modellläufe
  ergänzt, derzeit für November 2025 bis Mai 2026. Jede Ergänzung ändert die Features dieser
  Monate und damit die Backtest-Zahlen von A und B; jede Zahl trägt die Dataset-Revision
  (Fußzeile unter dem Ergebnis).
- Wie beim Engine: Signal, kein Handelssystem; kein Portfoliokontext, keine Intraday-Auktionen.

## Vorab festgelegte Live-Auswertung

Festgelegt vor dem ersten Live-Signal von B (Commit-Zeitpunkt dieses Abschnitts), danach
nicht geändert; die Werte stehen in [`strats/config.py`](strats/config.py).

- **Start:** das erste Signal nach diesem Commit. Gezählt wird jeder Liefertag, dessen Signal
  vor 11:50 Uhr fertig war; Tage ohne Signal werden aufgeführt, nicht nachgerechnet.
- **Auswertung nach 120 gezählten Tagen.** B ersetzt A nur, wenn B gegen A bei gleichem Risiko
  t > 1 erreicht, ungekappt **und** mit bei ±200 €/MWh gekapptem Spread, und der maximale
  Drawdown von B nicht schlechter ist als der von A. Sonst bleibt A.
- **Abbruch:** Fällt der kumulierte Live-PnL von B unter das 5-%-Quantil der Backtest-Summen
  über gleich viele Tage, wird B eingestellt.

## Live-Track-Record

- **Ablauf:** Täglich um 10:52 startet ein externer Scheduler die GitHub Action über die API
  (11:20 als Reserve, 18:35 für die Abrechnung). Sie rechnet das Signal des Engines neu, setzt
  die Shorts auf null und committet nach `signals/` (`side` = B, `side_engine` = A).
  Push-Zeitpunkt und Lauf-Protokoll belegen, dass das Signal vor Gate Closure existierte.
- **Abrechnung:** nach Veröffentlichung des ID-AEP mit der PnL-Funktion des Engines, zusammen
  mit A, A's Shorts, immer long und den gekappten Werten (`live/ledger.csv`).

<!-- LIVE:START -->
11 Tage abgerechnet (2026-10-19 bis 2026-10-29).

| | B: Long-only | A: Engine (Referenz) | A's Shorts | immer long |
|---|---:|---:|---:|---:|
| Netto € | **+8 342** (+4,03 €/MWh) | -317 | -8 660 | +19 395 |
| Spread gekappt ±200 €/MWh | +7 572 | -1 010 | | |
| Tage im Plus | 4 von 11 | 4 von 11 | | |

Abbruchgrenze nach 11 Tage (5-%-Quantil des Backtests über gleich lange Zeiträume): -9 888 €, nicht erreicht.
Vorab festgelegte Auswertung nach 120 gezählten Tagen: 11 von 120.

| Liefertag | Signal fertig (UTC) | Long-Viertelstunden | B € | A € | immer long € | B kumuliert € |
|---|---|---:|---:|---:|---:|---:|
| 2026-10-19 | 2026-10-18 08:55 | 96 | -880 | -880 | -880 | -880 |
| 2026-10-20 | 2026-10-19 08:54 | 96 | +1 831 | +1 831 | +1 831 | +951 |
| 2026-10-21 | 2026-10-20 08:55 | 96 | -244 | -244 | -244 | +707 |
| 2026-10-22 | 2026-10-21 08:55 | 96 | -6 575 | -6 575 | -6 575 | -5 868 |
| 2026-10-23 | 2026-10-22 08:55 | 36 | -2 061 | -4 926 | +1 231 | -7 929 |
| 2026-10-24 | 2026-10-23 08:55 | 48 | +1 861 | +968 | +3 112 | -6 068 |
| 2026-10-25 | 2026-10-24 08:55 | 67 | -88 | -3 039 | +4 730 | -6 156 |
| 2026-10-26 | 2026-10-25 09:54 | 77 | +11 316 | +9 521 | +12 529 | +5 160 |
| 2026-10-27 | 2026-10-26 09:55 | 74 | +11 262 | +10 341 | +14 058 | +16 422 |
| 2026-10-28 | 2026-10-27 09:55 | 59 | -1 939 | -2 688 | -1 452 | +14 484 |
| 2026-10-29 | 2026-10-28 09:54 | 84 | -6 141 | -4 626 | -8 946 | +8 342 |

Warten auf ID-AEP: 2026-10-30, 2026-10-31

<!-- LIVE:END -->

## Reproduktion

```bash
git clone --recursive https://github.com/ak16o7/de-power-strats
cd de-power-strats
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

python -m pytest                       # synthetische Daten, kein Netz
python -m strats fetch --full          # Daten seit 2025-10-01 (ohne API-Keys über freie Quellen)
python -m strats backtest --robustness # Engine-Walk-Forward, B und Zerlegung -> reports/, README
```

- **Code:** `strats/rule.py` (die Regel, zwei Zeilen), `strats/analysis.py` (Backtest und
  Zerlegung), `strats/live.py` (Signal, Abrechnung, Auswertung), `strats/report.py`.
- **Engine:** Submodul `engine` auf festem Commit. Ein Update des Engines ändert die
  Prognosen und wird als eigener Commit mit neuem Backtest dokumentiert.
- **Betrieb:** Workflows in `.github/workflows`, von außen per `workflow_dispatch`-API
  gestartet: `Live` (Signal 10:52, Reserve 11:20, Abrechnung 18:35), `Backtest` (sonntags 08:00,
  Ergebnisblock im README), `CI`. Optionale Secrets wie beim Engine (`ENTSOE_API_KEY`,
  `NTP_CLIENT_ID`, `NTP_CLIENT_SECRET`).
