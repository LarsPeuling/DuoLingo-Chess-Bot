"""Vakje helpers, kleurdetectie en coördinaten-mapping."""

import cv2
import numpy as np

from config import BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT, EMPTY_STD, WHITE_BLACK_P5


def square_rect(file, rank, img_w, img_h):
    sw = img_w / 8
    sh = img_h / 8
    return int(file * sw), int(rank * sh), int((file + 1) * sw), int((rank + 1) * sh)


def get_square(image, file, rank):
    h, w = image.shape[:2]
    x1, y1, x2, y2 = square_rect(file, rank, w, h)
    return image[y1:y2, x1:x2]


def get_center(image, file, rank):
    h, w = image.shape[:2]
    x1, y1, x2, y2 = square_rect(file, rank, w, h)
    mx = (x2 - x1) // 5
    my = (y2 - y1) // 5
    return image[y1 + my:y2 - my, x1 + mx:x2 - mx]


def get_inner_norm(image, file, rank):
    h, w = image.shape[:2]
    x1, y1, x2, y2 = square_rect(file, rank, w, h)
    ix = (x2 - x1) // 4
    iy = (y2 - y1) // 4
    region = image[y1 + iy:y2 - iy, x1 + ix:x2 - ix]
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY).astype(float)
    m, sd = np.mean(gray), np.std(gray)
    return (gray - m) / sd if sd > 1 else gray - m


def detect_color(image):
    """Detecteer of wij wit of zwart spelen."""
    p5_values = []
    for file in [0, 3, 4, 7]:
        center = get_center(image, file, 7)
        gray = cv2.cvtColor(center, cv2.COLOR_BGR2GRAY)
        if np.std(gray) > EMPTY_STD:
            p5_values.append(np.percentile(gray, 5))
    avg = np.mean(p5_values) if p5_values else 200
    color = "white" if avg > WHITE_BLACK_P5 else "black"
    print(f"Onderste rij p5={avg:.0f} -> wij spelen: {color}")
    return color


def screen_to_chess(file, rank, color):
    if color == "white":
        return file, 7 - rank
    return 7 - file, rank


def chess_to_screen(col, row, color):
    if color == "white":
        return col, 7 - row
    return 7 - col, row


def square_to_pixels(sq_name, color):
    col = ord(sq_name[0]) - ord('a')
    row = int(sq_name[1]) - 1
    f, r = chess_to_screen(col, row, color)
    sw = BOARD_WIDTH / 8
    sh = BOARD_HEIGHT / 8
    return BOARD_X + int(f * sw + sw / 2), BOARD_Y + int(r * sh + sh / 2)