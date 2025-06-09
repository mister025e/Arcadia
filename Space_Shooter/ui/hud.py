from ursina import *
from panda3d.core import Point3, Point2
from panda3d.core import BitMask32
# from ursina.internal_utils import get_panda3d_node_path
from math import atan2, degrees, radians, sin, cos
from ursina import Vec3


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
        font ='models/Tiny5-Regular.ttf',
    )
    crosshair_p2 = Text(
        text='||',
        position=(0.445, 0.10),  # (x, y) de -1 à 1, coin haut gauche
        origin=(0,0),
        scale=1.5,
        color=color.rgba(1, 0, 0, 0.6),  # Couleur orange
        font ='models/Tiny5-Regular.ttf',
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
        texture='models/overlay',  # <-- c'est ici qu'on met l'image
        parent=hud_right,
        color=color.rgba(255, 255, 255, 255),
        scale=(0.7, 1),
        enabled=False,  # désactivé par défaut
    )
    # “Player X Wins!\nScore: Y”
    pauser_text = Text(
        text='azerrtyuiop',
        position=(0, 0.1),  # (x, y) de -1 à 1, coin haut gauche
        origin=(0,0),
        scale=1.5,
        color=color.rgb(255, 235, 82),  # Couleur orange
        font ='models/Tiny5-Regular.ttf',
        enabled=False
    )

    boussole = Entity(
        model='plane',  # Utilise un modèle circulaire au lieu de 'quad'
        color=color.rgba(255,0,0,0),
        position=Vec3(0, 0, 0),  # coin haut droit
        origin=(0, 0, -5),  # origine au centre du cercle
    )

    modelwayfinderP1 = Entity(
        parent=boussole,
        model='models/modelwayfinder',  # Utilise un modèle circulaire au lieu de 'quad'
        texture='models/modelwayfinderTexture',
        color=color.rgba(255,255,255,128),
        position=Vec3(0, 0, 5),  # coin haut droit
        scale = Vec3(0.8, 0.8, 0.8),  # Ajuste la taille du modèle
    )
    boussole2 = Entity(
        model='plane',  # Utilise un modèle circulaire au lieu de 'quad'
        color=color.rgba(255,0,0,0),
        position=Vec3(0, 0, 0),  # coin haut droit
        origin=(0, 0, -5),  # origine au centre du cercle
    )

    modelwayfinderP2 = Entity(
        parent=boussole2,
        model='models/modelwayfinder',  # Utilise un modèle circulaire au lieu de 'quad'
        texture='models/modelwayfinderTexture',
        color=color.rgba(255,255,255,128),
        position=Vec3(0, 0, 5),  # coin haut droit
        scale = Vec3(0.8, 0.8, 0.8),  # Ajuste la taille du modèle
    )

    return crosshair_p1, crosshair_p2, focus_circle_1, focus_circle_2, pause_panel, pauser_text, boussole, modelwayfinderP1, modelwayfinderP2, boussole2

