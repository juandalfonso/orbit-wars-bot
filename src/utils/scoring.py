"""
scoring.py — Funciones de puntuación de objetivos
===================================================
Funciones para evaluar y comparar objetivos potenciales.
Diseñadas para ser fácilmente ajustables en cada iteración.
"""

from src.utils.geometry import dist, crosses_sun

# Pesos configurables
WEIGHT_PRODUCTION = 12.0
WEIGHT_DISTANCE = 1.6
WEIGHT_SHIPS = 1.1
BONUS_NEUTRAL = 18.0
BONUS_ENEMY = 8.0
SUN_PENALTY = 25.0

MIN_DEFENSE = 8
MAX_ATTACK_FRACTION = 0.6
ENEMY_ATTACK_EXTRA = 6


def ships_available(planet):
    """
    Naves disponibles para atacar desde `planet`.
    Respeta reserva mínima defensiva y límite de fracción máxima.
    """
    reserve = max(MIN_DEFENSE, planet.production * 2)
    available = planet.ships - reserve
    max_send = int(planet.ships * MAX_ATTACK_FRACTION)
    return max(0, min(available, max_send))


def required_ships(target):
    """
    Naves mínimas necesarias para capturar `target`.
    Agrega margen si es planeta enemigo.
    """
    base = target.ships + 1
    if target.owner == -1:
        return base
    return base + ENEMY_ATTACK_EXTRA


def target_score(source, target):
    """
    Puntaú la calidad de atacar `target` desde `source`.
    Mayor score = mejor objetivo.
    """
    d = dist(source, target)
    need = required_ships(target)
    if need <= 0:
        return -1e9

    owner_bonus = BONUS_NEUTRAL if target.owner == -1 else BONUS_ENEMY
    production_value = target.production * WEIGHT_PRODUCTION
    distance_penalty = d * WEIGHT_DISTANCE
    ship_penalty = need * WEIGHT_SHIPS
    sun_penalty = SUN_PENALTY if crosses_sun(source, target) else 0.0

    return production_value + owner_bonus - distance_penalty - ship_penalty - sun_penalty


def rank_targets(source, targets, available_ships):
    """
    Devuelve la lista de objetivos ordenados por score descendente,
    filtrados por los que se pueden pagar con `available_ships`.
    """
    affordable = [
        (t, target_score(source, t))
        for t in targets
        if required_ships(t) <= available_ships
    ]
    affordable.sort(key=lambda x: -x[1])
    return [t for t, _ in affordable]
