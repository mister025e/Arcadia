from ursina import Entity, Vec3, held_keys, time
import math
from .projectile import Projectile


class Player(Entity):
    """
    A Player extends Ursina’s Entity. It handles movement, rotation, shooting, and health.
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
        self.keys = keys  # e.g. {'up':'w','down':'s','left':'a','right':'d','shoot':'space'}
        self.speed = 5
        self.shoot_cooldown = 0.3
        self._last_shot = time.time()
        self.hp_penalty = hp_penalty
        self.spawn_callback = spawn_callback  # called with the new Projectile

    def update(self):
        """
        This empty override prevents Ursina from trying to call game_update()
        automatically. All actual per-frame logic happens in game_update().
        """
        pass

    def game_update(self, game_state):
        """
        Called each frame by GameManager.update(), passing in the current game_state.
        Only moves/shoots if game_state == 'playing'.
        """
        if game_state != 'playing':
            return

        dx = held_keys[self.keys['right']] - held_keys[self.keys['left']]
        dz = held_keys[self.keys['up']] - held_keys[self.keys['down']]
        movement = Vec3(dx, 0, dz)
        if movement != Vec3(0, 0, 0):
            movement = movement.normalized() * self.speed * time.dt
            new_pos = self.position + movement

            # Keep inside ±19.5 on X (east/west) and ±10.5 on Z (north/south at z=±11.5)
            if abs(new_pos.x) <= 19.5 and abs(new_pos.z) <= 10.5:
                self.position = new_pos

            # Rotate to face direction of movement
            angle = math.degrees(math.atan2(movement.x, movement.z))
            self.rotation_y = angle

        # Shooting
        if held_keys[self.keys['shoot']]:
            now = time.time()
            if (now - self._last_shot) >= self.shoot_cooldown:
                self._shoot()
                self._last_shot = now

    def _shoot(self):
        """
        Spawns a Projectile in front of the player and calls spawn_callback.
        """
        spawn_pos = self.position + self.forward * 0.75
        proj = Projectile(
            position=Vec3(spawn_pos.x, 0.5, spawn_pos.z),
            direction=self.forward,
            owner=self
        )
        if self.spawn_callback:
            self.spawn_callback(proj)
