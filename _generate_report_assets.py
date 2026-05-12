"""
Helper script: runs simulations and generates all charts that go into the
final report. Output goes to FinalSubmission/ReportAssets/
"""
import os
import random

import matplotlib.pyplot as plt
import numpy as np

from simulation import Simulation

random.seed(42)
np.random.seed(42)

OUT = "FinalSubmission/ReportAssets"
os.makedirs(OUT, exist_ok=True)


def run_batch(num_runs=30, honest_nodes=None, attacker_nodes=12):
    if honest_nodes is None:
        honest_nodes = [2, 2, 2, 2, 2]
    base_wins, prot_wins, rejected = 0, 0, 0
    chain_lens_baseline, chain_lens_protected = [], []
    for _ in range(num_runs):
        sim = Simulation(
            honest_nodes=honest_nodes,
            attacker_nodes=attacker_nodes,
            total_blocks=30,
            difficulty=2,
        )
        b = sim.run_baseline()
        p = sim.run_protected()
        if b["attack_success"]:
            base_wins += 1
        if p["attack_success"]:
            prot_wins += 1
        rejected += p["blocks_rejected"]
        chain_lens_baseline.append(b["total_blocks"])
        chain_lens_protected.append(p["total_blocks"])
    return {
        "baseline_success_rate": base_wins / num_runs,
        "protected_success_rate": prot_wins / num_runs,
        "avg_rejected": rejected / num_runs,
        "chain_lens_baseline": chain_lens_baseline,
        "chain_lens_protected": chain_lens_protected,
    }


# ---------- Chart 1: Attack success comparison ----------
print("Running batch for main comparison chart...")
res = run_batch(num_runs=30)

fig, ax = plt.subplots(figsize=(7, 4.5))
labels = ["Baseline\n(no defense)", "Protected\n(LPC + Safe Mode)"]
values = [res["baseline_success_rate"] * 100, res["protected_success_rate"] * 100]
colors = ["#e74c3c", "#2ecc71"]
bars = ax.bar(labels, values, color=colors, width=0.5, edgecolor="black")
for bar, v in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width() / 2, v + 1.5, f"{v:.0f}%",
            ha="center", fontsize=12, fontweight="bold")
ax.set_ylabel("Attack success rate (%)")
ax.set_title("Effect of Safe Mode Detection on 51% attack success rate (30 runs)")
ax.set_ylim(0, 105)
ax.grid(axis="y", linestyle="--", alpha=0.4)
plt.tight_layout()
plt.savefig(f"{OUT}/chart_attack_success.png", dpi=130)
plt.close()


# ---------- Chart 2: Hashrate vs attack success curve ----------
print("Running hashrate sweep...")
hashrates = []
base_rates = []
prot_rates = []
for atk_nodes in [4, 6, 8, 10, 12, 14, 18, 25]:
    r = run_batch(num_runs=15, attacker_nodes=atk_nodes)
    total = sum([2, 2, 2, 2, 2]) + atk_nodes
    hashrates.append(atk_nodes / total * 100)
    base_rates.append(r["baseline_success_rate"] * 100)
    prot_rates.append(r["protected_success_rate"] * 100)

fig, ax = plt.subplots(figsize=(7.5, 4.5))
ax.plot(hashrates, base_rates, marker="o", color="#e74c3c", label="Baseline", linewidth=2)
ax.plot(hashrates, prot_rates, marker="s", color="#2ecc71", label="With Safe Mode", linewidth=2)
ax.axvline(x=50, color="gray", linestyle="--", alpha=0.6)
ax.text(50.5, 85, "51% threshold", color="gray", fontsize=10)
ax.set_xlabel("Attacker hashrate (%)")
ax.set_ylabel("Attack success rate (%)")
ax.set_title("Attack success rate at different attacker hashrates")
ax.legend(loc="lower right")
ax.grid(alpha=0.4)
plt.tight_layout()
plt.savefig(f"{OUT}/chart_hashrate_vs_success.png", dpi=130)
plt.close()


# ---------- Chart 3: Chain length distribution ----------
fig, ax = plt.subplots(figsize=(7.5, 4.5))
bins = range(min(res["chain_lens_baseline"] + res["chain_lens_protected"]) - 1,
             max(res["chain_lens_baseline"] + res["chain_lens_protected"]) + 2)
ax.hist([res["chain_lens_baseline"], res["chain_lens_protected"]],
        bins=bins, label=["Baseline", "Protected"],
        color=["#e74c3c", "#2ecc71"], edgecolor="black")
ax.set_xlabel("Final chain length (blocks)")
ax.set_ylabel("Number of runs")
ax.set_title("Distribution of final chain length across 30 runs")
ax.legend()
ax.grid(axis="y", alpha=0.4)
plt.tight_layout()
plt.savefig(f"{OUT}/chart_chain_length_dist.png", dpi=130)
plt.close()