def update_hud_play(crosshair_p1, crosshair_p2, focus_circle_1, focus_circle_2, player, player2, cam1, cam2, lens1, lens2, pause_panel, pauser_text, boussole, modelwayfinderP1, modelwayfinderP2, boussole2, CAM1_MASK, CAM2_MASK):
     # ----- Gun orienté comme la caméra -----
    crosshair_p1.text = f'{player.speed}\n| |'
    crosshair_p2.text = f'{player2.speed}\n| |'
    
    modelwayfinderP1.show(CAM1_MASK)
    modelwayfinderP1.hide(CAM2_MASK)
    modelwayfinderP2.show(CAM2_MASK)
    modelwayfinderP2.hide(CAM1_MASK)

    screen_pos = project_to_screen(player2, cam1, lens1, region_offset=Vec2(-0.5, 0), region_scale=Vec2(0.5, 1))
    #print(f"Screen position player2: {screen_pos}")
    if screen_pos:
        focus_circle_1.position = Vec3(screen_pos.x * 0.89, screen_pos.y * 0.5, 0)
        focus_circle_1.visible = True
        #ajuster la taille du cercle en fonction de la distance
        distance_to_player2 = distance(player.world_position, player2.world_position)
        focus_circle_1.scale = Vec3(min(max(5 - distance_to_player2, 0.08), 0.5), min(max(5 - distance_to_player2, 0.08), 0.5), 1)
        focus_circle_1.rotation_z += 2
        if 0 < focus_circle_1.position.y < 0.152 and -0.52 < focus_circle_1.position.x < -0.37:
            focus_circle_1.color = color.rgba(0, 255, 0, 200)  # Change la couleur du cercle si le joueur est dans la zone
        else:
            focus_circle_1.color = color.rgba(255, 255, 0, 200)
        #print(focus_circle_1.position)
        #print(f"Distance to player2: {distance_to_player2}, Circle scale: {focus_circle_1.scale}")
        boussole.visible = False
    else:
        focus_circle_1.visible = False
        # ----- Boussole -----
        boussole.visible = True
        #s'orienter vers le joueur 2
        boussole.position = player.position  # Positionner la boussole au-dessus du joueur
        boussole.look_at(player2.world_position)
        modelwayfinderP1.rotation = (0, 0, 0)  # reset local rotation
        modelwayfinderP1.rotation_z = 0  # aligne la flèche vers le haut de la boussole
        modelwayfinderP1.rotation_x += 90  # Réinitialiser la rotation X pour éviter l'inclinaison
        

    screen_pos2 = project_to_screen(player, cam2, lens2, region_offset=Vec2(0.5, 0), region_scale=Vec2(0.5, 1))
    #print(f"Screen position player: {screen_pos2}")
    if screen_pos2:
        focus_circle_2.position = Vec3(screen_pos2.x * 0.89, screen_pos2.y * 0.5, 0)
        focus_circle_2.visible = True
        #ajuster la taille du cercle en fonction de la distance
        distance_to_player = distance(player2.world_position, player.world_position)
        focus_circle_2.scale = Vec3(min(max(5 - distance_to_player, 0.08), 0.5), min(max(5 - distance_to_player, 0.08), 0.5), 1)
        focus_circle_2.rotation_z += 2
        if 0 < focus_circle_2.position.y < 0.152 and 0.37 < focus_circle_2.position.x < 0.52:
            focus_circle_2.color = color.rgba(0, 255, 0, 200)  # Change la couleur du cercle si le joueur est dans la zone
        else:
            focus_circle_2.color = color.rgba(255, 255, 0, 200)
        boussole2.visible = False
    else:
        focus_circle_2.visible = False
        boussole2.visible = True
        #s'orienter vers le joueur 2
        boussole2.position = player2.position  # Positionner la boussole au-dessus du joueur
        boussole2.look_at(player.world_position)
        modelwayfinderP2.rotation = (0, 0, 0)  # reset local rotation
        modelwayfinderP2.rotation_z = 0  # aligne la flèche vers le haut de la boussole
        modelwayfinderP2.rotation_x += 90  # Réinitialiser la rotation X pour éviter l'inclinaison


    # ----- Pause panel -----
    pause_panel.enabled = False
    pauser_text.enabled = False

def update_hud_pause(pause_panel, pauser_text):
    pause_panel.enabled = True
    pauser_text.enabled = True
    pauser_text.text = 'PAUSED\nPress A to resume'
    # On peut ajouter d'autres éléments d'interface utilisateur ici si nécessaire

def update_hud_end_game(pause_panel, pauser_text, player_win):
    pause_panel.enabled = True
    pauser_text.enabled = True
    pauser_text.text = f'GAME END\n{player_win}\nPress A to restart\nPress W to quit'

    # On peut ajouter d'autres éléments d'interface utilisateur ici si nécessaire