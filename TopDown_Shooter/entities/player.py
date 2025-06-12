from ursina import Entity, Vec3, held_keys, time
from .projectile import Projectile
import pygame


class Player(Entity):
    """
    A Player extends Ursina’s Entity. It handles rotation‐based movement:
      - Left/Right arrows rotate the character (swapped direction)
      - Up/Down move forward/backward in facing direction
    """

    def __init__(self, name, position, keys, color, hp_penalty, spawn_callback=None, controller=None):
        super().__init__(model='cube', color=color, scale=1, position=position, collider='box')
        self.name = name
        self.keys = keys
        self.hp_penalty = hp_penalty
        self.spawn_callback = spawn_callback
        # Store the pygame joystick.Joystick (or None)
        self.controller = controller

        # Stats (overridden by GameManager.start_game)
        self.turn_speed = 120
        self.move_speed = 5
        self.health_max = 100
        self.health = 100
        self.shoot_cooldown = 0.3
        self._last_shot = time.time()
        self.shot_power = 10
        self.projectile_speed = 10

    def update(self):
        # no-op so Ursina doesn’t auto-call game_update
        pass

    def game_update(self, game_state):
        if game_state != 'playing':
            return

        dt = time.dt

        # ─── JOYSTICK INPUT IF AVAILABLE ─────────────────────────────
        if self.controller:
            # Read axes: 0 = horizontal (±1), 1 = vertical (±1)
            ax = self.controller.get_axis(0)
            ay = self.controller.get_axis(1)
            deadzone = 0.2

            # Rotation from horizontal axis
            if abs(ax) > deadzone:
                # invert sign if you want left-stick-left to rotate left
                self.rotation_y += ax * self.turn_speed * dt

            # Movement from vertical axis
            if abs(ay) > deadzone:
                self.position += self.forward * (-ay) * self.move_speed * dt

            # Shooting from button 0
            if self.controller.get_button(0):
                now = time.time()
                if now - self._last_shot >= self.shoot_cooldown:
                    self._shoot()
                    self._last_shot = now

            # Keep within bounds & handle collisions just as before
            # ... (you can reuse your clamp-and-intersect logic) ...
            return  # skip keyboard if joystick plugged in

        # ─── FALLBACK TO KEYBOARD ────────────────────────────────────
        # 1) Rotation (directions swapped)
        if held_keys[self.keys['left']]:
            self.rotation_y -= self.turn_speed * dt
        if held_keys[self.keys['right']]:
            self.rotation_y += self.turn_speed * dt

        # 2) Movement forward/back
        move_dir = Vec3(0, 0, 0)
        if held_keys[self.keys['up']]:
            move_dir += self.forward
        if held_keys[self.keys['down']]:
            move_dir -= self.forward

        if move_dir != Vec3(0, 0, 0):
            movement = move_dir.normalized() * self.move_speed * dt
            old_pos = self.position
            new_pos = old_pos + movement

            # clamp within bounds
            if abs(new_pos.x) > 19.5 or abs(new_pos.z) > 10.5:
                new_pos = old_pos

            # attempt move
            self.position = new_pos

            # collision check: walls or covers
            hit = self.intersects()
            if hit.hit and hasattr(hit.entity, 'tag') and hit.entity.tag in ('wall', 'cover'):
                self.position = old_pos

        # 3) Shooting
        if held_keys[self.keys['shoot']]:
            now = time.time()
            if (now - self._last_shot) >= self.shoot_cooldown:
                self._shoot()
                self._last_shot = now

    def _shoot(self):
        spawn_pos = self.position + self.forward * 1.1
        proj = Projectile(
            position=Vec3(spawn_pos.x, 0.5, spawn_pos.z),
            direction=self.forward,
            owner=self,
            speed=self.projectile_speed,
            damage=self.shot_power
        )
        if self.spawn_callback:
            self.spawn_callback(proj)
