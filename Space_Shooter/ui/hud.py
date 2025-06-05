from ursina import *
from panda3d.core import Point3, Point2


def project_to_screen(entity, cam_np, lens, region_offset=Vec2(0,0), region_scale=Vec2(1,1)):
    target_pos = entity.get_pos(render) + Vec3(0, .5, 0)  # vise le haut du vaisseau
    pos_3d = cam_np.get_relative_point(render, target_pos)

    p2d = Point2()
    if lens.project(pos_3d, p2d):
        return Vec2(p2d.x * region_scale.x + region_offset.x,
                    p2d.y * region_scale.y + region_offset.y)
    return None

def hud_creation(player, player2):
    crosshair_p1 = Text(
        text='||',
        position=(-0.445, 0.10),  # (x, y) de -1 à 1, coin haut gauche
        origin=(0,0),
        scale=1.5,
        color=color.rgba(1, 0, 0, 0.6),  # Couleur orange
        font ='VeraMono.ttf',
    )
    crosshair_p2 = Text(
        text='||',
        position=(0.445, 0.10),  # (x, y) de -1 à 1, coin haut gauche
        origin=(0,0),
        scale=1.5,
        color=color.rgba(1, 0, 0, 0.6),  # Couleur orange
        font ='VeraMono.ttf',
    )

    hud_left = Entity(parent=camera.ui)

    focus_circle_1 = Entity(
        parent=hud_left,
        model='quad',  # ou 'plane'
        #agrendir le model pour qu'il soit plus grand
        model_scale=Vec3(5, 5, 5),
        texture='models/cursor',  # <-- c'est ici qu'on met l'image
        color=color.rgba(255, 255, 0, 200),
    )

    hud_right = Entity(parent=camera.ui)

    focus_circle_2 = Entity(
        parent=hud_right,
        model='quad',
        #agrendir le model pour qu'il soit plus grand
        model_scale=Vec3(5, 5, 5),
        texture='models/cursor',  # <-- c'est ici qu'on met l'image
        color=color.rgba(255, 255, 0, 200),
    )

    pause_panel = Entity(
        model='quad',
        parent=hud_right,
        color=color.rgba(0, 0, 0, 0.6),
        scale=(1, 1),
        enabled=False,  # désactivé par défaut
    )
    # “Player X Wins!\nScore: Y”
    pauser_text = Text(
        text='azerrtyuiop',
        position=(0, 0),  # (x, y) de -1 à 1, coin haut gauche
        origin=(0,0),
        scale=1.5,
        color=color.rgba(1, 0, 0, 0.6),  # Couleur orange
        font ='VeraMono.ttf',
        enabled=False
    )
    return crosshair_p1, crosshair_p2, focus_circle_1, focus_circle_2, pause_panel, pauser_text

def update_hud_play(crosshair_p1, crosshair_p2, focus_circle_1, focus_circle_2, player, player2, cam1, cam2, lens1, lens2, speed, pause_panel, pauser_text):
     # ----- Gun orienté comme la caméra -----
    crosshair_p1.text = f'{speed}\n||'
    crosshair_p2.text = f'{player2.speed}\n||'

    screen_pos = project_to_screen(player2, cam1, lens1, region_offset=Vec2(-0.5, 0), region_scale=Vec2(0.5, 1))
    #print(f"Screen position player2: {screen_pos}")
    if screen_pos:
        focus_circle_1.position = Vec3(screen_pos.x * 0.89, screen_pos.y * 0.5, 0)
        focus_circle_1.visible = True
        #ajuster la taille du cercle en fonction de la distance
        distance_to_player2 = distance(player.world_position, player2.world_position)
        focus_circle_1.scale = Vec3(min(max(5 - distance_to_player2, 0.08), 0.5), min(max(5 - distance_to_player2, 0.08), 0.5), 1)
        focus_circle_1.rotation_z += 2
        #print(f"Distance to player2: {distance_to_player2}, Circle scale: {focus_circle_1.scale}")
    else:
        focus_circle_1.visible = False

    screen_pos2 = project_to_screen(player, cam2, lens2, region_offset=Vec2(0.5, 0), region_scale=Vec2(0.5, 1))
    #print(f"Screen position player: {screen_pos2}")
    if screen_pos2:
        focus_circle_2.position = Vec3(screen_pos2.x * 0.89, screen_pos2.y * 0.5, 0)
        focus_circle_2.visible = True
        #ajuster la taille du cercle en fonction de la distance
        distance_to_player = distance(player2.world_position, player.world_position)
        focus_circle_2.scale = Vec3(min(max(5 - distance_to_player, 0.08), 0.5), min(max(5 - distance_to_player, 0.08), 0.5), 1)
        focus_circle_2.rotation_z += 2
    else:
        focus_circle_2.visible = False

    # ----- Pause panel -----
    pause_panel.enabled = False
    pauser_text.enabled = False

def update_hud_pause(pause_panel, pauser_text):
    pause_panel.enabled = True
    pauser_text.enabled = True
    pauser_text.text = 'PAUSED\nPress A to resume'
    # On peut ajouter d'autres éléments d'interface utilisateur ici si nécessaire

def update_hud_end_game(pause_panel, pauser_text):
    pause_panel.enabled = True
    pauser_text.enabled = True
    pauser_text.text = 'GAME END\nPress A to resume'

    # On peut ajouter d'autres éléments d'interface utilisateur ici si nécessaire