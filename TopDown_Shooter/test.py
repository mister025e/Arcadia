from ursina import *
import time
import math
import json
import os

# --- GLOBALS & STATE VARIABLES ---
game_state = 'menu'       # 'menu' | 'playing' | 'gameover' | 'name_entry' | 'leaderboard'
match_start_time = 0
match_end_time = 0
last_score = 0            # will be set when game ends
score_saved = False       # tracks if the current match’s score was saved

# Penalty values (not shown in UI)
P1_HP_PENALTY = 2
P2_HP_PENALTY = 2

# For name‐entry:
name_slots = [''] * 6
current_slot_index = 0

# Leaderboard: list of {'name':str, 'score':int}
leaderboard = []

# Determine where to save leaderboard.json (same folder as main.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LEADERBOARD_FILE = os.path.join(SCRIPT_DIR, 'leaderboard.json')


# --- FILE‐BASED LEADERBOARD LOAD/SAVE FUNCTIONS ---

def load_leaderboard():
    global leaderboard
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, 'r') as f:
                data = json.load(f)
            cleaned = []
            for e in data:
                if isinstance(e, dict) and 'name' in e and 'score' in e:
                    cleaned.append({'name': e['name'], 'score': e['score']})
            leaderboard[:] = sorted(cleaned, key=lambda x: x['score'], reverse=True)[:10]
        except Exception:
            leaderboard[:] = []
    else:
        leaderboard[:] = []


def save_leaderboard():
    global leaderboard
    data = leaderboard[:10]
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def add_score_to_leaderboard(name: str, score: int):
    global leaderboard
    if not name:
        return
    entry = {'name': name, 'score': score}
    leaderboard.append(entry)
    leaderboard[:] = sorted(leaderboard, key=lambda x: x['score'], reverse=True)[:10]
    save_leaderboard()


# --- SCREEN‐SWITCHING FUNCTIONS ---

def show_main_menu():
    global game_state
    game_state = 'menu'

    # Disable game entities
    for e in game_entities:
        e.enabled = False

    # Disable game UI
    timer_text.enabled = False
    p1_hp_text.enabled = False
    p2_hp_text.enabled = False

    # Disable gameover UI
    gameover_panel.enabled = False
    gameover_winner_text.enabled = False
    btn_restart.enabled = False
    btn_main_menu.enabled = False
    btn_save_score.enabled = False
    btn_view_leaderboard.enabled = False

    # Disable name‐entry UI
    name_panel.enabled = False
    name_instr.enabled = False
    for t in name_slot_texts:
        t.enabled = False

    # Disable leaderboard UI
    leaderboard_panel.enabled = False
    for t in leaderboard_entry_texts:
        t.enabled = False
    btn_leaderboard_back.enabled = False

    # Enable main menu UI
    menu_panel.enabled = True
    btn_play.enabled = True
    btn_quit.enabled = True


def start_game():
    global game_state, match_start_time, last_score, score_saved
    game_state = 'playing'

    # Reset players
    p1.health = 100
    p2.health = 100
    p1.position = Vec3(-5, 0.5, -5)
    p2.position = Vec3(5, 0.5, 5)

    # Reset timer & score_saved
    match_start_time = time.time()
    last_score = 0
    score_saved = False

    # Hide menus & gameover/UI
    menu_panel.enabled = False
    btn_play.enabled = False
    btn_quit.enabled = False

    gameover_panel.enabled = False
    gameover_winner_text.enabled = False
    btn_restart.enabled = False
    btn_main_menu.enabled = False
    btn_save_score.enabled = False
    btn_view_leaderboard.enabled = False

    # Hide name entry
    name_panel.enabled = False
    name_instr.enabled = False
    for t in name_slot_texts:
        t.enabled = False

    # Hide leaderboard
    leaderboard_panel.enabled = False
    for t in leaderboard_entry_texts:
        t.enabled = False
    btn_leaderboard_back.enabled = False

    # Enable game UI & entities
    for e in game_entities:
        e.enabled = True

    timer_text.enabled = True
    p1_hp_text.enabled = True
    p2_hp_text.enabled = True


