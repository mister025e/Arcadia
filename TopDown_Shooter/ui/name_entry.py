from ursina import Entity, Text, Button, color


class NameEntryScreen:
    """
    Full‐screen panel that allows the player to type a 6‐character name with W/S/A/D/Space.
    """

    def __init__(self, ui_parent, on_finish):
        self.on_finish = on_finish

        self.name_panel = Entity(
            parent=ui_parent,
            model='quad',
            color=color.rgba(0, 0, 0, 0.6),
            scale=(1, 1),
            enabled=False
        )
        self.name_instr = Text(
            parent=ui_parent,
            text='Use W/S to change letter, A/D to change slot, Space to confirm',
            position=(0, 0.4),
            origin=(0, 0),
            scale=1,
            color=color.white,
            enabled=False
        )
        self.slot_texts = []
        slot_start_x = -0.15
        slot_spacing = 0.06
        for i in range(6):
            t = Text(
                parent=ui_parent,
                text='_',  # underscore means “blank”
                position=(slot_start_x + i * slot_spacing, 0.2),
                origin=(0, 0),
                scale=2,
                color=color.white,
                enabled=False
            )
            self.slot_texts.append(t)

        # Internally track the current slot (0–5) and the chosen characters
        self.name_slots = [''] * 6
        self.current_slot_index = 0

    def show(self):
        """Display name‐entry; highlight slot 0."""
        self.name_panel.enabled = True
        self.name_instr.enabled = True
        for t in self.slot_texts:
            t.text = '_'
            t.color = color.white
            t.enabled = True
        self.current_slot_index = 0
        self.slot_texts[0].color = color.yellow

    def hide(self):
        """Hide all name‐entry UI."""
        self.name_panel.enabled = False
        self.name_instr.enabled = False
        for t in self.slot_texts:
            t.enabled = False

    def input(self, key):
        """
        Called from GameManager.input(). Respond to W/S/A/D/Space only
        if this screen is active.
        """
        if not self.name_panel.enabled:
            return

        i = self.current_slot_index

        if key == 'w':
            # cycle letter upward
            current_char = self.name_slots[i]
            if current_char == '':
                new_char = 'A'
            else:
                idx = ord(current_char) - ord('A')
                new_char = chr(ord('A') + ((idx + 1) % 26))
            self.name_slots[i] = new_char
            self.slot_texts[i].text = new_char

        elif key == 's':
            # cycle letter downward
            current_char = self.name_slots[i]
            if current_char == '':
                new_char = 'A'
            else:
                idx = ord(current_char) - ord('A')
                new_char = chr(ord('A') + ((idx - 1) % 26))
            self.name_slots[i] = new_char
            self.slot_texts[i].text = new_char

        elif key == 'd':
            # move to next slot only if current slot has a letter and i < 5
            if self.name_slots[i] != '' and i < 5:
                self.slot_texts[i].color = color.white
                self.current_slot_index += 1
                self.slot_texts[self.current_slot_index].color = color.yellow

        elif key == 'a':
            # move to previous slot if i > 0
            if i > 0:
                self.slot_texts[i].color = color.white
                self.current_slot_index -= 1
                self.slot_texts[self.current_slot_index].color = color.yellow

        elif key == 'space' or key == 'space hold':
            # Confirm entry
            self._finish_entry()

    def _finish_entry(self):
        """
        Called when the player presses Space. Build the actual username,
        then call the callback (to save and return to gameover).
        """
        i = self.current_slot_index
        if self.name_slots[i] == '':
            username = ''.join(self.name_slots[:i])
        else:
            username = ''.join(self.name_slots[:i + 1])

        self.hide()
        self.on_finish(username)
