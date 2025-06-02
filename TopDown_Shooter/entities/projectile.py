from ursina import Entity, color, time, destroy
from ursina import Vec3

class Projectile(Entity):
    """
    A small sphere that travels in ‘direction’ and damages the other player.
    """

    def __init__(self, position, direction, owner):
        super().__init__(
            model='sphere',
            color=color.red,
            scale=0.2,
            position=position,
            collider='sphere'
        )
        self.direction = direction.normalized()
        self.speed = 10
        self.owner = owner

    def update(self):
        """
        Empty override so Ursina can call update() without error.
        """
        pass

    def game_update(self, game_state, end_game_callback):
        """
        Move each frame; check for collisions. If it hits a player (not the owner), deal damage.
        If that lowers the player’s HP ≤ 0, call end_game_callback(owner).
        Catch Panda3D empty‐node errors if destroy(self) was already called.
        """
        if game_state != 'playing':
            return

        # Wrap position update in try/except to avoid empty‐node assertion
        try:
            self.position += self.direction * self.speed * time.dt
        except AssertionError:
            # This entity has been destroyed or its node is empty; bail out
            return

        # If out of bounds, destroy and return
        try:
            if abs(self.position.x) > 20 or abs(self.position.z) > 20:
                destroy(self)
                return
        except AssertionError:
            return

        # Now check collisions, again catching empty‐node errors
        try:
            hit = self.intersects()
        except AssertionError:
            return

        if hit.hit:
            ent = hit.entity

            # Avoid circular import at top
            from .player import Player

            # If it hits a Player (and not the one who fired)
            if isinstance(ent, Player) and ent is not self.owner:
                ent.health -= 20
                destroy(self)
                if ent.health <= 0:
                    end_game_callback(self.owner)
                return

            # If it hits a wall or cover (tagged 'wall'), destroy it
            if hasattr(ent, 'tag') and ent.tag == 'wall':
                destroy(self)
                return