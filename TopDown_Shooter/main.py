from ursina import *
import time
import math

# --- GLOBALS & STATE ---
game_state = 'menu'   # 'menu', 'playing', 'gameover'
match_start_time = 0
match_end_time = 0

# Penalty values for health lost (not visible in UI)
P1_HP_PENALTY = 2
P2_HP_PENALTY = 2

# --- FUNCTIONS TO SWITCH SCREENS ---


def show_main_menu():
    """Enable main menu UI and disable game/gameover UI."""
    global game_state
    game_state = 'menu'
    # Disable game entities
    for e in game_entities:
        e.enabled = False

    timer_text.enabled = False
    p1_hp_text.enabled = False
    p2_hp_text.enabled = False

    # Disable gameover UI
    gameover_panel.enabled = False
    gameover_winner_text.enabled = False
    btn_restart.enabled = False
    btn_main_menu.enabled = False

    # Enable main menu UI
    menu_panel.enabled = True
    btn_play.enabled = True
    btn_quit.enabled = True


def start_game():
    """Initialize or restart the match: reset values, enable game entities, disable menus."""
    global game_state, match_start_time
    game_state = 'playing'

    # Reset players
    p1.health = 100
    p2.health = 100
    p1.position = Vec3(-5, 0.5, -5)
    p2.position = Vec3(5, 0.5, 5)

    # Reset timers
    match_start_time = time.time()

    # Hide main menu UI
    menu_panel.enabled = False
    btn_play.enabled = False
    btn_quit.enabled = False

    # Hide gameover UI (in case of restart)
    gameover_panel.enabled = False
    gameover_winner_text.enabled = False
    btn_restart.enabled = False
    btn_main_menu.enabled = False

    # Enable game UI and entities
    for e in game_entities:
        e.enabled = True

    timer_text.enabled = True
    p1_hp_text.enabled = True
    p2_hp_text.enabled = True


def end_game(winner: 'Player'):
    """Handle end of match: calculate score, show gameover UI, disable game entities."""
    global game_state, match_end_time
    game_state = 'gameover'
    match_end_time = time.time()

    # Disable game entities (players won't move or shoot)
    for e in game_entities:
        e.enabled = False

    timer_text.enabled = False
    p1_hp_text.enabled = False
    p2_hp_text.enabled = False

    # Calculate elapsed time
    elapsed = match_end_time - match_start_time

    # Calculate health lost for winner
    hp_lost = 100 - winner.health

    # Choose penalty per HP lost based on which player
    penalty = P1_HP_PENALTY if winner is p1 else P2_HP_PENALTY

    # Simple scoring formula: base_score - (time * 10) - (hp_lost * penalty)
    base_score = 1000
    score = max(0, int(base_score - elapsed * 10 - hp_lost * penalty))

    # Update gameover winner text
    gameover_winner_text.text = f'{winner.name} Wins!\nScore: {score}'
    gameover_winner_text.enabled = True

    # Show gameover UI
    gameover_panel.enabled = True
    btn_restart.enabled = True
    btn_main_menu.enabled = True


# --- ENTITY CLASSES ---


class Player(Entity):
    def __init__(self, name, position, keys, color, hp_penalty):
        super().__init__(
            model='cube',
            color=color,
            scale=1,
            position=position,
            collider='box'
        )
        self.name = name
        self.health = 100
        self.keys = keys  # {'up':'w','down':'s','left':'a','right':'d','shoot':'space'}
        self.speed = 5
        self.shoot_cooldown = 0.3
        self._last_shot = time.time()
        self.hp_penalty = hp_penalty

    def update(self):
        if game_state != 'playing':
            return

        # Movement: W/↑ moves toward +Z, S/↓ toward -Z
        dx = held_keys[self.keys['right']] - held_keys[self.keys['left']]
        dz = held_keys[self.keys['up']] - held_keys[self.keys['down']]
        movement = Vec3(dx, 0, dz)
        if movement != Vec3(0, 0, 0):
            movement = movement.normalized() * self.speed * time.dt
            new_pos = self.position + movement

            # Prevent player from moving through border walls: keep within ±19.5
            if abs(new_pos.x) <= 19.5 and abs(new_pos.z) <= 19.5:
                self.position = new_pos

            # Rotate to face movement direction
            angle = math.degrees(math.atan2(movement.x, movement.z))
            self.rotation_y = angle

        # Shooting
        if held_keys[self.keys['shoot']]:
            now = time.time()
            if (now - self._last_shot) >= self.shoot_cooldown:
                self.shoot()
                self._last_shot = now

    def shoot(self):
        spawn_pos = self.position + self.forward * 0.75
        Projectile(
            position=Vec3(spawn_pos.x, 0.5, spawn_pos.z),
            direction=self.forward,
            owner=self
        )


class Projectile(Entity):
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
        if game_state != 'playing':
            return

        self.position += self.direction * self.speed * time.dt

        # Destroy if out of bounds
        if abs(self.position.x) > 20 or abs(self.position.z) > 20:
            destroy(self)
            return

        hit = self.intersects()
        if hit.hit:
            ent = hit.entity
            if isinstance(ent, Player) and ent is not self.owner:
                ent.health -= 20
                destroy(self)
                # Check if that player died
                if ent.health <= 0:
                    end_game(self.owner)
                return
            if hasattr(ent, 'tag') and ent.tag == 'wall':
                destroy(self)
                return


