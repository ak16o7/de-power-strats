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
Alle 37 924 Viertelstunden von 2025-10-01 bis 2026-10-31:

| ID-AEP − DA | €/MWh |
|---|---:|
| Mittelwert | +3,61 |
| **Median** | **-1,12** |
| Mittelwert ohne die äußersten 5 % je Seite | -0,17 |
| Mittelwert der Viertelstunden mit \|Spread\| ≤ 100 €/MWh | -1,09 |
| Anteil Viertelstunden mit ID-AEP > DA | 48 % |
| Anteil des obersten 1 % an der Summe aller Spreads | **129 %** |

Spikes über +200 €/MWh: 301 Viertelstunden an 98 Tagen; unter −200 €/MWh: 69. Sie häufen sich in den Rampenstunden (Grafik unten).

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
Testzeitraum 2026-01-01 bis 2026-10-30 (303 Tage), Walk-Forward des Engines, 10 MW je Viertelstunde, Kosten 1,5 €/MWh Round Trip, Exit ID-AEP. Stand 2026-11-01.

| | **B: Long-only** | A: Engine | immer long |
|---|---:|---:|---:|
| Netto-PnL € | +149 219 | +125 345 | +223 555 |
| Volumen MWh | 26 848 | 41 135 | 72 720 |
| €/MWh | +5,56 | +3,05 | +3,07 |
| Sharpe p. a. (täglich) | 2,28 | 1,61 | 2,09 |
| t (HAC, täglich) | 1,97 | 1,49 | 1,60 |
| Max. Drawdown € | -49 341 | -64 957 | -129 624 |
| Schlechtester Tag € | -38 857 | -38 827 | -48 138 |
| Break-even-Slippage €/MWh | 6,6 | 4,0 | 4,1 |
| Spread gekappt ±200 €/MWh: PnL € (t) | +84 750 (2,20) | +127 421 (2,79) | +34 316 (0,37) |
| Spread gekappt ±100 €/MWh: PnL € (t) | +39 752 (1,19) | +94 776 (2,45) | -54 402 (-0,68) |
| ohne die 10 besten Tage € | +2 804 | -27 787 | +483 |
| die 10 besten Viertelstunden € | +60 844 | +60 844 | +77 833 |
| Sharpe 1. / 2. Hälfte | -0,53 / 4,49 | -0,14 / 2,77 | 0,44 / 3,70 |
| Monate im Plus | 6 von 10 | 6 von 10 | 7 von 10 |

- **Zerlegung:** A = B + A's Shorts. Die Shorts allein: -23 874 € auf 14 288 MWh (t -0,45).
- **B gegen A:** +79 €/Tag; bei gleichem Risiko t = 0,91; Sharpe-Differenz +0,67, Block-Bootstrap P(Sharpe B > A) = 0,79, 90-%-Intervall [-0,66; 2,20].
- **B gegen A, Spread gekappt ±200 €/MWh:** bei gleichem Risiko t = -0,96, P(Sharpe B > A) = 0,16.
- **B gegen immer long:** bei gleichem Risiko t = 0,19; P(Sharpe B > immer long) = 0,64, 90-%-Intervall [-1,17; 1,73].

**Lesart**

- Ungekappt hat B die höhere Sharpe (2,28 gegen 1,61), mit gekapptem Spread A (3,01 gegen 2,19). B gewinnt also über die Spike-Flanke, A über die normalen Viertelstunden. Welche Sicht gilt, hängt davon ab, ob die Spike-Preise des ID-AEP tatsächlich erzielbar sind.
- Konzentration: Ohne seine 10 besten Tage bleiben von B +2 804 € (2 % des Gewinns). Das Profil ist rechtsschief: viele kleine Verlusttage, wenige große Gewinntage.
- Die unbedingte Long-Prämie (immer long: Sharpe 2,09, gekappt ±200: +34 316 €) ist fast vollständig Spike-Prämie. B filtert sie mit den Prognosen des Engines: gekappt ±200 bleibt B bei +84 750 €.

![PnL](reports/pnl.png)

**Robustheit von B**

| Variante | PnL € | Sharpe | t | t gekappt ±200 |
|---|---:|---:|---:|---:|
| feste Schwelle 2 €/MWh | +143 292 | 1,99 | 1,69 | 1,82 |
| feste Schwelle 5 €/MWh | +125 398 | 2,00 | 1,74 | 1,90 |
| feste Schwelle 10 €/MWh | +119 406 | 2,45 | 2,19 | 2,65 |
| B, Seeds 5–9 | +124 512 | 1,94 | 1,70 | 2,08 |
| A, Seeds 5–9 | +126 394 | 1,65 | 1,53 | 3,37 |

<sub>Engine 74ec0b4, Dataset-Revision b173afa, Code f7a76ba. Alle Zahlen in [reports/REPORT.md](reports/REPORT.md) und `reports/backtest.json`.</sub>

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
19 Tage abgerechnet (2026-10-19 bis 2026-11-06).

| | B: Long-only | A: Engine (Referenz) | A's Shorts | immer long |
|---|---:|---:|---:|---:|
| Netto € | **+12 096** (+5,18 €/MWh) | +2 839 | -9 257 | +36 991 |
| Spread gekappt ±200 €/MWh | +11 326 | +2 146 | | |
| Tage im Plus | 5 von 19 | 9 von 19 | | |

Abbruchgrenze nach 19 Tage (5-%-Quantil des Backtests über gleich lange Zeiträume): -32 051 €, nicht erreicht.
Vorab festgelegte Auswertung nach 120 gezählten Tagen: 19 von 120.

| Liefertag | Signal fertig (UTC) | Long-Viertelstunden | B € | A € | immer long € | B kumuliert € |
|---|---|---:|---:|---:|---:|---:|
| 2026-10-24 | 2026-10-23 08:55 | 48 | +1 861 | +968 | +3 112 | -6 068 |
| 2026-10-25 | 2026-10-24 08:55 | 67 | -88 | -3 039 | +4 730 | -6 156 |
| 2026-10-26 | 2026-10-25 09:54 | 77 | +11 316 | +9 521 | +12 529 | +5 160 |
| 2026-10-27 | 2026-10-26 09:55 | 74 | +11 262 | +10 341 | +14 058 | +16 422 |
| 2026-10-28 | 2026-10-27 09:55 | 59 | -1 939 | -2 688 | -1 452 | +14 484 |
| 2026-10-29 | 2026-10-28 09:54 | 84 | -6 141 | -4 626 | -8 946 | +8 342 |
| 2026-10-30 | 2026-10-29 09:55 | 33 | -226 | +662 | -2 658 | +8 117 |
| 2026-10-31 | 2026-10-30 09:55 | 72 | +3 980 | +3 266 | +5 061 | +12 096 |
| 2026-11-01 | 2026-10-31 09:55 | 0 | +0 | +136 | -1 126 | +12 096 |
| 2026-11-02 | 2026-11-01 09:55 | 0 | +0 | -2 730 | +12 914 | +12 096 |
| 2026-11-03 | 2026-11-02 09:55 | 0 | +0 | +0 | +12 973 | +12 096 |
| 2026-11-04 | 2026-11-03 09:55 | 0 | +0 | +991 | -5 990 | +12 096 |
| 2026-11-05 | 2026-11-04 09:55 | 0 | +0 | +830 | -8 289 | +12 096 |
| 2026-11-06 | 2026-11-05 09:55 | 0 | +0 | +0 | +4 712 | +12 096 |

Warten auf ID-AEP: 2026-11-07, 2026-11-08

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
