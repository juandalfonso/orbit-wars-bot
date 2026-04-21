# 📶 03 — Observación y Acciones

## 📥 Qué recibe el bot cada turno

La función `agent(obs)` recibe un objeto `obs` con los siguientes campos:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `player` | `int` | Tu ID de jugador (0-3) |
| `planets` | `list` | Todos los planetas incluyendo cometas |
| `fleets` | `list` | Todas las flotas activas |
| `angular_velocity` | `float` | Velocidad de rotación de planetas interiores (rad/turno) |
| `initial_planets` | `list` | Posiciones de planetas al inicio del juego |
| `comets` | `list` | Datos de grupos de cometas activos con trayectorias |
| `comet_planet_ids` | `list[int]` | IDs de planetas que son cometas |
| `remainingOverageTime` | `float` | Tiempo de exceso restante (segundos) |

## 🪐 Estructura de planeta

```python
[id, owner, x, y, radius, ships, production]
# owner: -1 neutral, 0-3 jugador
```

Usando named tuple:
```python
from kaggle_environments.envs.orbit_wars.orbit_wars import Planet
planet = Planet(*raw)
planet.id, planet.owner, planet.x, planet.y, planet.ships, planet.production
```

## 🚀 Estructura de flota

```python
[id, owner, x, y, angle, from_planet_id, ships]
```

Usando named tuple:
```python
from kaggle_environments.envs.orbit_wars.orbit_wars import Fleet
fleet = Fleet(*raw)
fleet.owner, fleet.angle, fleet.ships, fleet.from_planet_id
```

## 📤 Qué devuelve el bot

Una lista de acciones. Cada acción es:
```python
[from_planet_id, direction_angle, num_ships]
```

| Campo | Descripción |
|-------|-------------|
| `from_planet_id` | ID de un planeta que controlas |
| `direction_angle` | Ángulo en radianes (0 = derecha, π/2 = abajo) |
| `num_ships` | Entero de naves a enviar (no puede superar la guarnición) |

Si no quieres hacer nada, devuelve `[]`.

## 📌 Restricciones de acción

- Solo puedes lanzar desde planetas que controlas
- No puedes enviar más naves de las que tiene el planeta en ese turno
- Puedes lanzar múltiples flotas desde distintos planetas en el mismo turno
- Puedes lanzar múltiples flotas desde el mismo planeta en el mismo turno
- **Tiempo límite por turno**: 1 segundo (`actTimeout`). Tu bot debe responder rápido

## 📊 Parámetros del juego

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `episodeSteps` | 500 | Turnos máximos |
| `actTimeout` | 1 | Segundos por turno |
| `shipSpeed` | 6.0 | Velocidad máxima de flota |
| `sunRadius` | 10.0 | Radio del sol |
| `boardSize` | 100.0 | Tamaño del tablero |
| `cometSpeed` | 4.0 | Velocidad de cometas |

## 💡 Ejemplo mínimo de agente válido

```python
def agent(obs):
    # Leer estado
    player = obs.get('player', 0) if isinstance(obs, dict) else obs.player
    planets = obs.get('planets', []) if isinstance(obs, dict) else obs.planets
    # No hacer nada
    return []
```
