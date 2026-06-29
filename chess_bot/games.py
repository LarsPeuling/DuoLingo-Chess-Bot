"""Spelmodi: normaal spelen (winnen) en expres verliezen."""

import os
import time
import cv2
import chess

from config import TEMPLATE_FILE_WHITE, TEMPLATE_FILE_BLACK
from screen import capture_board, detect_verder, handle_game_over
from board import detect_color
from recognition import load_templates, calibrate, read_board_visual, validate, try_detect_opponent, get_templates
from engine import get_best_move, click_move, wait_opponent


def play_game(game_number):
    """Speel één game om te winnen."""
    print(f"\n{'='*40}")
    print(f"  GAME {game_number} (WIN)")
    print(f"{'='*40}\n")

    time.sleep(2)
    image = capture_board()
    our_color = detect_color(image)
    template_file = TEMPLATE_FILE_WHITE if our_color == "white" else TEMPLATE_FILE_BLACK

    # Templates laden
    templates = get_templates(our_color)

    time.sleep(2)
    image = capture_board()
    pos = read_board_visual(image, templates, our_color)
    ok, msg = validate(pos)
    if not ok:
        print(f"Scan ongeldig ({msg}): {pos}")
        cv2.imwrite("debug_error.png", image)
        return False

    fen_turn = "w" if our_color == "white" else "b"
    fen = f"{pos} {fen_turn} KQkq - 0 1"
    print(f"Start FEN: {fen}")

    try:
        board = chess.Board(fen)
    except ValueError as e:
        print(f"Ongeldige FEN: {e}")
        return False

    while True:
        if detect_verder():
            handle_game_over()
            return True

        if board.is_game_over():
            print(f"Einde: {board.result()}")
            time.sleep(3)
            if detect_verder():
                handle_game_over()
            return True

        print(f"FEN: {board.fen()}")

        try:
            move = get_best_move(board)
        except Exception as e:
            print(f"Stockfish: {e}")
            time.sleep(2)
            continue

        print(f"Zet: {move}")
        before_move = capture_board()
        click_move(move, our_color)
        board.push(move)

        if board.is_game_over():
            continue

        time.sleep(0.15)
        after_our_move = capture_board()

        print("Wachten op tegenstander...")
        status, after_opponent = wait_opponent(after_our_move)

        if status == "DONE":
            handle_game_over()
            return True
        if status == "TIMEOUT":
            print("Timeout.")
            return False

        max_attempts = 10
        detected = False
        for attempt in range(max_attempts):
            opponent_move = try_detect_opponent(board, after_our_move, after_opponent, templates, our_color)
            if opponent_move:
                board.push(opponent_move)
                print(f"Tegenstander: {opponent_move}\n")
                detected = True
                break
            time.sleep(1.0)
            if detect_verder():
                handle_game_over()
                return True
            after_opponent = capture_board()

        if not detected:
            print("Kon tegenstander-zet niet detecteren.")
            cv2.imwrite("debug_error.png", after_opponent)
            cv2.imwrite("debug_before.png", after_our_move)
            return False


def play_losing_game(game_number, color):
    """Speel een game om expres te verliezen."""
    print(f"\n{'='*40}")
    print(f"  GAME {game_number} (LOSE)")
    print(f"{'='*40}\n")

    time.sleep(2)
    image = capture_board()

    template_file = TEMPLATE_FILE_WHITE if color == "white" else TEMPLATE_FILE_BLACK
    templates = get_templates(color)

    if color == "white":
        board = chess.Board()
        # Fool's mate: f2f3, g2g4
        losing_moves = [chess.Move.from_uci("f2f3"), chess.Move.from_uci("g2g4")]

        for i, move in enumerate(losing_moves):
            print(f"Verlies-zet {i+1}: {move}")
            click_move(move, color)
            board.push(move)

            if board.is_game_over():
                break

            time.sleep(0.15)
            after = capture_board()
            print("Wachten op tegenstander...")
            status, after_opp = wait_opponent(after)

            if status == "DONE":
                handle_game_over()
                return True
            if status == "TIMEOUT":
                return False

            opp_move = _detect_with_retry(board, after, after_opp, templates, color)
            if opp_move:
                board.push(opp_move)
                print(f"Tegenstander: {opp_move}")
            else:
                return False

        # Fool's mate niet gelukt? Ga koning bewegen
        if not board.is_game_over():
            print("Fool's mate niet gelukt, koning bewegen...")
            return _play_king_only(board, templates, color, chess.WHITE)

    else:
        # Als zwart: lees bord, beweeg alleen de koning
        pos = read_board_visual(image, templates, color)
        ok, _ = validate(pos)
        if not ok:
            return False
        board = chess.Board(f"{pos} b KQkq - 0 1")
        return _play_king_only(board, templates, color, chess.BLACK)

    # Check of spel klaar is
    time.sleep(3)
    if detect_verder():
        handle_game_over()
        return True
    return True


def _play_king_only(board, templates, color, our_side):
    """Beweeg alleen de koning tot we verliezen."""
    while True:
        if detect_verder():
            handle_game_over()
            return True
        if board.is_game_over():
            time.sleep(3)
            if detect_verder():
                handle_game_over()
            return True

        king_sq = board.king(our_side)
        king_moves = [m for m in board.legal_moves if m.from_square == king_sq]
        move = king_moves[0] if king_moves else list(board.legal_moves)[0]

        print(f"Koning-zet: {move}")
        click_move(move, color)
        board.push(move)

        if board.is_game_over():
            continue

        time.sleep(0.15)
        after = capture_board()
        print("Wachten op tegenstander...")
        status, after_opp = wait_opponent(after)

        if status == "DONE":
            handle_game_over()
            return True
        if status == "TIMEOUT":
            return False

        opp_move = _detect_with_retry(board, after, after_opp, templates, color)
        if opp_move:
            board.push(opp_move)
            print(f"Tegenstander: {opp_move}\n")
        else:
            return False


def _detect_with_retry(board, before, after, templates, color):
    """Probeer tegenstander-zet te detecteren met 1 retry."""
    move = try_detect_opponent(board, before, after, templates, color)
    if move:
        return move
    time.sleep(1)
    after = capture_board()
    return try_detect_opponent(board, before, after, templates, color)