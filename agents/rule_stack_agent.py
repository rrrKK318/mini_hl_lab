"""
agents/rule_stack_agent.py
Plain accumulating rule system using linear ordered rules.
"""
class RuleStackAgent:
    def __init__(self):
        self.rule_count = 8
        self.conflict_count = 0
        self.triggered_rules = []
        self.chosen_action = None
        self.reason = ""

    def choose_action(self, raw_state, level_name=""):
        self.triggered_rules = []
        self.conflict_count = 0
        agent_pos = raw_state.get("agent_pos", (0,0))
        goal_pos = raw_state.get("goal_pos", (0,0))
        key_pos = raw_state.get("key_pos")
        door_pos = raw_state.get("door_pos")
        traps = raw_state.get("trap_positions", [])
        enemies = raw_state.get("enemy_positions", [])
        bonuses = raw_state.get("bonus_positions", [])
        has_key = raw_state.get("has_key", False)
        muds = raw_state.get("mud_positions", [])

        def dir_toward(target):
            if not target: return "right"
            ar, ac = agent_pos
            tr, tc = target
            if tr < ar: return "up"
            if tr > ar: return "down"
            if tc < ac: return "left"
            if tc > ac: return "right"
            return "wait"

        action = "wait"
        reason = "default wait"

        trap_ahead = any(abs(t[0] - agent_pos[0]) + abs(t[1] - agent_pos[1]) == 1 for t in traps)
        if trap_ahead:
            self.triggered_rules.append("avoid_trap")
            action = "wait"
            reason = "Avoid trap ahead (rule 1)"

        enemy_near = any(abs(e[0]-agent_pos[0])+abs(e[1]-agent_pos[1]) <= 1 for e in enemies)
        if enemy_near and "avoid_trap" not in self.triggered_rules:
            self.triggered_rules.append("avoid_enemy")
            action = "wait"
            reason = "Avoid enemy (rule 2)"

        if not has_key and key_pos and not trap_ahead and not enemy_near:
            self.triggered_rules.append("go_to_key")
            action = dir_toward(key_pos)
            reason = f"Go to key at {key_pos} (rule 3)"

        if has_key and door_pos and abs(door_pos[0]-agent_pos[0])+abs(door_pos[1]-agent_pos[1]) <= 1:
            self.triggered_rules.append("open_door")
            action = "open"
            reason = "Open door with key (rule 4)"

        if bonuses and not trap_ahead:
            bonus_near = any(abs(b[0]-agent_pos[0])+abs(b[1]-agent_pos[1]) <= 1 for b in bonuses)
            if bonus_near:
                self.triggered_rules.append("collect_bonus")
                action = "pickup"
                reason = "Collect bonus (rule 6)"
                self.conflict_count += 1

        if action == "wait" or (has_key or not door_pos):
            self.triggered_rules.append("go_to_goal")
            action = dir_toward(goal_pos)
            reason = f"Move toward goal (rule 7)"

        if not self.triggered_rules:
            self.triggered_rules.append("fallback_wait")
            action = "wait"
            reason = "Fallback (rule 8)"

        self.chosen_action = action
        self.reason = reason
        return action, reason, {"rule_count": self.rule_count, "conflict_count": self.conflict_count, "triggered_rules": self.triggered_rules[:] }
