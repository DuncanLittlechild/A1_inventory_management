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
## def checkStockChoice() ##
######################
# program branch for any operations that do not involve altering the contents 
# of the database
def checkStockChoice():
    pass

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
