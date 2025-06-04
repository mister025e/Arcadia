from ursina import Entity, Vec3, time
import math
from .projectile import Projectile
import pygame


class Player(Entity):
    """
    A Player extends Ursina’s Entity. It handles movement, rotation, shooting, and health.
    """

    def __init__(self, name, position, joystick_list, joystick_index, color, hp_penalty, spawn_callback=None):
        super().__init__(
            model='cube',
            color=color,
            scale=1,
            position=position,
            collider='box'
        )
        self.name = name
        self.health = 100
        self.speed = 5
        self.shoot_cooldown = 0.3
        self._last_shot = time.time()
        self.hp_penalty = hp_penalty
        self.spawn_callback = spawn_callback  # called with the new Projectile

        # store joystick reference
        self.joystick_list = joystick_list
        self.joystick_index = joystick_index

    def update(self):
        """
        Override so Ursina won’t call game_update() automatically.
        We’ll call .game_update() ourselves each frame.
        """
        pass

    def game_update(self, game_state):
        """
        Called each frame by GameManager.update().
        Polls joystick axes/buttons for movement & shooting.
        """
        if game_state != 'playing':
            return

        # Pump pygame events so joystick state stays current
        pygame.event.pump()

        # Get joystick or bail if not attached
        if self.joystick_index >= len(self.joystick_list):
            return
        js = self.joystick_list[self.joystick_index]

        # Poll joystick axes: axis 0 = left/right, axis 1 = up/down
        x_axis = js.get_axis(0)   # −1 (left) → +1 (right)
        y_axis = js.get_axis(1)   # −1 (up) → +1 (down)

        # Invert Y so pushing stick up → forward (−Z)
        dz = -y_axis
        dx = x_axis

        # Dead-zone threshold
        if abs(dx) < 0.1:
            dx = 0
        if abs(dz) < 0.1:
            dz = 0

        movement = Vec3(dx, 0, dz)
        if movement != Vec3(0, 0, 0):
            movement = movement.normalized() * self.speed * time.dt
            new_pos = self.position + movement

            # Keep inside ±19.5 on X and ±10.5 on Z
            if abs(new_pos.x) <= 19.5 and abs(new_pos.z) <= 10.5:
                self.position = new_pos

            # Rotate to face direction of movement
            angle = math.degrees(math.atan2(movement.x, movement.z))
            self.rotation_y = angle

        # Shooting: map button 0 to “fire”
        if js.get_button(0):
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
