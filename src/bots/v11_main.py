import math
from collections import Counter
from kaggle_environments.envs.orbit_wars.orbit_wars import Planet, Fleet

# ============================================================
# CONSTANTES
# ============================================================
SUN_X, SUN_Y        = 50.0, 50.0
SUN_RADIUS          = 10.0
WEIGHT_PRODUCTION   = 12.0
WEIGHT_DISTANCE     = 1.6
WEIGHT_SHIPS        = 1.1
BONUS_NEUTRAL       = 18.0
BONUS_ENEMY         = 8.0
BONUS_SLOW          = 15.0
SUN_PENALTY         = 25.0
SLOW_DIST_MAX       = 40.0
WEAKEST_BONUS       = 15.0
ENEMY_EXTRA         = 6
THREAT_RADIUS       = 8.0
CLOSE_RATIO         = 4

_ang_vel_memory = [0.032948880918056464]

def get_player(obs):
    return obs.get("player", 0) if isinstance(obs, dict) else obs.player

def get_planets(obs):
    raw = obs.get("planets", []) if isinstance(obs, dict) else obs.planets
    return [Planet(*p) for p in raw]

def get_fleets(obs):
    raw = obs.get("fleets", []) if isinstance(obs, dict) else obs.fleets
    return [Fleet(*f) for f in raw]

def get_ang_vel(obs):
    v = obs.get("angular_velocity", 0.0) if isinstance(obs, dict) else getattr(obs, "angular_velocity", 0.0)
    v = float(v or 0.0)
    if v != 0.0:
        _ang_vel_memory[0] = v
    return _ang_vel_memory[0]

def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)

def dist_sol(p):
    return math.hypot(p.x - SUN_X, p.y - SUN_Y)

def is_slow(p):
    return dist_sol(p) <= SLOW_DIST_MAX

def fleet_speed(ships):
    if ships <= 1: return 1.0
    return min(6.0, 1.0 + 5.0 * (math.log(max(ships, 2)) / math.log(1000)) ** 1.5)

def seg_dist_sun(ax, ay, bx, by):
    abx, aby = bx - ax, by - ay
    ab2 = abx * abx + aby * aby
    if ab2 == 0:
        return math.hypot(SUN_X - ax, SUN_Y - ay)
    t = max(0.0, min(1.0, ((SUN_X - ax) * abx + (SUN_Y - ay) * aby) / ab2))
    return math.hypot(SUN_X - (ax + t * abx), SUN_Y - (ay + t * aby))

def crosses_sun(ax, ay, bx, by):
    return seg_dist_sun(ax, ay, bx, by) <= SUN_RADIUS + 0.5

def predict(p, ang_vel, turns):
    dx, dy = p.x - SUN_X, p.y - SUN_Y
    r = math.hypot(dx, dy)
    theta = math.atan2(dy, dx) + ang_vel * turns
    return SUN_X + r * math.cos(theta), SUN_Y + r * math.sin(theta)

def aim_angle(src, tgt, ships, ang_vel):
    ships = max(1, ships)
    turns = dist(src, tgt) / fleet_speed(ships)
    fx, fy = tgt.x, tgt.y
    for _ in range(6):
        fx, fy = predict(tgt, ang_vel, turns)
        turns = math.hypot(src.x - fx, src.y - fy) / fleet_speed(ships)
    if crosses_sun(src.x, src.y, fx, fy):
        if not crosses_sun(src.x, src.y, tgt.x, tgt.y):
            return math.atan2(tgt.y - src.y, tgt.x - src.x), tgt.x, tgt.y
        return None, None, None
    return math.atan2(fy - src.y, fx - src.x), fx, fy

# FIX A — Threshold adaptativo
def get_expansion_threshold(num_enemies):
    return {1: 8, 2: 6, 3: 4}.get(num_enemies, 4)

# FIX B — Parámetros con modo cierre
def get_params(my_count, num_enemies=1, enemy_planet_count=0):
    if enemy_planet_count > 0 and my_count >= enemy_planet_count * CLOSE_RATIO:
        return dict(min_defense=1, max_frac=0.95, closing=True)
    threshold = get_expansion_threshold(num_enemies)
    if num_enemies >= 3:
        return dict(min_defense=1, max_frac=0.95, closing=False)
    if num_enemies == 2:
        return dict(min_defense=3, max_frac=0.88, closing=False)
    if my_count < threshold:
        return dict(min_defense=2, max_frac=0.90, closing=False)
    return dict(min_defense=6, max_frac=0.65, closing=False)

# FIX C — required_ships sin buffer en neutrales
def required_ships(t):
    base = t.ships + 1
    if t.owner == -1:
        return base
    return base + ENEMY_EXTRA

# FIX D — Defensa reactiva con radio estricto
def planet_under_threat(p, enemy_fleets):
    for fleet in enemy_fleets:
        if math.hypot(fleet.x - p.x, fleet.y - p.y) < THREAT_RADIUS:
            return True
    return False

