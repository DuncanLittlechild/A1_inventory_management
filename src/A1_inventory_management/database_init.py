import tkinter as tk
from tkinter import ttk
import sqlite3 as sql
from pathlib import Path


#########################
## def initialiseDb () ##
#########################
# If databases don't exist, initialise them from the db_sqlite_code file
def initialiseDb():
    path = Path(__file__).parent / "../../dbs/db_sqlite_code.sql"
    conn = sql.connect("dbs/stock_database.db")
    sqlScript = ""
    with open(path) as f:
        sqlScript = f.read()
    cursor = conn.cursor()
    cursor.executescript(sqlScript)
    conn.commit()
    conn.close()

