# DuoLingo-Chess-Bot

DuoLingo Chess Bot

---

## Function
This bot serves as a function to inflate your Elo on DuoLingo Chess.  
It also generates around 3000 XP.

---

## Setup

### 1. Install Stockfish
This project requires the Stockfish chess engine to run.

Download Stockfish here:  
https://stockfishchess.org/download/

Choose the correct version for your system (Windows x64 recommended).

---

### 2. Place the file
After downloading, place the executable in the following folder:

/stockfish


Your folder structure should look like this:
```text
DuoLingo-Chess-Bot/
├── stockfish/
│ └── board.py
│ └── config.py
│ └── counter.py
│ └── engine.py
│ └── games.py
│ └── main.py
│ └── overlay.py
│ └── recognition.py
│ └── screen.py
├── Pictures
├── pieces
├── stockfish/
│ └── stockfish-windows-x86-64-avx2.exe
├── venv
├── board_check.png
├── chess_daily.txt
├── chess_templates_black.npz
├── chess_templates_white.npz
├── chess_templates.npz
├── debug_after.png
├── debug_before.png
├── debug_error.ng
├── test.py
├── README.md
```
---
### 3. Install modules
Copy and paste this line in your vscode terminal:
``` bash
pip install screeninfo chess
```

### 4. Open DuoLingo in Chrome
https://www.duolingo.com/learn
Go to courses -> Add Course -> Chess
Download the app
![alt text](image.png)
Open the app

### 5. Run the bot
run 
``` bash
python chess_bot\main.py
```
---
### 6. Follow the instructions in the terminal
Follow every instruction in the terminal. 

---
### 7. Enjoy!
Enjoy the script, add and modify if you want, I will not accept any pushes to the main branch.
For issues create an issue in Github.

---
## Flow
After you completed step 5,6,7,
This is what the bot will do in order:
1. search for "Games"
2. Click "Start Game"
3. Win or Lose games (First lose 50 games then win 30 games)
4. Press "Continue" until you are at the main screen.
5. Loop untill you have lost 50 games and won 30 games.
---
## Manipulate games
You can choose to manipulate the games you play. Here is how ->
###-> To only win games:

2. Change the "losses" counter to 50
3. Enter the amount of games you want to win
i.e: you want to win 50 games -> "wins" : -20
Because -20 + 50 = 30.
If you want to win more games that 50, you should do: 
30 - (amount of games to win) = input wins

###-> To only lose games:
1. Go to chess_daily.txt
2. Change the "wins" counter to 30
3. Enter the amount of games you want to lose
i.e: you want to lose 100 games -> "losses" : -50
Because -50 + 100 = 50
If you wan to lose more games than 100, you should do:
50 - amount of games you want to lose = input lose

4. Watch and enjoy


---
## Note
This was my first time using pyautogui, .npz template files, cv2, stockfish, tkinter
It is not optimized to get the most xp, to play the most games or to get the highest elo in DuoLingo Chess.
The bot was tested on Google Chrome

## Legal Disclaimer

This software was developed solely for educational, research, and technical demonstration purposes. The primary objective of this project was to explore and demonstrate concepts in computer vision, automation, input simulation, and software engineering.

The software was not created with the intent to facilitate, encourage, or promote cheating, unfair competitive behavior, or the violation of any platform's Terms of Service, including those of Duolingo or any other online service.

Any use of this software is the sole responsibility of the end user. The author does not endorse or encourage its use in environments where automation is prohibited or where it would provide an unfair advantage over other users.

This project is provided "as is" without warranty of any kind. The author assumes no liability for any damages, account restrictions, suspensions, bans, legal consequences, or other outcomes resulting from the use or misuse of this software.

By using this software, you acknowledge that you are responsible for ensuring compliance with all applicable laws, regulations, and the Terms of Service of any platform on which the software is used.