# --- SET UP URSINA APP & CAMERA ---
app = Ursina()
window.borderless = False
window.title = 'Top‐Down 1v1 Shooter'
window.fps_counter.enabled = False

# Camera: higher so 40×40 map fully fits
camera.position = (0, 60, 0)
camera.rotation_x = 90

# --- MAIN MENU UI ---
menu_panel = Entity(parent=camera.ui, model='quad', color=color.rgba(0, 0, 0, 0.6),
                    scale=(1, 1), enabled=True)

btn_play = Button(parent=camera.ui, text='Play', scale=(0.2, 0.1), position=(0, 0.1, 0),
                  color=color.azure, on_click=lambda: start_game())
btn_quit = Button(parent=camera.ui, text='Quit', scale=(0.2, 0.1), position=(0, -0.1, 0),
                  color=color.red, on_click=lambda: application.quit())

# --- GAMEOVER UI ---
gameover_panel = Entity(parent=camera.ui, model='quad', color=color.rgba(0, 0, 0, 0.6),
                        scale=(1, 1), enabled=False)
gameover_winner_text = Text(parent=camera.ui, text='', origin=(0, 0), scale=2,
                            position=(0, 0.2), color=color.white, enabled=False)
btn_restart = Button(parent=camera.ui, text='Restart', scale=(0.2, 0.1), position=(0, -0.05, 0),
                     color=color.azure, enabled=False, on_click=lambda: start_game())
btn_main_menu = Button(parent=camera.ui, text='Main Menu', scale=(0.2, 0.1), position=(0, -0.25, 0),
                       color=color.orange, enabled=False, on_click=lambda: show_main_menu())

# --- GAME UI (TIMER & HP) ---
timer_text = Text(parent=camera.ui, text='Time: 0.0s', position=Vec2(0, 0.48),
                  origin=(0, 0), scale=1.5, color=color.white, enabled=False)
p1_hp_text = Text(parent=camera.ui, text='P1 HP: 100', position=Vec2(-0.45, 0.45),
                  scale=1.5, color=color.white, enabled=False)
p2_hp_text = Text(parent=camera.ui, text='P2 HP: 100', position=Vec2(0.45, 0.45),
                  scale=1.5, color=color.white, enabled=False)

# --- BUILD MAP & COVER & BORDERS (initially disabled) ---
floor = Entity(model='plane', scale=(40, 1, 40), texture='white_cube',
               texture_scale=(40, 40), color=color.gray, collider='box', enabled=False)

# Border walls (thickness=1, length=40)
border_top = Entity(model='cube', color=color.dark_gray, scale=(40, 1, 1),
                    position=(0, 0.5, 20.5), collider='box', tag='wall', enabled=False)
border_bottom = Entity(model='cube', color=color.dark_gray, scale=(40, 1, 1),
                       position=(0, 0.5, -20.5), collider='box', tag='wall', enabled=False)
border_right = Entity(model='cube', color=color.dark_gray, scale=(1, 1, 40),
                      position=(20.5, 0.5, 0), collider='box', tag='wall', enabled=False)
border_left = Entity(model='cube', color=color.dark_gray, scale=(1, 1, 40),
                     position=(-20.5, 0.5, 0), collider='box', tag='wall', enabled=False)

cover_positions = [
    Vec3(5, 0.5, 0),
    Vec3(-5, 0.5, 0),
    Vec3(0, 0.5, 5),
    Vec3(0, 0.5, -5),
    Vec3(5, 0.5, 5),
    Vec3(-5, 0.5, -5),
]
covers = []
for pos in cover_positions:
    c = Entity(model='cube', color=color.brown, scale=(2, 1, 2),
               position=pos, collider='box', tag='wall', enabled=False)
    covers.append(c)

# --- CREATE PLAYERS (initially disabled) ---
p1 = Player(
    name='Player 1',
    position=Vec3(-5, 0.5, -5),
    keys={'up': 'w', 'down': 's', 'left': 'a', 'right': 'd', 'shoot': 'space'},
    color=color.azure,
    hp_penalty=P1_HP_PENALTY
)
p1.enabled = False

p2 = Player(
    name='Player 2',
    position=Vec3(5, 0.5, 5),
    keys={'up': 'up arrow', 'down': 'down arrow', 'left': 'left arrow', 'right': 'right arrow', 'shoot': 'right shift'},
    color=color.orange,
    hp_penalty=P2_HP_PENALTY
)
p2.enabled = False

# Collect all game-related entities for easy enabling/disabling
game_entities = [
    floor,
    border_top, border_bottom, border_left, border_right
] + covers + [p1, p2]


# --- MAIN UPDATE FUNCTION ---
def update():
    # Only update timer and HP UI if in playing state
    if game_state == 'playing':
        # Update timer
        elapsed = time.time() - match_start_time
        timer_text.text = f'Time: {elapsed:.1f}s'

        # Update HP UI
        p1_hp_text.text = f'P1 HP: {p1.health}'
        p2_hp_text.text = f'P2 HP: {p2.health}'

        # Safety check: if somehow both die simultaneously, declare draw (not implemented)
        if p1.health <= 0 and p2.health <= 0:
            # For simplicity, declare Player 1 winner in tie
            end_game(p1)
        # Individual death is handled in Projectile.update()

# --- INITIAL CALL TO SHOW MAIN MENU ---
show_main_menu()

# --- RUN APP ---
if __name__ == '__main__':
    app.run()
