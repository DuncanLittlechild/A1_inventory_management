import tkinter as tk
from tkinter import ttk
import sqlite3 as sql
from pathlib import Path

import A1_inventory_management.utils.tkinter_tools as tk_tools
import A1_inventory_management.utils.query_classes_dict as qcd

MAIN_WINDOW_WIDTH_G  = 600
MAIN_WINDOW_HEIGHT_G = 300
 # Start to set up Tkinter window
ROOT_G = tk.Tk()
tk_tools.resizeAndCentreWindow(MAIN_WINDOW_WIDTH_G, MAIN_WINDOW_HEIGHT_G, ROOT_G)

#########################
## def initialiseDb () ##
#########################
# If databases don't exist, initialise them from the db_sqlite_code file
def initialiseDb():
    path = Path(__file__).parent / "./dbs/db_sqlite_code.sql"
    conn = sql.connect("dbs/stock_database.db")
    sqlScript = ""
    with open(path) as f:
        sqlScript = f.read()
    cursor = conn.cursor()
    cursor.executescript(sqlScript)
    conn.commit()
    conn.close()

#################################
## def alterStock (Add : bool) ##
#################################
# Displays option and creates object to allow user to either add or remove 
# stock.
def alterStock(add):
    print(f"alterStock called with add at {add}")
    query = None
    if add:
        query = qcd.alterStockClassesList["add"]()
    else:
        query = qcd.alterStockClassesList["remove"]()
## Initial input and validation ##

# while not query.Valid:
#   Alter Tkinter screen to show the fields in the query object
#   After data submitted, check to ensure that all data is valid
#   Use a method that flips the valid flags if they are valid, or have become invalid, and updates the valid flag
# Should also reset invalid datafields
#   query.checkValid()
#   if not query.valid:
#       display an error conveying what information was incorrect
#       query.displayInvalid()

## sqlite3 query generation ##

# Call a member to generate the specific query, and thence to try and execute it
# The member should also update the queryAdded flag if it succeeds, and leave it as false if it fails. This shouldn't happen due to earlier checks, but belts and braces.
# query.updateDatabase()
# if not query.queryAdded:
#   Display error message saying failed to add if Add, or failed to remove if not Add
# return


######################
## def checkStock() ##
######################
def checkStock():
    print("checkStock called")

# initialise query to null
# Ask to choose between querying a batch; querying transactions; or querying total stock levels
# if batch:
#   query = BatchCheckQuery()
# else if transactions:
#   query = TransactionCheckQuery()
# else:
#   query = StockCheckQuery()
# Run a function that takes the Tkinter widget, and displays appropriate fields to construct the query
# batch should ask if they are interested in a specific batch, then allow them to enter either a batch number; or a date range and/or name  to construct the query
# Transaction shoud ask if they are interested in additions, withdrawals, or both, then give an option to refine by date range and/or name
# Stock should give them the option to refine by name
# This should be followed by checks very similar to those described in alterStock to ensure validity
# query.displayOptions(widget)
# Call a member to generate the specific query, and thence to try and execute it
# The member should also update the queryAdded flag if it succeeds, and leave it as false if it fails. This shouldn't happen due to earlier checks, but belts and braces.
# query.updateDatabase()
# if not query.queryAdded:
#   Display error message saying failed to find
# return



###########################
## displayInitialOptions ##
###########################
# Gives the option to choose the initial operation the user wants to perform
def displayInitialOptions():
    tk_tools.clearWindow(ROOT_G)
    # set up Tkinter window
    ROOT_G.title('Choose database operation')
    # Currently just basic options for appreance, nothing fancy
    # Add buttons and labels to add, remove, or check stock
    optionsLabel = ttk.Label(ROOT_G, text="What would you like to do today?").pack()
    addStockButton = ttk.Button(ROOT_G, text="Add stock", command=lambda: alterStock(True)).pack()
    removeStockButton = ttk.Button(ROOT_G, text="Remove stock", command=lambda: alterStock(False)).pack()
    checkStockButton = ttk.Button(ROOT_G, text="Check stock", command=checkStock).pack()
    # Add exit button
    exitButton = ttk.Button(ROOT_G, text="exit", command=ROOT_G.destroy).pack()
    # display
    ROOT_G.mainloop()