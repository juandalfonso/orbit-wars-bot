# ⚙️ 02 — Mecánicas del Juego

## 🎮 Tablero

- Espacio 2D continuo de **100x100** unidades, origen arriba-izquierda
- **Sol** centrado en (50, 50) con radio 10. Las flotas que lo crucen son destruidas
- Simetría de 4 cuadrantes: los planetas se colocan en grupos simétricos `(x,y)`, `(100-x,y)`, `(x,100-y)`, `(100-x,100-y)`

## 🪐 Planetas

Cada planeta: `[id, owner, x, y, radius, ships, production]`

| Campo | Descripción |
|-------|-------------|
| `owner` | ID del dueño (0-3) o -1 si es neutral |
| `radius` | Calculado como `1 + ln(production)` |
| `production` | Entero 1-5. Naves generadas por turno cuando es propio |
| `ships` | Guarnición actual. Inicia entre 5 y 99 |

### Tipos de planeta
- **Orbitales**: radio orbital + radio planeta < 50. Rotan alrededor del sol a velocidad angular constante (0.025–0.05 rad/turno)
- **Estáticos**: más lejos del centro, no rotan
- El mapa tiene 20-40 planetas (5-10 grupos simétricos). Al menos 3 grupos estáticos y 1 orbital garantizados

### Planeta base
Un grupo simétrico es el punto de inicio. En 2 jugadores: cuadrantes diagonales (Q1 y Q4). En 4 jugadores: uno por cuadrante. Inician con 10 naves.

## 🚀 Flotas

Cada flota: `[id, owner, x, y, angle, from_planet_id, ships]`

### Velocidad
```
speed = 1.0 + (maxSpeed - 1.0) * (log(ships) / log(1000))^1.5
```
- 1 nave → 1.0 unidades/turno
- ~500 naves → ~5.0 unidades/turno
- ~1000 naves → 6.0 (máximo)

### Movimiento y eliminación
Las flotas se eliminan si:
- Salen del tablero (100x100)
- Cruzan el sol (detección continua por segmento, no solo el punto final)
- Colisionan con cualquier planeta (dispara combate)

## ☄️ Cometas

- Planetas temporales en órbitas elípticas muy alargadas
- Aparecen en grupos de 4 (uno por cuadrante) en turnos 50, 150, 250, 350 y 450
- Radio fijo: 1.0 | Producción: 1 nave/turno cuando son propios
- Al salir del tablero, desaparecen junto con las naves garnisonadas
- Identificarlos con `comet_planet_ids` en la observación
- Sus trayectorias futuras están disponibles en `comets[].paths`

## 🔄 Orden de turno

1. Expiración de cometas
2. Creación de nuevos cometas
3. Lanzamiento de flotas (tus acciones)
4. Producción de naves en planetas propios
5. Movimiento de flotas + detección de colisiones
6. Rotación de planetas y avance de cometas
7. Resolución de combates

> 👀 **Clave**: la producción ocurre ANTES del movimiento. El combate ocurre DESPUÉS de la rotación.

## ⚔️ Combate

Cuando una o más flotas llegan a un planeta:
1. Se agrupan por dueño y se suman las naves del mismo dueño
2. La fuerza mayor combate con la segunda mayor; sobrevive la diferencia
3. Si hay sobreviviente atacante:
   - Mismo dueño que el planeta → se suman a la guarnición
   - Dueño diferente → combate contra la guarnición. Si el atacante gana, el planeta cambia de dueño
4. Si dos fuerzas empatan → ambas se destruyen, no hay sobrevivientes

## 🏁 Fin del juego

- Se acaban los 500 turnos, O
- Solo queda un jugador con planetas o flotas

**Puntaje final** = naves en planetas propios + naves en flotas propias
