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
speed = 20

crosshair_p1, crosshair_p2, focus_circle_1, focus_circle_2, pause_panel, pauser_text = hud_creation(player, player2)

class GameState:
    current = 'play'

    @classmethod
    def toggle(cls):
        cls.current = 'pause' if cls.current == 'play' else 'play' if cls.current != 'end_game' else cls.current
        print(f"Game state changed to: {cls.current}")

    @classmethod
    def end_game(cls):
        cls.current = 'end_game'

    @classmethod
    def reset(cls):
        cls.current = 'play'
        players_setup(player, player2)


def update():
    global pivot_rotation_x, speed, crosshair_p1, crosshair_p2, pause_panel, pauser_text
    if GameState.current == 'play':
        cam1.look_at(player)
        cam2.look_at(player2)
        # ----- Mouvement joueur -----
        speed = players_input(player, player2, cam1, cam2, speed)

        update_hud_play(crosshair_p1, crosshair_p2, focus_circle_1, focus_circle_2, player, player2, cam1, cam2, lens1, lens2, speed, pause_panel, pauser_text)

        if entities_interaction(player, player2) != 0:
            GameState.end_game()
    elif GameState.current == 'pause':
        # On ne fait rien, le jeu est en pause
        update_hud_pause(pause_panel, pauser_text)
    elif GameState.current == 'end_game':
        update_hud_end_game(pause_panel, pauser_text)

def pause_input(key):
    if key == 'q':
        if GameState.current == 'end_game':
            GameState.reset()
        else:
            GameState.toggle()
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