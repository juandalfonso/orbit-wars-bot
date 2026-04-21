# 📓 05 — Bitácora de Experimentos

Registro cronológico de versiones, cambios, hipótesis y resultados.

---

## 📌 Cómo usar esta bitácora

Cada entrada debe tener:
- **Versión** y fecha
- **Idea / hipótesis**: qué se intentó mejorar y por qué
- **Cambios principales**: qué se modificó en el código
- **Resultado**: victorias en pruebas locales, posición en leaderboard, observaciones de replays
- **Conclusión**: ¿funcionó? ¿qué aprendimos? ¿qué sigue?

---

## ✅ v1 — Base sólida (21 abril 2026)

**Hipótesis**: El bot base solo mira cercanía. Si priorizamos producción y dejamos reserva defensiva, evitaremos suicidios y capturaremos planetas más rentables.

**Cambios principales**:
- Función `target_score()`: pondera producción, distancia, costo de captura y riesgo de trayectoria por el sol
- `ships_available()`: reserva mínima defensiva configurable (`MIN_DEFENSE = 8`)
- Prefiere neutrales sobre enemigos (bonus extra)
- Estructura modular con helpers separados (`geometry.py`, `scoring.py`)
- Arquitectura de 5 capas: parseo, geometría, evaluación, seguridad, política de acciones

**Resultado**: pendiente (primera submission)

**Conclusión**: Base limpia para iterar. Próximos pasos: probar contra `random`, revisar replays.

---

## 🔜 v2 — Predicción de órbitas (próxima)

**Hipótesis**: el bot v1 apunta a donde está el planeta ahora, no a donde estará cuando la flota llegue. Esto causa misses en planetas orbitales.

**Cambios planeados**:
- Calcular ETA de la flota: `ETA = distancia / velocidad`
- Predecir posición futura del planeta orbital: `theta_futuro = theta_actual + angular_velocity * ETA`
- Apuntar a la posición predicha, no a la actual

---

## 📅 Plantilla para nuevas entradas

```
## [En progreso / ✅] vX — Nombre descriptivo (fecha)

**Hipótesis**: ...

**Cambios principales**:
- ...

**Resultado**: ...

**Conclusión**: ...
```
