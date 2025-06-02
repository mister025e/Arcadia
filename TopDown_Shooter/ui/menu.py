from ursina import Entity, Button, color


class MainMenu:
    """
    Full‐screen semi‐transparent quad + two buttons: Play and Quit.
    """

    def __init__(self, ui_parent, on_play, on_quit):
        # background panel
        self.menu_panel = Entity(
            parent=ui_parent,
            model='quad',
            color=color.rgba(0, 0, 0, 0.6),
            scale=(1, 1),
            enabled=False
        )
        # Play button
        self.btn_play = Button(
            parent=ui_parent,
            text='Play',
            scale=(0.2, 0.1),
            position=(0, 0.1, 0),
            color=color.azure,
            on_click=on_play,
            enabled=False
        )
        # Quit button
        self.btn_quit = Button(
            parent=ui_parent,
            text='Quit',
            scale=(0.2, 0.1),
            position=(0, -0.1, 0),
            color=color.red,
            on_click=on_quit,
            enabled=False
        )

    def show(self):
        self.menu_panel.enabled = True
        self.btn_play.enabled = True
        self.btn_quit.enabled = True

    def hide(self):
        self.menu_panel.enabled = False
        self.btn_play.enabled = False
        self.btn_quit.enabled = False
