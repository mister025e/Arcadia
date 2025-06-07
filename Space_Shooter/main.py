from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
from ursina import raycast
from panda3d.core import PerspectiveLens, Camera, NodePath
from panda3d.core import Point3, Point2
from world.map_gen import map_generation
from entities.players import players_creation, players_input, entities_interaction, players_setup
from ui.camera import camera_creation
from ui.hud import hud_creation, update_hud_play, update_hud_pause, update_hud_end_game

app = Ursina()

random.seed(0)
Entity.default_shader = lit_with_shadows_shader

map_generation()

editor_camera = EditorCamera(enabled=False, ignore_paused=True)

player, player2 = players_creation(editor_camera)

# Lens avec bon ratio (2x car demi-largeur)
cam1, cam2, lens1, lens2 = camera_creation(player, player2)
# Variables pour stocker la rotation
pivot_rotation_x = 10
player_win = None

crosshair_p1, crosshair_p2, focus_circle_1, focus_circle_2, pause_panel, pauser_text, boussole, modelwayfinderP1 = hud_creation(player, player2)

class GameState:
    current = 'setup_game'
    changed = True  # pour détecter les transitions

    @classmethod
    def toggle(cls):
        cls.current = 'pause' if cls.current == 'play' else 'play' if cls.current == 'pause' else cls.current

    @classmethod
    def end_game(cls):
        cls.current = 'end_game'

    @classmethod
    def reset(cls):
        if cls.current != 'setup_game':
            cls.current = 'setup_game'
            cls.changed = True

    @classmethod
    def start_game(cls):
        cls.current = 'play'


def update():
    global pivot_rotation_x, crosshair_p1, crosshair_p2, pause_panel, pauser_text, player_win, boussole, modelwayfinderP1
    cam1.look_at(player)
    cam2.look_at(player2)
    if GameState.current == 'play':
        # ----- Mouvement joueur -----
        players_input(player, player2, cam1, cam2)

        update_hud_play(crosshair_p1, crosshair_p2, focus_circle_1, focus_circle_2, player, player2, cam1, cam2, lens1, lens2, pause_panel, pauser_text, boussole, modelwayfinderP1)

        if entities_interaction(player, player2) != 0:
            player_win = 'PLAYER 2' if entities_interaction(player, player2) == 1 else 'PLAYER 1'
            GameState.end_game()
    elif GameState.current == 'pause':
        # On ne fait rien, le jeu est en pause
        update_hud_pause(pause_panel, pauser_text)
    elif GameState.current == 'end_game':
        update_hud_end_game(pause_panel, pauser_text, player_win)
    if GameState.current == 'setup_game':
        if GameState.changed:
            GameState.changed = False
            players_setup(player, player2)
            def show_3():
                pauser_text.enabled = True
                pauser_text.text = '3'
                invoke(show_2, delay=1)
            def show_2():
                pauser_text.text = '2'
                invoke(show_1, delay=1)
            def show_1():
                pauser_text.text = '1'
                invoke(hide_and_start, delay=1)
            def hide_and_start():
                pauser_text.enabled = False
                GameState.start_game()
            show_3()

def pause_input(key):
    if key == 'q':
        if GameState.current == 'end_game':
            GameState.reset()
        else:
            GameState.toggle()
    elif key == 'z':
        #quitter la fenetre
        application.quit()
    elif key == 'tab':    # press tab to toggle edit/play mode
        editor_camera.enabled = not editor_camera.enabled
        #gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position

        application.paused = editor_camera.enabled

pause_handler = Entity(ignore_paused=True, input=pause_input)


sun = DirectionalLight()
sun.look_at(Vec3(1,-1,-1))
sun.color = color.white
sun.intensity = 2

ambient = AmbientLight()
ambient.color = color.rgba(255, 255, 255, 64)

Sky(texture='models/ciel_etoile2')

base.win.remove_display_region(base.camNode.get_display_region(0))
player.cursor.enabled = False

sun.color = color.white  # lumière blanche pure
sun.intensity = 10       # valeur >1 pour plus de lumière (par défaut 1)

app.run()