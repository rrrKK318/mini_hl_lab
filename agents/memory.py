"""
agents/memory.py
Persistent memory for hs_agent.
"""
import json
import os

MEMORY_FILE = "data/memory.json"

DEFAULT_MEMORY = {
    "failed_cases": [],
    "successful_cases": [],
    "learned_constraints": [],
    "golden_traces": [],
    "known_bad_rules": [],
    "version_notes": ["Initial mini HL memory v0.1"]
}

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        save_memory(DEFAULT_MEMORY)
        return DEFAULT_MEMORY.copy()
    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return DEFAULT_MEMORY.copy()

def save_memory(mem):
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(mem, f, indent=2, ensure_ascii=False)

def update_memory(mem, episode_result, level_name, agent_name="hs"):
    success = episode_result.get("success", False)
    failure = episode_result.get("failure_reason", "")
    score = episode_result.get("score", 0)
    steps = episode_result.get("steps", 0)

    case = {"level": level_name, "success": success, "failure_reason": failure, "score": score, "steps": steps}

    if success:
        mem["successful_cases"].append(case)
        if level_name not in [g.get("level") for g in mem.get("golden_traces", [])]:
            mem.setdefault("golden_traces", []).append({"level": level_name, "trace_summary": f"Solved {level_name} in {steps} steps"})
    else:
        mem["failed_cases"].append(case)
        if "trap" in failure:
            c = "reject actions with immediate lethal next-state risk (trap)"
            if c not in mem["learned_constraints"]: mem["learned_constraints"].append(c)
        elif "enemy" in failure:
            c = "timing-sensitive enemy risk must be evaluated before navigation"
            if c not in mem["learned_constraints"]: mem["learned_constraints"].append(c)
        elif "key" in failure or "door" in failure:
            c = "key must be obtained before attempting door"
            if c not in mem["learned_constraints"]: mem["learned_constraints"].append(c)

    save_memory(mem)
    return mem

def get_constraints(mem):
    return mem.get("learned_constraints", [])
