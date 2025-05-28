from ursina import Ursina, Entity, Text, color, camera, destroy, time, held_keys
import random

# Initialize the Ursina app
app = Ursina()

# Configure the camera for 2D
camera.orthographic = True
camera.fov = 10  # Adjust the view size

# Create the player entity
player = Entity(
    model='quad',
    color=color.azure,
    scale=(1, 1),
    position=(0, 0, 0)
)

# Generate some collectible coins
coins = []
for _ in range(5):
    x = random.uniform(-5, 5)
    y = random.uniform(-5, 5)
    coin = Entity(
        model='quad',
        color=color.yellow,
        scale=0.5,
        position=(x, y, 0)
    )
    coins.append(coin)

# Track the player's score
score = 0
score_text = Text(
    text=f'Score: {score}',
    position=(-0.85, 0.45),  # Top-left corner
    scale=2
)

# Update function called every frame
def update():
    global score
    move_speed = 5 * time.dt

    # Player movement (WASD)
    if held_keys['a']:
        player.x -= move_speed
    if held_keys['d']:
        player.x += move_speed
    if held_keys['w']:
        player.y += move_speed
    if held_keys['s']:
        player.y -= move_speed

    # Check for collisions with coins
    for coin in coins.copy():
        distance = (player.position - coin.position).length()
        # Simple collision threshold based on scale
        if distance < (player.scale_x + coin.scale_x) * 0.5:
            destroy(coin)
            coins.remove(coin)
            score += 1
            score_text.text = f'Score: {score}'

# Run the game
app.run()
