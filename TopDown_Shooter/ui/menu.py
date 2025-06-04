from ursina import Entity, Button, color, Text


class MainMenu:
    """
    Full screen semi‐transparent quad with four buttons:
      - Play
      - Instructions
      - Leaderboard
      - Quit
    """

    def __init__(self, ui_parent, on_play, on_instructions, on_leaderboard, on_quit):
        # background panel
        self.menu_panel = Entity(
            parent=ui_parent,
            model='quad',
            color=color.rgba(0, 0, 0, 0.6),
            scale=(1, 1),
            enabled=False
        )

        # Title text
        self.title = Text(
            parent=ui_parent,
            text='Top-Down Shooter',
            scale=2,
            position=(0, 0.4),
            color=color.white,
            enabled=False
        )

        # Play button
        self.btn_play = Button(
            parent=ui_parent,
            text='Play',
            scale=(0.25, 0.1),
            position=(0, 0.15, 0),
            color=color.azure,
            on_click=on_play,
            enabled=False
        )

        # Instructions button
        self.btn_instructions = Button(
            parent=ui_parent,
            text='Instructions',
            scale=(0.25, 0.1),
            position=(0, 0.0, 0),
            color=color.yellow,
            on_click=on_instructions,
            enabled=False
        )

        # Leaderboard button
        self.btn_leaderboard = Button(
            parent=ui_parent,
            text='Leaderboard',
            scale=(0.25, 0.1),
            position=(0, -0.15, 0),
            color=color.violet,
            on_click=on_leaderboard,
            enabled=False
        )

        # Quit button
        self.btn_quit = Button(
            parent=ui_parent,
            text='Quit',
            scale=(0.25, 0.1),
            position=(0, -0.30, 0),
            color=color.red,
            on_click=on_quit,
            enabled=False
        )

        # Ordered list for keyboard navigation (top to bottom)
        self.buttons = [
            self.btn_play,
            self.btn_instructions,
            self.btn_leaderboard,
            self.btn_quit
        ]

    def show(self):
        self.menu_panel.enabled = True
        self.title.enabled = True
        for btn in self.buttons:
            btn.enabled = True

    def hide(self):
        self.menu_panel.enabled = False
        self.title.enabled = False
        for btn in self.buttons:
            btn.enabled = False