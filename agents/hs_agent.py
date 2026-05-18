"""
agents/hs_agent.py
Heuristic System agent using state_reader, policy_modules, memory.
"""
from agents.state_reader import read_state
from agents.policy_modules import POLICIES
from agents.memory import load_memory, update_memory, get_constraints

class HSAgent:
    def __init__(self, debug=False):
        self.debug = debug
        self.memory = load_memory()
        self.rule_count = 0
        self.conflict_count = 0
        self.memory_updates = []
        self.triggered_rules = []

    def choose_action(self, raw_state, level_name=""):
        state = read_state(raw_state)
        proposals = []
        for policy_fn in POLICIES:
            prop = policy_fn(state)
            if prop:
                proposals.append(prop)

        if self.debug:
            print(f"[HS] Proposals: {[p['policy'] for p in proposals]}")

        selected = None
        reason = ""
        constraints = get_constraints(self.memory)
        bonus_suppressed = any("bonus collection cannot override survival" in c for c in constraints)

        for p in proposals:
            pol = p["policy"]
            if pol == "safety" and p.get("risk", 0.5) < 0.3:
                selected = p
                reason = p["reason"]
                break
            if pol == "enemy_avoidance":
                selected = p
                reason = p["reason"]
                break
            if pol == "key_door":
                selected = p
                reason = p["reason"]
                break

        if not selected:
            for p in proposals:
                if p["policy"] == "navigation":
                    selected = p
                    reason = p["reason"]
                    break
                if p["policy"] == "bonus" and not bonus_suppressed:
                    selected = p
                    reason = p["reason"]
                    break

        if not selected:
            for p in proposals:
                if p["policy"] == "fallback":
                    selected = p
                    reason = p["reason"]
                    break

        if not selected and proposals:
            selected = proposals[0]
            reason = selected["reason"]
        if not selected:
            selected = {"policy": "fallback", "action": "wait", "reason": "Emergency fallback", "confidence": 0.1, "risk": 0.5}

        action = selected["action"]
        self.triggered_rules = [selected["policy"]]
        self.chosen_action = action
        self.reason = reason

        mem_ref = f"constraints_active={len(constraints)}" if constraints else "no_constraints_yet"
        return action, reason, {"proposals": proposals, "selected": selected, "memory_ref": mem_ref}

    def update_after_episode(self, episode_result, level_name):
        self.memory = update_memory(self.memory, episode_result, level_name)
        self.memory_updates.append({"level": level_name, "success": episode_result.get("success"), "failure": episode_result.get("failure_reason")})
        return self.memory_updates[-1]
