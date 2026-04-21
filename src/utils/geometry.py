"""
geometry.py — Utilidades geométricas para Orbit Wars
=====================================================
Funciones reutilizables de geometría 2D para el bot.
Pueden importarse desde cualquier versión del bot.
"""

import math

SUN_X = 50.0
SUN_Y = 50.0
SUN_RADIUS = 10.0
BOARD_SIZE = 100.0


def euclidean_dist(x1, y1, x2, y2):
    """Distancia euclidiana entre dos puntos."""
    return math.hypot(x1 - x2, y1 - y2)


def dist(a, b):
    """Distancia entre dos objetos con campos .x y .y."""
    return math.hypot(a.x - b.x, a.y - b.y)


def angle_between(a, b):
    """Ángulo en radianes desde el objeto a hacia el objeto b."""
    return math.atan2(b.y - a.y, b.x - a.x)


def point_to_segment_dist(px, py, ax, ay, bx, by):
    """
    Distancia mínima desde punto (px, py) al segmento (ax,ay)-(bx,by).
    """
    abx, aby = bx - ax, by - ay
    apx, apy = px - ax, py - ay
    ab2 = abx * abx + aby * aby
    if ab2 == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, (apx * abx + apy * aby) / ab2))
    cx, cy = ax + t * abx, ay + t * aby
    return math.hypot(px - cx, py - cy)


def crosses_sun(source, target, margin=0.5):
    """
    True si la trayectoria directa de source a target pasa
    a menos de (SUN_RADIUS + margin) del centro del sol.
    """
    d = point_to_segment_dist(
        SUN_X, SUN_Y,
        source.x, source.y,
        target.x, target.y
    )
    return d <= SUN_RADIUS + margin


def fleet_speed(num_ships, max_speed=6.0):
    """
    Velocidad de una flota según su tamaño.
    Fórmula: speed = 1.0 + (maxSpeed - 1.0) * (log(ships) / log(1000))^1.5
    """
    if num_ships <= 1:
        return 1.0
    speed = 1.0 + (max_speed - 1.0) * (math.log(num_ships) / math.log(1000)) ** 1.5
    return min(speed, max_speed)


def eta(source, target, num_ships, max_speed=6.0):
    """
    Estimación de turnos que tarda una flota de `num_ships` naves
    en llegar de `source` a `target`.
    """
    d = dist(source, target)
    speed = fleet_speed(num_ships, max_speed)
    return d / speed if speed > 0 else float('inf')


def predict_orbital_position(planet, angular_velocity, turns_ahead):
    """
    Predice la posición de un planeta orbital en `turns_ahead` turnos.
    Usa rotación alrededor del centro (50, 50).
    """
    dx = planet.x - SUN_X
    dy = planet.y - SUN_Y
    current_angle = math.atan2(dy, dx)
    orbital_radius = math.hypot(dx, dy)
    future_angle = current_angle + angular_velocity * turns_ahead
    return (
        SUN_X + orbital_radius * math.cos(future_angle),
        SUN_Y + orbital_radius * math.sin(future_angle)
    )
