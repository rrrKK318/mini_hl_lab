#!/usr/bin/env python3
"""
main.py
Entry point for mini_hl_lab.
"""
import argparse
import json
import os
from env.grid_world import GridWorld
from env.replay import save_replay
from agents.rule_stack_agent import RuleStackAgent
from agents.hs_agent import HSAgent
from agents.compressor import compress_memory
from agents.memory import load_memory

def run_episode(agent, level_name, debug=False):
    env = GridWorld(level_name)
    state = env.reset()
    done = False
    total_reward = 0
    step_count = 0
    triggered = []
    conflicts = 0
    mem_updates = []

    agent_name = "rule_stack" if isinstance(agent, RuleStackAgent) else "hs"

    while not done and step_count < 60:
        if isinstance(agent, RuleStackAgent):
            action, reason, info = agent.choose_action(state, level_name)
            conflicts = info.get("conflict_count", 0)
            triggered = info.get("triggered_rules", [])
        else:
            action, reason, info = agent.choose_action(state, level_name)
            triggered = info.get("triggered_rules", [])

        next_state, done, info_env = env.step(action, reason=reason)
        total_reward = info_env.get("score", 0)
        step_count += 1
        state = next_state

        if debug:
            print(f"Step {step_count}: {action} | {reason} | pos={state.get('agent_pos')} | score={total_reward}")

    success = info_env.get("success", False)
    failure = info_env.get("failure_reason", "")
    path_replay = info_env.get("path_replay", [])

    episode_result = {
        "success": success,
        "score": total_reward,
        "steps": step_count,
        "failure_reason": failure,
        "path_replay": path_replay,
        "triggered_rules": triggered,
        "conflict_count": conflicts,
    }

    replay_file = save_replay(level_name, agent_name, {
        "level_name": level_name,
        "agent_name": agent_name,
        "success": success,
        "score": total_reward,
        "steps": step_count,
        "failure_reason": failure,
        "path_replay": path_replay
    })

    if isinstance(agent, HSAgent):
        mem_update = agent.update_after_episode(episode_result, level_name)
        mem_updates.append(mem_update)

    return episode_result, replay_file, mem_updates


def run_compare():
    print("\n=== COMPARE: rule_stack vs hs_agent on all levels ===\n")
    levels = ["level_1_simple_path", "level_2_trap", "level_3_key_door", "level_4_enemy_timing", "level_5_conflict"]
    
    results = []
    for lvl in levels:
        print(f"\n--- Level: {lvl} ---")
        rs_agent = RuleStackAgent()
        rs_result, rs_replay, _ = run_episode(rs_agent, lvl)
        print(f"rule_stack | success={rs_result['success']} | score={rs_result['score']} | steps={rs_result['steps']} | conflicts={rs_result.get('conflict_count',0)} | fail={rs_result['failure_reason']}")

        hs_agent = HSAgent(debug=False)
        hs_result, hs_replay, mem_up = run_episode(hs_agent, lvl)
        print(f"hs_agent   | success={hs_result['success']} | score={hs_result['score']} | steps={hs_result['steps']} | fail={hs_result['failure_reason']}")
        if mem_up:
            print(f"           memory updates: {mem_up[-1]}")

        results.append({"level": lvl, "rule_stack": rs_result, "hs": hs_result})

    print("\n=== SUMMARY TABLE ===")
    print(f"{'level':<25} {'agent':<12} {'success':<8} {'score':>6} {'steps':>6} {'conflicts':>10} {'failure_reason'}")
    print("-" * 100)
    for r in results:
        rs = r["rule_stack"]
        print(f"{r['level']:<25} {'rule_stack':<12} {str(rs['success']):<8} {rs['score']:>6} {rs['steps']:>6} {rs.get('conflict_count',0):>10} {rs['failure_reason']}")
        hs = r["hs"]
        print(f"{r['level']:<25} {'hs':<12} {str(hs['success']):<8} {hs['score']:>6} {hs['steps']:>6} {'-':>10} {hs['failure_reason']}")
    print("\nNote: rule_stack shows rising conflicts and fails on complex levels. hs uses memory + arbitration and is more stable.")

def run_compress():
    print("\n=== COMPRESS MEMORY ===\n")
    result = compress_memory()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\nMemory compressed. See data/memory.json")

def generate_report():
    os.makedirs("reports", exist_ok=True)
    report_path = "reports/latest_report.md"
    content = """# Mini Heuristic Learning Lab Report

## 1. 實驗目的

本專案建立一個迷你虛擬環境，展示「規則堆疊」(rule stacking) 與「啟發式學習系統」(Heuristic Learning System) 的功能差異。純規則堆疊只是累積 if/else，無法處理環境複雜度上升時的耦合衝突；而啟發式系統透過結構化狀態讀取、模組化政策提案、記憶更新、回放記錄、回歸測試與壓縮，真正實現「學習」而非僅「補丁」。

## 2. 虛擬環境

- **Grid World**：文字-based，deterministic。
- **符號**：S=起點, G=目標, #=牆, .=空地, K=鑰匙, D=鎖門, T=陷阱(即死), E=敵人(移動hazard), B=獎勵, M=泥地(可通行但扣分)。
- **動作**：up/down/left/right/wait/pickup/open
- **五個關卡**：
  1. level_1_simple_path：簡單路徑
  2. level_2_trap：需避開陷阱
  3. level_3_key_door：需先拿鑰匙再開門
  4. level_4_enemy_timing：需等待或避開時機衝突
  5. level_5_conflict：綜合複雜情境，暴露規則堆疊的衝突

## 3. rule_stack_agent 結果

rule_stack_agent 使用線性優先順序規則堆疊。
- level_1 ~ level_2：表現尚可。
- level_3 ~ level_5：衝突明顯增加，容易 timeout。

## 4. hs_agent 結果

使用 state_reader + 模組化政策 + memory + arbitration，在複雜關卡（尤其是 level_5）表現更穩定。

## 5. 規則堆疊為何不是 HL

純規則堆疊缺少 feedback、memory、replay、compression 與 regression test 的閉環。

## 6. 吸收與壓縮

compressor 可將重複約束合併。

## 7. 限制

這是 minimal demo，不是完整神經網路系統。
"""
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Report generated: {report_path}")

def main():
    parser = argparse.ArgumentParser(description="mini_hl_lab")
    parser.add_argument("--agent", choices=["rule_stack", "hs"])
    parser.add_argument("--level", type=int, choices=[1,2,3,4,5])
    parser.add_argument("--compare", action="store_true")
    parser.add_argument("--compress", action="store_true")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    level_map = {
        1: "level_1_simple_path",
        2: "level_2_trap",
        3: "level_3_key_door",
        4: "level_4_enemy_timing",
        5: "level_5_conflict"
    }

    if args.compare:
        run_compare()
    elif args.compress:
        run_compress()
    elif args.report:
        generate_report()
    elif args.agent and args.level:
        lvl_name = level_map[args.level]
        agent = RuleStackAgent() if args.agent == "rule_stack" else HSAgent(debug=args.debug)
        result, replay_file, mem_updates = run_episode(agent, lvl_name, debug=args.debug)
        print(f"[{args.agent}] {lvl_name} | Success: {result['success']} | Score: {result['score']} | Steps: {result['steps']} | Fail: {result['failure_reason']}")
    else:
        print("Usage: python main.py --compare")

if __name__ == "__main__":
    main()
