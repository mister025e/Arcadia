from ursina import Entity, color


class World:
    """
    Creates the floor, border walls, and cover blocks.
    Collects them in a single list to enable/disable as needed.
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
        # Four walls: just outside ±20 units
        top = Entity(
            model='cube',
            color=color.dark_gray,
            scale=(40, 1, 1),
            position=(0, 0.5, 20.5),
            collider='box',
            tag='wall'
        )
        bottom = Entity(
            model='cube',
            color=color.dark_gray,
            scale=(40, 1, 1),
            position=(0, 0.5, -20.5),
            collider='box',
            tag='wall'
        )
        right = Entity(
            model='cube',
            color=color.dark_gray,
            scale=(1, 1, 40),
            position=(20.5, 0.5, 0),
            collider='box',
            tag='wall'
        )
        left = Entity(
            model='cube',
            color=color.dark_gray,
            scale=(1, 1, 40),
            position=(-20.5, 0.5, 0),
            collider='box',
            tag='wall'
        )
        self.entities.extend([top, bottom, right, left])

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
