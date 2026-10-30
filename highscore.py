import json
import os

# Saved next to the game code so it works regardless of the CWD the game
# is started from.
FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "highscore.json")


def load_high_score() -> int:
    """ Read the saved high score; 0 when the file is missing or invalid. """
    try:
        with open(FILE_PATH) as f:
            return int(json.load(f).get("high_score", 0))
    except (OSError, ValueError):
        return 0


def save_high_score(score: int) -> None:
    with open(FILE_PATH, "w") as f:
        json.dump({"high_score": score}, f)
