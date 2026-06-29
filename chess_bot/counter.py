"""Dagelijkse game counter in chess_daily.txt."""

import json
import os
from datetime import date

from config import COUNTER_FILE, LOSE_TARGET, WIN_TARGET


def load_daily_counter():
    """Laad counter. Reset als het een nieuwe dag is."""
    today = str(date.today())
    if os.path.exists(COUNTER_FILE):
        try:
            with open(COUNTER_FILE, 'r') as f:
                data = json.load(f)
            if data.get("date") == today:
                return data
        except (json.JSONDecodeError, KeyError):
            pass
    data = {"date": today, "losses": 0, "wins": 0, "total": 0}
    save_daily_counter(data)
    return data


def save_daily_counter(data):
    with open(COUNTER_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def print_status(counter):
    losses_left = max(0, LOSE_TARGET - counter['losses'])
    wins_left = max(0, WIN_TARGET - counter['wins'])
    print(f"Vandaag: {counter['losses']}L + {counter['wins']}W = {counter['total']} totaal")
    print(f"Nog: {losses_left}L + {wins_left}W")


def is_done(counter):
    return counter['losses'] >= LOSE_TARGET and counter['wins'] >= WIN_TARGET