from ursina import Ursina, camera, time, color, application
from entities.player import Player
from entities.projectile import Projectile
from map.world import World
from ui.hud import HUD
from ui.menu import MainMenu
from ui.gameover import GameOverScreen
from ui.name_entry import NameEntryScreen
from ui.leaderboard import LeaderboardScreen
from utils.file_manager import load_leaderboard, add_score_to_leaderboard

import os


class GameManager:
    """
    Orchestrates game states, transitions, and Ursina’s update/input callbacks.
    """

    def __init__(self, app):
        # Keep reference to the Ursina app
        self.app = app

        # Game state can be: 'menu', 'playing', 'gameover', 'name_entry', 'leaderboard'
        self.game_state = 'menu'
        self.match_start_time = 0
        self.match_end_time = 0
        self.last_score = 0
        self.score_saved = False

        # Load existing leaderboard once
        self.leaderboard_data = load_leaderboard()

        # Create world (map)
        self.world = World()

        # List of active projectiles
        self.projectiles = []

        # Create two players (pass spawn_callback so we can track projectiles)
        from ursina import color  # import here to get color constants

        self.p1 = Player(
            name='Player 1',
            position=(-5, 0.5, -5),
            keys={'up': 'w', 'down': 's', 'left': 'a', 'right': 'd', 'shoot': 'space'},
            color=color.azure,
            hp_penalty=2,
            spawn_callback=self.register_projectile
        )
        self.p2 = Player(
            name='Player 2',
            position=(5, 0.5, 5),
            keys={'up': 'up arrow', 'down': 'down arrow', 'left': 'left arrow', 'right': 'right arrow', 'shoot': 'right shift'},
            color=color.orange,
            hp_penalty=2,
            spawn_callback=self.register_projectile
        )

        # Create HUD (timer + HP bars)
        self.hud = HUD()

        # Create UI screens (attach to camera.ui)
        self.main_menu = MainMenu(
            ui_parent=camera.ui,
            on_play=self.start_game,
            on_quit=application.quit
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

        # Attach HUD texts to camera.ui
        self.hud.attach_to_ui(camera.ui)

        # Collect all “game entities” (map + players) so we can toggle them as a group:
        self.game_entities = (
            self.world.entities + [self.p1, self.p2]
        )

        # Initially, hide everything except the main menu
        self._hide_all_entities_and_ui()
        self.show_main_menu()

    def register_projectile(self, proj):
        """
        Called by Player._shoot() whenever a new Projectile is created.
        We append it to our list so we can update it each frame.
        """
        self.projectiles.append(proj)

    def _hide_all_entities_and_ui(self):
        # Disable every map entity + players
        for e in self.game_entities:
            e.enabled = False

        # Disable HUD
        self.hud.disable()

        # Hide all UI screens
        self.main_menu.hide()
        self.gameover_screen.hide()
        self.name_entry.hide()
        self.leaderboard_screen.hide()

    def show_main_menu(self):
        """
        Enter the 'menu' state: hide all others, show only main menu.
        """
        self.game_state = 'menu'
        self._hide_all_entities_and_ui()
        self.main_menu.show()

    def start_game(self):
        """
        Enter the 'playing' state: reset HP, timer, enable world & players & HUD.
        """
        self.game_state = 'playing'
        self.match_start_time = time.time()
        self.last_score = 0
        self.score_saved = False

        # Hide all UI screens
        self.main_menu.hide()
        self.gameover_screen.hide()
        self.name_entry.hide()
        self.leaderboard_screen.hide()

        # Reset player health and positions
        self.p1.health = 100
        self.p2.health = 100
        self.p1.position = (-5, 0.5, -5)
        self.p2.position = ( 5, 0.5,  5)

        # Enable world entities and players
        for e in self.game_entities:
            e.enabled = True

        # Enable HUD
        self.hud.enable()

    def end_game(self, winner: Player):
        """
        Called when one player's HP ≤ 0. Calculate final score, show game‐over UI.
        """
        self.game_state = 'gameover'
        self.match_end_time = time.time()
        self.score_saved = False  # newly ended match, not yet saved

        # Disable world & players
        for e in self.game_entities:
            e.enabled = False

        # Disable HUD
        self.hud.disable()

        # Compute final score
        elapsed = self.match_end_time - self.match_start_time
        hp_lost = 100 - winner.health
        penalty = winner.hp_penalty
        base_score = 1000
        raw_score = base_score - int(elapsed * 10) - (hp_lost * penalty)
        self.last_score = max(0, raw_score)

        # Show Game Over screen
        self.gameover_screen.show(winner.name, self.last_score, self.score_saved)

    def show_name_entry(self):
        """
        Transition to the name‐entry UI. Keep gameover text behind but hide its buttons.
        """
        self.game_state = 'name_entry'
        self.gameover_screen.hide()  # hide all gameover elements
        self.name_entry.show()

    def finish_name_entry(self, username):
        """
        Called after player confirms the 6‐letter name (or leaves blank).
        If non‐empty, save it to leaderboard.json.
        Then return to gameover screen.
        """
        if username:
            add_score_to_leaderboard(username, self.last_score)
            self.score_saved = True

        # Return to Game Over screen (with Save Score disabled if already saved)
        self.name_entry.hide()
        self.gameover_screen.show(
            self.gameover_screen.gameover_winner_text.text.split('\n')[0].replace(' Wins!', ''),
            self.last_score,
            self.score_saved
        )
        self.game_state = 'gameover'

    def show_leaderboard(self):
        """
        Hide gameover UI; display the top‐10 leaderboard list.
        """
        self.game_state = 'leaderboard'
        self.gameover_screen.hide()
        # Reload the leaderboard data from file, in case it changed
        self.leaderboard_data = load_leaderboard()
        self.leaderboard_screen.show(self.leaderboard_data)

    def back_to_gameover(self):
        """
        From the leaderboard screen, return to the gameover UI
        (Save Score only if not yet saved).
        """
        self.game_state = 'gameover'
        self.leaderboard_screen.hide()
        self.gameover_screen.show(
            self.gameover_screen.gameover_winner_text.text.split('\n')[0].replace(' Wins!', ''),
            self.last_score,
            self.score_saved
        )

    def update(self):
        """
        Called every frame by Ursina.
        - If ‘playing’, update players, projectiles, HUD, and check for simultaneous death.
        """
        if self.game_state == 'playing':
            elapsed = time.time() - self.match_start_time
            self.hud.update(elapsed, self.p1.health, self.p2.health)

            # Update players via game_update
            self.p1.game_update(self.game_state)
            self.p2.game_update(self.game_state)

            # Update all active projectiles
            for proj in self.projectiles.copy():
                if proj.enabled:
                    proj.game_update(self.game_state, self.end_game)
                else:
                    self.projectiles.remove(proj)

            # If both died in same frame, give a default winner (e.g. p1)
            if self.p1.health <= 0 and self.p2.health <= 0:
                self.end_game(self.p1)

    def input(self, key):
        """
        Called whenever a key is pressed or released.
        - If we’re in name‐entry, delegate to that screen.
        - Otherwise, do nothing (players handle movement/shooting themselves).
        """
        if self.game_state == 'name_entry':
            self.name_entry.input(key)

    def run(self):
        """
        Finally kick off Ursina’s main loop.
        """
        self.app.run()
