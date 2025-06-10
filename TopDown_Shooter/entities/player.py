from ursina import Entity, Vec3, held_keys, time
import math
from .projectile import Projectile

class Player(Entity):
    """
    A Player extends Ursina’s Entity. It handles movement, rotation, shooting, and health.
    Movement is blocked by any Entity tagged 'wall' (borders or covers).
    """

    def __init__(self, name, position, keys, color, hp_penalty, spawn_callback=None):
        super().__init__(
            model='cube',
            color=color,
            scale=1,
            position=position,
            collider='box'
        )
        self.name = name
        self.health = 100
        self.keys = keys
        self.speed = 5
        self.shoot_cooldown = 0.3
        self._last_shot = time.time()
        self.hp_penalty = hp_penalty
        self.spawn_callback = spawn_callback

    def update(self):
        pass  # override so Ursina doesn’t call game_update automatically

    def game_update(self, game_state):
        if game_state != 'playing':
            return

        dx = held_keys[self.keys['right']] - held_keys[self.keys['left']]
        dz = held_keys[self.keys['up']] - held_keys[self.keys['down']]
        movement = Vec3(dx, 0, dz)

        if movement != Vec3(0, 0, 0):
            movement = movement.normalized() * self.speed * time.dt
            old_pos = self.position
            new_pos = old_pos + movement

            # keep within bounds
            if abs(new_pos.x) > 19.5 or abs(new_pos.z) > 10.5:
                new_pos = old_pos

            # tentatively move
            self.position = new_pos

            # check for collisions with covers/borders
            hit = self.intersects()
            if hit.hit and hasattr(hit.entity, 'tag') and hit.entity.tag in ('wall', 'cover'):
                # revert if collided
                self.position = old_pos
            else:
                # rotate to face movement direction
                angle = math.degrees(math.atan2(movement.x, movement.z))
                self.rotation_y = angle

        # shooting
        if held_keys[self.keys['shoot']]:
            now = time.time()
            if (now - self._last_shot) >= self.shoot_cooldown:
                self._shoot()
                self._last_shot = now

    def _shoot(self):
        spawn_pos = self.position + self.forward * 0.75
        proj = Projectile(
            position=Vec3(spawn_pos.x, 0.5, spawn_pos.z),
            direction=self.forward,
            owner=self
        )
        if self.spawn_callback:
            self.spawn_callback(proj)
