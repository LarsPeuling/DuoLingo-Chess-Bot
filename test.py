import pyautogui
import time

def debug_click_position():
    print("Beweeg je muis naar 'Partijen' en wacht...")
    time.sleep(5)
    x, y = pyautogui.position()
    print(f"Gebruik deze coords: {x}, {y}")


debug_click_position()
# just to commit