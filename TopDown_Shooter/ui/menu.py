from ursina import Entity, Button, color, Text

class MainMenu:
    def __init__(self, ui_parent, on_play, on_settings, on_instructions, on_leaderboard, on_quit):
        self.menu_panel = Entity(
            parent=ui_parent, model='quad',
            color=color.rgba(0,0,0,0.6), scale=(1,1), enabled=False)

        self.title = Text(
            parent=ui_parent, text='Top-Down Shooter',
            scale=2, position=(0, 0.45), color=color.white, enabled=False)

        # Adjusted Y positions by 0.15 steps
        self.btn_play = Button(
            parent=ui_parent, text='Play',
            scale=(0.25,0.1), position=(0, 0.2, 0),
            color=color.azure, on_click=on_play, enabled=False)

        self.btn_settings = Button(
            parent=ui_parent, text='Settings',
            scale=(0.25,0.1), position=(0, 0.05, 0),
            color=color.green, on_click=on_settings, enabled=False)

        self.btn_instructions = Button(
            parent=ui_parent, text='Instructions',
            scale=(0.25,0.1), position=(0, -0.1, 0),
            color=color.yellow, on_click=on_instructions, enabled=False)

        self.btn_leaderboard = Button(
            parent=ui_parent, text='Leaderboard',
            scale=(0.25,0.1), position=(0, -0.25, 0),
            color=color.violet, on_click=on_leaderboard, enabled=False)

        self.btn_quit = Button(
            parent=ui_parent, text='Quit',
            scale=(0.25,0.1), position=(0, -0.4, 0),
            color=color.red, on_click=on_quit, enabled=False)

        # Include Settings in navigation order
        self.buttons = [
            self.btn_play,
            self.btn_settings,
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
