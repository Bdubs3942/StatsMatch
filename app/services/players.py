"""CSV access shared by both screens."""
import csv
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[2] / 'data' / 'mock_players.csv'


def load_players():
    with DATA_FILE.open(encoding='utf-8', newline='') as file:
        return list(csv.DictReader(file))
