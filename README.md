# mini_hl_lab

Mini Heuristic Learning Virtual Environment Lab

Demonstrates why plain **rule stacking** fails as environment complexity increases, and why a real **Heuristic System** requires feedback loops, memory, replay, regression tests, and compression.

## Quick Start

```bash
cd mini_hl_lab

# Run single agent
python main.py --agent rule_stack --level 1
python main.py --agent hs --level 5 --debug

# Full comparison (key demo)
python main.py --compare

# Compress memory & constraints
python main.py --compress

# Generate Traditional Chinese report
python main.py --report

# Run regression tests
python tests/test_regression.py
```

## Key Demonstration

- `rule_stack_agent`: Linear if/elif rules. Works on simple levels, **conflict_count rises** and fails on level_5 due to coupled rules (bonus vs survival, timing vs navigation).
- `hs_agent`: Uses `state_reader` + modular `policy_modules` (safety first, then key/door dependency, then navigation) + `memory` + `replay` + `compressor`. More stable on complex levels.

## Why rule stacking ≠ Heuristic Learning

Rule stacking only adds patches.  
Heuristic Learning connects **feedback → memory update → constraint compression → regression testing → replay**.

This minimal lab makes the difference **executable and visible**.

## Project Structure

```
mini_hl_lab/
├── main.py
├── env/
│   ├── grid_world.py
│   ├── levels.py
│   └── replay.py
├── agents/
│   ├── rule_stack_agent.py
│   ├── hs_agent.py
│   ├── state_reader.py
│   ├── policy_modules.py
│   ├── memory.py
│   └── compressor.py
├── tests/
│   └── test_regression.py
├── data/
│   ├── memory.json
│   └── replays/
└── reports/
    └── latest_report.md
```

## Limitations (honest)

- Not a neural net / gradient descent
- Not proof of scalability
- Minimal demo to experience the mechanism

Run `python main.py --compare` to see the concrete difference.
