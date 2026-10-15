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
_Wird vom Backtest erzeugt (`python -m strats backtest`)._
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
_Wird vom Backtest erzeugt (`python -m strats backtest`)._
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
_Noch kein abgerechneter Tag._
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
