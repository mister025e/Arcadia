from ursina import Entity, Text, Button, color


class InstructionsScreen:
    """
    Full-screen overlay showing game controls/instructions, plus a Back button.
    """

    def __init__(self, ui_parent, on_back):
        self.on_back = on_back

        # Semi-transparent background
        self.instructions_panel = Entity(
            parent=ui_parent,
            model='quad',
            color=color.rgba(0, 0, 0, 0.6),
            scale=(1, 1),
            enabled=False
        )

        # Title
        self.title_text = Text(
            parent=ui_parent,
            text='Instructions',
            scale=2,
            position=(0, 0.4),
            color=color.white,
            enabled=False
        )

        # Body instructions
        self.body_text = Text(
            parent=ui_parent,
            text=(
                "Player 1 (Blue):\n"
                "  Move: Joystick #1\n"
                "  Shoot: Button A\n\n"
                "Player 2 (Orange):\n"
                "  Move: Joystick #2\n"
                "  Shoot: Button A\n\n"
                "Menu Nav:\n"
                "  P1 Stick UP/DOWN to move\n"
                "  P1 Button A to select\n\n"
                "Save Score:\n"
                "  Stick UP/DOWN to change letter\n"
                "  Stick LEFT/RIGHT to change slot\n"
                "  Button A to confirm\n"
            ),
            position=(0, 0),
            origin=(0, 0),
            scale=1.2,
            color=color.white,
            enabled=False,
            line_height=1.3
        )

        # Back button
        self.btn_back = Button(
            parent=ui_parent,
            text='Back',
            scale=(0.2, 0.1),
            position=(0, -0.4, 0),
            color=color.azure,
            on_click=on_back,
            enabled=False
        )

        self.buttons = [self.btn_back]

    def show(self):
        self.instructions_panel.enabled = True
        self.title_text.enabled = True
        self.body_text.enabled = True
        self.btn_back.enabled = True

    def hide(self):
        self.instructions_panel.enabled = False
        self.title_text.enabled = False
        self.body_text.enabled = False
        self.btn_back.enabled = False