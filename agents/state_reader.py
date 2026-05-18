"""
agents/state_reader.py
Converts raw grid state into structured readable state.
"""
import math

def read_state(raw_state):
    if not raw_state:
        return {}

    agent = raw_state.get("agent_pos", (0,0))
    goal = raw_state.get("goal_pos", (0,0))
    key_pos = raw_state.get("key_pos")
    door_pos = raw_state.get("door_pos")
    traps = raw_state.get("trap_positions", [])
    enemies = raw_state.get("enemy_positions", [])
    bonuses = raw_state.get("bonus_positions", [])
    muds = raw_state.get("mud_positions", [])
    has_key = raw_state.get("has_key", False)

    def manhattan(p1, p2):
        if not p1 or not p2:
            return 999
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    def get_neighbors(pos):
        r, c = pos
        return [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]

    safe_neighbors = []
    immediate_risk_actions = []
    for action, (dr, dc) in [("up",(-1,0)), ("down",(1,0)), ("left",(0,-1)), ("right",(0,1))]:
        nr, nc = agent[0] + dr, agent[1] + dc
        npos = (nr, nc)
        risk = False
        if npos in traps or npos in enemies:
            risk = True
            immediate_risk_actions.append(action)
        if not risk:
            safe_neighbors.append((action, npos))

    reachable_targets = []
    if key_pos:
        reachable_targets.append(("key", key_pos, manhattan(agent, key_pos)))
    if door_pos and has_key:
        reachable_targets.append(("door", door_pos, manhattan(agent, door_pos)))
    reachable_targets.append(("goal", goal, manhattan(agent, goal)))

    state = {
        "agent_pos": agent,
        "goal_pos": goal,
        "key_pos": key_pos,
        "door_pos": door_pos,
        "trap_positions": traps,
        "enemy_positions": enemies,
        "bonus_positions": bonuses,
        "mud_positions": muds,
        "has_key": has_key,
        "safe_neighbors": safe_neighbors,
        "immediate_risk_actions": list(set(immediate_risk_actions)),
        "estimated_distance_to_goal": manhattan(agent, goal),
        "estimated_distance_to_key": manhattan(agent, key_pos) if key_pos else 0,
        "estimated_distance_to_door": manhattan(agent, door_pos) if door_pos else 0,
        "reachable_targets": reachable_targets,
        "raw_grid_snapshot": raw_state.get("grid", []),
    }
    return state
