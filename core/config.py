import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATA_DIR / "parser_data.db"

KEYWORDS = {
    "modular_synth": [
        "модульный синтезатор", "eurorack", "модуль vca", "модуль vco",
        "синтезатор модульный", "модульная система", "doepfer"
    ],
    "percussion": [
        "барабан", "тарелка", "кахон", "джембе", "перкуссия", "ударная установка",
        "барабаны", "djembe", "cajon"
    ],
    "gong": [
        "гонг", "трубогон", "поющая чаша", "тибетская чаша", "звуковая терапия",
        "медитационная музыка", "gong", "singing bowl"
    ],
    "string": [
        "гитара", "скрипка", "виолончель", "балалайка", "домра",
        "струнные инструменты", "guitar", "violin"
    ],
    "wind": [
        "флейта", "саксофон", "труба", "кларнет", "гобой",
        "духовые инструменты", "flute", "saxophone"
    ]
}

REQUEST_DELAY = 2  
MAX_RETRIES = 3
TIMEOUT = 30

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
]