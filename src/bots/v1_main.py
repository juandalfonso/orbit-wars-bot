"""
Orbit Wars — Bot v1: Base Sólida
=================================
Autor: juandalfonso
Fecha: 21 abril 2026

ESTRATEGIA:
  - Prioriza planetas neutrales antes que enemigos
  - Pondera producción alta y menor costo de captura
  - Penaliza distancias largas
  - Deja reserva defensiva en cada planeta propio
  - Evita trayectorias que pasan cerca del sol
  - Un ataque por planeta por turno (política simple y controlable)

ARQUITECTURA:
  Capa 1: Parseo del estado (planets, fleets, player)
  Capa 2: Utilidades geométricas (dist, angle, sun check)
  Capa 3: Evaluación de objetivos (target_score)
  Capa 4: Reglas de seguridad (ships_available, required_ships)
  Capa 5: Política de acciones (choose_target, agent)

LIMITACIONES CONOCIDAS (para v2):
  - No predice posición futura de planetas orbitales
  - No estima ETA ni posición de flotas enemigas con precisión
  - No coordina ataques conjuntos desde múltiples planetas
  - No hace defensa reactiva basada en amenazas detectadas
"""

import math
from kaggle_environments.envs.orbit_wars.orbit_wars import Planet, Fleet

# ============================================================
# CONSTANTES CONFIGURABLES
# ============================================================

SUN_X = 50.0
SUN_Y = 50.0
SUN_RADIUS = 10.0

# Reserva mínima de naves que siempre se deja en cada planeta
MIN_DEFENSE = 8

# Fracción máxima de naves que se puede enviar desde un planeta en un turno
MAX_ATTACK_FRACTION = 0.6

# Naves extra que se envían al atacar un planeta enemigo (margen de seguridad)
ENEMY_ATTACK_EXTRA = 6

# Pesos de la función de puntuación
WEIGHT_PRODUCTION = 12.0   # Valor por unidad de producción
WEIGHT_DISTANCE = 1.6      # Penalización por unidad de distancia
WEIGHT_SHIPS = 1.1         # Penalización por naves necesarias
BONUS_NEUTRAL = 18.0       # Bonus extra por atacar neutrales vs enemigos
BONUS_ENEMY = 8.0          # Bonus base por atacar enemigos
SUN_PENALTY = 25.0         # Penalización si la trayectoria pasa cerca del sol


# ============================================================
# CAPA 1: PARSEO DEL ESTADO
# ============================================================

def get_player(obs):
    """Extrae el ID del jugador de la observación (dict o namedtuple)."""
    return obs.get("player", 0) if isinstance(obs, dict) else obs.player


def get_planets(obs):
    """Parsea la lista de planetas como named tuples Planet."""
    raw = obs.get("planets", []) if isinstance(obs, dict) else obs.planets
    return [Planet(*p) for p in raw]


def get_fleets(obs):
    """Parsea la lista de flotas como named tuples Fleet."""
    raw = obs.get("fleets", []) if isinstance(obs, dict) else obs.fleets
    return [Fleet(*f) for f in raw]


# ============================================================
# CAPA 2: UTILIDADES GEOMÉTRICAS
# ============================================================

def dist(a, b):
    """Distancia euclidiana entre dos objetos con campos .x y .y."""
    return math.hypot(a.x - b.x, a.y - b.y)


def angle_between(a, b):
    """Ángulo en radianes desde el objeto a hacia el objeto b."""
    return math.atan2(b.y - a.y, b.x - a.x)


def point_to_segment_dist(px, py, ax, ay, bx, by):
    """
    Distancia mínima desde el punto (px, py) al segmento (ax,ay)-(bx,by).
    Usada para verificar si una trayectoria pasa cerca del sol.
    """
    abx, aby = bx - ax, by - ay
    apx, apy = px - ax, py - ay
    ab2 = abx * abx + aby * aby
    if ab2 == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, (apx * abx + apy * aby) / ab2))
    cx, cy = ax + t * abx, ay + t * aby
    return math.hypot(px - cx, py - cy)


