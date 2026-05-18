"""
tests/test_regression.py
Runnable regression tests for hs_agent.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env.grid_world import GridWorld
from agents.hs_agent import HSAgent
from agents.compressor import compress_memory

def run_hs_on_level(level_name):
    env = GridWorld(level_name)
    agent = HSAgent(debug=False)
    state = env.reset()
    done = False
    steps = 0
    while not done and steps < 60:
        action, reason, _ = agent.choose_action(state, level_name)
        state, done, info = env.step(action, reason=reason)
        steps += 1
    return info.get("success", False), info.get("failure_reason", ""), steps

def main():
    tests = [
        ("level_1", "level_1_simple_path"),
        ("level_2", "level_2_trap"),
        ("level_3", "level_3_key_door"),
        ("level_5", "level_5_conflict"),
    ]
    all_pass = True
    print("Running regression tests...")
    for name, lvl in tests:
        success, fail, steps = run_hs_on_level(lvl)
        status = "PASS" if success else "FAIL"
        print(f"{status}: {name} - {'solved' if success else fail}")
        if not success: all_pass = False
    if all_pass:
        print("\nALL BASIC TESTS PASSED")
        sys.exit(0)
    else:
        print("\nSOME TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
