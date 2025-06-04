from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
from ursina import raycast
from panda3d.core import PerspectiveLens, Camera, NodePath
from panda3d.core import Point3, Point2

def project_to_screen(entity, cam_np, lens, region_offset=Vec2(0,0), region_scale=Vec2(1,1)):
    target_pos = entity.get_pos(render) + Vec3(0, .5, 0)  # vise le haut du vaisseau
    pos_3d = cam_np.get_relative_point(render, target_pos)

    p2d = Point2()
    if lens.project(pos_3d, p2d):
        return Vec2(p2d.x * region_scale.x + region_offset.x,
                    p2d.y * region_scale.y + region_offset.y)
    return None


app = Ursina()

random.seed(0)
Entity.default_shader = lit_with_shadows_shader

ground = Entity(model='plane', collider='box', scale=2048, texture='models/quadrillage', texture_scale=(4,4), color=color.rgba(255, 255, 255, 120))
wall = Entity(
    model='quad',
    collider='box',
    scale=(2048, 2048, 1),
    texture='models/quadrillage',
    texture_scale=(4,4),
    position=(0, 1024, 1024),
    color=color.rgba(255, 255, 255, 120)  # transparence ajoutée
)
wall2 = Entity(
    model='quad',
    collider='box',
    scale=(2048, 2048, 1),
    texture='models/quadrillage',
    texture_scale=(4,4),
    position=(0, 1024, -1024),
    rotation_y=180,
    color=color.rgba(255, 255, 255, 120)
)
wall3 = Entity(
    model='quad',
    collider='box',
    scale=(2048, 2048, 1),
    texture='models/quadrillage',
    texture_scale=(4,4),
    position=(1024, 1024, 0),
    rotation_y=90,
    color=color.rgba(255, 255, 255, 120)
)
wall4 = Entity(
    model='quad',
    collider='box',
    scale=(2048, 2048, 1),
    texture='models/quadrillage',
    texture_scale=(4,4),
    position=(-1024, 1024, 0),
    rotation_y=-90,
    color=color.rgba(255, 255, 255, 120)
)
wall5 = Entity(
    model='quad',
    collider='box',
    scale=(2048, 2048, 1),
    texture='models/quadrillage',
    texture_scale=(4,4),
    position=(0, 2048, 0),
    rotation_x=-90,
    color=color.rgba(255, 255, 255, 120)
)
#ground.collider.visible = True

editor_camera = EditorCamera(enabled=False, ignore_paused=True)
player = FirstPersonController(model='cube', color=color.blue, collider='box')
player.visible_self = editor_camera.enabled
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
player2_body = Entity(parent=player2, model='cube', texture = 'shore', position=(0,0,0), scale=(2,0.2,1), color=color.red)
player2.update = Func(lambda: None)  # désactive le comportement FPS par défaut
player2.collider = BoxCollider(player2, Vec3(0,0,0), Vec3(2,5,2))
#player2.collider.visible = True
player2.gun = Entity(model='scale_gizmo', parent=player2, position=(0,0,0), scale=(1,.5,1), origin_z=-.5, color=color.red, on_cooldown=False)

lazer = Entity()

# Crée un pivot pour la caméra autour du joueur
# Supprime la display region de la caméra Ursina

for i in range(512):
    scale_x_value = random.uniform(2,30)
    Entity(model='sphere', origin_y=-.5, scale=2, texture='models/sol_lune', texture_scale=(2,2),
        x=random.uniform(-1024,1024),
        z=random.uniform(-1024,1024),
        y=random.uniform(0,2048),
        collider='sphere',
        scale_x=scale_x_value,
        scale_y=scale_x_value,
        scale_z=scale_x_value,
        color=color.white if random.random() < 0.5 else color.gray,
        )
    #e = scene.entities[-1]
    #if hasattr(e, 'collider') and e.collider:
        #e.collider.visible = True

# Créer un second DisplayRegion (vue droite)
dr1 = base.win.make_display_region(0, 0.5, 0, 1)
dr1.set_sort(0)
dr2 = base.win.make_display_region(0.5, 1, 0, 1)
dr2.set_sort(1)

