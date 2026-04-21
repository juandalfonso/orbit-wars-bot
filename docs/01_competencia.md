# 🏆 01 — Competencia Orbit Wars

## 📌 ¿Qué es?

Orbit Wars es una competencia de tipo **Game AI / Simulación** en Kaggle, lanzada en abril 2026.  
No se trata de predecir un valor con datos tabulares. El reto es **programar un bot** que juegue un juego de estrategia en tiempo real contra otros bots.

> Kaggle llama a tu función `agent(obs)` cada turno. Tú devuelves acciones. El motor evalua resultados.

## 🌎 Enlace

https://www.kaggle.com/competitions/orbit-wars

## 📊 Formato

- **Jugadores**: 2 o 4 por partida (todos contra todos)
- **Turnos**: hasta 500 por partida
- **Evaluación**: tus bots juegan automáticamente contra otros y tu score sube o baja en el leaderboard
- **Lenguaje**: Python (kit oficial disponible)

## 🏅 Criterio de victoria

Gana el jugador con más **naves totales** al final del juego (naves en planetas propios + naves en flotas activas), o el último en sobrevivir si los demás son eliminados.

## 📦 Submission

- Archivo `main.py` con función `agent(obs)` en la raíz
- Si usas múltiples archivos: empacar en `submission.tar.gz` con `main.py` en la raíz
- Comandos:

```bash
# Submission simple
kaggle competitions submit orbit-wars -f main.py -m "v1"

# Submission multi-archivo
tar -czf submission.tar.gz main.py utils/geometry.py utils/scoring.py
kaggle competitions submit orbit-wars -f submission.tar.gz -m "v1 multi-file"
```

## 📅 Fechas importantes

- Lanzamiento: abril 2026
- Revisar deadline en: https://www.kaggle.com/competitions/orbit-wars/rules

## ⚠️ Reglas clave

- Debes aceptar las reglas en Kaggle antes de hacer cualquier submission
- Puedes verificar que estás inscrito con: `kaggle competitions list --group entered`
- Límite de submissions diarias: revisar en la página de reglas oficial
