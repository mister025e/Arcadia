from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from entities.lazer import Lazer

def players_creation(editor_camera):
    player = FirstPersonController(model='cube', color=color.blue, collider='box')
    player.visible_self = editor_camera.enabled
    player.name = 'player1'
    # Ajoute le visuel voulu comme enfant
    player_body = Entity(parent=player, model='cube', texture='shore', position=(0,0,0), scale=(2,0.2,1), color=color.blue)

    player.speed = 20
    player.update = Func(lambda: None)  # désactive le comportement FPS par défaut
    player.collider = BoxCollider(player, Vec3(0,0,0), Vec3(2,.5,2))
    #player.collider.visible = True
    player.gun = Entity(model='scale_gizmo', parent=player, position=(0,0,0), scale=(1,.5,1), origin_z=-.5, color=color.red, on_cooldown=False)

    # Joueur 2 (rouge)
    player2 = Entity(model='cube', color=color.orange, position=(5, 2, 0))
    player2.speed = 20
    player2.visible_self = editor_camera.enabled
    player2.name = 'player2'
    player2_body = Entity(parent=player2, model='cube', texture = 'shore', position=(0,0,0), scale=(2,0.2,1), color=color.red)
    player2.update = Func(lambda: None)  # désactive le comportement FPS par défaut
    player2.collider = BoxCollider(player2, Vec3(0,0,0), Vec3(2,5,2))
    #player2.collider.visible = True
    player2.gun = Entity(model='scale_gizmo', parent=player2, position=(0,0,0), scale=(1,.5,1), origin_z=-.5, color=color.red, on_cooldown=False)
    return player, player2

def players_input(player, player2, cam1, cam2, speed):
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
        speed += 2 
        if speed > 300:
            speed = 300
    if held_keys['y']:
        speed -= 2
        if speed < 10:
            speed = 10
    if held_keys['g']:
        #vue de derrière
        cam1.set_pos(0, 2.2, 20)
    else:
        #vue de devant
        cam1.set_pos(0, 2.2, -20 - 20 *(speed/500))
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
    
    player.position += player.gun.forward * speed * time.dt
    player2.position += player2.gun.forward * player2.speed * time.dt

    # ----- Tir -----
    if held_keys['f']:
        corrected_dir = player.gun.forward.normalized()

        # Position actuelle et vitesse estimée de l'adversaire
        enemy_pos = player2.world_position
        enemy_velocity = player2.gun.forward.normalized() * player2.speed

        # Estimation du temps que le lazer mettrait à atteindre la cible actuelle
        distance_to_enemy = distance(player.gun.world_position, enemy_pos)
        laser_speed = 150  # même valeur que dans ta classe Lazer
        estimated_time = distance_to_enemy / laser_speed

        # Position prédite
        predicted_pos = enemy_pos + enemy_velocity * estimated_time

        # Direction corrigée vers la position prédite
        to_enemy = (predicted_pos - player.gun.world_position).normalized()

        # Appliquer un aimbot léger si l’adversaire est proche du centre de visée
        dot_product = corrected_dir.dot(to_enemy)
        if dot_product > 0.94:  # tolérance ~20 degrés
            corrected_dir = lerp(corrected_dir, to_enemy, 0.6).normalized()


        dummy = Entity()
        dummy.look_at(player.gun.world_position + corrected_dir)
        aim_rotation = dummy.rotation
        destroy(dummy)

        #Entity(model='sphere', color=color.lime, position=predicted_pos, scale=0.3, lifetime=0.5)

        lazer_entity = Lazer(
            direction=corrected_dir,
            position=player.gun.world_position,
            color=color.red,
            rotation=aim_rotation,
            gun=player.gun
        )


    if held_keys['k']:
        corrected_dir = player2.gun.forward.normalized()
        to_enemy = (player.world_position - player2.gun.world_position).normalized()
        dot_product = corrected_dir.dot(to_enemy)

        if dot_product > 0.95:
            corrected_dir = lerp(corrected_dir, to_enemy, 0.5).normalized()

        dummy = Entity()
        dummy.look_at(player2.gun.world_position + corrected_dir)
        aim_rotation = dummy.rotation
        destroy(dummy)

        lazer_entity = Lazer(
            direction=corrected_dir,
            position=player2.gun.world_position,
            color=color.red,
            rotation=aim_rotation,
            gun=player2.gun
        )

    return speed

def entities_interaction(player, player2):
    # Détection collision player <-> sphères
    for e in scene.entities:
        if player.intersects(e).hit:
            print(f"Collision avec une sphère à la position {e.position}")
            player.position = Vec3(0, 5, 0)  # Réinitialise la position du joueur²
            # Tu peux ajouter ici une action (détruire la sphère, perdre de la vie, etc.)
        if player2.intersects(e).hit:
            print(f"Collision avec une sphère à la position {e.position}")
            player2.position = Vec3(0, 5, 0)  # Réinitialise la position du joueur²
            # Tu peux ajouter ici une action (détruire la sphère, perdre de la vie, etc.)