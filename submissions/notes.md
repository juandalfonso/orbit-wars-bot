# 📤 Registro de Submissions

Registro de cada submission oficial a Kaggle con su ID, versión y observaciones.

---

## Formato

| Fecha | Versión | Submission ID | Mensaje | Resultado / Observaciones |
|-------|---------|--------------|---------|---------------------------|
| — | — | — | — | Primera submission pendiente |

---

## 💡 Comandos útiles

```bash
# Ver todas tus submissions
kaggle competitions submissions orbit-wars

# Ver episodios de una submission
kaggle competitions episodes <SUBMISSION_ID>

# Descargar replay de un episodio
kaggle competitions replay <EPISODE_ID> -p ./replays

# Descargar logs del bot (agente 0)
kaggle competitions logs <EPISODE_ID> 0 -p ./logs

# Ver leaderboard
kaggle competitions leaderboard orbit-wars -s
```

---

## 📌 Notas generales

- Aceptar reglas antes de cualquier submission: https://www.kaggle.com/competitions/orbit-wars
- Verificar inscripción: `kaggle competitions list --group entered`
- Para submissions multi-archivo: empacar con `tar -czf submission.tar.gz main.py utils/`
