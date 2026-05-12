# visualization using matplotlib and seaborn

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from simulation import Simulation


def run_and_collect_data(num_runs=10):
    results = []

    for run in range(num_runs):
        sim = Simulation(
            num_honest_miners=5,
            attacker_hashrate=0.55,
            total_blocks=30,
            difficulty=2
        )

        baseline = sim.run_baseline()
        protected = sim.run_protected()

        results.append({
            "run": run + 1,
            "baseline_success": baseline["attack_success"],
            "protected_success": protected["attack_success"],
            "baseline_chain_length": baseline["total_blocks"],
            "protected_chain_length": protected["total_blocks"],
            "blocks_rejected": protected.get("blocks_rejected", 0)
        })

    return pd.DataFrame(results)


def create_visualizations(df):
    sns.set_style("whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Blockchain 51% Attack Simulation Results\nGroup ID: F25PROJECT5043F",
                 fontsize=16, fontweight='bold')

    # attack success rate comparison
    baseline_rate = df["baseline_success"].sum() / len(df) * 100
    protected_rate = df["protected_success"].sum() / len(df) * 100

    bars = axes[0, 0].bar(
        ["Without Defense\n(Baseline)", "With LPC Defense\n(Protected)"],
        [baseline_rate, protected_rate],
        color=["#E74C3C", "#2ECC71"],
        width=0.5,
        edgecolor="black"
    )
    axes[0, 0].set_ylabel("Attack Success Rate (%)", fontsize=11)
    axes[0, 0].set_title("Attack Success Rate Comparison", fontsize=13, fontweight='bold')
    axes[0, 0].set_ylim(0, 100)

    for bar, val in zip(bars, [baseline_rate, protected_rate]):
        axes[0, 0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                        f"{val:.0f}%", ha='center', fontsize=14, fontweight='bold')

    # blocks rejected per run
    sns.barplot(x="run", y="blocks_rejected", data=df, ax=axes[0, 1],
                color="#3498DB", edgecolor="black")
    axes[0, 1].set_xlabel("Simulation Run", fontsize=11)
    axes[0, 1].set_ylabel("Blocks Rejected", fontsize=11)
    axes[0, 1].set_title("Blocks Rejected by LPC Defense per Run", fontsize=13, fontweight='bold')

    # chain length comparison
    chain_data = pd.DataFrame({
        "Run": list(df["run"]) * 2,
        "Chain Length": list(df["baseline_chain_length"]) + list(df["protected_chain_length"]),
        "Scenario": ["Baseline"] * len(df) + ["Protected"] * len(df)
    })
    sns.barplot(x="Run", y="Chain Length", hue="Scenario", data=chain_data,
                ax=axes[1, 0], palette=["#E74C3C", "#2ECC71"], edgecolor="black")
    axes[1, 0].set_xlabel("Simulation Run", fontsize=11)
    axes[1, 0].set_ylabel("Final Chain Length", fontsize=11)
    axes[1, 0].set_title("Final Chain Length per Run", fontsize=13, fontweight='bold')
    axes[1, 0].legend(title="Scenario")

    # summary table
    axes[1, 1].axis("off")
    summary_data = [
        ["Total Runs", str(len(df))],
        ["Baseline Attack Success", f"{baseline_rate:.0f}%"],
        ["Protected Attack Success", f"{protected_rate:.0f}%"],
        ["Avg Blocks Rejected/Run", f"{df['blocks_rejected'].mean():.1f}"],
        ["Max Blocks Rejected", str(df["blocks_rejected"].max())],
        ["Min Blocks Rejected", str(df["blocks_rejected"].min())],
        ["Defense Effectiveness", f"{baseline_rate - protected_rate:.0f}% reduction"]
    ]

    table = axes[1, 1].table(
        cellText=summary_data,
        colLabels=["Metric", "Value"],
        cellLoc="center",
        loc="center",
        colWidths=[0.5, 0.3]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 1.8)

    for i in range(len(summary_data) + 1):
        for j in range(2):
            cell = table[i, j]
            if i == 0:
                cell.set_facecolor("#2C3E50")
                cell.set_text_props(color="white", fontweight="bold")
            elif i % 2 == 0:
                cell.set_facecolor("#EBF5FB")
            else:
                cell.set_facecolor("white")

    axes[1, 1].set_title("Summary Statistics", fontsize=13, fontweight='bold')

    plt.tight_layout()
    plt.savefig("simulation_results.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("\nChart saved as 'simulation_results.png'")


if __name__ == "__main__":
    print("Running simulations and collecting data...\n")
    df = run_and_collect_data(num_runs=10)

    print("\n\nData collected using Pandas:")
    print(df.to_string(index=False))

    print("\n\nGenerating visualizations...")
    create_visualizations(df)