def end_game(winner: 'Player'):
    global game_state, match_end_time, last_score, score_saved
    game_state = 'gameover'
    match_end_time = time.time()
    score_saved = False  # new match, not yet saved

    # Disable game entities
    for e in game_entities:
        e.enabled = False

    # Disable in‐game UI
    timer_text.enabled = False
    p1_hp_text.enabled = False
    p2_hp_text.enabled = False

    # Calculate elapsed time & health lost
    elapsed = match_end_time - match_start_time
    hp_lost = 100 - winner.health
    penalty = P1_HP_PENALTY if winner is p1 else P2_HP_PENALTY

    base_score = 1000
    raw_score = base_score - int(elapsed * 10) - (hp_lost * penalty)
    last_score = max(0, raw_score)

    # Show gameover text
    gameover_winner_text.text = f'{winner.name} Wins!\nScore: {last_score}'
    gameover_winner_text.enabled = True

    # Show gameover panel & buttons
    gameover_panel.enabled = True
    btn_restart.enabled = True
    btn_main_menu.enabled = True
    btn_save_score.enabled = True
    btn_view_leaderboard.enabled = True


def show_name_entry():
    global game_state, name_slots, current_slot_index
    game_state = 'name_entry'

    # Initialize slots
    name_slots[:] = [''] * 6
    current_slot_index = 0

    # Disable gameover UI buttons (except Save Score remains until saved)
    btn_restart.enabled = False
    btn_main_menu.enabled = False
    # ✅ Don’t disable btn_save_score here (they’re already on gameover)
    btn_view_leaderboard.enabled = False

    # Show name entry UI
    name_panel.enabled = True
    name_instr.enabled = True
    for t in name_slot_texts:
        t.text = '_'   # underscore indicates blank
        t.color = color.white
        t.enabled = True

    # Highlight first slot
    name_slot_texts[0].color = color.yellow


def finish_name_entry():
    global game_state, score_saved

    i = current_slot_index
    if name_slots[i] == '':
        username = ''.join(name_slots[:i])
    else:
        username = ''.join(name_slots[:i + 1])

    if username:
        add_score_to_leaderboard(username, last_score)
        score_saved = True
        btn_save_score.enabled = False

    # Hide name entry UI
    name_panel.enabled = False
    name_instr.enabled = False
    for t in name_slot_texts:
        t.enabled = False

    # Return to gameover UI
    gameover_panel.enabled = True
    gameover_winner_text.enabled = True
    btn_restart.enabled = True
    btn_main_menu.enabled = True
    # If user left name blank, they can still save later
    if not score_saved:
        btn_save_score.enabled = True
    btn_view_leaderboard.enabled = True

    game_state = 'gameover'


def show_leaderboard():
    global game_state
    game_state = 'leaderboard'

    # Disable gameover UI (including Save Score)
    gameover_panel.enabled = False
    gameover_winner_text.enabled = False
    btn_restart.enabled = False
    btn_main_menu.enabled = False
    btn_save_score.enabled = False  # 🔒 Hide Save Score while on leaderboard
    btn_view_leaderboard.enabled = False

    # Populate top-10
    for idx, t in enumerate(leaderboard_entry_texts):
        if idx < len(leaderboard):
            entry = leaderboard[idx]
            rank = idx + 1
            t.text = f'{rank}. {entry["name"]} – {entry["score"]}'
            t.enabled = True
        else:
            t.enabled = False

    leaderboard_panel.enabled = True
    btn_leaderboard_back.enabled = True


def back_to_gameover():
    global game_state
    game_state = 'gameover'

    # Hide leaderboard UI
    leaderboard_panel.enabled = False
    for t in leaderboard_entry_texts:
        t.enabled = False
    btn_leaderboard_back.enabled = False

    # Show gameover UI
    gameover_panel.enabled = True
    gameover_winner_text.enabled = True
    btn_restart.enabled = True
    btn_main_menu.enabled = True
    # Re‐enable Save Score only if not yet saved
    if not score_saved:
        btn_save_score.enabled = True
    btn_view_leaderboard.enabled = True


# --- ENTITY CLASSES (Players & Projectiles) ---

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
        self.keys = keys
        self.speed = 5
        self.shoot_cooldown = 0.3
        self._last_shot = time.time()
        self.hp_penalty = hp_penalty

    def update(self):
        if game_state != 'playing':
            return

        dx = held_keys[self.keys['right']] - held_keys[self.keys['left']]
        dz = held_keys[self.keys['up']] - held_keys[self.keys['down']]
        movement = Vec3(dx, 0, dz)
        if movement != Vec3(0, 0, 0):
            movement = movement.normalized() * self.speed * time.dt
            new_pos = self.position + movement
            if abs(new_pos.x) <= 19.5 and abs(new_pos.z) <= 19.5:
                self.position = new_pos
            angle = math.degrees(math.atan2(movement.x, movement.z))
            self.rotation_y = angle

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
        if abs(self.position.x) > 20 or abs(self.position.z) > 20:
            destroy(self)
            return

        hit = self.intersects()
        if hit.hit:
            ent = hit.entity
            if isinstance(ent, Player) and ent is not self.owner:
                ent.health -= 20
                destroy(self)
                if ent.health <= 0:
                    end_game(self.owner)
                return
            if hasattr(ent, 'tag') and ent.tag == 'wall':
                destroy(self)
                return


