"""Schermconfiguratie, coördinaten en thresholds."""

import pyautogui
import screeninfo

STOCKFISH_PATH = r"{add your path to stockfish here}\stockfish-windows-x86-64-avx2.exe"

# Detect laptop vs extern scherm
monitors = screeninfo.get_monitors()
MULTI_MONITOR = len(monitors) > 1

if MULTI_MONITOR:
    _BOARD_X, _BOARD_Y = 654, 330
    _BOARD_W, _BOARD_H = 598, 609
    _VERDER_X, _VERDER_Y = 1360, 950
    _PARTIJEN_X, _PARTIJEN_Y = 115, 205
    _START_X, _START_Y = 1060, 800
else:
    _BOARD_X, _BOARD_Y = 652, 406
    _BOARD_W, _BOARD_H = 1233 - 652, 968 - 406
    _VERDER_X, _VERDER_Y = 1426, 928
    _PARTIJEN_X, _PARTIJEN_Y = 151, 249
    _START_X, _START_Y = 1091, 861

# Schaling
REF_WIDTH = 1920
REF_HEIGHT = 1080
SCREEN_W, SCREEN_H = pyautogui.size()
SCALE_X = SCREEN_W / REF_WIDTH
SCALE_Y = SCREEN_H / REF_HEIGHT


def scale(x, y):
    return int(x * SCALE_X), int(y * SCALE_Y)


def scale_region(x, y, w, h):
    return int(x * SCALE_X), int(y * SCALE_Y), int(w * SCALE_X), int(h * SCALE_Y)


# Geschaalde coördinaten
BOARD_X, BOARD_Y = scale(_BOARD_X, _BOARD_Y)
BOARD_WIDTH, BOARD_HEIGHT = scale(_BOARD_W, _BOARD_H)

VERDER_X, VERDER_Y = scale(_VERDER_X, _VERDER_Y)
VERDER_REGION = scale_region(_VERDER_X - 40, _VERDER_Y - 25, 160, 50)

PARTIJEN_X, PARTIJEN_Y = scale(_PARTIJEN_X, _PARTIJEN_Y)
PARTIJEN_REGION = scale_region(_PARTIJEN_X - 40, _PARTIJEN_Y - 20, 140, 40)

START_PARTIJ_X, START_PARTIJ_Y = scale(_START_X, _START_Y)
START_PARTIJ_REGION = scale_region(_START_X - 50, _START_Y - 25, 300, 100)

# Engine
THINK_TIME = 0.5

# Templates
TEMPLATE_FILE_WHITE = "chess_templates_white.npz"
TEMPLATE_FILE_BLACK = "chess_templates_black.npz"

# Herkenning
EMPTY_STD = 18
WHITE_BLACK_P5 = 135
BOARD_CHANGE = 50000
SQUARE_DIFF_THRESHOLD = 8

# Dagelijks schema
LOSE_TARGET = 50
WIN_TARGET = 30
COUNTER_FILE = "chess_daily.txt"