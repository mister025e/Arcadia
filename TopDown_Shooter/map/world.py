from ursina import Entity, color

class World:
    """
    Creates the floor, four border walls (north, south, east, west) at ±20.5, and cover blocks.
    Collects them in a single list so GameManager can enable/disable them at once.
    """

    def __init__(self):
        self.entities = []
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
        # Place each border at ±20.5 so it sits just outside the 40×40 floor (±20).
        # Left and right were already at x = ±20.5; now top and bottom at z = ±20.5.

        # North / top edge (z = +20.5)
        north_wall = Entity(
            model='cube',
            color=color.dark_gray,
            scale=(40, 2, 1),      # length_x = 40, height_y = 2, thickness_z = 1
            position=(0, 1, 11.5),  # y = 1 so it sits on top of floor, z = 20.5 just beyond floor edge
            collider='box',
            tag='wall'
        )
        # South / bottom edge (z = -20.5)
        south_wall = Entity(
            model='cube',
            color=color.dark_gray,
            scale=(40, 2, 1),
            position=(0, 1, -11.5),
            collider='box',
            tag='wall'
        )
        # East / right edge (x = +20.5)
        east_wall = Entity(
            model='cube',
            color=color.dark_gray,
            scale=(1, 2, 40),      # thickness_x = 1, height_y = 2, length_z = 40
            position=(20.5, 1, 0),
            collider='box',
            tag='wall'
        )
        # West / left edge (x = -20.5)
        west_wall = Entity(
            model='cube',
            color=color.dark_gray,
            scale=(1, 2, 40),
            position=(-20.5, 1, 0),
            collider='box',
            tag='wall'
        )

        self.entities.extend([north_wall, south_wall, east_wall, west_wall])

    def _create_covers(self):
        cover_positions = [
            (5, 0.5, 0),
            (-5, 0.5, 0),
            (0, 0.5, 5),
            (0, 0.5, -5),
            (5, 0.5, 5),
            (-5, 0.5, -5),
        ]
        for pos in cover_positions:
            c = Entity(
                model='cube',
                color=color.brown,
                scale=(2, 1, 2),
                position=pos,
                collider='box',
                tag='wall'
            )
            self.entities.append(c)