# --- SET UP URSINA APP & CAMERA ---
app = Ursina()
window.borderless = False
window.title = 'Top-Down 1v1 Shooter with Leaderboard'
window.fps_counter.enabled = False

# Camera positioned high so 40×40 map fits at start
camera.position = (0, 60, 0)
camera.rotation_x = 90


# --- MAIN MENU UI ---
menu_panel = Entity(
    parent=camera.ui,
    model='quad',
    color=color.rgba(0, 0, 0, 0.6),
    scale=(1, 1),
    enabled=False
)
btn_play = Button(
    parent=camera.ui,
    text='Play',
    scale=(0.2, 0.1),
    position=(0, 0.1, 0),
    color=color.azure,
    on_click=lambda: start_game(),
    enabled=False
)
btn_quit = Button(
    parent=camera.ui,
    text='Quit',
    scale=(0.2, 0.1),
    position=(0, -0.1, 0),
    color=color.red,
    on_click=lambda: application.quit(),
    enabled=False
)


# --- GAMEOVER UI ---
gameover_panel = Entity(
    parent=camera.ui,
    model='quad',
    color=color.rgba(0, 0, 0, 0.6),
    scale=(1, 1),
    enabled=False
)
gameover_winner_text = Text(
    parent=camera.ui,
    text='',
    origin=(0, 0),
    scale=2,
    position=(0, 0.2),
    color=color.white,
    enabled=False
)
btn_restart = Button(
    parent=camera.ui,
    text='Restart',
    scale=(0.2, 0.1),
    position=(-0.25, -0.1, 0),
    color=color.azure,
    on_click=lambda: start_game(),
    enabled=False
)
btn_main_menu = Button(
    parent=camera.ui,
    text='Main Menu',
    scale=(0.2, 0.1),
    position=(0.25, -0.1, 0),
    color=color.orange,
    on_click=lambda: show_main_menu(),
    enabled=False
)
btn_save_score = Button(
    parent=camera.ui,
    text='Save Score',
    scale=(0.2, 0.1),
    position=(-0.25, -0.25, 0),
    color=color.green,
    on_click=lambda: show_name_entry(),
    enabled=False
)
btn_view_leaderboard = Button(
    parent=camera.ui,
    text='View Leaderboard',
    scale=(0.2, 0.1),
    position=(0.25, -0.25, 0),
    color=color.violet,
    on_click=lambda: show_leaderboard(),
    enabled=False
)


# --- NAME‐ENTRY UI (enter up to 6‐char username) ---
name_panel = Entity(
    parent=camera.ui,
    model='quad',
    color=color.rgba(0, 0, 0, 0.6),
    scale=(1, 1),
    enabled=False
)
name_instr = Text(
    parent=camera.ui,
    text='Use W/S to change letter, A/D to move slot, Space to confirm',
    position=(0, 0.4),
    origin=(0, 0),
    scale=1,
    color=color.white,
    enabled=False
)
name_slot_texts = []
slot_start_x = -0.15
slot_spacing = 0.06
for i in range(6):
    t = Text(
        parent=camera.ui,
        text='_',
        position=(slot_start_x + i * slot_spacing, 0.2),
        origin=(0, 0),
        scale=2,
        color=color.white,
        enabled=False
    )
    name_slot_texts.append(t)


# --- LEADERBOARD UI (top‐10 display) ---
leaderboard_panel = Entity(
    parent=camera.ui,
    model='quad',
    color=color.rgba(0, 0, 0, 0.6),
    scale=(1, 1),
    enabled=False
)
leaderboard_entry_texts = []
entry_y_start = 0.35
entry_spacing = 0.06
for i in range(10):
    t = Text(
        parent=camera.ui,
        text='',
        position=(0, entry_y_start - i * entry_spacing),
        origin=(0, 0),
        scale=1.2,
        color=color.white,
        enabled=False
    )
    leaderboard_entry_texts.append(t)
