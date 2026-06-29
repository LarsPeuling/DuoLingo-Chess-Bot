"""Templates, visuele herkenning en diff-detectie."""

import os
import cv2
import numpy as np
import chess

from config import EMPTY_STD, WHITE_BLACK_P5, SQUARE_DIFF_THRESHOLD, TEMPLATE_FILE_WHITE, TEMPLATE_FILE_BLACK
from board import get_center, get_inner_norm, get_square, screen_to_chess, chess_to_screen


# =========================
# TEMPLATES
# =========================

def build_templates(image, color):
    start = {
        'R': [(0, 0), (7, 0)], 'N': [(1, 0), (6, 0)], 'B': [(2, 0), (5, 0)],
        'Q': [(3, 0)], 'K': [(4, 0)], 'P': [(i, 1) for i in range(8)],
        'r': [(0, 7), (7, 7)], 'n': [(1, 7), (6, 7)], 'b': [(2, 7), (5, 7)],
        'q': [(3, 7)], 'k': [(4, 7)], 'p': [(i, 6) for i in range(8)],
    }
    templates = {}
    for piece, positions in start.items():
        tmps = []
        for col, row in positions:
            f, r = chess_to_screen(col, row, color)
            center = get_center(image, f, r)
            if np.std(cv2.cvtColor(center, cv2.COLOR_BGR2GRAY)) < EMPTY_STD:
                continue
            tmps.append(get_inner_norm(image, f, r))
        if tmps:
            templates[piece] = tmps
    return templates


def save_templates(templates, image, filepath):
    h, w = image.shape[:2]
    d = {"_img_w": np.array([w]), "_img_h": np.array([h])}
    for piece, tmps in templates.items():
        for i, t in enumerate(tmps):
            d[f"{piece}_{i}"] = t
    np.savez(filepath, **d)
    print(f"Templates opgeslagen in {filepath} ({len(templates)} typen, {w}x{h})")


def load_templates(filepath):
    data = np.load(filepath)
    saved_w = int(data["_img_w"][0])
    saved_h = int(data["_img_h"][0])
    templates = {}
    for key in data.files:
        if key.startswith("_"):
            continue
        piece = key.rsplit('_', 1)[0]
        if piece not in templates:
            templates[piece] = []
        templates[piece].append(data[key])
    print(f"Templates geladen uit {filepath} ({len(templates)} typen, {saved_w}x{saved_h})")
    return templates, saved_w, saved_h


def calibrate(color):
    from screen import capture_board
    print(f"\n=== KALIBRATIE ({color.upper()}) ===")
    print(f"Start een nieuw spel als {color} in LIGHT MODE.")
    if color == "black":
        print("(De tegenstander doet automatisch een eerste zet — dat is OK)")
    input("Druk Enter als het bord zichtbaar is...")
    import time
    time.sleep(2)
    image = capture_board()
    print(f"Bordgrootte: {image.shape[1]}x{image.shape[0]}")
    templates = build_templates(image, color)
    filepath = TEMPLATE_FILE_WHITE if color == "white" else TEMPLATE_FILE_BLACK
    save_templates(templates, image, filepath)
    fen = read_board_visual(image, templates, color)
    print(f"Gedetecteerd: {fen}")
    return templates


# Voeg toe onder de bestaande calibrate() functie:

def get_templates(color):
    """Laad templates met grootte-check, kalibreer als nodig."""
    from screen import capture_board

    template_file = TEMPLATE_FILE_WHITE if color == "white" else TEMPLATE_FILE_BLACK
    image = capture_board()
    curr_h, curr_w = image.shape[:2]

    if os.path.exists(template_file):
        templates, saved_w, saved_h = load_templates(template_file)
        if curr_w != saved_w or curr_h != saved_h:
            print(f"Bordgrootte veranderd: {saved_w}x{saved_h} -> {curr_w}x{curr_h}")
            templates = calibrate(color)
    else:
        print(f"Geen templates voor {color} — kalibratie nodig.")
        templates = calibrate(color)

    return templates


