"""
Duolingo Chess Bot — Main entry point.

Dagelijks schema:
  Fase 1: 50 games verliezen (500xp)
  Fase 2: 30 games winnen (~2550xp)
  Totaal: ~3050xp
"""

import pyautogui
import time

from config import SCREEN_W, SCREEN_H, SCALE_X, SCALE_Y, BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT, MULTI_MONITOR, LOSE_TARGET, WIN_TARGET
from screen import capture_board, detect_verder, navigate_to_game, handle_game_over
from board import detect_color
from overlay import GameOverlay
from counter import load_daily_counter, save_daily_counter, print_status, is_done
from games import play_game, play_losing_game


def main():
    mode = "laptop" if not MULTI_MONITOR else "extern"
    print(f"=== DUOLINGO CHESS BOT ({mode}) ===")
    print(f"Resolutie: {SCREEN_W}x{SCREEN_H}, schaal: {SCALE_X:.2f}x{SCALE_Y:.2f}")
    print(f"Bord: ({BOARD_X},{BOARD_Y}) {BOARD_WIDTH}x{BOARD_HEIGHT}\n")

    pyautogui.FAILSAFE = True
    print("Noodstop: muis naar linkerbovenhoek.\n")

    # Dagelijkse voortgang
    counter = load_daily_counter()
    print(f"Datum: {counter['date']}")
    print_status(counter)

    if is_done(counter):
        print("\nDagelijks doel al bereikt!")
        return

    losses_left = max(0, LOSE_TARGET - counter['losses'])
    wins_left = max(0, WIN_TARGET - counter['wins'])
    total_left = losses_left + wins_left
    total_target = LOSE_TARGET + WIN_TARGET

    print(f"\nNog te doen: {losses_left}L + {wins_left}W = {total_left} games")

    session_limit = input(f"Hoeveel games deze sessie? (Enter = alle {total_left}): ").strip()
    session_limit = int(session_limit) if session_limit else total_left

    input("Druk Enter om te beginnen...\n")

    input("Druk Enter om te beginnen...\n")

    overlay = GameOverlay()

    session_played = 0
    try:
        while not is_done(counter) and session_played < session_limit:
            counter = load_daily_counter()
            losses_left = max(0, LOSE_TARGET - counter['losses'])
            wins_left = max(0, WIN_TARGET - counter['wins'])

            # Bepaal modus
            if losses_left > 0:
                mode = "lose"
                phase = f"Verliezen {counter['losses']}/{LOSE_TARGET}"
            elif wins_left > 0:
                mode = "win"
                phase = f"Winnen {counter['wins']}/{WIN_TARGET}"
            else:
                break

            overlay.update(counter['total'] + 1, total_target, phase)

            # Navigeer naar nieuw spel
            if not navigate_to_game():
                print("Navigatie mislukt, opnieuw...")
                time.sleep(3)
                if not navigate_to_game():
                    print("Tweede poging mislukt. Stop.")
                    break

            # Detecteer kleur
            time.sleep(2)
            image = capture_board()
            our_color = detect_color(image)

            # Speel
            if mode == "lose":
                overlay.update(counter['total'] + 1, total_target,
                               f"Verliezen {counter['losses']+1}/{LOSE_TARGET}")
                success = play_losing_game(counter['total'] + 1, our_color)
                if success:
                    counter['losses'] += 1
            else:
                overlay.update(counter['total'] + 1, total_target,
                               f"Winnen {counter['wins']+1}/{WIN_TARGET}")
                success = play_game(counter['total'] + 1)
                if success:
                    counter['wins'] += 1

            counter['total'] += 1
            save_daily_counter(counter)
            session_played += 1

            print(f"\n--- Voortgang ---")
            print_status(counter)
            print()

            time.sleep(3)

    except KeyboardInterrupt:
        print("\n\nGestopt door gebruiker.")
    except pyautogui.FailSafeException:
        print("\n\nNoodstop.")
    finally:
        overlay.close()

    counter = load_daily_counter()
    print(f"\n=== KLAAR ===")
    print_status(counter)


if __name__ == "__main__":
    main()