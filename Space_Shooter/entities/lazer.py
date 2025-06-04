from ursina import *

lazer = Entity()

class Lazer(Entity):
    def __init__(self, direction=Vec3(0,0,-1), position=Vec3(0,0,0), color=color.red, rotation=Vec3(0,0,0), gun=None, **kwargs):
        # On passe le gun parent pour suivre sa position/rotation
        super().__init__(
            parent=lazer,
            model='cube',
            scale_y=1,
            scale_x=1,
            scale_z=5,
            color=color,
        )
        self.collider = BoxCollider(self, Vec3(0,0,5), Vec3(2,2,10))
        self.gun = gun
        self.offset = Vec3(0, 0, 2)  # décalage devant le gun
        self.direction = direction.normalized()

        # Positionne initialement devant le gun
        if self.gun:
            self.position = self.gun.world_position + self.gun.forward * 4
            self.rotation = self.gun.world_rotation
        else:
            self.position = Vec3(position)
            self.rotation = rotation
        #self.collider.visible = True
        self.look_at(self.position + self.direction)

    def update(self):
        """if not self.enabled or not self.has_parent():
            return  # Ne fait rien si l'entité a été détruite
        if not hasattr(self, 'direction'):
            return"""
        # Avance dans la direction du gun
        prev_pos = self.world_position
        self.position += self.forward * 1000 * time.dt
        #print(self.forward , 150 , time.dt)
        if self.x < -1024 or self.x > 1024 or self.y < 0 or self.y > 2048 or self.z < -1024 or self.z > 1024:
            destroy(self)
            return  # <-- Ajoute ce return pour éviter la suite du code si détruit

        # Raycast entre ancienne et nouvelle position
        hit = raycast(
            origin=prev_pos,
            direction=self.direction,
            distance=(self.position - prev_pos).length(),
            ignore=(self.gun,),
            debug=False
        )

        if hit.hit and hit.entity.name in ('player1', 'player2'):  # selon qui tire
            print(f"Touché : {hit.entities} à la position {hit.world_point}")
            hit.entity.position = Vec3(0, 5, 0)  # Réinitialise la position du joueur touché
            destroy(self)
            return  # <-- Ajoute ce return aussi
