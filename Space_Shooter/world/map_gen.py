from ursina import *

def map_generation():
    ground = Entity(model='plane', collider='box',name='wall', scale=2048, texture='models/quadrillage', texture_scale=(4,4), color=color.rgba(255, 255, 255, 64))
    wall = Entity(
        model='quad',
        collider='box',
        name='wall',
        scale=2048,
        texture='models/quadrillage',
        texture_scale=(4,4),
        position=(0, 1024, 1024),
        color=color.rgba(255, 255, 255, 64)  # transparence ajoutée
    )
    #wall.collider.visible = True
    wall2 = Entity(
        model='quad',
        collider='box',
        name='wall',
        scale=2048,
        texture='models/quadrillage',
        texture_scale=(4,4),
        position=(0, 1024, -1024),
        rotation_y=180,
        color=color.rgba(255, 255, 255, 64)
    )
    wall3 = Entity(
        model='quad',
        collider='box',
        name='wall',
        scale=2048,
        texture='models/quadrillage',
        texture_scale=(4,4),
        position=(1024, 1024, 0),
        rotation_y=90,
        color=color.rgba(255, 255, 255, 64)
    )
    wall4 = Entity(
        model='quad',
        collider='box',
        name='wall',
        scale=2048,
        texture='models/quadrillage',
        texture_scale=(4,4),
        position=(-1024, 1024, 0),
        rotation_y=-90,
        color=color.rgba(255, 255, 255, 64)
    )
    wall5 = Entity(
        model='quad',
        collider='box',
        name='wall',
        scale=2048,
        texture='models/quadrillage',
        texture_scale=(4,4),
        position=(0, 2048, 0),
        rotation_x=-90,
        color=color.rgba(255, 255, 255, 64)
    )
    #ground.collider.visible = True

    for i in range(512):
        scale_x_value = random.uniform(2,30)
        Entity(model='sphere', origin_y=-.5, scale=2, texture='models/sol_lune', texture_scale=(2,2),
            x=random.uniform(-1024,1024),
            z=random.uniform(-1024,1024),
            y=random.uniform(0,2048),
            collider='sphere',
            name='wall',
            scale_x=scale_x_value,
            scale_y=scale_x_value,
            scale_z=scale_x_value,
            color=color.white if random.random() < 0.5 else color.gray,
            )
        #e = scene.entities[-1]
        #if hasattr(e, 'collider') and e.collider:
            #e.collider.visible = True
    lucrehulk = Entity(model='models/lucrehulk', texture = 'models/lucrehulk', name='wall', collider='mesh', position=(0,250,0), scale=40)
    lucrehulk.rotation = Vec3(90, 0, 0)  # Pour que le Lucrehulk regarde dans la direction opposée
    #lucrehulk.collider.visible = True