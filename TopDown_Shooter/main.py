from ursina import Ursina, camera, window, mouse
from game_manager import GameManager

if __name__ == '__main__':
    # 1) Fullscreen Ursina
    app = Ursina(fullscreen=True, vsync=True)
    window.fullscreen = True

    # 2) Hide the mouse cursor
    mouse.visible = False    # ← Ursina-built-in :contentReference[oaicite:0]{index=0}

    # 3) Camera overhead
    camera.position = (0, 60, 0)
    camera.rotation_x = 90

    # 4) Game manager
    gm = GameManager(app)

    def update():
        gm.update()

    def input(key):
        gm.input(key)

    # 5) Run
    app.run()
