import pygame
from ursina import Ursina, camera, window, mouse
from game_manager import GameManager

if __name__ == '__main__':
    # ─── Initialize pygame & joysticks ─────────────────────────────────────────
    pygame.init()
    pygame.joystick.init()
    controllers = []
    for i in range(pygame.joystick.get_count()):
        js = pygame.joystick.Joystick(i)
        js.init()
        print(f"Detected joystick {i}: {js.get_name()}")
        controllers.append(js)

    # ─── Start Ursina fullscreen, hide mouse ────────────────────────────────────
    app = Ursina(fullscreen=True, vsync=True)
    window.fullscreen = True
    mouse.visible = False

    # ─── Position camera ─────────────────────────────────────────────────────────
    camera.position = (0, 60, 0)
    camera.rotation_x = 90

    # ─── Create GameManager with joystick list ──────────────────────────────────
    gm = GameManager(app, controllers)

    # ─── Main update: pump pygame events for joysticks, then game logic ────────
    def update():
        for event in pygame.event.get():
            gm.process_joystick_event(event)
        gm.update()

    def input(key):
        gm.input(key)

    app.run()
