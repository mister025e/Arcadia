from ursina import *

lazer_container = Entity()

class Lazer(Entity):
    def __init__(self, gun, focus_circle, target, color=color.red, speed=2000, **kwargs):
        super().__init__(
            parent=lazer_container,
            model='cube',
            scale=(0.5, 0.5, 5),
            color=color,
            position=gun.world_position + gun.forward * 4,
            rotation=gun.world_rotation,
            **kwargs
        )

        self.direction = self.forward.normalized()  # capturer la direction réelle
        self.gun = gun
        self.speed = speed
        self.collider = BoxCollider(self, center=Vec3(0,0,2.5), size=Vec3(1,1,5))
        print(focus_circle.position.x, focus_circle.position.y, focus_circle.position.z)
        if ((0 < focus_circle.position.y < 0.152 and -0.52 < focus_circle.position.x < -0.37) or (0 < focus_circle.position.y < 0.152 and 0.37 < focus_circle.position.x < 0.52)) and focus_circle.visible:
            self.look_at(target.world_position)
            self.direction = self.forward.normalized()

    def update(self):
        prev_pos = self.world_position
        self.position += self.direction * self.speed * time.dt

        # Détruire hors map
        if not (-1024 < self.x < 1024 and 0 < self.y < 2048 and -1024 < self.z < 1024):
            destroy(self)
            return

        # Raycast de collision
        hit = raycast(
            origin=prev_pos,
            direction=self.direction,
            distance=(self.world_position - prev_pos).length(),
            ignore=(self, self.gun),
            debug=False
        )

        if hit.hit and hit.entity.name in ('player1', 'player2'):
            print(f"Touché : {hit.entity} à {hit.world_point}")
            hit.entity.position = Vec3(0, 0, 0)
            destroy(self)
