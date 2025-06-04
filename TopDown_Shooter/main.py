from ursina import Ursina, camera
from game_manager import GameManager

if __name__ == '__main__':
    app = Ursina()

    # Position the camera (use the global `camera`, not app.camera)
    camera.position = (0, 60, 0)
    camera.rotation_x = 90

    gm = GameManager(app)

    # Forward Ursina’s update/input to our manager
    def update():
        gm.update()

    def input(key):
        gm.input(key)

    app.run()