# =========================
# VISUELE HERKENNING
# =========================

def identify(image, file, rank, templates):
    center = get_center(image, file, rank)
    gray = cv2.cvtColor(center, cv2.COLOR_BGR2GRAY)
    if np.std(gray) < EMPTY_STD:
        return None
    is_white = np.percentile(gray, 5) > WHITE_BLACK_P5
    norm = get_inner_norm(image, file, rank)
    best, best_score = None, -999
    for piece, tmps in templates.items():
        if is_white != piece.isupper():
            continue
        for tmpl in tmps:
            if tmpl.shape != norm.shape:
                tmpl = cv2.resize(tmpl, (norm.shape[1], norm.shape[0]))
            score = np.sum(tmpl * norm) / tmpl.size
            if score > best_score:
                best_score = score
                best = piece
    return best


def read_board_visual(image, templates, color):
    rows = []
    for chess_row in range(7, -1, -1):
        row, empty = "", 0
        for chess_col in range(8):
            f, r = chess_to_screen(chess_col, chess_row, color)
            piece = identify(image, f, r, templates)
            if piece:
                if empty:
                    row += str(empty)
                    empty = 0
                row += piece
            else:
                empty += 1
        if empty:
            row += str(empty)
        rows.append(row)
    return "/".join(rows)


def validate(pos):
    errs = []
    if pos.count('K') != 1: errs.append(f"{pos.count('K')} witte koningen")
    if pos.count('k') != 1: errs.append(f"{pos.count('k')} zwarte koningen")
    return (not errs), ", ".join(errs) if errs else "OK"


# =========================
# DIFF-DETECTIE
# =========================

def get_changed_squares(before, after, color):
    changed = []
    for rank in range(8):
        for file in range(8):
            sq_before = get_square(before, file, rank)
            sq_after = get_square(after, file, rank)
            diff = np.mean(cv2.absdiff(sq_before, sq_after))
            if diff > SQUARE_DIFF_THRESHOLD:
                col, row = screen_to_chess(file, rank, color)
                chess_sq = chess.square(col, row)
                changed.append((chess_sq, diff))
    return changed


def detect_move_from_diff(board, before, after, color):
    changed = get_changed_squares(before, after, color)
    if len(changed) < 2:
        return None
    changed.sort(key=lambda x: x[1], reverse=True)
    changed_squares = set(sq for sq, _ in changed[:8])
    print(f"  Diff vakjes: {[chess.square_name(sq) for sq, _ in changed[:6]]}")

    best_match, best_overlap = None, 0
    for move in board.legal_moves:
        move_squares = {move.from_square, move.to_square}
        if board.is_castling(move):
            if board.is_kingside_castling(move):
                r = chess.H1 if board.turn == chess.WHITE else chess.H8
                t = chess.F1 if board.turn == chess.WHITE else chess.F8
            else:
                r = chess.A1 if board.turn == chess.WHITE else chess.A8
                t = chess.D1 if board.turn == chess.WHITE else chess.D8
            move_squares.update([r, t])
        if board.is_en_passant(move):
            cap = chess.square(chess.square_file(move.to_square),
                               chess.square_rank(move.from_square))
            move_squares.add(cap)
        overlap = len(move_squares & changed_squares)
        if overlap > best_overlap:
            best_overlap = overlap
            best_match = move

    if best_match and best_overlap >= 2:
        print(f"  Diff-zet: {best_match} (overlap: {best_overlap})")
        return best_match
    return None


def try_detect_opponent(board, before, after, templates, color):
    move = detect_move_from_diff(board, before, after, color)
    if move:
        return move
    print("  Diff mislukt, probeer visueel...")
    pos = read_board_visual(after, templates, color)
    ok, msg = validate(pos)
    if not ok:
        print(f"  Visueel ongeldig ({msg})")
        return None
    for m in board.legal_moves:
        test = board.copy()
        test.push(m)
        if test.board_fen() == pos:
            print(f"  Visueel gevonden: {m}")
            return m
    print("  Visueel matcht geen legale zet")
    return None