def crosses_sun(source, target):
    """
    Devuelve True si la trayectoria directa de source a target
    pasa a menos de (SUN_RADIUS + margen) del sol.
    """
    d = point_to_segment_dist(
        SUN_X, SUN_Y,
        source.x, source.y,
        target.x, target.y
    )
    return d <= SUN_RADIUS + 0.5


# ============================================================
# CAPA 3: EVALUACIÓN DE OBJETIVOS
# ============================================================

def target_score(source, target):
    """
    Puntaú qué tan bueno es atacar `target` desde `source`.
    Mayor puntaje = mejor objetivo.

    Componentes:
      + producción alta (más naves por turno si lo capturamos)
      + bonus por ser neutral (más fácil y menos riesgo)
      - penalización por distancia larga (cuesta tiempo y naves en tránsito)
      - penalización por guarnición alta (cuesta más naves para capturar)
      - penalización extra si la trayectoria pasa por el sol
    """
    d = dist(source, target)
    need = required_ships(target)
    if need <= 0:
        return -1e9

    owner_bonus = BONUS_NEUTRAL if target.owner == -1 else BONUS_ENEMY
    distance_penalty = d * WEIGHT_DISTANCE
    ship_penalty = need * WEIGHT_SHIPS
    production_value = target.production * WEIGHT_PRODUCTION
    sun_penalty = SUN_PENALTY if crosses_sun(source, target) else 0.0

    return production_value + owner_bonus - distance_penalty - ship_penalty - sun_penalty


# ============================================================
# CAPA 4: REGLAS DE SEGURIDAD
# ============================================================

def ships_available(planet):
    """
    Naves disponibles para atacar desde `planet`.
    Respeta la reserva mínima defensiva y el límite de fracción máxima.
    """
    reserve = max(MIN_DEFENSE, planet.production * 2)
    available = planet.ships - reserve
    max_send = int(planet.ships * MAX_ATTACK_FRACTION)
    return max(0, min(available, max_send))


def required_ships(target):
    """
    Naves mínimas necesarias para capturar `target`.
    Agrega margen extra si es planeta enemigo.
    """
    base = target.ships + 1
    if target.owner == -1:
        return base
    return base + ENEMY_ATTACK_EXTRA


# ============================================================
# CAPA 5: POLÍTICA DE ACCIONES
# ============================================================

def choose_target(source, candidates, fleets, player):
    """
    Elige el mejor objetivo de `candidates` para lanzar desde `source`.
    Devuelve el planeta objetivo o None si no hay ataque viable.
    """
    available = ships_available(source)
    if available <= 0:
        return None

    best_target = None
    best_score = -1e9

    for target in candidates:
        need = required_ships(target)
        if need > available:
            continue  # No tenemos suficientes naves

        score = target_score(source, target)

        # Penalización leve si hay flotas enemigas apuntando a ese objetivo
        enemy_nearby = [
            f for f in fleets
            if f.owner != player and f.owner != -1
        ]
        if enemy_nearby:
            score -= min(8, len(enemy_nearby) * 2)

        if score > best_score:
            best_score = score
            best_target = target

    return best_target


def agent(obs):
    """
    Función principal del bot. Llamada por Kaggle cada turno.
    Devuelve lista de acciones: [[from_planet_id, angle, num_ships], ...]
    """
    player = get_player(obs)
    planets = get_planets(obs)
    fleets = get_fleets(obs)

    my_planets = [p for p in planets if p.owner == player]
    targets = [p for p in planets if p.owner != player]

    if not my_planets or not targets:
        return []

    # Ordenar planetas propios: primero los de mayor producción y más naves
    my_planets = sorted(my_planets, key=lambda p: (-p.production, -p.ships))

    moves = []
    targeted_ids = set()  # Evitar que dos planetas ataquen el mismo objetivo

    for source in my_planets:
        # Solo considerar objetivos que no estén ya en la mira de otro planeta propio
        candidates = [t for t in targets if t.id not in targeted_ids]
        if not candidates:
            break

        target = choose_target(source, candidates, fleets, player)
        if target is None:
            continue

        send_ships = required_ships(target)
        available = ships_available(source)

        if send_ships <= 0 or send_ships > available:
            continue

        angle = angle_between(source, target)
        moves.append([source.id, angle, int(send_ships)])
        targeted_ids.add(target.id)

    return moves
