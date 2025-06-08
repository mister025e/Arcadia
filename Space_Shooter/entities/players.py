from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from entities.lazer import Lazer
from ursina.shaders import lit_with_shadows_shader

def players_creation(editor_camera):
    player = FirstPersonController(model='cube', color=color.blue, collider='box', position=(0, 500, 0))
    player.visible_self = editor_camera.enabled
    player.name = 'player1'
    player_body = Entity(parent=player, model='models/Xwing', texture='models/Xwing_color',shader=lit_with_shadows_shader,color=color.white, position=(0,0,0), scale=(0.3,0.3,0.3))
    player_body.rotation = Vec3(0, 180, 0)  # Pour que le joueur regarde dans la direction opposée

    player.speed = 20
    player.update = Func(lambda: None)  # désactive le comportement FPS par défaut
    player.collider = BoxCollider(player, Vec3(0,0,0), Vec3(6.5,2,6.5))
    #player.collider.visible = True  # Rendre le collider visible pour le débogage
    player.gun = Entity(model='scale_gizmo', parent=player, position=(0,0,0), scale=(1,.5,1), origin_z=-.5, color=color.red, on_cooldown=False)

    player.position = (0, 500, 10)  # <-- Force la position après la désactivation du comportement

    # Joueur 2 (rouge)
    player2 = Entity(model='cube', color=color.orange, position=(5, 20, 0))
    player2.speed = 20
    player2.visible_self = editor_camera.enabled
    player2.name = 'player2'
    player2_body = Entity(parent=player2, model='models/imp_fly_tieinterceptor', texture = 'models/imp_fly_tiefighter',shader=lit_with_shadows_shader, position=(0,-0.5,0), scale=(0.5,0.5,0.5), color=color.white)
    player2_body.rotation = Vec3(0, 180, 0)  # Pour que le joueur regarde dans la direction opposée
    player2.update = Func(lambda: None)
    player2.collider = BoxCollider(player2, Vec3(0,0,.5), Vec3(3.5,2.5,3))
    #player2.collider.visible = True  # Rendre le collider visible pour le débogage
    player2.gun = Entity(model='scale_gizmo', parent=player2, position=(0,0,0), scale=(1,.5,1), origin_z=-.5, color=color.red, on_cooldown=False)
    player2.position = (0, 500, -10)  # <-- Idem pour player2
    player2.rotate(Vec3(0, 180, 0), relative_to=player2)  # Pour que player2 regarde dans la direction opposée

    return player, player2

def players_setup(player, player2):
    # Position initiale des joueurs
    player.position = (0, 500, 10)
    player2.position = (0, 500, -10)

    # Rotation initiale des joueurs
    player.rotation = Vec3(0, 0, 0)
    player2.rotation = Vec3(0, 180, 0)  # Pour que player2 regarde dans la direction opposée

    # Vitesse initiale
    player.speed = 20
    player2.speed = 20

def players_input(player, player2, cam1, cam2, focus_circle_1, focus_circle_2):
    rotation_speed = 60 * time.dt

    if held_keys['w']:
        player.rotate(Vec3(rotation_speed, 0, 0), relative_to=player)
    if held_keys['s']:
        player.rotate(Vec3(-rotation_speed, 0, 0), relative_to=player)
    if held_keys['d']:
        player.rotate(Vec3(0, 0, rotation_speed*3), relative_to=player)
    if held_keys['a']:
        player.rotate(Vec3(0, 0, -rotation_speed*3), relative_to=player)
    if held_keys['t']:
        player.speed += 2 
        if player.speed > 300:
            player.speed = 300
    if held_keys['y']:
        player.speed -= 2
        if player.speed < 10:
            player.speed = 10
    if held_keys['g']:
        #vue de derrière
        cam1.set_pos(0, 2.2, 20)
    else:
        #vue de devant
        cam1.set_pos(0, 2.2, -20 - 20 *(player.speed/500))
    if held_keys['l']:
        #vue de derrière
        cam2.set_pos(0, 2.2, 20)
    else:
        cam2.set_pos(0, 2.2, -20 - 20 *(player2.speed/500))

    if held_keys['up arrow']:
        player2.rotate(Vec3(rotation_speed, 0, 0), relative_to=player2)
    if held_keys['down arrow']:
        player2.rotate(Vec3(-rotation_speed, 0, 0), relative_to=player2)
    if held_keys['right arrow']:
        player2.rotate(Vec3(0, 0, rotation_speed*3), relative_to=player2)
    if held_keys['left arrow']:
        player2.rotate(Vec3(0, 0, -rotation_speed*3), relative_to=player2)
    if held_keys['o']:
        player2.speed += 2 
        if player2.speed > 300:
            player2.speed = 300
    if held_keys['p']:
        player2.speed -= 2
        if player2.speed < 10:
            player2.speed = 10
    # ----- Déplacement dans la direction du gun -----
    
    player.position += player.gun.forward * player.speed * time.dt
    player2.position += player2.gun.forward * player2.speed * time.dt

    # ----- Tir -----
    if held_keys['f']:
        lazer_entity = Lazer(gun=player.gun, focus_circle = focus_circle_1, target = player2, color=color.red)


    if held_keys['k']:
        lazer_entity = Lazer(gun=player2.gun, focus_circle = focus_circle_2, target = player, color=color.red)

def entities_interaction(player, player2):
    # Détection collision player <-> sphères
    for e in scene.entities:
        if player.intersects(e).hit:
            print(f"Collision1 avec une sphère à la position {e.position}, name: {e.name}, model: {e.model}")
            return 1
            # Tu peux ajouter ici une action (détruire la sphère, perdre de la vie, etc.)
        if player2.intersects(e).hit:
            print(f"Collision avec une sphère à la position {e.position}")
            return 2
            # Tu peux ajouter ici une action (détruire la sphère, perdre de la vie, etc.)
    return 0  # Pas de collision détectée