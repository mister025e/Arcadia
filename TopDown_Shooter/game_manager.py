import time
import pygame
from ursina import camera, application, time, destroy
from entities.player import Player
from map.world import World
from ui.hud import HUD
from ui.menu import MainMenu
from ui.gameover import GameOverScreen
from ui.name_entry import NameEntryScreen
from ui.leaderboard import LeaderboardScreen
from ui.instructions import InstructionsScreen
from ui.settings import SettingsScreen
from utils.file_manager import load_leaderboard, add_score_to_leaderboard
from utils.settings_manager import load_settings, DEFAULTS, STAT_LIMITS


class GameManager:
    """
    Orchestrates game states, transitions, and Ursina’s update/input callbacks.
    """

    def __init__(self, app, controllers):
        # Keep reference to the Ursina app
        self.app = app
        # keep the two pygame joystick.Joystick instances
        self.controllers = controllers

        # ------------ STATE VARIABLES ------------
        self.game_state = 'menu'      # 'menu' | 'playing' | 'gameover' | 'name_entry' | 'leaderboard' | 'instructions'
        self.match_start_time = 0
        self.match_end_time = 0
        self.last_score = 0
        self.score_saved = False

        # Delay before accepting Space on Game Over to avoid accidental restarts
        self.gameover_shown_time = 0
        self.gameover_space_delay = 0.5   # seconds

        # ------------ LOAD / WORLD / PLAYERS ------------
        # Load leaderboard
        self.leaderboard_data = load_leaderboard()

        # Define player spawn positions (x, y, z)
        p1_spawn = (-5, 0.5, -5)
        p2_spawn = (5, 0.5, 5)

        # Create world with covers excluding those spawns
        # Note: World expects exclude_positions as list of (x, z)
        self.world = World(exclude_positions=[
            (p1_spawn[0], p1_spawn[2]),
            (p2_spawn[0], p2_spawn[2])
        ])

        # Track active projectiles
        self.projectiles = []

        from ursina import color
        self.p1 = Player(
            name='Player 1',
            position=(-5, 0.5, -5),
            keys={'up': 'w', 'down': 's', 'left': 'a', 'right': 'd', 'shoot': 'space'},
            color=color.azure,
            hp_penalty=2,
            spawn_callback=self.register_projectile,
            controller = controllers[0] if len(controllers) > 0 else None
        )
        self.p2 = Player(
            name='Player 2',
            position=(5, 0.5, 5),
            keys={'up': 'up arrow', 'down': 'down arrow', 'left': 'left arrow', 'right': 'right arrow', 'shoot': 'right shift'},
            color=color.orange,
            hp_penalty=2,
            spawn_callback=self.register_projectile,
            controller = controllers[1] if len(controllers) > 1 else None
        )

        # Create HUD
        self.hud = HUD()

        # ------------ UI SCREENS ------------
        self.main_menu = MainMenu(
            ui_parent=camera.ui,
            on_play=self.start_game,
            on_settings=self.show_settings,
            on_instructions=self.show_instructions,
            on_leaderboard=self.show_leaderboard_from_menu,
            on_quit=application.quit    # call quit directly
        )
        self.gameover_screen = GameOverScreen(
            ui_parent=camera.ui,
            on_restart=self.start_game,
            on_main_menu=self.show_main_menu,
            on_save=self.show_name_entry,
            on_view_leaderboard=self.show_leaderboard
        )
        self.settings_screen = SettingsScreen(
            ui_parent = camera.ui,
            on_done = self.back_from_settings
        )
        self.name_entry = NameEntryScreen(
            ui_parent=camera.ui,
            on_finish=self.finish_name_entry
        )
        self.leaderboard_screen = LeaderboardScreen(
            ui_parent=camera.ui,
            on_back=self.back_to_gameover
        )
        self.instructions_screen = InstructionsScreen(
            ui_parent=camera.ui,
            on_back=self.back_from_instructions
        )

        # Attach HUD texts to camera.ui
        self.hud.attach_to_ui(camera.ui)

        # Collect all world entities + players
        self.game_entities = self.world.entities + [self.p1, self.p2]

        # ------------ BUTTON SCALES FOR OUTLINE ------------
        # Store each button's original scale so we can enlarge/shrink on focus
        self.original_scales = {}
        for btn in (
            self.main_menu.buttons +
            self.gameover_screen.buttons +
            self.leaderboard_screen.buttons +
            self.instructions_screen.buttons
        ):
            self.original_scales[btn] = btn.scale

        # ------------ KEYBOARD NAVIGATION ------------
        self.focused_buttons = []
        self.focus_index = 0

        # Initially hide everything except main menu
        self._hide_all_entities_and_ui()
        self.show_main_menu()

    # ─── INTERNAL HELPERS ───────────────────────────────────────────────────────

    def _hide_all_entities_and_ui(self):
        # Hide map / players
        for e in self.game_entities:
            e.enabled = False
        # Hide HUD
        self.hud.disable()
        # Hide every UI screen
        self.main_menu.hide()
        self.gameover_screen.hide()
        self.name_entry.hide()
        self.leaderboard_screen.hide()
        self.instructions_screen.hide()
        self.settings_screen.hide()
        # Clear any button focus
        self._clear_focus()

    def register_projectile(self, proj):
        """
        Called by Player._shoot() whenever a new Projectile is created.
        We append it to our list so we can update it each frame.
        """
        self.projectiles.append(proj)

    def _clear_focus(self):
        """
        Remove hover‐outline from all buttons on all screens (reset scale).
        """
        for btn_list in (
            self.main_menu.buttons,
            self.gameover_screen.buttons,
            self.leaderboard_screen.buttons,
            self.instructions_screen.buttons
        ):
            for btn in btn_list:
                try:
                    btn.on_mouse_exit()
                except:
                    pass
                # Reset scale
                if btn in self.original_scales:
                    btn.scale = self.original_scales[btn]

        self.focused_buttons = []
        self.focus_index = 0

    def _set_focus(self, buttons_list):
        """
        Assign a new list of focusable buttons, highlight the first enabled one.
        """
        self._clear_focus()
        self.focused_buttons = buttons_list
        if not buttons_list:
            return
        # Find first enabled button
        for idx, btn in enumerate(buttons_list):
            if btn.enabled:
                self.focus_index = idx
                try:
                    btn.on_mouse_enter()
                except:
                    pass
                # Enlarge scale for outline effect
                btn.scale = self.original_scales[btn] * 1.1
                return

    def _move_focus(self, direction):
        """
        Move focus among self.focused_buttons, skipping disabled buttons.
        direction: 'up','down','left','right'
        If in Game Over (4 buttons), use 2×2 grid; otherwise treat as single vertical list.
        """
        btns = self.focused_buttons
        n = len(btns)
        if n == 0:
            return

        # Collect indices of enabled buttons
        enabled_indices = [i for i, b in enumerate(btns) if b.enabled]
        if not enabled_indices:
            return

        old_idx = self.focus_index
        if old_idx not in enabled_indices:
            new_idx = enabled_indices[0]
        else:
            # Game Over’s 2×2 grid
            if self.game_state == 'gameover' and n == 4:
                row = old_idx // 2
                col = old_idx % 2
                new_row, new_col = row, col

                if direction == 'up' and row == 1:
                    new_row = 0
                elif direction == 'down' and row == 0:
                    new_row = 1
                elif direction == 'left' and col == 1:
                    new_col = 0
                elif direction == 'right' and col == 0:
                    new_col = 1

                candidate = new_row * 2 + new_col
                if candidate in enabled_indices:
                    new_idx = candidate
                else:
                    new_idx = old_idx
            else:
                # Single‐column list behavior (only W/S should move)
                if direction not in ('up', 'down'):
                    return
                pos = enabled_indices.index(old_idx)
                if direction == 'up':
                    pos = (pos - 1) % len(enabled_indices)
                elif direction == 'down':
                    pos = (pos + 1) % len(enabled_indices)
                new_idx = enabled_indices[pos]

        if new_idx != old_idx:
            # Reset old button
            try:
                btns[old_idx].on_mouse_exit()
            except:
                pass
            # Restore old scale
            if btns[old_idx] in self.original_scales:
                btns[old_idx].scale = self.original_scales[btns[old_idx]]

            # Highlight new button
            try:
                btns[new_idx].on_mouse_enter()
            except:
                pass
            # Enlarge new scale
            if btns[new_idx] in self.original_scales:
                btns[new_idx].scale = self.original_scales[btns[new_idx]] * 1.1

            self.focus_index = new_idx

    # ─── SCREEN TRANSITIONS ─────────────────────────────────────────────────────

    def show_main_menu(self):
        """
        Enter the 'menu' state: hide all others, show only main menu.
        """
        self.game_state = 'menu'
        self._hide_all_entities_and_ui()
        self.main_menu.show()
        self._set_focus(self.main_menu.buttons)

    def start_game(self):
        """
        Enter the 'playing' state: reset HP & timer, enable world & players & HUD.
        Also destroy any old covers (tag=='cover') and regenerate them.
        """
        # 1) Core state reset
        self.game_state = 'playing'
        self.match_start_time = time.time()
        self.last_score = 0
        self.score_saved = False

        # 2) Clear any lingering projectiles
        for proj in self.projectiles:
            proj.enabled = False
            destroy(proj)
        self.projectiles.clear()

        # 3) Load & apply settings to both players
        settings = load_settings()  # {'Player 1': {...}, 'Player 2': {...}}

        # Player 1 settings
        s1 = settings['Player 1']
        self.p1.turn_speed = s1['rotation_speed']
        self.p1.move_speed = s1['movement_speed']
        self.p1.health_max = s1['health_points']
        self.p1.health = self.p1.health_max
        self.p1.shoot_cooldown = s1['shot_delay']
        self.p1.shot_power = s1['shot_power']
        self.p1.projectile_speed = s1['projectile_speed']

        # Player 2 settings
        s2 = settings['Player 2']
        self.p2.turn_speed = s2['rotation_speed']
        self.p2.move_speed = s2['movement_speed']
        self.p2.health_max = s2['health_points']
        self.p2.health = self.p2.health_max
        self.p2.shoot_cooldown = s2['shot_delay']
        self.p2.shot_power = s2['shot_power']
        self.p2.projectile_speed = s2['projectile_speed']

        # 4) Hide all UI screens
        self.main_menu.hide()
        self.gameover_screen.hide()
        self.name_entry.hide()
        self.leaderboard_screen.hide()
        self.instructions_screen.hide()
        self.settings_screen.hide()

        # 5) Reset player positions & rotations
        p1_spawn = (-5, 0.5, -5)
        p2_spawn = (5, 0.5, 5)
        self.p1.position = p1_spawn
        self.p2.position = p2_spawn
        self.p1.rotation_y = 0  # face “north”
        self.p2.rotation_y = 180  # face “south”

        # 6) Regenerate covers
        survivors = []
        for e in self.world.entities:
            if getattr(e, 'tag', '') == 'cover':
                destroy(e)
            else:
                survivors.append(e)
        self.world.entities = survivors
        self.world._create_covers()

        # 7) Enable all map entities and players
        for e in self.world.entities + [self.p1, self.p2]:
            e.enabled = True

        # 8) Rebuild game_entities list
        self.game_entities = self.world.entities + [self.p1, self.p2]

        # 9) Enable the HUD
        self.hud.enable()

        # Reset focus if you’re returning to play
        self._clear_focus()

    def end_game(self, winner: Player):
        """
        Called when one player's HP ≤ 0. Calculate final score, show game-over UI.
        """
        self.game_state = 'gameover'
        self.match_end_time = time.time()
        self.score_saved = False

        # Disable map + players
        for e in self.game_entities:
            e.enabled = False
        # Disable HUD
        self.hud.disable()

        # Base score calculation
        elapsed = self.match_end_time - self.match_start_time
        hp_lost = winner.health_max - winner.health
        penalty = winner.hp_penalty
        base_score = 1000
        raw = base_score - int(elapsed * 5) - (hp_lost * penalty)
        raw = max(0, raw)

        # Load the saved stats (or defaults) and grab defaults
        settings = load_settings()  # e.g. {'Player 1':{...}, 'Player 2':{...}}
        player_stats = settings[winner.name]
        default_stats = DEFAULTS[winner.name]

        product = 1.0
        for stat in STAT_LIMITS:
            cur = player_stats[stat]
            df = default_stats[stat]
            if stat == 'shot_delay':
                # higher delay = disadvantage → multiplier >1; lower = advantage → <1
                m = cur / df if df != 0 else 1.0
            else:
                # higher stat = advantage → multiplier <1; lower = disadvantage → >1
                m = df / cur if cur != 0 else 1.0
            product *= m

        # Clamp overall multiplier between 0.1 and 2.0
        multiplier = max(0.1, min(product, 2.0))

        # Apply multiplier
        final_score = int(raw * multiplier)
        self.last_score = max(0, final_score)

        # Show Game Over UI
        self.gameover_screen.show(winner.name, self.last_score, self.score_saved)
        self.gameover_shown_time = time.time()
        self._set_focus(self.gameover_screen.buttons)

    def show_name_entry(self):
        """
        Switch to the username-entry UI.
        """
        self.game_state = 'name_entry'
        self.gameover_screen.hide()
        self.name_entry.show()
        self._clear_focus()

    def finish_name_entry(self, username):
        """
        Player finished entering their name. Save if any, then return to Game Over.
        """
        if username:
            add_score_to_leaderboard(username, self.last_score)
            self.score_saved = True

        self.name_entry.hide()
        self.gameover_screen.show(
            self.gameover_screen.gameover_winner_text.text.split('\n')[0].replace(' Wins!', ''),
            self.last_score,
            self.score_saved
        )
        self.gameover_shown_time = time.time()
        self.game_state = 'gameover'
        self._set_focus(self.gameover_screen.buttons)

    def show_leaderboard(self):
        """
        (Called from Game Over) Hide GameOver UI and display leaderboard. Back → Game Over.
        """
        self.game_state = 'leaderboard'
        self.main_menu.hide()
        self.gameover_screen.hide()
        self.name_entry.hide()
        self.instructions_screen.hide()

        self.leaderboard_data = load_leaderboard()
        self.leaderboard_screen.btn_back.on_click = self.back_to_gameover
        self.leaderboard_screen.show(self.leaderboard_data)
        self._set_focus(self.leaderboard_screen.buttons)

    def show_leaderboard_from_menu(self):
        """
        (Called from Main Menu) Hide MainMenu and show leaderboard. Back → Main Menu.
        """
        self.game_state = 'leaderboard'
        self.main_menu.hide()
        self.gameover_screen.hide()
        self.name_entry.hide()
        self.instructions_screen.hide()

        self.leaderboard_data = load_leaderboard()
        self.leaderboard_screen.btn_back.on_click = self.back_to_menu_from_leaderboard
        self.leaderboard_screen.show(self.leaderboard_data)
        self._set_focus(self.leaderboard_screen.buttons)

    def back_to_gameover(self):
        """
        From leaderboard (launched by Game Over), return to Game Over.
        """
        self.game_state = 'gameover'
        self.leaderboard_screen.hide()
        self.gameover_screen.show(
            self.gameover_screen.gameover_winner_text.text.split('\n')[0].replace(' Wins!', ''),
            self.last_score,
            self.score_saved
        )
        self.gameover_shown_time = time.time()
        self._set_focus(self.gameover_screen.buttons)

    def back_to_menu_from_leaderboard(self):
        """
        From leaderboard (launched by Main Menu), return to Main Menu.
        """
        self.game_state = 'menu'
        self.leaderboard_screen.hide()
        self.main_menu.show()
        self._set_focus(self.main_menu.buttons)

    def show_instructions(self):
        """
        Hide Main Menu (or any) and display the instructions screen.
        """
        self.game_state = 'instructions'
        self.main_menu.hide()
        self.gameover_screen.hide()
        self.name_entry.hide()
        self.leaderboard_screen.hide()

        self.instructions_screen.show()
        self._set_focus(self.instructions_screen.buttons)

    def back_from_instructions(self):
        """
        From instructions, return to Main Menu.
        """
        self.game_state = 'menu'
        self.instructions_screen.hide()
        self.main_menu.show()
        self._set_focus(self.main_menu.buttons)

    def show_settings(self):
        """
        Hide Main Menu (or any) and display the settings screen.
        """
        self.game_state = 'settings'
        self._hide_all_entities_and_ui()
        self.settings_screen.show()

    def back_from_settings(self):
        """
        From settings, return to Main Menu.
        """
        self.game_state = 'menu'
        self.settings_screen.hide()
        self.main_menu.show()
        self._set_focus(self.main_menu.buttons)

    # ─── URSINA UPDATE & INPUT ─────────────────────────────────────────────────

    def process_joystick_event(self, event):
        """
        Handle pygame joystick events for:
          - NameEntry screen
          - Settings screen
          - Other UI screens (MainMenu, GameOver, Leaderboard, Instructions)
        """
        deadzone = 0.5

        # ───── NameEntry ────────────────────────────
        if self.game_state == 'name_entry':
            # Only player1’s stick (joy 0) drives name entry
            if event.joy != 0:
                return

            if event.type == pygame.JOYAXISMOTION:
                # Vertical axis 1 for W/S
                if event.axis == 1:
                    if event.value < -deadzone:
                        self.name_entry.input('w')
                    elif event.value > deadzone:
                        self.name_entry.input('s')
                # Horizontal axis 0 for A/D
                elif event.axis == 0:
                    if event.value < -deadzone:
                        self.name_entry.input('a')
                    elif event.value > deadzone:
                        self.name_entry.input('d')

            elif event.type == pygame.JOYBUTTONDOWN:
                # Any button on stick 0 is "space" to confirm
                self.name_entry.input('space')
            return


        # ───── Settings ─────────────────────────────
        if self.game_state == 'settings':
            # Player1 = joy 0 → WASD/space; Player2 = joy 1 → arrows/RightShift
            if event.type == pygame.JOYAXISMOTION:
                # map each stick separately
                if event.axis == 1:  # vertical
                    if event.value < -deadzone:
                        key = 'w' if event.joy == 0 else 'up arrow'
                    elif event.value > deadzone:
                        key = 's' if event.joy == 0 else 'down arrow'
                    else:
                        return
                    self.settings_screen.input(key)

                elif event.axis == 0:  # horizontal
                    if event.value < -deadzone:
                        key = 'a' if event.joy == 0 else 'left arrow'
                    elif event.value > deadzone:
                        key = 'd' if event.joy == 0 else 'right arrow'
                    else:
                        return
                    self.settings_screen.input(key)

            elif event.type == pygame.JOYBUTTONDOWN:
                # joy 0 → space, joy 1 → right shift
                key = 'space' if event.joy == 0 else 'right shift'
                self.settings_screen.input(key)
            return


        # ───── Other UI Screens ──────────────────────
        if self.game_state in ('menu','gameover','leaderboard','instructions'):
            # Axis motion for focus
            if event.type == pygame.JOYAXISMOTION:
                # only vertical for menus
                if event.axis == 1:
                    if event.value < -deadzone:
                        self._move_focus('up')
                    elif event.value > deadzone:
                        self._move_focus('down')

                # game over’s 2×2 grid uses axis 0 as well
                if self.game_state == 'gameover' and event.axis == 0:
                    if event.value < -deadzone:
                        self._move_focus('left')
                    elif event.value > deadzone:
                        self._move_focus('right')

            # Any button confirms
            elif event.type == pygame.JOYBUTTONDOWN:
                self._activate_focused_button()

            return

    def _activate_focused_button(self):
        if not self.focused_buttons:
            return
        btn = self.focused_buttons[self.focus_index]
        if btn.enabled:
            btn.on_click()

    def update(self):
        """
        Called every frame by Ursina.
        - If ‘playing’, update players, projectiles, HUD, and check for simultaneous death.
        """
        if self.game_state == 'playing':
            elapsed = time.time() - self.match_start_time
            self.hud.update(elapsed, self.p1.health, self.p2.health)

            # Update players
            self.p1.game_update(self.game_state)
            self.p2.game_update(self.game_state)

            # Update projectiles
            for proj in self.projectiles.copy():
                if proj.enabled:
                    proj.game_update(self.game_state, self.end_game)
                else:
                    self.projectiles.remove(proj)

            # If both died simultaneously, default winner = p1
            if self.p1.health <= 0 and self.p2.health <= 0:
                self.end_game(self.p1)

    def input(self, key):
        """
        Called whenever a key is pressed or released.
        - If we’re in name‐entry, delegate there.
        - Otherwise, handle W/S/A/D/Space for UI navigation if a screen with buttons is active.
        """
        if self.game_state == 'settings':
            self.settings_screen.input(key)
            return

        if self.game_state == 'name_entry':
            self.name_entry.input(key)
            return

        if self.game_state in ('menu', 'gameover', 'leaderboard', 'instructions','settings'):
            # On Game Over, ignore Space if still within delay
            if self.game_state == 'gameover' and key in ('space', 'space hold'):
                if time.time() - self.gameover_shown_time < self.gameover_space_delay:
                    return

            # Up/Down navigation (single‐column screens)
            if key == 'w':
                self._move_focus('up')
                return
            if key == 's':
                self._move_focus('down')
                return

            # Left/Right navigation on Game Over (2×2 grid)
            if self.game_state == 'gameover':
                if key == 'a':
                    self._move_focus('left')
                    return
                if key == 'd':
                    self._move_focus('right')
                    return

            # Confirm with Space
            if key in ('space', 'space hold'):
                if self.focused_buttons:
                    btn = self.focused_buttons[self.focus_index]
                    if btn.enabled:
                        # Special‐case Quit in the main menu
                        if self.game_state == 'menu' and btn is self.main_menu.btn_quit:
                         application.quit()
                        else:
                            btn.on_click()
                return