# ---------- Chart 4: Single run chain growth (baseline) ----------
print("Generating single run progress chart...")
sim = Simulation(honest_nodes=[2, 2, 2, 2, 2], attacker_nodes=12, total_blocks=30)
history = []
def collect(ev):
    if ev["kind"] == "progress":
        history.append((ev["step"], ev["honest_len"], ev["private_len"]))
sim.on_event = collect
sim.run_baseline()

steps = [h[0] for h in history]
honest = [h[1] for h in history]
private = [h[2] for h in history]
fig, ax = plt.subplots(figsize=(7.5, 4.5))
ax.plot(steps, honest, marker=".", color="#2ecc71", label="Honest chain", linewidth=2)
ax.plot(steps, private, marker=".", color="#e74c3c", label="Attacker private chain", linewidth=2, linestyle="--")
ax.set_xlabel("Mining step")
ax.set_ylabel("Chain length")
ax.set_title("Chain growth during a single baseline run")
ax.legend()
ax.grid(alpha=0.4)
plt.tight_layout()
plt.savefig(f"{OUT}/chart_chain_growth.png", dpi=130)
plt.close()


# ---------- Chart 5: Architecture diagram (simple text-based) ----------
fig, ax = plt.subplots(figsize=(9, 6))
ax.axis("off")

boxes = [
    (0.5, 0.85, 0.9, 0.10, "Presentation Layer:  Streamlit GUI  +  CLI", "#3498db"),
    (0.5, 0.55, 0.9, 0.20,
     "Business Logic Layer\n"
     "Simulation Engine | Consensus Manager | LPC Defense | Safe Mode Detector",
     "#2ecc71"),
    (0.5, 0.20, 0.9, 0.20,
     "Data Layer\n"
     "Block | Blockchain | Transaction | UTXO Set | Miner / Network | Logger",
     "#f39c12"),
]
from matplotlib.patches import FancyBboxPatch
for x, y, w, h, label, color in boxes:
    box = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                         boxstyle="round,pad=0.02", linewidth=1.5,
                         edgecolor="black", facecolor=color, alpha=0.7)
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center",
            fontsize=11, fontweight="bold", color="white")
# arrows between layers
ax.annotate("", xy=(0.5, 0.66), xytext=(0.5, 0.79),
            arrowprops=dict(arrowstyle="->", lw=2))
ax.annotate("", xy=(0.5, 0.31), xytext=(0.5, 0.44),
            arrowprops=dict(arrowstyle="->", lw=2))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_title("3-Tier Architecture", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUT}/diagram_architecture.png", dpi=130)
plt.close()


# ---------- Chart 6: Class diagram-ish overview ----------
fig, ax = plt.subplots(figsize=(10, 6))
ax.axis("off")
classes = [
    (0.15, 0.80, "Block\n--------\nindex\ntimestamp\nprev_hash\nmerkle / hash\nnonce\nminer_id"),
    (0.40, 0.80, "Blockchain\n--------\nchain[]\ndifficulty\nmine_block()\nis_chain_valid()"),
    (0.65, 0.80, "Transaction\n--------\nsender\nreceiver\namount"),
    (0.88, 0.80, "UTXOSet\n--------\nbalances{}\napply_transaction()\ncompare_with()"),
    (0.15, 0.40, "Miner\n--------\nminer_id\nnum_nodes\nhashrate\nblocks_mined"),
    (0.40, 0.40, "HonestMiner\n--------\nmine()"),
    (0.65, 0.40, "MaliciousMiner\n--------\nprivate_chain\nstart_private_chain()\nshould_publish()"),
    (0.88, 0.40, "Network\n--------\nminers[]\nrecalculate()"),
    (0.30, 0.10, "LPCDefense\n--------\nmax_consecutive\nshould_reject_block()"),
    (0.65, 0.10, "Simulation\n--------\nrun_baseline()\nrun_protected()\non_event"),
]
for (x, y, t) in classes:
    ax.text(x, y, t, ha="center", va="center", fontsize=8.5,
            family="monospace",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#ecf0f1",
                      edgecolor="#34495e", linewidth=1.2))

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_title("Class overview", fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUT}/diagram_classes.png", dpi=130)
plt.close()


# ---------- Print summary ----------
print()
print("=" * 50)
print("RESULTS USED IN REPORT:")
print(f"  Baseline attack success rate:  {res['baseline_success_rate'] * 100:.0f}%")
print(f"  Protected attack success rate: {res['protected_success_rate'] * 100:.0f}%")
print(f"  Avg blocks rejected by LPC:    {res['avg_rejected']:.1f}")
print()
print("Hashrate sweep:")
for h, b, p in zip(hashrates, base_rates, prot_rates):
    print(f"  hashrate={h:5.1f}%  baseline={b:5.0f}%  protected={p:5.0f}%")
print()
print(f"Charts written to {OUT}/")
print("=" * 50)
