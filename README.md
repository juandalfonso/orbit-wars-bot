# 🛸 Orbit Wars Bot

> Bot competitivo para la competencia [Orbit Wars en Kaggle](https://www.kaggle.com/competitions/orbit-wars) — construido de forma iterativa con documentación, experimentos y versiones trazables.

---

## 🗂 Estructura del repositorio

```
orbit-wars-bot/
├── README.md                      ← Este archivo
├── docs/
│   ├── 01_competencia.md          ← Descripción de la competencia
│   ├── 02_mecanicas.md            ← Mecánicas del juego en detalle
│   ├── 03_obs_y_acciones.md       ← Formato de observación y acciones
│   ├── 04_estrategia_general.md   ← Ideas y principios estratégicos
│   └── 05_bitacora.md             ← Bitácora de experimentos y versiones
├── src/
│   ├── bots/
│   │   ├── v1_main.py             ← Bot v1 (base sólida)
│   │   └── current_main.py       ← Versión activa (enlace simbólico)
│   └── utils/
│       ├── geometry.py            ← Utilidades geométricas
│       └── scoring.py             ← Funciones de puntuación de objetivos
├── submissions/
│   └── notes.md                   ← Registro de submissions a Kaggle
├── notebooks/
│   └── colab_lab.ipynb            ← Notebook de laboratorio para Colab
└── logs/                          ← Logs y replays descargados de Kaggle
```

---

## 🚀 Inicio rápido

### Opción A — Google Colab
1. Abre `notebooks/colab_lab.ipynb` en Colab
2. Ejecuta todas las celdas en orden
3. El notebook instala dependencias, carga el bot y corre partidas de prueba

### Opción B — Local
```bash
git clone https://github.com/juandalfonso/orbit-wars-bot.git
cd orbit-wars-bot
pip install kaggle-environments
python -c "
from kaggle_environments import make
import importlib.util, sys
spec = importlib.util.spec_from_file_location('agent_module', 'src/bots/v1_main.py')
mod = importlib.util.load_from_spec(spec)
spec.loader.exec_module(mod)
env = make('orbit_wars', debug=True)
env.run([mod.agent, 'random'])
print([(i, s.reward) for i, s in enumerate(env.steps[-1])])
"
```

---

## 📌 Versiones del bot

| Versión | Estado | Descripción |
|---------|--------|-------------|
| v1 | ✅ Activa | Expansión segura, scoring por producción, reserva defensiva, penalización sol |
| v2 | 🔜 Próxima | Predicción de órbitas, estimación de llegada de flotas |
| v3 | 📅 Planeada | Defensa reactiva, refuerzos entre planetas |
| v4 | 📅 Planeada | Ataques coordinados multi-planeta |
| v5 | 📅 Planeada | Simulación multi-turno, tuning sistemático |

---

## 🏆 Objetivo

Ganar o quedar en el top del leaderboard de [Orbit Wars 2026](https://www.kaggle.com/competitions/orbit-wars).

---

## 📚 Documentación

Ver la carpeta [`docs/`](./docs/) para mecánicas, estrategia y bitácora de experimentos.
