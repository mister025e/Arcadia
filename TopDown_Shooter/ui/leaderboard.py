from ursina import Entity, Text, Button, color


class LeaderboardScreen:
    """
    Full‐screen panel that shows up to 10 high‐score entries,
    plus a Back button to return to the Game Over screen.
    """

    def __init__(self, ui_parent, on_back):
        self.on_back = on_back

        self.leaderboard_panel = Entity(
            parent=ui_parent,
            model='quad',
            color=color.rgba(0, 0, 0, 0.6),
            scale=(1, 1),
            enabled=False
        )
        # 10 lines, stacked vertically
        self.entry_texts = []
        y_start = 0.35
        y_spacing = 0.06
        for i in range(10):
            t = Text(
                parent=ui_parent,
                text='',
                position=(0, y_start - i * y_spacing),
                origin=(0, 0),
                scale=1.2,
                color=color.white,
                enabled=False
            )
            self.entry_texts.append(t)

        self.btn_back = Button(
            parent=ui_parent,
            text='Back',
            scale=(0.2, 0.1),
            position=(0, -0.4, 0),
            color=color.orange,
            on_click=on_back,
            enabled=False
        )

    def show(self, leaderboard_data):
        """
        Display the top‐10 entries from leaderboard_data (list of dicts).
        """
        self.leaderboard_panel.enabled = True
        for i, t in enumerate(self.entry_texts):
            if i < len(leaderboard_data):
                entry = leaderboard_data[i]
                rank = i + 1
                t.text = f'{rank}. {entry["name"]} – {entry["score"]}'
                t.enabled = True
            else:
                t.enabled = False
        self.btn_back.enabled = True

    def hide(self):
        self.leaderboard_panel.enabled = False
        for t in self.entry_texts:
            t.enabled = False
        self.btn_back.enabled = False
