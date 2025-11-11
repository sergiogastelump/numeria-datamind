import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

MEMORY_FILE = DATA_DIR / "memory_log.json"
CYCLES_FILE = DATA_DIR / "cycles.json"

APP_NAME = "PredictMind"
DEBUG = True
HOST = "0.0.0.0"
PORT = 5000
