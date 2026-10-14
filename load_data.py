from pathlib import Path
import sqlite3

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "raw" / "ipl.db"
TABLES_DIR = BASE_DIR / "data" / "raw" / "tables"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

files = {
    "matches": TABLES_DIR / "matches.csv",
    "deliveries": TABLES_DIR / "deliveries.csv",
    "players": TABLES_DIR / "players.csv",
    "teams": TABLES_DIR / "teams.csv",
    "venues": TABLES_DIR / "venues.csv",
}

conn = sqlite3.connect(DB_PATH)

for table_name, file_path in files.items():
    if not file_path.exists():
        raise FileNotFoundError(f"Missing CSV: {file_path}")

    df = pd.read_csv(file_path)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"{table_name} table loaded: {len(df)} rows")

conn.close()
print(f"All IPL data loaded successfully into {DB_PATH}!")