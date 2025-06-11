from ursina import Entity, Text, Button, color
from utils.settings_manager import load_settings, save_settings, STAT_LIMITS

class SettingsScreen:
    """
    Split‐screen settings UI for Player 1 and Player 2.
    Navigate with each player’s controls, lock with OK.
    Selected OK button is enlarged.
    """

    def __init__(self, ui_parent, on_done):
        self.on_done = on_done
        self.stats = list(STAT_LIMITS.keys())
        self.data = {}
        self.p1_idx = 0
        self.p2_idx = 0
        self.p1_locked = False
        self.p2_locked = False

        # Background panel
        self.panel = Entity(
            parent=ui_parent, model='quad',
            color=color.rgba(0,0,0,0.6), scale=(1.5, 1.1),
            enabled=False
        )

        # Title
        self.title = Text(
            parent=ui_parent, text='Settings',
            scale=2, y=0.45, color=color.white, enabled=False
        )

        # Load initial settings
        self.load()

        # Player 1 side labels + values
        self.p1_lbls = []
        lbl_x, val_x = -0.65, -0.35
        for i, stat in enumerate(self.stats):
            y = 0.25 - i*0.1
            lbl = Text(parent=ui_parent, text=f'{stat}:', x=lbl_x, y=y,
                       scale=1, color=color.white, enabled=False)
            val = Text(parent=ui_parent,
                       text=self.format_val(self.data['Player 1'][stat]),
                       x=val_x, y=y, scale=1, color=color.white, enabled=False)
            self.p1_lbls.append((lbl, val))

        # Player 2 side labels + values
        self.p2_lbls = []
        lbl2_x, val2_x = 0.15, 0.55
        for i, stat in enumerate(self.stats):
            y = 0.25 - i*0.1
            lbl = Text(parent=ui_parent, text=f'{stat}:', x=lbl2_x, y=y,
                       scale=1, color=color.white, enabled=False)
            val = Text(parent=ui_parent,
                       text=self.format_val(self.data['Player 2'][stat]),
                       x=val2_x, y=y, scale=1, color=color.white, enabled=False)
            self.p2_lbls.append((lbl, val))

        # OK buttons, default unlocked = red
        self.ok1 = Button(parent=ui_parent, text='OK', x=-0.45, y=-0.4,
                          scale=(0.1, 0.05), color=color.red, enabled=False)
        self.ok2 = Button(parent=ui_parent, text='OK', x= 0.45, y=-0.4,
                          scale=(0.1, 0.05), color=color.red, enabled=False)

        # Store original scales for OK buttons
        self.ok1_orig_scale = self.ok1.scale
        self.ok2_orig_scale = self.ok2.scale

    def format_val(self, v):
        return f'{v:.1f}' if isinstance(v, float) else str(int(v))

    def load(self):
        self.data = load_settings()

    def show(self):
        self.load()
        self.panel.enabled = True
        self.title.enabled = True

        # Show stats
        for (lbl, val), stat in zip(self.p1_lbls, self.stats):
            lbl.enabled = True
            val.text = self.format_val(self.data['Player 1'][stat])
            val.enabled = True
        for (lbl, val), stat in zip(self.p2_lbls, self.stats):
            lbl.enabled = True
            val.text = self.format_val(self.data['Player 2'][stat])
            val.enabled = True

        # Enable OK buttons, reset color & scale
        self.ok1.enabled = True
        self.ok2.enabled = True
        self.ok1.color = color.red
        self.ok2.color = color.red
        self.ok1.scale = self.ok1_orig_scale
        self.ok2.scale = self.ok2_orig_scale

        # Reset indices & locks
        self.p1_idx = 0
        self.p2_idx = 0
        self.p1_locked = False
        self.p2_locked = False

        # Highlight initial fields
        self._highlight(1)
        self._highlight(2)

    def hide(self):
        self.panel.enabled = False
        self.title.enabled = False
        for lbl, val in self.p1_lbls + self.p2_lbls:
            lbl.enabled = False
            val.enabled = False
        self.ok1.enabled = False
        self.ok2.enabled = False

    def _highlight(self, player):
        # Choose list and OK button based on player
        if player == 1:
            lst = self.p1_lbls + [(None, self.ok1)]
            ok_button = self.ok1
            ok_orig = self.ok1_orig_scale
        else:
            lst = self.p2_lbls + [(None, self.ok2)]
            ok_button = self.ok2
            ok_orig = self.ok2_orig_scale

        idx = self.p1_idx if player==1 else self.p2_idx

        # Reset all label/value colors and OK scale
        for lbl, val in lst:
            if lbl and val:
                lbl.color = color.white
                val.color = color.white
        ok_button.scale = ok_orig

        # Highlight current
        lbl, val = lst[idx]
        if lbl:  # stat label/value
            lbl.color = color.yellow
            val.color = color.yellow
        else:
            # OK button: enlarge instead of coloring
            ok_button.scale = ok_orig * 1.2

    def _adjust(self, player, delta):
        idx = self.p1_idx if player==1 else self.p2_idx
        locked = self.p1_locked if player==1 else self.p2_locked

        # OK slot
        if idx >= len(self.stats):
            if player==1:
                self.p1_locked = not self.p1_locked
                self.ok1.color = color.green if self.p1_locked else color.red
            else:
                self.p2_locked = not self.p2_locked
                self.ok2.color = color.green if self.p2_locked else color.red
            if self.p1_locked and self.p2_locked:
                save_settings(self.data)
                self.hide()
                self.on_done()
            return

        # Stat slots: only if not locked
        if locked:
            return

        stat = self.stats[idx]
        mn, mx, step = STAT_LIMITS[stat]
        key = 'Player 1' if player==1 else 'Player 2'
        new = self.data[key][stat] + delta * step
        self.data[key][stat] = max(mn, min(mx, new))

        # Update display
        lbl, val = (self.p1_lbls if player==1 else self.p2_lbls)[idx]
        val.text = self.format_val(self.data[key][stat])

    def input(self, key):
        if not self.panel.enabled:
            return

        # Player 1
        if key == 'space':
            self._adjust(1, 0)
            return

        if not self.p1_locked:
            if key == 'w':
                self.p1_idx = (self.p1_idx - 1) % (len(self.stats) + 1)
                self._highlight(1)
                return
            if key == 's':
                self.p1_idx = (self.p1_idx + 1) % (len(self.stats) + 1)
                self._highlight(1)
                return
            if key == 'a':
                self._adjust(1, -1)
                return
            if key == 'd':
                self._adjust(1, +1)
                return

        # Player 2
        if key == 'right shift':
            self._adjust(2, 0)
            return

        if not self.p2_locked:
            if key == 'up arrow':
                self.p2_idx = (self.p2_idx - 1) % (len(self.stats) + 1)
                self._highlight(2)
                return
            if key == 'down arrow':
                self.p2_idx = (self.p2_idx + 1) % (len(self.stats) + 1)
                self._highlight(2)
                return
            if key == 'left arrow':
                self._adjust(2, -1)
                return
            if key == 'right arrow':
                self._adjust(2, +1)
                return