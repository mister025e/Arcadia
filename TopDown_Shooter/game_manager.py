from ursina import Ursina, camera, application, time
from entities.player import Player
from entities.projectile import Projectile
from map.world import World
from ui.hud import HUD
from ui.menu import MainMenu
from ui.gameover import GameOverScreen
from ui.name_entry import NameEntryScreen
from ui.leaderboard import LeaderboardScreen
from ui.instructions import InstructionsScreen
from utils.file_manager import load_leaderboard, add_score_to_leaderboard
import pygame


class GameManager:
    """
    Orchestrates game states, transitions, and Ursina’s update/input callbacks,
    including joystick‐axis polling for menus and name‐entry.
    """

    def __init__(self, app):
        # Keep reference to the Ursina app
        self.app = app

        # ------------ STATE VARIABLES ------------
        self.game_state = 'menu'      # 'menu' | 'playing' | 'gameover' | 'name_entry' | 'leaderboard' | 'instructions'
        self.match_start_time = 0
        self.match_end_time = 0
        self.last_score = 0
        self.score_saved = False

        # Delay before accepting confirm on Game Over to avoid accidental restarts
        self.gameover_shown_time = 0
        self.gameover_confirm_delay = 0.5   # seconds  ⬅ CHANGED (renamed for clarity)

        # ------------ LOAD / WORLD / PLAYERS ------------
        self.leaderboard_data = load_leaderboard()
        self.world = World()
        self.projectiles = []

        # Initialize Pygame joystick system
        pygame.init()
        pygame.joystick.init()
        self.joysticks = []
        for i in range(pygame.joystick.get_count()):
            js = pygame.joystick.Joystick(i)
            js.init()
            print(f"Detected joystick {i}: {js.get_name()}")
            self.joysticks.append(js)

        from ursina import color
        # Player 1
        self.p1 = Player(
            name='Player 1',
            position=(-5, 0.5, -5),
            joystick_list=self.joysticks,
            joystick_index=0,
            color=color.azure,
            hp_penalty=2,
            spawn_callback=self.register_projectile
        )
        # Player 2
        self.p2 = Player(
            name='Player 2',
            position=(5, 0.5, 5),
            joystick_list=self.joysticks,
            joystick_index=1,
            color=color.orange,
            hp_penalty=2,
            spawn_callback=self.register_projectile
        )

        # Create HUD
        self.hud = HUD()

        # ------------ UI SCREENS ------------
        self.main_menu = MainMenu(
            ui_parent=camera.ui,
            on_play=self.start_game,
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
        self.original_scales = {}
        for btn in (
            self.main_menu.buttons +
            self.gameover_screen.buttons +
            self.leaderboard_screen.buttons +
            self.instructions_screen.buttons
        ):
            self.original_scales[btn] = btn.scale

        # ------------ UI NAVIGATION STATE ------------
        self.focused_buttons = []
        self.focus_index = 0

        # Remember previous axis/button0 states (to edge‐detect)
        self.prev_axis_x = 0.0
        self.prev_axis_y = 0.0
        self.prev_button0 = False

        # ------------ NAME-ENTRY STATE ------------
        # Also track prev axis/button for name entry
        self.prev_ne_axis_x = 0.0
        self.prev_ne_axis_y = 0.0
        self.prev_ne_button0 = False

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

        for idx, btn in enumerate(buttons_list):
            if btn.enabled:
                self.focus_index = idx
                try:
                    btn.on_mouse_enter()
                except:
                    pass
                btn.scale = self.original_scales[btn] * 1.1
                return

    def _move_focus(self, direction):
        """
        Move focus among self.focused_buttons, skipping disabled buttons.
        direction: 'up','down','left','right'
        """
        btns = self.focused_buttons
        n = len(btns)
        if n == 0:
            return

        enabled_indices = [i for i, b in enumerate(btns) if b.enabled]
        if not enabled_indices:
            return

        old_idx = self.focus_index
        if old_idx not in enabled_indices:
            new_idx = enabled_indices[0]
        else:
            # Game Over’s 2×2 grid
            if self.game_state == 'gameover' and len(btns) == 4:
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
                new_idx = candidate if candidate in enabled_indices else old_idx
            else:
                # Single‐column list behavior (only 'up'/'down')
                if direction not in ('up', 'down'):
                    return
                pos = enabled_indices.index(old_idx)
                if direction == 'up':
                    pos = (pos - 1) % len(enabled_indices)
                elif direction == 'down':
                    pos = (pos + 1) % len(enabled_indices)
                new_idx = enabled_indices[pos]

        if new_idx != old_idx:
            try:
                btns[old_idx].on_mouse_exit()
            except:
                pass
            if btns[old_idx] in self.original_scales:
                btns[old_idx].scale = self.original_scales[btns[old_idx]]

            try:
                btns[new_idx].on_mouse_enter()
            except:
                pass
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
        """
        self.game_state = 'playing'
        self.match_start_time = time.time()
        self.last_score = 0
        self.score_saved = False

        # Hide UI
        self.main_menu.hide()
        self.gameover_screen.hide()
        self.name_entry.hide()
        self.leaderboard_screen.hide()
        self.instructions_screen.hide()

        # Reset players
        self.p1.health = 100
        self.p2.health = 100
        self.p1.position = (-5, 0.5, -5)
        self.p2.position = (5, 0.5, 5)

        # Enable map + players
        for e in self.game_entities:
            e.enabled = True

        # Enable HUD
        self.hud.enable()

    def end_game(self, winner: Player):
        """
        Called when one player's HP ≤ 0. Calculate final score, show Game Over UI.
        """
        self.game_state = 'gameover'
        self.match_end_time = time.time()
        self.score_saved = False

        # Disable map + players
        for e in self.game_entities:
            e.enabled = False
        # Disable HUD
        self.hud.disable()

        # Compute score
        elapsed = self.match_end_time - self.match_start_time
        hp_lost = 100 - winner.health
        penalty = winner.hp_penalty
        base_score = 1000
        raw_score = base_score - int(elapsed * 10) - (hp_lost * penalty)
        self.last_score = max(0, raw_score)

        # Show Game Over UI and start confirm-delay timer
        self.gameover_screen.show(winner.name, self.last_score, self.score_saved)
        self.gameover_shown_time = time.time()

        # Prevent any held‐down Button 0 or axis from immediately retriggering
        self.prev_button0 = True
        self.prev_axis_x  = 0.0
        self.prev_axis_y  = 0.0

        # Rebuild focus list so it skips “Save Score” if we just saved before
        self._set_focus(self.gameover_screen.buttons)


    def show_name_entry(self):
        """
        Switch to the username-entry UI. Consume any Button 0 so it
        won’t immediately confirm here or back out.
        """
        self.game_state = 'name_entry'
        self.gameover_screen.hide()
        self.name_entry.show()
        self._clear_focus()

        # Consume any held Button 0 or axis so name-entry won't immediately fire ‘space’
        self.prev_ne_button0 = True
        self.prev_ne_axis_x  = 0.0
        self.prev_ne_axis_y  = 0.0


    def finish_name_entry(self, username):
        """
        Player finished entering their name. Save if any, then return to Game Over.
        """
        if username:
            add_score_to_leaderboard(username, self.last_score)
            self.score_saved = True

        self.name_entry.hide()

        # Re‐show Game Over UI, but now “Save Score” will be disabled
        self.gameover_screen.show(
            self.gameover_screen.gameover_winner_text.text.split('\n')[0].replace(' Wins!', ''),
            self.last_score,
            self.score_saved
        )
        self.gameover_shown_time = time.time()
        self.game_state = 'gameover'

        # Consume Button 0 and axis so we don’t immediately slip into another action
        self.prev_button0 = True
        self.prev_axis_x  = 0.0
        self.prev_axis_y  = 0.0

        # Rebuild focus list so it lands on the first enabled button (Restart or Main Menu)
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
        self.prev_axis_x = self.prev_axis_y = 0.0  # reset so navigation works cleanly
        self.prev_button0 = True
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
        self.prev_axis_x = self.prev_axis_y = 0.0
        self.prev_button0 = True
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
        self.prev_button0 = True
        self.prev_axis_x = self.prev_axis_y = 0.0
        self._set_focus(self.gameover_screen.buttons)

    def back_to_menu_from_leaderboard(self):
        """
        From leaderboard (launched by Main Menu), return to Main Menu.
        """
        self.game_state = 'menu'
        self.leaderboard_screen.hide()
        self.main_menu.show()
        self.prev_axis_x = self.prev_axis_y = 0.0
        self.prev_button0 = True
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
        self.prev_axis_x = self.prev_axis_y = 0.0
        self.prev_button0 = True
        self._set_focus(self.instructions_screen.buttons)

    def back_from_instructions(self):
        """
        From instructions, return to Main Menu.
        """
        self.game_state = 'menu'
        self.instructions_screen.hide()
        self.main_menu.show()
        self.prev_axis_x = self.prev_axis_y = 0.0
        self.prev_button0 = True
        self._set_focus(self.main_menu.buttons)

    # ─── URSINA UPDATE & INPUT ─────────────────────────────────────────────────

    def update(self):
        """
        Called every frame by Ursina.
        - Always pump pygame so joysticks stay current.
        - If in a menu state, poll P1’s joystick axes/button0 for navigation.
        - If in name_entry, translate axes/button0 into letter/slot changes.
        - If in playing, update players, projectiles, HUD, and check for simultaneous death.
        """
        # Pump pygame events so joystick/axis/button states update
        pygame.event.pump()

        # ----- MENU NAVIGATION (menu, gameover, leaderboard, instructions) -----
        if self.game_state in ('menu', 'gameover', 'leaderboard', 'instructions'):
            js0 = self.joysticks[0] if len(self.joysticks) > 0 else None
            if js0:
                # Read axes
                axis_x = js0.get_axis(0)  # left/right
                axis_y = js0.get_axis(1)  # up/down
                btn0 = js0.get_button(0)  # confirm/select

                # UP: axis_y < -0.5 edge‐detect
                if axis_y < -0.5 and self.prev_axis_y >= -0.5:
                    self._move_focus('up')
                # DOWN: axis_y > 0.5 edge‐detect
                if axis_y > 0.5 and self.prev_axis_y <= 0.5:
                    self._move_focus('down')
                # ONLY in Game Over: LEFT/RIGHT via axis_x
                if self.game_state == 'gameover':
                    if axis_x < -0.5 and self.prev_axis_x >= -0.5:
                        self._move_focus('left')
                    if axis_x > 0.5 and self.prev_axis_x <= 0.5:
                        self._move_focus('right')

                # CONFIRM: Button 0 (edge‐detect + delay on Game Over)  ⬅ CHANGED
                if btn0 and not self.prev_button0:
                    if not (self.game_state == 'gameover' and (time.time() - self.gameover_shown_time) < self.gameover_confirm_delay):
                        if self.focused_buttons:
                            btn = self.focused_buttons[self.focus_index]
                            if btn.enabled:
                                # If in main menu and Quit button, quit
                                if self.game_state == 'menu' and btn is self.main_menu.btn_quit:
                                    application.quit()
                                else:
                                    btn.on_click()

                # Update “prev” for next frame
                self.prev_axis_x = axis_x
                self.prev_axis_y = axis_y
                self.prev_button0 = btn0

        # ----- NAME ENTRY SCREEN -----
        if self.game_state == 'name_entry':
            js0 = self.joysticks[0] if len(self.joysticks) > 0 else None
            if js0:
                # Read axes + button0
                ne_axis_x = js0.get_axis(0)
                ne_axis_y = js0.get_axis(1)
                ne_btn0 = js0.get_button(0)

                # CYCLE LETTER UP: axis_y < -0.5 edge‐detect
                if ne_axis_y < -0.5 and self.prev_ne_axis_y >= -0.5:
                    self.name_entry.input('w')
                # CYCLE LETTER DOWN: axis_y > 0.5 edge‐detect
                if ne_axis_y > 0.5 and self.prev_ne_axis_y <= 0.5:
                    self.name_entry.input('s')
                # MOVE SLOT RIGHT: axis_x > 0.5 edge‐detect
                if ne_axis_x > 0.5 and self.prev_ne_axis_x <= 0.5:
                    self.name_entry.input('d')
                # MOVE SLOT LEFT: axis_x < -0.5 edge‐detect
                if ne_axis_x < -0.5 and self.prev_ne_axis_x >= -0.5:
                    self.name_entry.input('a')
                # CONFIRM: Button 0 (edge‐detect)
                if ne_btn0 and not self.prev_ne_button0:
                    self.name_entry.input('space')

                # Update previous for next frame
                self.prev_ne_axis_x = ne_axis_x
                self.prev_ne_axis_y = ne_axis_y
                self.prev_ne_button0 = ne_btn0

            return  # skip further update until name entry is done

        # ----- PLAYING STATE -----
        if self.game_state == 'playing':
            # Update HUD
            elapsed = time.time() - self.match_start_time
            self.hud.update(elapsed, self.p1.health, self.p2.health)

            # Update players (each polls its own joystick)
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
        Called whenever a keyboard/mouse event fires.
        We still keep original keyboard fallbacks here, but joystick
        navigation & name‐entry are handled entirely in update().
        """
        # In name‐entry, we want to allow typing via keyboard as well
        if self.game_state == 'name_entry':
            self.name_entry.input(key)
            return

        if self.game_state in ('menu', 'gameover', 'leaderboard', 'instructions'):
            # On Game Over, ignore Space if still within delay
            if self.game_state == 'gameover' and key in ('space', 'space hold'):
                if (time.time() - self.gameover_shown_time) < self.gameover_confirm_delay:
                    return

            # Fallback keyboard navigation (in case user hits keys instead of joystick)
            if key == 'w':
                self._move_focus('up')
                return
            if key == 's':
                self._move_focus('down')
                return
            if self.game_state == 'gameover':
                if key == 'a':
                    self._move_focus('left')
                    return
                if key == 'd':
                    self._move_focus('right')
                    return
            if key in ('space', 'space hold'):
                if self.focused_buttons:
                    btn = self.focused_buttons[self.focus_index]
                    if btn.enabled:
                        if self.game_state == 'menu' and btn is self.main_menu.btn_quit:
                            application.quit()
                        else:
                            btn.on_click()
                return
