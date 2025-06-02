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
        # Restart button
        self.btn_restart = Button(
            parent=ui_parent,
            text='Restart',
            scale=(0.2, 0.1),
            position=(-0.25, -0.1, 0),
            color=color.azure,
            on_click=on_restart,
            enabled=False
        )
        # Main Menu button
        self.btn_main_menu = Button(
            parent=ui_parent,
            text='Main Menu',
            scale=(0.2, 0.1),
            position=(0.25, -0.1, 0),
            color=color.orange,
            on_click=on_main_menu,
            enabled=False
        )
        # Save Score button
        self.btn_save_score = Button(
            parent=ui_parent,
            text='Save Score',
            scale=(0.2, 0.1),
            position=(-0.25, -0.25, 0),
            color=color.green,
            on_click=on_save,
            enabled=False
        )
        # View Leaderboard button
        self.btn_view_leaderboard = Button(
            parent=ui_parent,
            text='View Leaderboard',
            scale=(0.2, 0.1),
            position=(0.25, -0.25, 0),
            color=color.violet,
            on_click=on_view_leaderboard,
            enabled=False
        )

    def show(self, winner_name, score, score_saved):
        """
        Show the panel, set the winner/score text.
        If score_saved is True, disable “Save Score” so it can’t be clicked again.
        """
        self.gameover_winner_text.text = f'{winner_name} Wins!\nScore: {score}'
        self.gameover_panel.enabled = True
        self.gameover_winner_text.enabled = True
        self.btn_restart.enabled = True
        self.btn_main_menu.enabled = True
        # If the score already saved this match, hide the button
        self.btn_save_score.enabled = not score_saved
        self.btn_view_leaderboard.enabled = True

    def hide(self):
        self.gameover_panel.enabled = False
        self.gameover_winner_text.enabled = False
        self.btn_restart.enabled = False
        self.btn_main_menu.enabled = False
        self.btn_save_score.enabled = False
        self.btn_view_leaderboard.enabled = False
