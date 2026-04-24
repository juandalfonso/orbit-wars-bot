# 🚀 Orbit Wars Bot — juandalfonso

Bot para la competencia [Orbit Wars en Kaggle](https://www.kaggle.com/competitions/orbit-wars).
Desarrollo iterativo: cada versión mejora sobre la anterior con diagnóstico de replays y torneos locales.

---

## 📊 Historial de submissions

| # | Versión | Fecha | Score | Win | Loss | Posición | Nota |
|---|---------|-------|-------|-----|------|----------|------|
| 1 | v5.1 | 23 abr 2026 | 564.9 | 1818 | 369 | 734/1161 | Primera submission |

---

## 🤖 Versiones del bot

### v1 — Base Sólida
**Archivo:** `src/bots/v1_main.py`

- Arquitectura simple: cada planeta busca el mejor objetivo y dispara cada turno
- Penaliza trayectorias que cruzan el sol
- Prioriza planetas neutrales sobre enemigos
- Reserva defensiva fija (`MIN_DEFENSE=8`)
- **Sin** predicción orbital — apunta a posición actual del objetivo

**Resultado local:** línea base de referencia

---

### v5.1 — Parámetros Adaptativos + Predicción Orbital ⭐ ACTIVA
**Archivo:** `src/bots/v5_1_main.py`

**Mejoras sobre v1:**
1. **Predicción orbital** (`aim_angle`): calcula la posición futura del objetivo con 6 iteraciones convergentes para apuntar donde estará el planeta, no donde está ahora
2. **Parámetros adaptativos por fase:**
   - 1 planeta → `min_defense=3, max_frac=0.85` (arranque agresivo)
   - 2-3 planetas → `min_defense=5, max_frac=0.75` (expansión)
   - 4+ planetas → `min_defense=8, max_frac=0.60` (consolidación)
3. **Fallback de puntería:** si la trayectoria predicha cruza el sol, intenta apuntar directo antes de descartar el objetivo
4. **Bonus planetas lentos:** incentivo suave de scoring para planetas con órbita lenta (dist_sol ≤ 40)

**Resultado local:**
- vs random: **9W / 1L** (10 partidas)
- vs v1: **6W / 4L** (10 partidas)

**Resultado Kaggle:**
- Score: **564.9** | Win: 1818 | Loss: 369
- Posición: **734 / 1161** | Líder: 2546.4

**Observaciones del replay:**
- ✅ Ninguna nave atravesó el sol
- ⚠️ Disparos desviados observados en ciertos turnos
- ⚠️ Sin defensa reactiva ante flotas enemigas

---

## 🗺️ Roadmap — próximas mejoras

| Prioridad | Mejora | Impacto esperado |
|-----------|--------|------------------|
| Alta | Defensa reactiva ante flotas enemigas entrantes | Reducir losses |
| Alta | Corrección de disparos desviados en replay | Subir Win validation |
| Media | Coordinación de ataque multi-planeta | Tomar objetivos difíciles |
| Media | Estimación de ETA de flotas enemigas | Mejor timing |
| Baja | Aprendizaje por refuerzo (RL) | Salto de score a largo plazo |

---

## 🏗️ Estructura del proyecto

```
orbit-wars-bot/
├── src/
│   └── bots/
│       ├── v1_main.py         # Versión 1 — base sólida
│       ├── v5_1_main.py       # Versión 5.1 — activa en Kaggle
│       └── current_main.py    # Apunta a la versión activa
├── README.md
```

---

## 🔧 Desarrollo

Todo el desarrollo se realiza en Google Colab.
Cada versión se prueba con:
1. **Torneo vs random** (10 partidas) — mide robustez general
2. **Head-to-head vs versión anterior** (10 partidas) — mide mejora real
3. **Replay visual** — diagnóstico de comportamiento turno a turno
4. **Diagnóstico de planetas/naves por turno** — detecta bloqueos o pérdidas de territorio
