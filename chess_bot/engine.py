"""Stockfish engine, zetten klikken en wacht-functies."""

import pyautogui
import cv2
import numpy as np
import chess
import chess.engine
import time

from config import STOCKFISH_PATH, THINK_TIME, BOARD_X, BOARD_WIDTH, BOARD_HEIGHT, BOARD_CHANGE
from board import square_to_pixels
from screen import capture_board, detect_verder


def get_best_move(board):
    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as eng:
        return eng.play(board, chess.engine.Limit(time=THINK_TIME)).move


def click_move(move, color):
    x1, y1 = square_to_pixels(chess.square_name(move.from_square), color)
    x2, y2 = square_to_pixels(chess.square_name(move.to_square), color)
    pyautogui.click(x1, y1)
    time.sleep(0.15)
    pyautogui.click(x2, y2)

    if move.promotion:
        time.sleep(0.5)
        sw = BOARD_WIDTH / 8
        sh = BOARD_HEIGHT / 8
        menu_width = sw * 3.5

        menu_center_x = x2
        menu_left = menu_center_x - menu_width / 2

        board_left = BOARD_X
        board_right = BOARD_X + BOARD_WIDTH

        if menu_left < board_left:
            menu_left = board_left
        if menu_left + menu_width > board_right:
            menu_left = board_right - menu_width

        queen_x = int(menu_left + sw * 0.55 - 10)
        queen_y = y2 + int(sh * 1.3) + 40

        pyautogui.click(queen_x, queen_y)
        print(f"  Promotie: koningin geselecteerd ({queen_x}, {queen_y})")
        time.sleep(0.3)


def wait_stable(timeout=5, interval=0.1, count=2):
    stable, prev, t0 = 0, capture_board(), time.time()
    while time.time() - t0 < timeout:
        time.sleep(interval)
        if detect_verder():
            return "DONE", None
        curr = capture_board()
        if np.sum(cv2.absdiff(prev, curr)) < BOARD_CHANGE:
            stable += 1
            if stable >= count:
                return "OK", curr
        else:
            stable = 0
        prev = curr
    return "OK", prev


def wait_opponent(ref, timeout=120, interval=0.1):
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(interval)
        if detect_verder():
            return "DONE", None
        curr = capture_board()
        if np.sum(cv2.absdiff(ref, curr)) > BOARD_CHANGE:
            time.sleep(0.5)
            return wait_stable(timeout=5)
    return "TIMEOUT", None