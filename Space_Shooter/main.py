from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
from ursina import raycast, window
from panda3d.core import PerspectiveLens, Camera, NodePath
from panda3d.core import Point3, Point2
from panda3d.core import BitMask32
from direct.showbase.Loader import Loader
from panda3d.core import MovieTexture
from world.map_gen import map_generation
from entities.players import players_creation, players_input, entities_interaction, players_setup
from ui.camera import camera_creation
from ui.hud import hud_creation, update_hud_play, update_hud_pause, update_hud_end_game, update_hud_menu
import random

CAM1_MASK = BitMask32.bit(1)
CAM2_MASK = BitMask32.bit(2)

app = Ursina()

random.seed(0)
rng_fx = random.Random()
Entity.default_shader = lit_with_shadows_shader

map_generation()

editor_camera = EditorCamera(enabled=False, ignore_paused=True)

player, player2 = players_creation(editor_camera)

# Lens avec bon ratio (2x car demi-largeur)
cam1, cam2, lens1, lens2 = camera_creation(player, player2, CAM1_MASK, CAM2_MASK)
# Variables pour stocker la rotation
pivot_rotation_x = 10
player_win = None

crosshair_p1, crosshair_p2, focus_circle_1, focus_circle_2, pause_panel, pauser_text, boussole, modelwayfinderP1, modelwayfinderP2, boussole2, hyperspeed, video_tex, hyperspeed_preview, control = hud_creation(player, player2)
music_menu = Audio('audio/Star_Wars_The_Imperial_March_Theme_Song.ogg', loop=True, autoplay=True, volume=0.5)
music_play = Audio('audio/Battle_Of_The_Heroes.ogg', loop=True, autoplay=False, volume=0.5)
list_music = ['Anakin_Vs_Obi-Wan.ogg', 'Battle_Of_The_Heroes.ogg', 'Imperial_Attack.ogg', 'The_Battle_Of_Endor_I.ogg', 'The_Battle_Of_Endor_III.ogg']

class GameState:
    current = 'menu'
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

    @classmethod
    def menu(cls):
        cls.current = 'menu'


def update():
    global pivot_rotation_x, crosshair_p1, crosshair_p2, pause_panel, pauser_text, player_win, boussole, modelwayfinderP1, modelwayfinderP2, boussole2, hyperspeed, video_tex, hyperspeed_preview, music_menu, list_music, control
    cam1.look_at(player)
    cam2.look_at(player2)
    if GameState.current == 'play':
        # ----- Mouvement joueur -----
        players_input(player, player2, cam1, cam2, focus_circle_1, focus_circle_2)

        update_hud_play(crosshair_p1, crosshair_p2, focus_circle_1, focus_circle_2, player, player2, cam1, cam2, lens1, lens2, pause_panel, pauser_text, boussole, modelwayfinderP1, modelwayfinderP2, boussole2, CAM1_MASK, CAM2_MASK, video_tex)
        #print(player.pv, player2.pv)

        if entities_interaction(player, player2) != 0:
            player_win = 'PLAYER 2 WIN' if entities_interaction(player, player2) == 1 else 'PLAYER 1 WIN' if entities_interaction(player, player2) == 2 else "ALL PLAYERS LOOSE"
            GameState.end_game()
            music_play.stop()
            music_menu.play()
            #print(player.pv, player2.pv)
    elif GameState.current == 'pause':
        # On ne fait rien, le jeu est en pause
        # si n'importe quel touche est pressé
        if any(held_keys.values()) and not held_keys['q'] and not held_keys['z']:
            control.enabled = True
            pauser_text.enabled = False
        # si aucune touche pressée
        else:
            control.enabled = False
            update_hud_pause(pause_panel, pauser_text)
    elif GameState.current == 'end_game':
        hyperspeed_preview.enabled = True
        update_hud_end_game(pause_panel, pauser_text, player_win)
    if GameState.current == 'menu':
        focus_circle_1.enabled = False
        focus_circle_2.enabled = False
        #video_tex.update()
        update_hud_menu(pause_panel, pauser_text)
    if GameState.current == 'setup_game':
        if GameState.changed:
            GameState.changed = False
            pause_panel.enabled = False
            pauser_text.enabled = False
            hyperspeed.enabled = True
            hyperspeed_preview.enabled = False
            video_tex.play()
            players_setup(player, player2)
            def show_1():
                invoke(show_2, delay=1.7)
            def show_2():
                Audio('audio/Star_Wars_Hyperdrive_Sound_Effect.ogg', volume=0.5)
                invoke(hide_and_start, delay=1.5)
            def hide_and_start():
                pauser_text.enabled = False
                focus_circle_1.enabled = True
                focus_circle_2.enabled = True
                hyperspeed.enabled = False
                music_menu.stop()
                global music_play
                music_play = Audio(f'audio/{list_music[rng_fx.randint(0, len(list_music)-1)]}', loop=True, autoplay=True, volume=0.5)
                GameState.start_game()
            show_1()

def pause_input(key):
    if key == 'q':
        if GameState.current == 'end_game' or GameState.current == 'menu':
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

window.fullscreen = True
window.fps_counter.enabled = False  # désactive les FPS
window.exit_button.visible = False  # désactive le bouton de fermeture de la fenêtre

app.run()