btn_leaderboard_back = Button(
    parent=camera.ui,
    text='Back',
    scale=(0.2, 0.1),
    position=(0, -0.4, 0),
    color=color.orange,
    on_click=lambda: back_to_gameover(),
    enabled=False
)


# --- GAME UI (TIMER & HP) ---
timer_text = Text(
    parent=camera.ui,
    text='Time: 0.0s',
    position=Vec2(0, 0.48),
    origin=(0, 0),
    scale=1.5,
    color=color.white,
    enabled=False
)
p1_hp_text = Text(
    parent=camera.ui,
    text='P1 HP: 100',
    position=Vec2(-0.45, 0.45),
    scale=1.5,
    color=color.white,
    enabled=False
)
p2_hp_text = Text(
    parent=camera.ui,
    text='P2 HP: 100',
    position=Vec2(0.45, 0.45),
    scale=1.5,
    color=color.white,
    enabled=False
)


# --- BUILD MAP & COVERS & BORDERS (initially disabled) ---
floor = Entity(
    model='plane',
    scale=(40, 1, 40),
    texture='white_cube',
    texture_scale=(40, 40),
    color=color.gray,
    collider='box',
    enabled=False
)

border_top = Entity(
    model='cube',
    color=color.dark_gray,
    scale=(40, 1, 1),
    position=(0, 0.5, 20.5),
    collider='box',
    tag='wall',
    enabled=False
)
border_bottom = Entity(
    model='cube',
    color=color.dark_gray,
    scale=(40, 1, 1),
    position=(0, 0.5, -20.5),
    collider='box',
    tag='wall',
    enabled=False
)
border_right = Entity(
    model='cube',
    color=color.dark_gray,
    scale=(1, 1, 40),
    position=(20.5, 0.5, 0),
    collider='box',
    tag='wall',
    enabled=False
)
border_left = Entity(
    model='cube',
    color=color.dark_gray,
    scale=(1, 1, 40),
    position=(-20.5, 0.5, 0),
    collider='box',
    tag='wall',
    enabled=False
)

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
    c = Entity(
        model='cube',
        color=color.brown,
        scale=(2, 1, 2),
        position=pos,
        collider='box',
        tag='wall',
        enabled=False
    )
    covers.append(c)


# --- CREATE PLAYER ENTITIES (initially disabled) ---
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

game_entities = [
    floor,
    border_top, border_bottom, border_left, border_right
] + covers + [p1, p2]


# --- INPUT HANDLER for name‐entry (W/S/A/D/Space) ---

def input(key):
    global current_slot_index

    if game_state != 'name_entry':
        return

    if key == 'w':  # Up: cycle letter up
        current_char = name_slots[current_slot_index]
        if current_char == '':
            new_char = 'A'
        else:
            idx = ord(current_char) - ord('A')
            new_char = chr(ord('A') + ((idx + 1) % 26))
        name_slots[current_slot_index] = new_char
        name_slot_texts[current_slot_index].text = new_char

    elif key == 's':  # Down: cycle letter down
        current_char = name_slots[current_slot_index]
        if current_char == '':
            new_char = 'A'
        else:
            idx = ord(current_char) - ord('A')
            new_char = chr(ord('A') + ((idx - 1) % 26))
        name_slots[current_slot_index] = new_char
        name_slot_texts[current_slot_index].text = new_char

    elif key == 'd':  # Right: advance slot if current is non‐blank
        if name_slots[current_slot_index] != '' and current_slot_index < 5:
            name_slot_texts[current_slot_index].color = color.white
            current_slot_index += 1
            name_slot_texts[current_slot_index].color = color.yellow

    elif key == 'a':  # Left: go back a slot
        if current_slot_index > 0:
            name_slot_texts[current_slot_index].color = color.white
            current_slot_index -= 1
            name_slot_texts[current_slot_index].color = color.yellow

    elif key == 'space' or key == 'space hold':
        finish_name_entry()


# --- MAIN UPDATE FUNCTION (runs every frame) ---

def update():
    if game_state == 'playing':
        elapsed = time.time() - match_start_time
        timer_text.text = f'Time: {elapsed:.1f}s'
        p1_hp_text.text = f'P1 HP: {p1.health}'
        p2_hp_text.text = f'P2 HP: {p2.health}'

        if p1.health <= 0 and p2.health <= 0:
            end_game(p1)


# --- INITIALIZATION & SHOW MAIN MENU ON STARTUP ---

if __name__ == '__main__':
    load_leaderboard()
    show_main_menu()
    app.run()
