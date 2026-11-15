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
Alle 39 268 Viertelstunden von 2025-10-01 bis 2026-11-14:

| ID-AEP − DA | €/MWh |
|---|---:|
| Mittelwert | +3,91 |
| **Median** | **-1,06** |
| Mittelwert ohne die äußersten 5 % je Seite | +0,07 |
| Mittelwert der Viertelstunden mit \|Spread\| ≤ 100 €/MWh | -0,94 |
| Anteil Viertelstunden mit ID-AEP > DA | 48 % |
| Anteil des obersten 1 % an der Summe aller Spreads | **118 %** |

Spikes über +200 €/MWh: 321 Viertelstunden an 103 Tagen; unter −200 €/MWh: 69. Sie häufen sich in den Rampenstunden (Grafik unten).

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
Testzeitraum 2026-01-01 bis 2026-11-13 (317 Tage), Walk-Forward des Engines, 10 MW je Viertelstunde, Kosten 1,5 €/MWh Round Trip, Exit ID-AEP. Stand 2026-11-15.

| | **B: Long-only** | A: Engine | immer long |
|---|---:|---:|---:|
| Netto-PnL € | +152 236 | +121 450 | +260 590 |
| Volumen MWh | 23 198 | 34 715 | 76 080 |
| €/MWh | +6,56 | +3,50 | +3,43 |
| Sharpe p. a. (täglich) | 2,79 | 1,77 | 2,33 |
| t (HAC, täglich) | 2,58 | 1,61 | 1,85 |
| Max. Drawdown € | -25 064 | -72 617 | -129 624 |
| Schlechtester Tag € | -19 759 | -30 602 | -48 138 |
| Break-even-Slippage €/MWh | 7,6 | 4,5 | 4,4 |
| Spread gekappt ±200 €/MWh: PnL € (t) | +86 807 (2,61) | +119 939 (2,85) | +66 250 (0,70) |
| Spread gekappt ±100 €/MWh: PnL € (t) | +49 749 (1,68) | +95 250 (2,63) | -32 620 (-0,40) |
| ohne die 10 besten Tage € | +16 586 | -15 232 | +37 519 |
| die 10 besten Viertelstunden € | +60 622 | +60 622 | +77 833 |
| Sharpe 1. / 2. Hälfte | 0,59 / 4,18 | 1,39 / 2,12 | 0,31 / 4,26 |
| Monate im Plus | 6 von 11 | 6 von 11 | 8 von 11 |

- **Zerlegung:** A = B + A's Shorts. Die Shorts allein: -30 786 € auf 11 518 MWh (t -0,63).
- **B gegen A:** +97 €/Tag; bei gleichem Risiko t = 1,36; Sharpe-Differenz +1,02, Block-Bootstrap P(Sharpe B > A) = 0,85, 90-%-Intervall [-0,49; 2,49].
- **B gegen A, Spread gekappt ±200 €/MWh:** bei gleichem Risiko t = -0,83, P(Sharpe B > A) = 0,20.
- **B gegen immer long:** bei gleichem Risiko t = 0,42; P(Sharpe B > immer long) = 0,69, 90-%-Intervall [-1,10; 1,94].

**Lesart**

- Ungekappt hat B die höhere Sharpe (2,79 gegen 1,77), mit gekapptem Spread A (3,06 gegen 2,46). B gewinnt also über die Spike-Flanke, A über die normalen Viertelstunden. Welche Sicht gilt, hängt davon ab, ob die Spike-Preise des ID-AEP tatsächlich erzielbar sind.
- Konzentration: Ohne seine 10 besten Tage bleiben von B +16 586 € (11 % des Gewinns). Das Profil ist rechtsschief: viele kleine Verlusttage, wenige große Gewinntage.
- Die unbedingte Long-Prämie (immer long: Sharpe 2,33, gekappt ±200: +66 250 €) ist fast vollständig Spike-Prämie. B filtert sie mit den Prognosen des Engines: gekappt ±200 bleibt B bei +86 807 €.

![PnL](reports/pnl.png)

**Robustheit von B**

| Variante | PnL € | Sharpe | t | t gekappt ±200 |
|---|---:|---:|---:|---:|
| feste Schwelle 2 €/MWh | +154 758 | 2,08 | 1,80 | 2,10 |
| feste Schwelle 5 €/MWh | +145 660 | 2,22 | 1,95 | 2,21 |
| feste Schwelle 10 €/MWh | +129 208 | 2,71 | 2,47 | 2,79 |
| B, Seeds 5–9 | +137 126 | 2,00 | 1,77 | 2,18 |
| A, Seeds 5–9 | +129 288 | 1,61 | 1,47 | 3,01 |

<sub>Engine 74ec0b4, Dataset-Revision 9cef7d2, Code a399eba. Alle Zahlen in [reports/REPORT.md](reports/REPORT.md) und `reports/backtest.json`.</sub>

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
27 Tage abgerechnet (2026-10-19 bis 2026-11-14).

| | B: Long-only | A: Engine (Referenz) | A's Shorts | immer long |
|---|---:|---:|---:|---:|
| Netto € | **+12 096** (+5,18 €/MWh) | +295 | -11 801 | +46 687 |
| Spread gekappt ±200 €/MWh | +11 326 | +362 | | |
| Tage im Plus | 5 von 27 | 11 von 27 | | |

Abbruchgrenze nach 27 Tage (5-%-Quantil des Backtests über gleich lange Zeiträume): -10 145 €, nicht erreicht.
Vorab festgelegte Auswertung nach 120 gezählten Tagen: 27 von 120.

| Liefertag | Signal fertig (UTC) | Long-Viertelstunden | B € | A € | immer long € | B kumuliert € |
|---|---|---:|---:|---:|---:|---:|
| 2026-11-01 | 2026-10-31 09:55 | 0 | +0 | +136 | -1 126 | +12 096 |
| 2026-11-02 | 2026-11-01 09:55 | 0 | +0 | -2 730 | +12 914 | +12 096 |
| 2026-11-03 | 2026-11-02 09:55 | 0 | +0 | +0 | +12 973 | +12 096 |
| 2026-11-04 | 2026-11-03 09:55 | 0 | +0 | +991 | -5 990 | +12 096 |
| 2026-11-05 | 2026-11-04 09:55 | 0 | +0 | +830 | -8 289 | +12 096 |
| 2026-11-06 | 2026-11-05 09:55 | 0 | +0 | +0 | +4 712 | +12 096 |
| 2026-11-07 | 2026-11-06 09:55 | 0 | +0 | +329 | -2 423 | +12 096 |
| 2026-11-08 | 2026-11-07 09:55 | 0 | +0 | -234 | +134 | +12 096 |
| 2026-11-09 | 2026-11-08 09:55 | 0 | +0 | +318 | +10 609 | +12 096 |
| 2026-11-10 | 2026-11-09 09:55 | 0 | +0 | -635 | +3 804 | +12 096 |
| 2026-11-11 | 2026-11-10 09:55 | 0 | +0 | -2 260 | +7 464 | +12 096 |
| 2026-11-12 | 2026-11-11 09:55 | 0 | +0 | -62 | -2 707 | +12 096 |
| 2026-11-13 | 2026-11-12 09:55 | 0 | +0 | +0 | -100 | +12 096 |
| 2026-11-14 | 2026-11-13 09:55 | 0 | +0 | +0 | -7 085 | +12 096 |

Warten auf ID-AEP: 2026-11-15, 2026-11-16

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
