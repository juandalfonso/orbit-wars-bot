"""
Orbit Wars — Bot v5.1: Parámetros Adaptativos + Predicción Orbital
====================================================================
Autor: juandalfonso
Fecha: 23 abril 2026

RESULTADOS LOCALES:
  - vs random:  9W / 1L / 0E (10 partidas)
  - vs v1:      6W / 4L / 0E (10 partidas)

RESULTADOS KAGGLE (Submission #1):
  - Score:           564.9
  - Win validation:  1818
  - Loss validation: 369
  - Posición:        734 / 1161
  - Líder:           2546.4

ESTRATEGIA:
  Fusión de v1 (arquitectura simple, cada planeta dispara cada turno)
  con predicción orbital de v4 (aim_angle convergente).

  Mejoras sobre v5:
    1. Parámetros adaptativos por fase:
       - 1 planeta  → min_defense=3, max_frac=0.85  (arranque agresivo)
       - 2-3 planetas → min_defense=5, max_frac=0.75 (expansión)
       - 4+ planetas → min_defense=8, max_frac=0.60  (consolidación)
    2. Fallback de puntería: si la trayectoria predicha cruza el sol,
       intenta apuntar a posición actual antes de descartar el objetivo.
    3. Bonus por planetas lentos (dist_sol ≤ 40) como incentivo suave
       de scoring, sin bloquear el flujo de ataque.

LIMITACIONES CONOCIDAS (para v6):
  - Disparos desviados observados en replay de Kaggle
  - Sin defensa reactiva ante flotas enemigas entrantes
  - Sin coordinación de ataque desde múltiples planetas
  - Sin estimación de ETA de flotas enemigas

ARQUITECTURA:
  Capa 1: Parseo del estado + aprendizaje de angular_velocity
  Capa 2: Geometría orbital (predict, aim_angle, crosses_sun)
  Capa 3: Parámetros adaptativos por fase (get_params)
  Capa 4: Reglas de combate (ships_available, required_ships)
  Capa 5: Scoring (target_score con bonus planetas lentos)
  Capa 6: Política de acciones (choose_target, agent)
"""

import math
from kaggle_environments.envs.orbit_wars.orbit_wars import Planet, Fleet

# ============================================================
# CONSTANTES
# ============================================================
SUN_X, SUN_Y     = 50.0, 50.0
SUN_RADIUS        = 10.0
ENEMY_EXTRA       = 6
WEIGHT_PRODUCTION = 12.0
WEIGHT_DISTANCE   = 1.6
WEIGHT_SHIPS      = 1.1
BONUS_NEUTRAL     = 18.0
BONUS_ENEMY       = 8.0
BONUS_SLOW        = 15.0
SUN_PENALTY       = 25.0
SLOW_DIST_MAX     = 40.0

_ang_vel_memory = [0.032948880918056464]

# ============================================================
# CAPA 3: PARÁMETROS ADAPTATIVOS
# ============================================================
def get_params(my_count):
    """
    Ajusta agresividad según cuántos planetas tenemos.
    Con pocos planetas: muy agresivo para arrancar.
    Con muchos: más conservador para no perder territorio.
    """
    if my_count <= 1:
        return dict(min_defense=3, max_frac=0.85)
    elif my_count <= 3:
        return dict(min_defense=5, max_frac=0.75)
    else:
        return dict(min_defense=8, max_frac=0.60)

# ============================================================
# CAPA 1: PARSEO
# ============================================================
def get_player(obs):
    return obs.get("player", 0) if isinstance(obs, dict) else obs.player

def get_planets(obs):
    raw = obs.get("planets", []) if isinstance(obs, dict) else obs.planets
    return [Planet(*p) for p in raw]

def get_fleets(obs):
    raw = obs.get("fleets", []) if isinstance(obs, dict) else obs.fleets
    return [Fleet(*f) for f in raw]

def get_ang_vel(obs):
    """Extrae angular_velocity y aprende el valor real desde turno 1."""
    v = obs.get("angular_velocity", 0.0) if isinstance(obs, dict) else getattr(obs, "angular_velocity", 0.0)
    v = float(v or 0.0)
    if v != 0.0:
        _ang_vel_memory[0] = v
    return _ang_vel_memory[0]

# ============================================================
# CAPA 2: GEOMETRÍA ORBITAL
# ============================================================
def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)

def dist_sol(p):
    return math.hypot(p.x - SUN_X, p.y - SUN_Y)

def is_slow(p):
    """Planeta de rotación lenta — prioridad táctica alta."""
    return dist_sol(p) <= SLOW_DIST_MAX

def fleet_speed(ships):
    if ships <= 1: return 1.0
    return min(6.0, 1.0 + 5.0*(math.log(max(ships, 2))/math.log(1000))**1.5)

