"""reports/REPORT.md, reports/pnl.png and the generated sections of the README."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from . import config
from dps.report import _fmt, update_section

INK, INK2, GRID, SURFACE = "#0b0b0b", "#8a8984", "#e4e3df", "#fcfcfb"
BLUE = "#2a78d6"
NAMES = {"B": "B: Long-only", "A": "A: Engine (long/short)", "always_long": "immer long"}


def chart(daily: pd.DataFrame, an: dict, out: Path) -> None:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7.2), gridspec_kw={"height_ratios": [3, 2]}, facecolor=SURFACE)
    x = pd.to_datetime(daily.index)
    for k, color, ls, lw in (("always_long", INK2, "--", 1.2), ("A", INK, "-", 1.4), ("B", BLUE, "-", 2.0)):
        ax1.plot(x, daily[k].cumsum() / 1e3, color=color, ls=ls, lw=lw, label=NAMES[k])
    ax1.axhline(0, color=GRID, lw=1)
    ax1.set_ylabel("kumulierter Netto-PnL, Tsd. €")
    ax1.set_title("Backtest: 10 MW je Viertelstunde, Exit ID-AEP, nach Kosten", loc="left", fontsize=11, color=INK)
    ax1.legend(frameon=False, loc="upper left")
    if an.get("by_hour"):
        h = pd.DataFrame(an["by_hour"]).T.sort_index()
        h.index = h.index.astype(int)
        ax2.bar(h.index - 0.2, h["mean"], width=0.4, color=BLUE, label="Mittelwert")
        ax2.bar(h.index + 0.2, h["median"], width=0.4, color=INK2, label="Median")
        ax2.axhline(0, color=INK, lw=0.8)
        ax2.set_xticks(range(0, 24, 2))
        ax2.set_xlabel("Stunde (Lieferung, lokal)")
        ax2.set_ylabel("ID-AEP − DA, €/MWh")
        ax2.set_title("Spread je Stunde: der Mittelwert kommt aus wenigen Spitzen", loc="left", fontsize=11, color=INK)
        ax2.legend(frameon=False, loc="upper left", ncol=2)
    for ax in (ax1, ax2):
        ax.set_facecolor(SURFACE)
        ax.grid(axis="y", color=GRID, lw=0.8)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(out, dpi=140, facecolor=SURFACE)
    plt.close(fig)


def _row(label, vals):
    return f"| {label} | " + " | ".join(vals) + " |"


def key_table(bt: dict) -> list[str]:
    L, c = bt["legs"], bt["capped"]
    ks = ("B", "A", "always_long")
    cap = [str(int(x)) for x in config.CAPS]
    rows = [
        "| | **B: Long-only** | A: Engine | immer long |", "|---|---:|---:|---:|",
        _row("Netto-PnL €", [_fmt(L[k]["net_eur"], 0, True) for k in ks]),
        _row("Volumen MWh", [_fmt(L[k]["mwh"]) for k in ks]),
        _row("€/MWh", [_fmt(L[k]["eur_per_mwh"], 2, True) for k in ks]),
        _row("Sharpe p. a. (täglich)", [_fmt(L[k]["sharpe_daily_ann"], 2) for k in ks]),
        _row("t (HAC, täglich)", [_fmt(L[k]["t_daily_hac"], 2) for k in ks]),
        _row("Max. Drawdown €", [_fmt(L[k]["max_drawdown_eur"], 0, True) for k in ks]),
        _row("Schlechtester Tag €", [_fmt(L[k]["worst_day_eur"], 0, True) for k in ks]),
        _row("Break-even-Slippage €/MWh", [_fmt(L[k]["break_even_slippage_eur_mwh"], 1) for k in ks]),
    ]
    for cp in cap:
        rows.append(_row(f"Spread gekappt ±{cp} €/MWh: PnL € (t)",
                         [f"{_fmt(c[k][cp]['net_eur'], 0, True)} ({_fmt(c[k][cp]['t_daily_hac'], 2)})" for k in ks]))
    rows += [
        _row(f"ohne die {config.BEST_DAYS} besten Tage €", [_fmt(L[k]["without_best_days_eur"], 0, True) for k in ks]),
        _row(f"die {config.TOP_QH} besten Viertelstunden €", [_fmt(L[k]["top_qh_net_eur"], 0, True) for k in ks]),
        _row("Sharpe 1. / 2. Hälfte", [f"{_fmt(L[k]['sharpe_first_half'], 2)} / {_fmt(L[k]['sharpe_second_half'], 2)}" for k in ks]),
        _row("Monate im Plus", [f"{L[k]['positive_months']} von {L[k]['months']}" for k in ks]),
    ]
    return rows


def comparison_lines(bt: dict) -> list[str]:
    P, L = bt["paired"], bt["legs"]
    c = str(int(config.CAPS[0]))
    pa, pl, pc = P["B_vs_A"], P["B_vs_always_long"], P[f"B_vs_A_capped_{c}"]
    sh = L["A_short"]
    ci = lambda p: f"[{_fmt(p['sharpe_diff_ci90'][0], 2)}; {_fmt(p['sharpe_diff_ci90'][1], 2)}]" if p.get("sharpe_diff_ci90") else "–"
    return [
        f"- **Zerlegung:** A = B + A's Shorts. Die Shorts allein: {_fmt(sh['net_eur'], 0, True)} € auf "
        f"{_fmt(sh['mwh'])} MWh (t {_fmt(sh['t_daily_hac'], 2)}).",
        f"- **B gegen A:** {_fmt(pa['mean_diff_eur_per_day'], 0, True)} €/Tag; bei gleichem Risiko t = "
        f"{_fmt(pa['t_equal_risk'], 2)}; Sharpe-Differenz {_fmt(pa['sharpe_diff'], 2, True)}, Block-Bootstrap "
        f"P(Sharpe B > A) = {_fmt(pa['p_sharpe_higher'], 2)}, 90-%-Intervall {ci(pa)}.",
        f"- **B gegen A, Spread gekappt ±{c} €/MWh:** bei gleichem Risiko t = {_fmt(pc['t_equal_risk'], 2)}, "
        f"P(Sharpe B > A) = {_fmt(pc['p_sharpe_higher'], 2)}.",
        f"- **B gegen immer long:** bei gleichem Risiko t = {_fmt(pl['t_equal_risk'], 2)}; "
        f"P(Sharpe B > immer long) = {_fmt(pl['p_sharpe_higher'], 2)}, 90-%-Intervall {ci(pl)}.",
    ]


def reading(bt: dict) -> list[str]:
    """Generated reading of the numbers, so the prose cannot go stale."""
    L, c = bt["legs"], bt["capped"]
    cp = str(int(config.CAPS[0]))
    out = []
    b_un, a_un = L["B"]["sharpe_daily_ann"] or 0, L["A"]["sharpe_daily_ann"] or 0
    b_c, a_c = c["B"][cp]["sharpe_daily_ann"] or 0, c["A"][cp]["sharpe_daily_ann"] or 0
    if b_un > a_un and b_c < a_c:
        out.append(f"- Ungekappt hat B die höhere Sharpe ({_fmt(b_un, 2)} gegen {_fmt(a_un, 2)}), mit gekapptem Spread "
                   f"A ({_fmt(a_c, 2)} gegen {_fmt(b_c, 2)}). B gewinnt also über die Spike-Flanke, A über die normalen "
                   "Viertelstunden. Welche Sicht gilt, hängt davon ab, ob die Spike-Preise des ID-AEP tatsächlich "
                   "erzielbar sind.")
    elif b_un > a_un and b_c >= a_c:
        out.append(f"- B hat ungekappt ({_fmt(b_un, 2)} gegen {_fmt(a_un, 2)}) und mit gekapptem Spread "
                   f"({_fmt(b_c, 2)} gegen {_fmt(a_c, 2)}) die höhere Sharpe.")
    else:
        out.append(f"- B hat ungekappt keine höhere Sharpe als A ({_fmt(b_un, 2)} gegen {_fmt(a_un, 2)}).")
    tot, wo = L["B"]["net_eur"], L["B"]["without_best_days_eur"]
    if tot and tot > 0:
        share = (f"liegt B bei {_fmt(wo, 0, True)} €: der ganze Gewinn stammt aus diesen Tagen" if wo <= 0 else
                 f"bleiben von B {_fmt(wo, 0, True)} € ({_fmt(100 * wo / tot, 0)} % des Gewinns)")
        out.append(f"- Konzentration: Ohne seine {config.BEST_DAYS} besten Tage {share}. Das Profil ist rechtsschief: "
                   "viele kleine Verlusttage, wenige große Gewinntage.")
    al = L["always_long"]
    out.append(f"- Die unbedingte Long-Prämie (immer long: Sharpe {_fmt(al['sharpe_daily_ann'], 2)}, gekappt ±{cp}: "
               f"{_fmt(c['always_long'][cp]['net_eur'], 0, True)} €) ist fast vollständig Spike-Prämie. B filtert sie "
               f"mit den Prognosen des Engines: gekappt ±{cp} bleibt B bei {_fmt(c['B'][cp]['net_eur'], 0, True)} €.")
    return out


def anatomy_markdown(an: dict) -> str:
    if not an:
        return "_Keine Daten._\n"
    return "\n".join([
        f"Alle {_fmt(an['quarter_hours'])} Viertelstunden von {an['from']} bis {an['to']}:", "",
        "| ID-AEP − DA | €/MWh |", "|---|---:|",
        f"| Mittelwert | {_fmt(an['mean'], 2, True)} |",
        f"| **Median** | **{_fmt(an['median'], 2, True)}** |",
        f"| Mittelwert ohne die äußersten 5 % je Seite | {_fmt(an['trimmed_mean_5'], 2, True)} |",
        f"| Mittelwert der Viertelstunden mit \\|Spread\\| ≤ 100 €/MWh | {_fmt(an['body_mean_abs_le_100'], 2, True)} |",
        f"| Anteil Viertelstunden mit ID-AEP > DA | {_fmt(100 * an['share_positive'], 0)} % |",
        f"| Anteil des obersten 1 % an der Summe aller Spreads | **{_fmt(100 * an['top1pct_share_of_sum'], 0)} %** |",
        "",
        f"Spikes über +{_fmt(config.SPIKE_EUR_MWH)} €/MWh: {an['spikes_up']} Viertelstunden an {an['spike_days']} Tagen; "
        f"unter −{_fmt(config.SPIKE_EUR_MWH)} €/MWh: {an['spikes_down']}. Sie häufen sich in den Rampenstunden "
        "(Grafik unten).", ""])


def readme_results(bt: dict, image: str = "reports/pnl.png") -> str:
    tp = bt["test_period"]
    a = bt["assumptions"]
    rt = 2 * a["fee_eur_mwh_per_leg"] + a["slippage_eur_mwh"]
    L = [f"Testzeitraum {tp['from']} bis {tp['to']} ({tp['days']} Tage), Walk-Forward des Engines, "
         f"{_fmt(a['size_mw'])} MW je Viertelstunde, Kosten {_fmt(rt, 1)} €/MWh Round Trip, Exit ID-AEP. "
         f"Stand {bt['generated_at'][:10]}.", ""]
    L += key_table(bt) + [""] + comparison_lines(bt) + [""] + ["**Lesart**", ""] + reading(bt) + ["", f"![PnL]({image})", ""]
    rob = bt.get("robustness")
    if rob:
        L += ["**Robustheit von B**", "", "| Variante | PnL € | Sharpe | t | t gekappt ±200 |", "|---|---:|---:|---:|---:|"]
        for v in rob.values():
            L.append(f"| {v['label']} | {_fmt(v['net_eur'], 0, True)} | {_fmt(v['sharpe_daily_ann'], 2)} | "
                     f"{_fmt(v['t_daily_hac'], 2)} | {_fmt(v['capped_t'], 2)} |")
        L.append("")
    pv = bt["provenance"]
    eng = (pv.get("engine_commit") or "?")[:7]
    hf = ", ".join(r[:7] for r in pv.get("engine_provenance", {}).get("hf_revisions", []) or []) or "?"
    L.append(f"<sub>Engine {eng}, Dataset-Revision {hf}, Code {(pv.get('strats_commit') or '?')[:7]}. "
             "Alle Zahlen in [reports/REPORT.md](reports/REPORT.md) und `reports/backtest.json`.</sub>")
    return "\n".join(L) + "\n"


def report_markdown(bt: dict) -> str:
    L = ["# Backtest-Report: B (Long-only)", "", readme_results(bt, image="pnl.png"), "## Monate", "",
         "| Monat | B € | A € | immer long € | Schwelle des Engines €/MWh |", "|---|---:|---:|---:|---:|"]
    th = {m["month"]: m["threshold"] for m in bt.get("engine_months", [])}
    for mo, v in sorted(bt["monthly"].items()):
        L.append(f"| {mo} | {_fmt(v.get('B'), 0, True)} | {_fmt(v.get('A'), 0, True)} | {_fmt(v.get('always_long'), 0, True)} | "
                 f"{_fmt(th.get(mo), 0)} |")
    an = bt.get("anatomy", {})
    L += ["", "## Der Spread", "", anatomy_markdown(an), "| Stunde | Mittelwert | Median | Spikes > +200 | Spikes < −200 |",
          "|---:|---:|---:|---:|---:|"]
    for h, r in sorted((int(k), v) for k, v in an.get("by_hour", {}).items()):
        L.append(f"| {h} | {_fmt(r['mean'], 1, True)} | {_fmt(r['median'], 1, True)} | {_fmt(r['up'])} | {_fmt(r['down'])} |")
    L += ["", "## Alle Kennzahlen je Bein", "", "```json", json.dumps(bt["legs"], indent=1), "```", ""]
    return "\n".join(L)


def run(readme: bool = True) -> str:
    rep = Path(config.REPORTS_DIR)
    bt = json.loads((rep / "backtest.json").read_text())
    daily = pd.read_csv(rep / "daily.csv", index_col="day")
    chart(daily, bt.get("anatomy", {}), rep / "pnl.png")
    (rep / "REPORT.md").write_text(report_markdown(bt))
    body = readme_results(bt)
    if readme:
        update_section(Path(config.README), "RESULTS", body)
        update_section(Path(config.README), "ANATOMY", anatomy_markdown(bt.get("anatomy", {})))
    return body