def ships_available(p, params, enemy_fleets):
    threat_bonus = p.ships // 3 if planet_under_threat(p, enemy_fleets) else 0
    reserve  = max(params["min_defense"], p.production * 2) + threat_bonus
    max_send = int(p.ships * params["max_frac"])
    return max(0, min(p.ships - reserve, max_send))

def get_weakest_enemy(planets, player):
    counts = Counter(p.owner for p in planets if p.owner not in (player, -1))
    if not counts:
        return None
    return min(counts, key=counts.get)

def count_enemies(planets, player):
    return len(set(p.owner for p in planets if p.owner not in (player, -1)))

def get_covered_targets(my_fleets, targets, ang_vel):
    covered = {}
    for fleet in my_fleets:
        best_planet, best_align = None, 1e9
        for p in targets:
            d   = math.hypot(fleet.x - p.x, fleet.y - p.y)
            eta = d / fleet_speed(fleet.ships)
            fx, fy = predict(p, ang_vel, eta)
            dest_x = fleet.x + math.cos(fleet.angle) * d
            dest_y = fleet.y + math.sin(fleet.angle) * d
            alignment = math.hypot(dest_x - fx, dest_y - fy)
            if alignment < best_align:
                best_align  = alignment
                best_planet = p
        if best_planet is not None and best_align < 10.0:
            covered[best_planet.id] = covered.get(best_planet.id, 0) + fleet.ships
    return covered

def expansion_score(src, tgt):
    d       = dist(src, tgt)
    need    = required_ships(tgt)
    sun_pen = SUN_PENALTY if crosses_sun(src.x, src.y, tgt.x, tgt.y) else 0.0
    return -d - need * 0.5 - sun_pen

def consolidation_score(src, tgt, fleets, player, weakest):
    d    = dist(src, tgt)
    need = required_ships(tgt)
    if need <= 0:
        return -1e9
    ob   = BONUS_NEUTRAL if tgt.owner == -1 else BONUS_ENEMY
    sb   = BONUS_SLOW if is_slow(tgt) else 0.0
    sun  = SUN_PENALTY if crosses_sun(src.x, src.y, tgt.x, tgt.y) else 0.0
    wb   = WEAKEST_BONUS if (tgt.owner != -1 and tgt.owner == weakest) else 0.0
    score = tgt.production * WEIGHT_PRODUCTION + ob + sb + wb \
            - d * WEIGHT_DISTANCE - need * WEIGHT_SHIPS - sun
    enemy_fleets = [f for f in fleets if f.owner not in (player, -1)]
    if enemy_fleets:
        score -= min(8, len(enemy_fleets) * 2)
    return score

def choose_target(src, candidates, fleets, player, ang_vel, params,
                  covered, expanding, weakest, enemy_fleets):
    avail = ships_available(src, params, enemy_fleets)
    if avail <= 0:
        return None, None
    if expanding:
        neutrals = [t for t in candidates if t.owner == -1]
        pool     = neutrals if neutrals else candidates
        ranked   = sorted(pool, key=lambda t: expansion_score(src, t), reverse=True)
    else:
        ranked = sorted(candidates,
                        key=lambda t: consolidation_score(src, t, fleets, player, weakest),
                        reverse=True)
    for tgt in ranked:
        need = required_ships(tgt)
        if need > avail: continue
        if covered.get(tgt.id, 0) >= need: continue
        angle, fx, fy = aim_angle(src, tgt, need, ang_vel)
        if angle is None: continue
        return tgt, angle
    return None, None

def agent(obs):
    player  = get_player(obs)
    planets = get_planets(obs)
    fleets  = get_fleets(obs)
    ang_vel = get_ang_vel(obs)

    my_planets    = [p for p in planets if p.owner == player]
    targets       = [p for p in planets if p.owner != player]
    enemy_fleets  = [f for f in fleets if f.owner not in (player, -1)]

    if not my_planets or not targets: return []

    num_enemies        = count_enemies(planets, player)
    enemy_planet_count = sum(1 for p in planets if p.owner not in (player, -1) and p.owner != -1)
    threshold          = get_expansion_threshold(num_enemies)
    params             = get_params(len(my_planets), num_enemies, enemy_planet_count)
    closing            = params.get("closing", False)
    expanding          = (not closing) and (len(my_planets) < threshold)
    weakest            = get_weakest_enemy(planets, player)

    my_fleets = [f for f in fleets if f.owner == player]
    covered   = get_covered_targets(my_fleets, targets, ang_vel)

    my_planets   = sorted(my_planets, key=lambda p: (-p.production, -p.ships))
    moves        = []
    targeted_ids = set()

    for src in my_planets:
        candidates = list(targets) if closing \
                     else [t for t in targets if t.id not in targeted_ids]
        if not candidates: break
        tgt, angle = choose_target(src, candidates, fleets, player, ang_vel,
                                   params, covered, expanding, weakest, enemy_fleets)
        if tgt is None: continue
        send = required_ships(tgt)
        if send <= 0 or send > ships_available(src, params, enemy_fleets): continue
        moves.append([src.id, angle, int(send)])
        if not closing:
            targeted_ids.add(tgt.id)
        covered[tgt.id] = covered.get(tgt.id, 0) + send

    return moves
