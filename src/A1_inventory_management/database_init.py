from platformdirs import user_data_dir
import sqlite3 as sql
from pathlib import Path

# Construct the path to the final location of the database
G_DATA_DIR = Path(user_data_dir("A1_inventory_management"))
G_DATA_DIR.mkdir(parents=True, exist_ok=True)
G_DB_PATH = G_DATA_DIR / "stock_database.db"

#########################
## def initialiseDb () ##
#########################
# If databases don't exist, initialise them from the db_sqlite_code file
def initialiseDb():
    # Find the path to the sql code for the database
    path = Path(__file__).parent / "dbs/db_sqlite_code.sql"


    conn = sql.connect(G_DB_PATH)
    sqlScript = ""
    with open(path) as f:
        sqlScript = f.read()
    cursor = conn.cursor()
    cursor.executescript(sqlScript)
    conn.commit()
    conn.close()

