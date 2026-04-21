# 🧮 04 — Estrategia General

## 🎯 Principios fundamentales

Estos principios deben guiar cada versión del bot, independientemente de su complejidad:

1. **No te suicides**: nunca vacíes un planeta por completo. Siempre deja una reserva defensiva.
2. **Expande con razón**: prioriza planetas de alta producción. No ataques lo más cercano, ataca lo más rentable.
3. **Respeta el sol**: las flotas que cruzan el sol se pierden. Un ataque mal apuntado puede destruir toda una fuerza.
4. **El tiempo importa**: un planeta lejano puede que ya haya cambiado de dueño cuando tu flota llegue.
5. **Naves en tránsito cuentan**: las flotas en vuelo siguen sumando al puntaje final.
6. **Los cometas son trampas y oportunidades**: tienen producción pero desaparecen. Evalúa si vale la pena antes de invertir.

## 📊 Fases del juego

### Fase temprana (turnos 0–100)
- Expansión agresiva a neutrales cercanos y de alta producción
- Consolidar control del cuadrante propio
- Evitar conflictos directos con enemigos si hay neutrales disponibles

### Fase media (turnos 100–350)
- Atacar planetas enemigos débiles o expuestos
- Aprovechar cometas si el camino es seguro
- Reforzar planetas amenazados con flotas enemigas en curso

### Fase final (turnos 350–500)
- Maximizar naves totales (planetas + flotas en vuelo)
- Lanzar flotas hacia objetivos aunque no alcancen a llegar: suman al puntaje
- Defender lo que ya se tiene más que expandir

## 🧐 Preguntas estratégicas por responder en cada versión

- ¿Cómo predecir la posición futura de planetas orbitales?
- ¿Cómo calcular el ETA (tiempo de llegada) de una flota propia o enemiga?
- ¿Cuándo vale la pena atacar un planeta enemigo vs. esperar refuerzos?
- ¿Cómo coordinar ataques desde múltiples planetas sobre el mismo objetivo?
- ¿Cómo defender proactivamente antes de que llegue la amenaza?
- ¿Cuándo usar cometas y cuándo ignorarlos?

## 📚 Referencias de estrategia similares

- [Halite III](https://halite.io/) — estrategia de control de mapa con flotas
- [Lux AI Season 3](https://github.com/Lux-AI-Challenge/Lux-Design-S3) — kit de referencia
- Planet Wars (Google AI Challenge) — precursor directo de Orbit Wars

## 🗨️ Glosario rápido

| Término | Significado |
|--------|-------------|
| ETA | Tiempo estimado de llegada de una flota |
| Guarnición | Naves en un planeta (`ships`) |
| Producción | Naves generadas por turno en un planeta propio |
| Neutral | Planeta sin dueño (`owner == -1`) |
| Flota propia | Flota en vuelo con `owner == player` |
| Comet | Planeta temporal en órbita elíptica |
