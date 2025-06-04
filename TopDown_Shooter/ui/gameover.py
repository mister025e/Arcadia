from ursina import Entity, Text, Button, color


class GameOverScreen:
    """
    Full‐screen panel with:
      - winner+score Text
      - Restart / Main Menu / Save Score / View Leaderboard buttons
    """

    def __init__(self, ui_parent, on_restart, on_main_menu, on_save, on_view_leaderboard):
        self.gameover_panel = Entity(
            parent=ui_parent,
            model='quad',
            color=color.rgba(0, 0, 0, 0.6),
            scale=(1, 1),
            enabled=False
        )
        # “Player X Wins!\nScore: Y”
        self.gameover_winner_text = Text(
            parent=ui_parent,
            text='',
            origin=(0, 0),
            scale=2,
            position=(0, 0.2),
            color=color.white,
            enabled=False
        )
        # Restart button (row 0, col 0)
        self.btn_restart = Button(
            parent=ui_parent,
            text='Restart',
            scale=(0.2, 0.1),
            position=(-0.25, -0.1, 0),
            color=color.azure,
            on_click=on_restart,
            enabled=False
        )
        # Main Menu button (row 0, col 1)
        self.btn_main_menu = Button(
            parent=ui_parent,
            text='Main Menu',
            scale=(0.2, 0.1),
            position=(0.25, -0.1, 0),
            color=color.orange,
            on_click=on_main_menu,
            enabled=False
        )
        # Save Score button (row 1, col 0)
        self.btn_save_score = Button(
            parent=ui_parent,
            text='Save Score',
            scale=(0.2, 0.1),
            position=(-0.25, -0.25, 0),
            color=color.green,
            on_click=on_save,
            enabled=False
        )
        # View Leaderboard button (row 1, col 1)
        self.btn_view_leaderboard = Button(
            parent=ui_parent,
            text='View Leaderboard',
            scale=(0.2, 0.1),
            position=(0.25, -0.25, 0),
            color=color.violet,
            on_click=on_view_leaderboard,
            enabled=False
        )

        # For keyboard navigation: row-major order
        self.buttons = [
            self.btn_restart,         # index 0 (row=0,col=0)
            self.btn_main_menu,       # index 1 (row=0,col=1)
            self.btn_save_score,      # index 2 (row=1,col=0)
            self.btn_view_leaderboard # index 3 (row=1,col=1)
        ]

    def show(self, winner_name, score, score_saved):
        """
        Show the panel, set the winner/score text.
        If score_saved is True, disable “Save Score” so it can’t be clicked again.
        """
        self.gameover_winner_text.text = f'{winner_name} Wins!\nScore: {score}'
        self.gameover_panel.enabled = True
        self.gameover_winner_text.enabled = True

        # Enable buttons, except disable “Save Score” if already saved
        for btn in self.buttons:
            btn.enabled = True
        self.btn_save_score.enabled = (not score_saved)

    def hide(self):
        self.gameover_panel.enabled = False
        self.gameover_winner_text.enabled = False
        for btn in self.buttons:
            btn.enabled = False