import pygame

pygame.init()
pygame.joystick.init()

# Initialize both controllers
controllers = []
for i in range(pygame.joystick.get_count()):
    js = pygame.joystick.Joystick(i)
    js.init()
    print(f"Detected joystick {i}: {js.get_name()}")
    controllers.append(js)

# In your game loop:
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Button pressed
        elif event.type == pygame.JOYBUTTONDOWN:
            print(f"Controller {event.joy} button {event.button} down")

        # Axis motion (sticks)
        elif event.type == pygame.JOYAXISMOTION:
            print(f"Controller {event.joy} axis {event.axis} value {event.value:.2f}")
