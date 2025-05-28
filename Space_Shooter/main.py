from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
from panda3d.core import PerspectiveLens, Camera, NodePath

app = Ursina()

random.seed(0)
Entity.default_shader = lit_with_shadows_shader

ground = Entity(model='plane', collider='box', scale=2048, texture='grass', texture_scale=(4,4))

editor_camera = EditorCamera(enabled=False, ignore_paused=True)
player = FirstPersonController(model='cube', color=color.blue, collider='box')
player.visible_self = editor_camera.enabled
# Ajoute le visuel voulu comme enfant
player_body = Entity(parent=player, model='cube', texture = 'shore', position=(0,0,0), scale=(2,0.2,1), color=color.blue, y=1)

player.speed = 20
player.update = Func(lambda: None)  # désactive le comportement FPS par défaut
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

# Joueur 2 (rouge)
player2 = player2 = Entity(model='cube', color=color.orange, position=(5, 2, 0))
player2.speed = 20
player2.visible_self = editor_camera.enabled
player2_body = Entity(parent=player2, model='cube', texture = 'shore', position=(0,0,0), scale=(2,0.2,1), color=color.red, y=1)
player2.update = Func(lambda: None)  # désactive le comportement FPS par défaut
player2.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))
player2.gun = Entity(model='scale_gizmo', parent=player2, position=(0,1,0), scale=(1,.5,1), origin_z=-.5, color=color.red, on_cooldown=False)


gun = Entity(model='scale_gizmo', parent=player, position=(0,1,0), scale=(1,.5,1), origin_z=-.5, color=color.red, on_cooldown=False)
gun.muzzle_flash = Entity(parent=gun, z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False)

lazer = Entity()


for i in range(512):
    scale_x_value = random.uniform(2,30)
    Entity(model='sphere', origin_y=-.5, scale=2, texture='perlin_noise', texture_scale=(2,2),
        x=random.uniform(-1024,1024),
        z=random.uniform(-1024,1024),
        y=random.uniform(0,1024),
        collider='box',
        scale_x=scale_x_value,
        scale_y=scale_x_value,
        scale_z=scale_x_value,
        color=color.red
        )

# Crée un pivot pour la caméra autour du joueur
# Supprime la display region de la caméra Ursina
base.win.remove_display_region(base.camNode.get_display_region(0))

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
dr1.set_camera(cam1)

lens2 = PerspectiveLens()
lens2.set_aspect_ratio(window.aspect_ratio / 2)
cam_node2 = Camera('cam2', lens2)
cam2 = NodePath(cam_node2)
dr2.set_camera(cam2)

# Position caméras
cam1.reparent_to(player)
cam1.set_pos(0, 2.2, -20)
cam1.node().get_lens().set_fov(40)  # champ de vision
cam2.reparent_to(player2)
cam2.node().get_lens().set_fov(40)  # champ de vision
cam2.set_pos(0, 2.2, -20)

v_text = Text(
    text='speed : 0',
    position=(0, 0.45),  # (x, y) de -1 à 1, coin haut gauche
    origin=(0,0),
    scale=2,
    color=color.white,
    font ='VeraMono.ttf',
)

p_text = Text(
    text='position : (0, 0, 0)',
    position=(0, 0.4),  # (x, y) de -1 à 1, coin haut gauche
    origin=(0,0),
    scale=1,
    color=color.white,
    font ='VeraMono.ttf',
)

crosshair_p1 = Text(
    text='+',
    position=(-0.445, 0.12),  # (x, y) de -1 à 1, coin haut gauche
    origin=(0,0),
    scale=1,
    color=color.white,
    font ='VeraMono.ttf',
)
crosshair_p2 = Text(
    text='+',
    position=(0.445, 0.13),  # (x, y) de -1 à 1, coin haut gauche
    origin=(0,0),
    scale=1,
    color=color.white,
    font ='VeraMono.ttf',
)

player.cursor.enabled = False