# Lens avec bon ratio (2x car demi-largeur)
lens1 = PerspectiveLens()
lens1.set_aspect_ratio(window.aspect_ratio / 2)
cam_node1 = Camera('cam1', lens1)
cam1 = NodePath(cam_node1)
cam1.reparent_to(render)
dr1.set_camera(cam1)

lens2 = PerspectiveLens()
lens2.set_aspect_ratio(window.aspect_ratio / 2)
cam_node2 = Camera('cam2', lens2)
cam2 = NodePath(cam_node2)
cam2.reparent_to(render)
dr2.set_camera(cam2)

# Position caméras
cam1.reparent_to(player)
cam1.set_pos(0, 2.2, -20)
cam1.node().get_lens().set_fov(40)  # champ de vision
cam2.reparent_to(player2)
cam2.node().get_lens().set_fov(40)  # champ de vision
cam2.set_pos(0, 2.2, -20)

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

# Variables pour stocker la rotation
pivot_rotation_x = 10
speed = 20

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

def update():
    global pivot_rotation_x, speed, crosshair_p1, crosshair_p2
    cam1.look_at(player)
    cam2.look_at(player2)

    # ----- Contrôle de l'orientation -----
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

    # ----- Rotation caméra -----
    """pivot_rotation_x += mouse.velocity[1] * 100
    pivot_rotation_x = clamp(pivot_rotation_x, -80, 80)
    camera_pivot.rotation_x = pivot_rotation_x"""

    # ----- Gun orienté comme la caméra -----
    #gun.rotation = camera_pivot.rotation
    #cam1.set_pos(0, 2.2, -20 - 20 *(speed/500))
    #cam2.set_pos(0, 2.2, -20 - 20 *(player2.speed/500))
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

    #print(f"{len(scene.children)} entités dans la scène")

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

class Lazer(Entity):
    def __init__(self, direction=Vec3(0,0,-1), position=Vec3(0,0,0), color=color.red, rotation=Vec3(0,0,0), gun=None):
        # On passe le gun parent pour suivre sa position/rotation
        super().__init__(
            parent=lazer,
            model='cube',
            scale_y=1,
            scale_x=1,
            scale_z=5,
            color=color,
        )
        self.collider = BoxCollider(self, Vec3(0,0,5), Vec3(2,2,10))
        self.gun = gun
        self.offset = Vec3(0, 0, 2)  # décalage devant le gun
        self.direction = direction.normalized()

        # Positionne initialement devant le gun
        if self.gun:
            self.position = self.gun.world_position + self.gun.forward * 4
            self.rotation = self.gun.world_rotation
        else:
            self.position = Vec3(position)
            self.rotation = rotation
        #self.collider.visible = True
        self.look_at(self.position + self.direction)

    def update(self):
        """if not self.enabled or not self.has_parent():
            return  # Ne fait rien si l'entité a été détruite
        if not hasattr(self, 'direction'):
            return"""
        # Avance dans la direction du gun
        prev_pos = self.world_position
        self.position += self.forward * 1000 * time.dt
        #print(self.forward , 150 , time.dt)
        if self.x < -1024 or self.x > 1024 or self.y < 0 or self.y > 2048 or self.z < -1024 or self.z > 1024:
            destroy(self)
            return  # <-- Ajoute ce return pour éviter la suite du code si détruit

        # Raycast entre ancienne et nouvelle position
        hit = raycast(
            origin=prev_pos,
            direction=self.direction,
            distance=(self.position - prev_pos).length(),
            ignore=(self.gun,),
            debug=False
        )

        if hit.hit and hit.entity in (player, player2):  # selon qui tire
            print(f"Touché : {hit.entities} à la position {hit.world_point}")
            hit.entity.position = Vec3(0, 5, 0)  # Réinitialise la position du joueur touché
            destroy(self)
            return  # <-- Ajoute ce return aussi


def pause_input(key):
    if key == 'tab':    # press tab to toggle edit/play mode
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