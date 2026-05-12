# Blockchain 51% Attack Simulation

A simulation-based framework for studying and mitigating 51% attacks on Proof-of-Work blockchain networks.

**Group ID:** F25PROJECT5043F
**Course:** CS619 Final Year Project
**University:** Virtual University of Pakistan
**Supervisor:** Dr. Fouzia Jumani

## What it does

The project simulates a Proof-of-Work blockchain (similar to Bitcoin) and demonstrates two things:

1. How a malicious miner with more than 50% of the network's hash power can carry out a 51% attack to perform double spending.
2. How the proposed defense, called "Safe Mode Detection", can stop this attack by combining two checks: a long private chain (LPC) rule that rejects any block if it would make six or more consecutive blocks by the same miner, and a UTXO comparison that detects double-spend attempts when a competing chain is published.

Hashrate is not set as a fixed number. Each miner runs a number of mining nodes, and the hashrate is calculated dynamically as `nodes / total_nodes`. Adding more nodes to a miner increases its share of block production.

## Project structure

```
.
├── app.py              # Streamlit GUI (main interface)
├── main.py             # Command-line batch runner
├── simulation.py       # Simulation engine (shared by GUI and CLI)
├── miner.py            # Miner classes + Network (computes hashrate from nodes)
├── blockchain.py       # Blockchain + Block linking
├── block.py            # Block data structure with PoW hashing
├── transaction.py      # Transaction + UTXO set
├── lpc_defense.py      # Long Private Chain defense logic
├── visualize.py        # Matplotlib helpers for charts
├── requirements.txt    # Python dependencies
└── README.md           # this file
```

## How to run

### 1. Set up the environment

```bash
python3 -m venv venv
source venv/bin/activate           # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the GUI (recommended for demo)

```bash
streamlit run app.py
```

Then open your browser at `http://localhost:8501`.

In the sidebar you can:
- Set the number of honest miners and their nodes.
- Set the attacker's number of nodes (the hashrate updates live as you slide).
- Toggle simulation parameters like total blocks, PoW difficulty, attack start time.
- Choose between Baseline only, Protected only, or Compare Both.
- Press **Run Simulation** to start.

The dashboard shows the live event log, chain growth chart, miner statistics, and a color-coded view of the final chain.

### 3. Run the CLI batch mode (for collecting statistics)

```bash
python main.py
```

This runs ten simulation rounds back-to-back and prints aggregate statistics: how many baseline attacks succeeded, how many were blocked by the defense, total blocks rejected by LPC.

## Configuration example

If you want a 54% attacker (a textbook 51% attack scenario):

- 5 honest miners, 2 nodes each = 10 honest nodes
- Attacker with 12 nodes
- Total = 22 nodes
- Attacker's hashrate = 12 / 22 ≈ 54.5%

Both the GUI sliders and the `Simulation()` constructor in `main.py` accept these values.

## Notes

The project is purely a research simulation. It does not connect to any real cryptocurrency network and does not transmit real money. All transactions, balances and miners exist only inside the simulation.

Storage is file-based (CSV download from the GUI for log export). No database server is required.