# Variables pour stocker la rotation
pivot_rotation_x = 10
speed = 20

def update():
    global pivot_rotation_x, speed, v_text, p_text, crosshair_p1, crosshair_p2
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
        speed += 1 
        if speed > 300:
            speed = 300
    if held_keys['y']:
        speed -= 1
        if speed < 10:
            speed = 10

    if held_keys['up arrow']:
        player2.rotate(Vec3(rotation_speed, 0, 0), relative_to=player2)
    if held_keys['down arrow']:
        player2.rotate(Vec3(-rotation_speed, 0, 0), relative_to=player2)
    if held_keys['right arrow']:
        player2.rotate(Vec3(0, 0, rotation_speed*3), relative_to=player2)
    if held_keys['left arrow']:
        player2.rotate(Vec3(0, 0, -rotation_speed*3), relative_to=player2)
    if held_keys['o']:
        player2.speed += 1 
        if player2.speed > 300:
            player2.speed = 300
    if held_keys['p']:
        player2.speed -= 1
        if player2.speed < 10:
            player2.speed = 10
    # ----- Déplacement dans la direction du gun -----
    
    player.position += gun.forward * speed * time.dt
    player2.position += player2.gun.forward * player2.speed * time.dt

    # ----- Rotation caméra -----
    """pivot_rotation_x += mouse.velocity[1] * 100
    pivot_rotation_x = clamp(pivot_rotation_x, -80, 80)
    camera_pivot.rotation_x = pivot_rotation_x"""

    # ----- Gun orienté comme la caméra -----
    #gun.rotation = camera_pivot.rotation
    cam1.set_pos(0, 2.2, -20 - 20 *(speed/500))
    cam2.set_pos(0, 2.2, -20 - 20 *(player2.speed/500))

    v_text.text = f'speed : {speed}'
    p_text.text = f'position : ({round(player.x, 2)}, {round(player.y, 2)}, {round(player.z, 2)})'

    # ----- Tir -----
    if held_keys['f']:
        lazer_entity = Lazer(
            direction=gun.forward,
            position=gun.world_position,
            color=color.red,
            rotation=gun.world_rotation  # <-- passe la rotation du gun
        )

    if held_keys['k']:
        print('shoot')
        lazer_entity = Lazer(
            direction=player2.gun.forward,
            position=player2.gun.world_position,
            color=color.red,
            rotation=player2.gun.world_rotation  # <-- passe la rotation du gun
        )


def shoot():
    if not gun.on_cooldown:
        # print('shoot')
        gun.on_cooldown = True
        gun.muzzle_flash.enabled=True
        from ursina.prefabs.ursfx import ursfx
        ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise', pitch=random.uniform(-13,-12), pitch_change=-12, speed=3.0)
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)

class Lazer(Entity):
    def __init__(self, direction=Vec3(0,0,-1), position=Vec3(0,0,0), color=color.red, rotation=Vec3(0,0,0)):
        position = Vec3(position)
        super().__init__(
            parent=lazer,
            model='cube',
            scale_y=.1,
            scale_x=.1,
            color=color,
            collider='box',
            direction=direction,
            position=position,
            rotation=rotation  # <-- applique la rotation du gun
        )

    def update(self):
        # Utilise la direction locale du lazer (toujours -z dans son espace local)
        self.position += self.forward * 1000 * time.dt
        if self.x < -1000 or self.x > 1000 or self.y < -1000 or self.y > 1000 or self.z < -1000 or self.z > 1000:
            destroy(self)

def pause_input(key):
    if key == 'tab':    # press tab to toggle edit/play mode
        editor_camera.enabled = not editor_camera.enabled

        #player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        #gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position

        application.paused = editor_camera.enabled

pause_handler = Entity(ignore_paused=True, input=pause_input)


sun = DirectionalLight()
sun.look_at(Vec3(1,-1,-1))
Sky(texture='sky_sunset')

# Optionnel : désactive le curseur du joueur
player.cursor.enabled = False

app.run()