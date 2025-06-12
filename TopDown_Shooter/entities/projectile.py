from ursina import Entity, color, time, destroy
from ursina import Vec3

class Projectile(Entity):
    """
    A small sphere that travels in ‘direction’ and damages the other player.
    """

    def __init__(self, position, direction, owner, speed=10, damage=10):
        super().__init__(
            model='sphere',
            color=color.red,
            scale=0.3,
            position=position,
            collider='sphere'
        )
        self.owner = owner
        self.direction = direction.normalized()
        self.speed = speed
        self.damage = damage
        self.tag = 'projectile'

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
            from .player import Player
            # hit other player?
            if isinstance(ent, Player) and ent is not self.owner:
                ent.health -= self.damage
                if ent.health <= 0:
                    end_game_callback(self.owner)
                # disable then destroy so GameManager removes us
                self.enabled = False
                destroy(self)
                return
            # hit wall or cover?
            if hasattr(ent, 'tag') and ent.tag in ('wall', 'cover'):
                self.enabled = False
                destroy(self)
                return
