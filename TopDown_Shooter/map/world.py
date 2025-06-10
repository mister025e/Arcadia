import random
import math
from ursina import Entity, color

class World:
    """
    Creates the floor, four border walls, and a set of dynamically placed red cover blocks.
    Covers avoid any positions in exclude_positions (player spawns), are 8+ units apart,
    and there are between 4 and 6 of them each run.
    """

    def __init__(self, exclude_positions=None):
        self.entities = []
        self.exclude_positions = exclude_positions or []
        self._create_floor()
        self._create_borders()
        self._create_covers()

    def _create_floor(self):
        floor = Entity(
            model='plane',
            scale=(40, 1, 40),
            texture='white_cube',
            texture_scale=(40, 40),
            color=color.gray,
            collider='box'
        )
        self.entities.append(floor)

    def _create_borders(self):
        wall_specs = [
            ((0,1,11.5),(40,2,1)),
            ((0,1,-11.5),(40,2,1)),
            ((20.5,1,0),(1,2,40)),
            ((-20.5,1,0),(1,2,40)),
        ]
        for pos, scale in wall_specs:
            wall = Entity(
                model='cube',
                color=color.dark_gray,
                scale=scale,
                position=pos,
                collider='box',
                tag='wall'
            )
            self.entities.append(wall)

    def _create_covers(self):
        # Possible grid points
        xs = list(range(-15, 16, 5))   # -15, -10, -5, 0, 5, 10, 15
        zs = list(range(-8, 9, 4))     # -8, -4, 0, 4, 8
        candidates = [(x, 0.5, z) for x in xs for z in zs]

        # Exclude any too‐close to spawn positions
        def too_close_to_spawn(pos):
            x, _, z = pos
            for sx, sz in self.exclude_positions:
                if abs(x - sx) < 2 and abs(z - sz) < 2:
                    return True
            return False

        safe = [pos for pos in candidates if not too_close_to_spawn(pos)]

        # Decide how many covers: 4 to 6
        target = random.randint(4, 6)
        selected = []
        attempts = 0

        # Greedy random packing with minimum 8‐unit separation
        while len(selected) < target and attempts < 1000:
            pos = random.choice(safe)
            # Check 8‐unit min distance from existing selection
            if all(math.hypot(pos[0] - s[0], pos[2] - s[2]) >= 8 for s in selected):
                selected.append(pos)
                safe.remove(pos)  # don't pick same one again
            attempts += 1

        # Instantiate covers
        for pos in selected:
            cover = Entity(
                model='cube',
                color=color.red,
                scale=(2, 1, 2),
                position=pos,
                collider='box',
                tag='cover'
            )
            self.entities.append(cover)
