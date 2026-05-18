"""
agents/policy_modules.py
Modular policies for hs_agent.
"""
from agents.state_reader import read_state

def _dir_toward(agent, target):
    if not target:
        return "right"
    ar, ac = agent
    tr, tc = target
    if tr < ar: return "up"
    if tr > ar: return "down"
    if tc < ac: return "left"
    if tc > ac: return "right"
    return "wait"

def safety_policy(state):
    risks = state.get("immediate_risk_actions", [])
    if risks:
        return {
            "policy": "safety",
            "action": "wait",
            "reason": "Immediate lethal risk detected, waiting or avoiding",
            "confidence": 0.95,
            "risk": 0.9
        }
    return None

def key_door_policy(state):
    has_key = state.get("has_key", False)
    key_pos = state.get("key_pos")
    door_pos = state.get("door_pos")
    agent = state.get("agent_pos")
    if not has_key and key_pos:
        dist = state.get("estimated_distance_to_key", 999)
        if dist < 15:
            action = _dir_toward(agent, key_pos)
            return {"policy": "key_door", "action": action, "reason": f"Need key at {key_pos}, moving toward it", "confidence": 0.85, "risk": 0.2}
    if has_key and door_pos:
        action = _dir_toward(agent, door_pos)
        return {"policy": "key_door", "action": action, "reason": "Has key, heading to door", "confidence": 0.8, "risk": 0.15}
    return None

def enemy_avoidance_policy(state):
    enemies = state.get("enemy_positions", [])
    if enemies:
        return {"policy": "enemy_avoidance", "action": "wait", "reason": "Enemy nearby, waiting for safe timing", "confidence": 0.75, "risk": 0.6}
    return None

def navigation_policy(state):
    goal_dist = state.get("estimated_distance_to_goal", 999)
    goal_pos = state.get("goal_pos")
    agent = state.get("agent_pos")
    if goal_dist < 30 and goal_pos:
        action = _dir_toward(agent, goal_pos)
        return {"policy": "navigation", "action": action, "reason": f"Progressing toward goal (dist~{goal_dist})", "confidence": 0.6, "risk": 0.3}
    return None

def bonus_policy(state):
    bonuses = state.get("bonus_positions", [])
    agent = state.get("agent_pos")
    if bonuses:
        action = _dir_toward(agent, bonuses[0])
        return {"policy": "bonus", "action": action, "reason": "Bonus visible, considering collection", "confidence": 0.5, "risk": 0.4}
    return None

def fallback_policy(state):
    return {"policy": "fallback", "action": "wait", "reason": "No strong proposal, waiting safely", "confidence": 0.3, "risk": 0.5}

POLICIES = [safety_policy, key_door_policy, enemy_avoidance_policy, navigation_policy, bonus_policy, fallback_policy]
