from ursina import Text, Vec2, color


class HUD:
    """
    Displays the timer and each player’s HP in the corners.
    """

    def __init__(self):
        # Timer at top center
        self.timer_text = Text(
            parent=None,  # will attach after Ursina app is created
            text='Time: 0.0s',
            position=Vec2(0, 0.48),
            origin=(0, 0),
            scale=1.5,
            color=color.white,
            enabled=False
        )
        # P1 HP top-left
        self.p1_hp_text = Text(
            parent=None,
            text='P1 HP: 100',
            position=Vec2(-0.45, 0.45),
            scale=1.5,
            color=color.white,
            enabled=False
        )
        # P2 HP top-right
        self.p2_hp_text = Text(
            parent=None,
            text='P2 HP: 100',
            position=Vec2(0.45, 0.45),
            scale=1.5,
            color=color.white,
            enabled=False
        )

    def attach_to_ui(self, ui_parent):
        """
        After Ursina ‘app’ is created, call hud.attach_to_ui(camera.ui)
        so all Texts are children of camera.ui.
        """
        self.timer_text.parent = ui_parent
        self.p1_hp_text.parent = ui_parent
        self.p2_hp_text.parent = ui_parent

    def enable(self):
        self.timer_text.enabled = True
        self.p1_hp_text.enabled = True
        self.p2_hp_text.enabled = True

    def disable(self):
        self.timer_text.enabled = False
        self.p1_hp_text.enabled = False
        self.p2_hp_text.enabled = False

    def update(self, elapsed, p1_hp, p2_hp):
        """
        Call every frame (if game_state == 'playing'):
        - elapsed: float seconds since match start
        - p1_hp, p2_hp: current health integers
        """
        self.timer_text.text = f'Time: {elapsed:.1f}s'
        self.p1_hp_text.text = f'P1 HP: {p1_hp}'
        self.p2_hp_text.text = f'P2 HP: {p2_hp}'
