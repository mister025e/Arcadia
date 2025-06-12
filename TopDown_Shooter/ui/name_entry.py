from ursina import Entity, Text, color

class NameEntryScreen:
    """
    Full-screen panel that allows the player to type a 6-character name
    with W/S to change letters, A/D to move slots, and Space to confirm.
    """

    def __init__(self, ui_parent, on_finish):
        self.on_finish = on_finish

        # Background
        self.name_panel = Entity(
            parent=ui_parent,
            model='quad',
            color=color.rgba(0, 0, 0, 0.6),
            scale=(1, 1),
            enabled=False
        )
        # Instructions
        self.name_instr = Text(
            parent=ui_parent,
            text='Stick UP/DOWN : letter  LEFT/RIGHT : slot   Button A : confirm',
            position=(0, 0.4),
            origin=(0, 0),
            scale=1,
            color=color.white,
            enabled=False
        )
        # Six character slots
        self.slot_texts = []
        slot_start_x = -0.15
        slot_spacing = 0.06
        for i in range(6):
            t = Text(
                parent=ui_parent,
                text='_',  # blank
                position=(slot_start_x + i * slot_spacing, 0.2),
                origin=(0, 0),
                scale=2,
                color=color.white,
                enabled=False
            )
            self.slot_texts.append(t)

        # Internal state
        self.name_slots = [''] * 6
        self.current_slot_index = 0

    def show(self):
        """Display the entry UI and reset all slots to blank."""
        # Reset internal buffer
        self.name_slots = [''] * 6
        self.current_slot_index = 0

        # Show UI
        self.name_panel.enabled = True
        self.name_instr.enabled = True
        for t in self.slot_texts:
            t.text = '_'          # blank
            t.color = color.white
            t.enabled = True

        # Highlight first slot
        self.slot_texts[0].color = color.yellow

    def hide(self):
        """Hide the entry UI."""
        self.name_panel.enabled = False
        self.name_instr.enabled = False
        for t in self.slot_texts:
            t.enabled = False

    def input(self, key):
        """Handle inputs when the entry UI is active."""
        if not self.name_panel.enabled:
            return

        i = self.current_slot_index

        if key == 'w':   # cycle letter up
            current = self.name_slots[i]
            if current == '':
                new = 'A'
            else:
                idx = ord(current) - ord('A')
                new = chr(ord('A') + ((idx + 1) % 26))
            self.name_slots[i] = new
            self.slot_texts[i].text = new

        elif key == 's':  # cycle letter down
            current = self.name_slots[i]
            if current == '':
                new = 'A'
            else:
                idx = ord(current) - ord('A')
                new = chr(ord('A') + ((idx - 1) % 26))
            self.name_slots[i] = new
            self.slot_texts[i].text = new

        elif key == 'd':  # move to next slot (only if current has a letter)
            if self.name_slots[i] != '' and i < 5:
                self.slot_texts[i].color = color.white
                self.current_slot_index += 1
                self.slot_texts[self.current_slot_index].color = color.yellow

        elif key == 'a':  # move to previous slot
            if i > 0:
                self.slot_texts[i].color = color.white
                self.current_slot_index -= 1
                self.slot_texts[self.current_slot_index].color = color.yellow

        elif key in ('space', 'space hold'):
            self._finish_entry()

    def _finish_entry(self):
        """Build the final username and invoke the callback."""
        i = self.current_slot_index
        if self.name_slots[i] == '':
            username = ''.join(self.name_slots[:i])
        else:
            username = ''.join(self.name_slots[:i + 1])

        self.hide()
        self.on_finish(username)