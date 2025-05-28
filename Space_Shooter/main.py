from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader

# add pygame for joystick handling
import pygame
import random
from panda3d.core import PerspectiveLens, Camera, NodePath

app = Ursina()
random.seed(0)
Entity.default_shader = lit_with_shadows_shader

# initialize pygame for joysticks
pygame.init()
pygame.joystick.init()
joysticks = []
for i in range(pygame.joystick.get_count()):
    js = pygame.joystick.Joystick(i)
    js.init()
    print(f'Detected joystick {i}: {js.get_name()}')
    joysticks.append(js)
if len(joysticks) < 2:
    print('Warning: less than 2 joysticks detected!')

ground = Entity(model='plane', collider='box', scale=2048, texture='grass', texture_scale=(4,4))

# cameras & players setup (unchanged)...
editor_camera = EditorCamera(enabled=False, ignore_paused=True)
player = FirstPersonController(model='cube', color=color.blue, collider='box')
player.visible_self = editor_camera.enabled
player_body = Entity(parent=player, model='cube', texture='shore', position=(0,0,0), scale=(2,0.2,1), color=color.blue, y=1)
player.speed = 20
player.update = Func(lambda: None)
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

player2 = Entity(model='cube', color=color.orange, position=(10,0,0), scale=(1,0.3,2), collider='box')
player2.speed = 20
player2.collider = BoxCollider(player2, Vec3(0,1,0), Vec3(1,2,1))
player2.gun = Entity(model='cube', parent=player2, position=(0,0,0), scale=(1,0.5,1), origin_z=-.5, color=color.black)

gun = Entity(model='scale_gizmo', parent=player, position=(0,1,0), scale=(1,0.5,1), origin_z=-.5, color=color.red, on_cooldown=False)
gun.muzzle_flash = Entity(parent=gun, z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False)
shootables_parent = Entity()
mouse.traverse_target = shootables_parent

# random spheres...
for i in range(512):
    s = random.uniform(2,30)
    Entity(model='sphere', origin_y=-.5, scale=s, texture='perlin_noise', texture_scale=(2,2),
           x=random.uniform(-1024,1024), z=random.uniform(-1024,1024), y=random.uniform(0,1024),
           collider='box', color=color.red)

# split-screen camera setup (unchanged)…
base.win.remove_display_region(base.camNode.get_display_region(0))
dr1 = base.win.make_display_region(0,0.5,0,1); dr1.set_sort(0)
dr2 = base.win.make_display_region(0.5,1,0,1); dr2.set_sort(1)

lens1 = PerspectiveLens(); lens1.set_aspect_ratio(window.aspect_ratio/2)
cam1 = NodePath(Camera('cam1', lens1)); dr1.set_camera(cam1)
lens2 = PerspectiveLens(); lens2.set_aspect_ratio(window.aspect_ratio/2)
cam2 = NodePath(Camera('cam2', lens2)); dr2.set_camera(cam2)

cam1.reparent_to(player); cam1.set_pos(0,2.2,-20)
cam2.reparent_to(player2); cam2.set_pos(0,2.2,-20)

v_text = Text(text='speed : 0', position=(0,0.45), scale=2, color=color.white, font='VeraMono.ttf')
p_text = Text(text='position : (0,0,0)', position=(0,0.4), scale=1, color=color.white, font='VeraMono.ttf')
player.cursor.enabled = False

# mapping: axis 0 = left/right stick X, axis1 = up/down stick Y, buttons 0 & 1 = speed +/-
AXIS_ROT_X = 1  # up/down
AXIS_ROT_Z = 0  # left/right
BTN_SPEED_UP = 0
BTN_SPEED_DOWN = 1

def update():
    global v_text, p_text

    # pump pygame events so joystick state updates
    pygame.event.pump()

    dt = time.dt
    rot_speed = 60 * dt

    # --- Player 1 via joystick 0 ---
    if len(joysticks) > 0:
        js = joysticks[0]
        # rotation: pitch from axis1, roll from axis0
        pitch = -js.get_axis(AXIS_ROT_X) * rot_speed
        roll  =  js.get_axis(AXIS_ROT_Z) * rot_speed
        player.rotate(Vec3(pitch, 0, roll), relative_to=player)
        # speed buttons
        if js.get_button(BTN_SPEED_UP):
            player.speed = min(300, player.speed + 40*dt)
        if js.get_button(BTN_SPEED_DOWN):
            player.speed = max(10, player.speed - 40*dt)

    # --- Player 2 via joystick 1 ---
    if len(joysticks) > 1:
        js2 = joysticks[1]
        pitch2 = -js2.get_axis(AXIS_ROT_X) * rot_speed
        roll2  =  js2.get_axis(AXIS_ROT_Z) * rot_speed
        player2.rotate(Vec3(pitch2, 0, roll2), relative_to=player2)
        if js2.get_button(BTN_SPEED_UP):
            player2.speed = min(300, player2.speed + 40*dt)
        if js2.get_button(BTN_SPEED_DOWN):
            player2.speed = max(10, player2.speed - 40*dt)

    # move forward along each gun's facing
    player.position  += gun.forward * player.speed * dt
    player2.position += player2.gun.forward * player2.speed * dt

    # update on-screen text
    v_text.text = f'speed : {round(player.speed,1)} / {round(player2.speed,1)}'
    p_text.text = f'pos1:({round(player.x,1)},{round(player.y,1)},{round(player.z,1)})'

    # shooting (player 1 only)
    if held_keys['left mouse']:
        shoot()

def shoot():
    if not gun.on_cooldown:
        gun.on_cooldown = True
        gun.muzzle_flash.enabled = True
        from ursina.prefabs.ursfx import ursfx
        ursfx([(0,0),(0.1,0.9),(0.15,0.75),(0.3,0.14),(0.6,0)], volume=0.5,
              wave='noise', pitch=random.uniform(-13,-12), pitch_change=-12, speed=3.0)
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)

def pause_input(key):
    if key == 'tab':
        editor_camera.enabled = not editor_camera.enabled
        player.cursor.enabled  = not editor_camera.enabled
        mouse.locked            = not editor_camera.enabled
        editor_camera.position = player.position
        application.paused      = editor_camera.enabled

pause_handler = Entity(ignore_paused=True, input=pause_input)

sun = DirectionalLight(); sun.look_at(Vec3(1,-1,-1))
Sky(texture='sky_sunset')
app.run()
