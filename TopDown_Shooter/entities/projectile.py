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
        We set self.enabled = False before destroy(self) so that GameManager removes this projectile next frame.
        """
        if game_state != 'playing':
            return

        # If somehow already disabled, bail
        if not self.enabled:
            return

        # 1) Move forward (wrap in try/except to avoid leftover‐node assertions)
        try:
            self.position += self.direction * self.speed * time.dt
        except AssertionError:
            # Node is already empty/destroyed; bail
            return

        # 2) Out‐of‐bounds? disable + destroy, then return
        try:
            # Out of bounds: Z beyond ±11.5 (north/south) or X beyond ±20 (east/west)
            if abs(self.position.z) > 11.5 or abs(self.position.x) > 20:
                self.enabled = False
                destroy(self)
                return
        except AssertionError:
            return

        # 3) Check for collisions (wrap in try/except)
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
                self.enabled = False
                destroy(self)
                if ent.health <= 0:
                    end_game_callback(self.owner)
                return

            # If it hits a wall or cover (tagged 'wall'), disable + destroy
            if hasattr(ent, 'tag') and ent.tag == 'wall':
                self.enabled = False
                destroy(self)
                return
