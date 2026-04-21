"""
smoke_test.py — Test rápido local del bot
==========================================
Corre una partida de prueba entre el bot actual y el agente random.
Usarlo antes de hacer cualquier submission para verificar que el bot
no explota con errores.

Uso:
  python src/local_tests/smoke_test.py
  python src/local_tests/smoke_test.py --bot v1
  python src/local_tests/smoke_test.py --games 5
"""

import argparse
import importlib.util
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from kaggle_environments import make


def load_agent(bot_name="v1"):
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "bots",
        f"{bot_name}_main.py"
    )
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el bot: {path}")
    spec = importlib.util.spec_from_file_location("agent_module", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent


def run_game(agent_fn, opponent="random", debug=False):
    env = make("orbit_wars", debug=debug)
    env.run([agent_fn, opponent])
    final = env.steps[-1]
    results = [(i, s.reward, s.status) for i, s in enumerate(final)]
    return results


def main():
    parser = argparse.ArgumentParser(description="Smoke test para bot de Orbit Wars")
    parser.add_argument("--bot", default="v1", help="Versión del bot (ej: v1, v2)")
    parser.add_argument("--games", type=int, default=3, help="Número de partidas")
    parser.add_argument("--debug", action="store_true", help="Activar modo debug")
    args = parser.parse_args()

    print(f"\n🚀 Cargando bot: {args.bot}")
    try:
        agent = load_agent(args.bot)
    except Exception as e:
        print(f"❌ Error cargando bot: {e}")
        sys.exit(1)

    wins = 0
    print(f"🎮 Corriendo {args.games} partidas contra 'random'...\n")

    for i in range(args.games):
        try:
            results = run_game(agent, debug=args.debug)
            player_result = results[0]
            opponent_result = results[1]
            won = player_result[1] is not None and (
                opponent_result[1] is None or
                player_result[1] > opponent_result[1]
            )
            status = "✅ GANA" if won else "❌ PIERDE"
            if won:
                wins += 1
            print(f"  Partida {i+1}: {status} | "
                  f"Bot: reward={player_result[1]:.0f if player_result[1] else 'N/A'} status={player_result[2]} | "
                  f"Random: reward={opponent_result[1]:.0f if opponent_result[1] else 'N/A'} status={opponent_result[2]}")
        except Exception as e:
            print(f"  Partida {i+1}: ⚠️ ERROR — {e}")

    print(f"\n📊 Resultado: {wins}/{args.games} victorias ({wins/args.games*100:.0f}%)")
    print("✔️ Bot validado. Listo para submission.\n" if wins > 0 else "⚠️ Revisa el bot antes de enviar.\n")


if __name__ == "__main__":
    main()
