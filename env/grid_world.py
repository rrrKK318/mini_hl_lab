"""
env/grid_world.py
Deterministic text-based grid world environment.
"""
import copy
from env.levels import get_level

DIRECTIONS = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
    "wait": (0, 0),
}

class GridWorld:
    def __init__(self, level_name):
        self.level_name = level_name
        self.grid = [list(row) for row in get_level(level_name)]
        self.rows = len(self.grid)
        self.cols = len(self.grid[0]) if self.rows > 0 else 0
        self.reset()

    def reset(self):
        self.agent_pos = self._find_pos('S')
        self.goal_pos = self._find_pos('G')
        self.key_pos = self._find_pos('K')
        self.door_pos = self._find_pos('D')
        self.trap_positions = self._find_all('T')
        self.enemy_positions = self._find_all('E')
        self.bonus_positions = self._find_all('B')
        self.mud_positions = self._find_all('M')
        self.has_key = False
        self.door_open = False
        self.steps = 0
        self.score = 0
        self.done = False
        self.success = False
        self.failure_reason = ""
        self.path_replay = []
        self.enemy_direction = 1
        self.max_steps = 50
        self.collected_bonus = set()
        return self._get_state()

    def _find_pos(self, symbol):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == symbol:
                    return (r, c)
        return None

    def _find_all(self, symbol):
        positions = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == symbol:
                    positions.append((r, c))
        return positions

    def _get_state(self):
        state = {
            "level_name": self.level_name,
            "agent_pos": self.agent_pos,
            "goal_pos": self.goal_pos,
            "key_pos": self.key_pos if not self.has_key else None,
            "door_pos": self.door_pos if not self.door_open else None,
            "trap_positions": self.trap_positions,
            "enemy_positions": self._get_current_enemy_positions(),
            "bonus_positions": [b for b in self.bonus_positions if b not in self.collected_bonus],
            "mud_positions": self.mud_positions,
            "has_key": self.has_key,
            "door_open": self.door_open,
            "steps": self.steps,
            "score": self.score,
            "grid": [row[:] for row in self.grid],
        }
        return state

    def _get_current_enemy_positions(self):
        current_enemies = []
        for i, (er, ec) in enumerate(self.enemy_positions):
            move = (self.steps // 2) % 2
            new_c = ec + (move * 2 - 1) * self.enemy_direction
            if new_c < 0 or new_c >= self.cols or self.grid[er][new_c] == '#':
                new_c = ec
            current_enemies.append((er, new_c))
        return current_enemies

    def get_valid_actions(self):
        return ["up", "down", "left", "right", "wait", "pickup", "open"]

    def step(self, action, reason=""):
        if self.done:
            return self._get_state(), self.done, self._get_info()

        self.steps += 1
        old_pos = self.agent_pos
        dr, dc = DIRECTIONS.get(action, (0, 0))
        new_r = self.agent_pos[0] + dr
        new_c = self.agent_pos[1] + dc

        moved = False
        if action in ["up", "down", "left", "right"]:
            if 0 <= new_r < self.rows and 0 <= new_c < self.cols and self.grid[new_r][new_c] != '#':
                self.agent_pos = (new_r, new_c)
                moved = True
        elif action == "wait":
            pass
        elif action == "pickup":
            if self.agent_pos == self.key_pos and not self.has_key:
                self.has_key = True
                self.key_pos = None
                self.score += 10
            elif self.agent_pos in self.bonus_positions and self.agent_pos not in self.collected_bonus:
                self.collected_bonus.add(self.agent_pos)
                self.score += 5
        elif action == "open":
            if self.agent_pos == self.door_pos and self.has_key and not self.door_open:
                self.door_open = True
                self.score += 5

        current_enemy_pos = self._get_current_enemy_positions()
        failure = None
        if self.agent_pos in self.trap_positions:
            failure = "stepped_on_trap"
        elif self.agent_pos in current_enemy_pos:
            failure = "collided_with_enemy"
        elif self.steps > self.max_steps:
            failure = "max_steps_exceeded"

        if failure:
            self.done = True
            self.success = False
            self.failure_reason = failure
            self.score -= 50
        else:
            if self.agent_pos == self.goal_pos:
                self.done = True
                self.success = True
                self.failure_reason = ""
                self.score += 100
            if self.agent_pos in self.mud_positions:
                self.score -= 1
            self.score -= 1

        self.path_replay.append({
            "step": self.steps,
            "pos": self.agent_pos,
            "action": action,
            "reason": reason,
            "has_key": self.has_key,
            "score": self.score,
            "terminal": self.done
        })

        info = self._get_info()
        return self._get_state(), self.done, info

    def _get_info(self):
        return {
            "success": self.success,
            "score": self.score,
            "steps": self.steps,
            "failure_reason": self.failure_reason,
            "path_replay": copy.deepcopy(self.path_replay),
            "has_key": self.has_key,
            "door_open": self.door_open,
        }

    def render(self):
        g = [row[:] for row in self.grid]
        ar, ac = self.agent_pos
        g[ar][ac] = 'A'
        for er, ec in self._get_current_enemy_positions():
            if 0 <= er < self.rows and 0 <= ec < self.cols:
                g[er][ec] = 'E'
        return '\n'.join(''.join(row) for row in g)