def seg_dist_sun(ax, ay, bx, by):
    abx, aby = bx-ax, by-ay
    ab2 = abx*abx + aby*aby
    if ab2 == 0: return math.hypot(SUN_X-ax, SUN_Y-ay)
    t = max(0.0, min(1.0, ((SUN_X-ax)*abx+(SUN_Y-ay)*aby)/ab2))
    return math.hypot(SUN_X-(ax+t*abx), SUN_Y-(ay+t*aby))

def crosses_sun(ax, ay, bx, by):
    return seg_dist_sun(ax, ay, bx, by) <= SUN_RADIUS + 0.5

def predict(p, ang_vel, turns):
    """Posición futura del planeta en `turns` turnos."""
    dx, dy = p.x - SUN_X, p.y - SUN_Y
    r = math.hypot(dx, dy)
    theta = math.atan2(dy, dx) + ang_vel * turns
    return SUN_X + r*math.cos(theta), SUN_Y + r*math.sin(theta)

def aim_angle(src, tgt, ships, ang_vel):
    """
    Ángulo con predicción orbital convergente (6 iteraciones).
    Fallback: apuntar directo si la trayectoria predicha cruza el sol.
    Retorna (angle, fx, fy) o (None, None, None) si ambas cruzan el sol.
    """
    ships = max(1, ships)
    turns = dist(src, tgt) / fleet_speed(ships)
    fx, fy = tgt.x, tgt.y
    for _ in range(6):
        fx, fy = predict(tgt, ang_vel, turns)
        turns = math.hypot(src.x-fx, src.y-fy) / fleet_speed(ships)
    if crosses_sun(src.x, src.y, fx, fy):
        if not crosses_sun(src.x, src.y, tgt.x, tgt.y):
            return math.atan2(tgt.y-src.y, tgt.x-src.x), tgt.x, tgt.y
        return None, None, None
    return math.atan2(fy-src.y, fx-src.x), fx, fy

# ============================================================
# CAPA 4: REGLAS DE COMBATE
# ============================================================
def ships_available(p, params):
    reserve  = max(params["min_defense"], p.production * 2)
    max_send = int(p.ships * params["max_frac"])
    return max(0, min(p.ships - reserve, max_send))

def required_ships(t):
    base = t.ships + 1
    return base + ENEMY_EXTRA if t.owner != -1 else base

# ============================================================
# CAPA 5: SCORING
# ============================================================
def target_score(src, tgt, fleets, player):
    d    = dist(src, tgt)
    need = required_ships(tgt)
    if need <= 0: return -1e9
    ob   = BONUS_NEUTRAL if tgt.owner == -1 else BONUS_ENEMY
    sb   = BONUS_SLOW if is_slow(tgt) else 0.0
    sun  = SUN_PENALTY if crosses_sun(src.x, src.y, tgt.x, tgt.y) else 0.0
    score = tgt.production*WEIGHT_PRODUCTION + ob + sb \
            - d*WEIGHT_DISTANCE - need*WEIGHT_SHIPS - sun
    enemy_fleets = [f for f in fleets if f.owner not in (player, -1)]
    if enemy_fleets:
        score -= min(8, len(enemy_fleets) * 2)
    return score

# ============================================================
# CAPA 6: POLÍTICA DE ACCIONES
# ============================================================
def choose_target(src, candidates, fleets, player, ang_vel, params):
    avail = ships_available(src, params)
    if avail <= 0: return None, None
    ranked = sorted(candidates, key=lambda t: target_score(src, t, fleets, player), reverse=True)
    for tgt in ranked:
        need = required_ships(tgt)
        if need > avail: continue
        angle, fx, fy = aim_angle(src, tgt, need, ang_vel)
        if angle is None: continue
        return tgt, angle
    return None, None


def agent(obs):
    """
    Función principal — llamada por Kaggle cada turno.
    Devuelve lista de acciones: [[from_planet_id, angle, num_ships], ...]
    """
    player  = get_player(obs)
    planets = get_planets(obs)
    fleets  = get_fleets(obs)
    ang_vel = get_ang_vel(obs)

    my_planets = [p for p in planets if p.owner == player]
    targets    = [p for p in planets if p.owner != player]

    if not my_planets or not targets: return []

    params = get_params(len(my_planets))
    my_planets = sorted(my_planets, key=lambda p: (-p.production, -p.ships))

    moves        = []
    targeted_ids = set()

    for src in my_planets:
        candidates = [t for t in targets if t.id not in targeted_ids]
        if not candidates: break
        tgt, angle = choose_target(src, candidates, fleets, player, ang_vel, params)
        if tgt is None: continue
        send = required_ships(tgt)
        if send <= 0 or send > ships_available(src, params): continue
        moves.append([src.id, angle, int(send)])
        targeted_ids.add(tgt.id)

    return moves
