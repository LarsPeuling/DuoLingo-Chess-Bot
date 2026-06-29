"""Screenshot, knoppen detectie en navigatie."""

import pyautogui
import cv2
import numpy as np
import time

from config import (
    BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT,
    VERDER_X, VERDER_Y, VERDER_REGION,
    PARTIJEN_X, PARTIJEN_Y, PARTIJEN_REGION,
    START_PARTIJ_X, START_PARTIJ_Y, START_PARTIJ_REGION,
)


def capture_board():
    img = pyautogui.screenshot(region=(BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def detect_verder():
    s = pyautogui.screenshot(region=VERDER_REGION)
    hsv = cv2.cvtColor(np.array(s), cv2.COLOR_RGB2HSV)
    green = cv2.inRange(hsv, np.array([35, 150, 150]), np.array([85, 255, 255]))
    red1 = cv2.inRange(hsv, np.array([0, 150, 150]), np.array([10, 255, 255]))
    red2 = cv2.inRange(hsv, np.array([170, 150, 150]), np.array([180, 255, 255]))
    orange = cv2.inRange(hsv, np.array([10, 150, 150]), np.array([25, 255, 255]))
    total = cv2.countNonZero(green) + cv2.countNonZero(red1) + cv2.countNonZero(red2) + cv2.countNonZero(orange)
    return total > 1000


def click_verder():
    pyautogui.click(VERDER_X, VERDER_Y)
    time.sleep(1)
    pyautogui.click(VERDER_X, VERDER_Y)
    time.sleep(2)
    print("VERDER aangeklikt.")


def detect_partijen():
    s = pyautogui.screenshot(region=PARTIJEN_REGION)
    hsv = cv2.cvtColor(np.array(s), cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, np.array([0, 0, 200]), np.array([180, 40, 255]))
    return cv2.countNonZero(mask) > 500


def detect_start_partij():
    s = pyautogui.screenshot(region=START_PARTIJ_REGION)
    hsv = cv2.cvtColor(np.array(s), cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, np.array([70, 80, 120]), np.array([110, 255, 255]))
    return cv2.countNonZero(mask) > 500


def navigate_to_game():
    """Navigeer naar een nieuw spel. Geeft True als gelukt."""
    print("Zoeken naar Partijen...")
    for _ in range(30):
        if detect_partijen():
            print("Partijen gevonden!")
            pyautogui.click(PARTIJEN_X, PARTIJEN_Y)
            time.sleep(2)
            break
        time.sleep(0.5)
    else:
        print("Partijen niet gevonden.")
        return False

    print("Zoeken naar Start Partij...")
    for _ in range(20):
        if detect_start_partij():
            print("Start Partij gevonden!")
            pyautogui.click(START_PARTIJ_X, START_PARTIJ_Y)
            time.sleep(1)
            break
        time.sleep(0.5)
    else:
        print("Start Partij niet gevonden.")
        return False

    print("Wachten tot bord laadt...")
    time.sleep(3)
    for _ in range(14):
        image = capture_board()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if np.std(gray) > 20:
            print("Bord geladen!")
            return True
        time.sleep(0.5)

    print("Bord niet geladen (timeout).")
    return False


def handle_game_over():
    """Klik VERDER na einde spel."""
    print("\nSpel afgelopen!")
    time.sleep(2)
    for _ in range(20):
        if detect_verder():
            click_verder()
            break
        time.sleep(0.5)
    time.sleep(2)
    if detect_verder():
        click_verder()
        time.sleep(2)