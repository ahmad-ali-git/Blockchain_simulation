from simulation import Simulation


def main():
    print("=" * 60)
    print("  BLOCKCHAIN 51% ATTACK SIMULATION")
    print("  A Simulation-Based Framework for Mitigating")
    print("  a 51% Attack on Blockchain Networks")
    print("  Group ID: F25PROJECT5043F")
    print("=" * 60)

    num_runs = 10
    baseline_successes = 0
    protected_successes = 0
    total_rejected = 0

    print(f"\nRunning {num_runs} simulation rounds...\n")

    for run in range(num_runs):
        print(f"\n{'#' * 60}")
        print(f"  SIMULATION RUN {run + 1} of {num_runs}")
        print(f"{'#' * 60}")

        sim = Simulation(
            num_honest_miners=5,
            attacker_hashrate=0.55,
            total_blocks=30,
            difficulty=2
        )

        baseline_result = sim.run_baseline()
        protected_result = sim.run_protected()

        if baseline_result["attack_success"]:
            baseline_successes += 1
        if protected_result["attack_success"]:
            protected_successes += 1
        total_rejected += protected_result.get("blocks_rejected", 0)

    print("\n" + "=" * 60)
    print("  FINAL ANALYSIS")
    print("=" * 60)
    print(f"  Total Simulation Runs:        {num_runs}")
    print(f"  Baseline Attack Successes:     {baseline_successes}/{num_runs} ({baseline_successes/num_runs*100:.0f}%)")
    print(f"  Protected Attack Successes:    {protected_successes}/{num_runs} ({protected_successes/num_runs*100:.0f}%)")
    print(f"  Total Blocks Rejected by LPC:  {total_rejected}")
    print(f"  Avg Blocks Rejected per Run:   {total_rejected/num_runs:.1f}")
    print("=" * 60)

    if baseline_successes > protected_successes:
        print("\n  CONCLUSION: LPC Defense significantly reduces")
        print("  the success rate of 51% attacks!")
    elif protected_successes == 0:
        print("\n  CONCLUSION: LPC Defense completely prevented")
        print("  all 51% attack attempts!")
    print("=" * 60)


if __name__ == "__main__":
    main()