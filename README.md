# 🚀 Orbit Wars Bot — juandalfonso

Bot para la competencia [Orbit Wars en Kaggle](https://www.kaggle.com/competitions/orbit-wars).
Desarrollo iterativo: cada versión mejora sobre la anterior con diagnóstico de replays y torneos locales.

---

## 📊 Historial de submissions

| # | Versión | Fecha | Score Kaggle | vs Random | vs v1 | Nota |
|---|---------|-------|-------------|-----------|-------|------|
| 1 | v5.1 | 23 abr 2026 | 407.6 | 9W/1L | 6W/4L | Primera submission |
| 2 | v6 | 24 abr 2026 | 338.9 | — | 9W/1L | Defensa reactiva |
| 3 | v7 | 25 abr 2026 | 437.5 | 10W/0L | 5W/5L | Sin ataques duplicados |
| 4 | v8 | 25 abr 2026 | 363.5 | 10W/0L | 6W/4L | Expansión greedy + consolidación |
| 5 | v9 | 28 abr 2026 | 410.6 | 10W/0L | 3W/7L | Multi-jugador inteligente |
| 6 | v11 | 28 abr 2026 | 431.1 | 10W/0L | 7W/3L | Modo cierre agresivo |

---

## 🤖 Versiones del bot

### v1 — Base Sólida
**Archivo:** `src/bots/v1_main.py`

- Arquitectura simple: cada planeta busca el mejor objetivo y dispara cada turno
- Penaliza trayectorias que cruzan el sol
- Prioriza planetas neutrales sobre enemigos
- Reserva defensiva fija (`MIN_DEFENSE=8`)
- Sin predicción orbital — apunta a posición actual del objetivo

**Resultado local:** línea base de referencia

---

### v5.1 — Parámetros Adaptativos + Predicción Orbital
**Archivo:** `src/bots/v5_1_main.py`

**Mejoras sobre v1:**
1. **Predicción orbital** (`aim_angle`): calcula posición futura con 6 iteraciones convergentes
2. **Parámetros adaptativos por fase:** arranque agresivo → expansión → consolidación
3. **Fallback de puntería:** si trayectoria predicha cruza el sol, intenta directo
4. **Bonus planetas lentos:** incentivo para planetas con órbita lenta (dist_sol ≤ 40)

**Resultado local:** vs random 9W/1L | vs v1 6W/4L
**Score Kaggle:** 407.6 (score final)

---

### v6 — Defensa Reactiva
**Archivo:** `src/bots/v6_main.py`

**Mejoras sobre v5.1:**
1. Detección de flotas enemigas entrantes
2. Refuerzo dinámico de planetas amenazados

**Score Kaggle:** 338.9 (score final)

---

### v7 — Sin Ataques Duplicados
**Archivo:** `src/bots/v7_main.py`

**Mejoras sobre v6:**
1. `targeted_ids`: cada objetivo solo recibe un atacante por turno
2. Distribución más eficiente de flotas

**Resultado local:** vs random 10W/0L | vs v1 5W/5L
**Score Kaggle:** 437.5 (score final)

---

### v8 — Expansión Greedy + Consolidación
**Archivo:** `src/bots/v8_main.py`

**Mejoras sobre v7:**
1. `expansion_score`: scoring dedicado para fase de expansión
2. `consolidation_score`: scoring dedicado para fase de consolidación
3. Transición automática entre fases según número de planetas

**Resultado local:** vs random 10W/0L | vs v1 6W/4L
**Diagnóstico turno a turno:** domina desde turno 80, elimina v1 en turno 140
**Score Kaggle:** 363.5 (score final)

---

### v9 — Multi-jugador Inteligente
**Archivo:** `src/bots/v9_main.py`

**Mejoras sobre v8:**
1. **FIX 1** — `required_ships` sin buffer en neutrales (expansión más barata)
2. **FIX 2** — `get_weakest_enemy`: bonus +15 por atacar al rival con menos planetas
3. **FIX 3** — `get_params` proporcional al número de enemigos (3+ → ultra agresivo)
4. `EXPANSION_THRESHOLD`: 10 → 6 (más agresivos en fase temprana)

**Resultado local:** vs random 10W/0L | vs v1 3W/7L
**Observación:** fixes de multi-jugador sobrecompensaron en 1v1
**Score Kaggle:** 410.6 (~30 partidas)

---

### v11 — Modo Cierre Agresivo ⭐ ACTIVA
**Archivo:** `src/bots/v11_main.py`

**Mejoras sobre v10:**
1. **FIX A** — `get_expansion_threshold` adaptativo: 1v1=8, 2v=6, 3v+=4
2. **FIX B** — `get_params` diferenciado por modo: 1v1 / 2 jugadores / 3+ jugadores
3. **FIX C** — `required_ships` sin buffer en neutrales (velocidad de expansión)
4. **FIX D** — `THREAT_RADIUS=8.0` defensa reactiva calibrada (antes 15.0)
5. **MODO CIERRE** — cuando tenemos 4x más planetas que el enemigo:
   - `min_defense=1, max_frac=0.95`
   - Todos los planetas pueden atacar el mismo objetivo simultáneamente
   - Cierra partidas en ~20 turnos en vez de 70

**Resultado local:** vs random 10W/0L | vs v1 7W/3L ✅ mejor head-to-head
**Diagnóstico turno a turno:** domina desde turno 60, modo cierre activo desde turno ~120
**Score Kaggle:** 431.1 (~30 partidas, en acumulación)

---

## 🗺️ Roadmap — próximas mejoras

| Prioridad | Mejora | Impacto esperado |
|-----------|--------|------------------|
| Alta | CLOSE_RATIO 4x → 3x (cierre más temprano) | Reducir las 3 derrotas restantes vs v1 |
| Alta | Aceleración expansión turnos 0-30 | Ventaja temprana en todos los modos |
| Media | Validación en partidas de 4 jugadores | Confirmar mejora multi-jugador |
| Media | Estimación ETA flotas enemigas | Mejor timing defensivo |
| Baja | Aprendizaje por refuerzo (RL) | Salto de score a largo plazo |

---

## 🏗️ Estructura del proyecto

```
orbit-wars-bot/
├── src/
│   └── bots/
│       ├── v1_main.py         # Versión 1 — base
│       ├── v5_1_main.py       # Versión 5.1
│       ├── v6_main.py         # Versión 6
│       ├── v7_main.py         # Versión 7
│       ├── v8_main.py         # Versión 8
│       ├── v9_main.py         # Versión 9
│       ├── v11_main.py        # Versión 11 — activa en Kaggle ⭐
│       └── current_main.py    # Apunta a la versión activa
├── README.md
```

---

## 🔧 Desarrollo

Todo el desarrollo se realiza en Google Colab.
Cada versión se prueba con:
1. **Torneo vs random** (10 partidas) — mide robustez general
2. **Head-to-head vs versión anterior** (10 partidas) — mide mejora real
3. **Diagnóstico de planetas/naves por turno** — detecta bloqueos o pérdidas de territorio
