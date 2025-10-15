# This file defines the query classes that will be used to check, construct,
# and execute the sqlite3 queries.

# See the UML diagram for a clearer picture of their relationship to each other
from enum import Enum
import tkinter as tk
from tkinter import ttk
import sqlite3 as sql

from A1_inventory_management.utils.query_classes_valid import isDate, dateInFuture, removeLeadingZeroes, dateLessThan

TRANSACTION_TYPE_ADDITION_STRING = 'addition'
TRANSACTION_TYPE_REMOVAL_STRING = 'removal'

FAILURE_STRING_G = "failed"
SUCCESS_STRING_G = "succeeded"

TYPE_STRING_ADD = "ADD"
TYPE_STRING_REMOVE = "remove"
TYPE_STRING_CHECK = "check"

OUTCOME_STRINGS = {
    TYPE_STRING_ADD : "added to",
    TYPE_STRING_REMOVE: "removed from",
    TYPE_STRING_CHECK: "checked in"
}

MAX_ROWS_TO_DISPLAY = 10


########################
## enum RemovalReason ##
########################
# Enum used to record the reason for goods being removed from a batch
RemovalReason = [
    # Display text  # Database record
    ("Used",        "used"       ),
    ("Out of Date", "out_of_date"),
    ("Returned",    "returned"   ),
    ("Lost",        "lost"       ),
    ("Destroyed",   "destroyed"  )
]

##########################
## enum TransactionType ##
##########################
# Enum used to record the type of transaction data desired
class TransactionType(Enum):
    ADD    = 0
    REMOVE = 1
    BOTH   = 2




###############
## class App ##
###############
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fylde Aero inventory mangement")
        # Get screen height and width
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        
        # set height and width
        width = 600
        height = 400
        
        #find the offsets needed to centre the window
        offsetX = int(screenWidth/2 - width / 2)
        offsetY = int(screenHeight / 2 - height / 2)
    
        # Set the window to the centre of the screen
        self.geometry(f'{width}x{height}+{offsetX}+{offsetY}')

        # Create container for active frames
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand="true")

        # Datafield to contain the fulfilled, returned query
        self.queryData = {
            "type" : "Not started",
            "outcome": "Not started",
            "parameters" : {},
            "result" : []
        }

        self.showFrame(MainPage)
        
    # Method to display a new frame of a set class
    def showFrame(self, frameClass):
        """Remove a prior frame and display a new one of the class frameClass

        Args:
            frameClass (class <ttk.Frame>): the name of the class of the frame
              to be instantiated
        """        
        # Clear the current frame from the container
        for widget in self.container.winfo_children():
            widget.destroy()
        # create a new frame attached to the container
        frame = frameClass(self.container, self)
        # display the new frame
        frame.pack(fill="both", expand="true")

####################
## class MainPage ##
####################
# Basic initial frame to display the page where the query is chosen
class MainPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Labels and options to perform different queries
        self.optionsLabel = ttk.Label(self, text="What would you like to do today?").pack()
    
        self.addStockButton = ttk.Button(self, text=f"Add Stock", command=lambda: self.controller.showFrame(AddPage)).pack()
        self.removeStockButton = ttk.Button(self, text=f"Remove Stock", command=lambda: self.controller.showFrame(RemovePage)).pack()
    
        self.checkStockButton = ttk.Button(self, text=f"Check Batches", command=lambda: self.controller.showFrame(CheckBatchPage)).pack()
        self.checkStockButton = ttk.Button(self, text=f"Check Transactions", command=lambda: self.controller.showFrame(CheckTransactionPage)).pack()
        self.checkStockButton = ttk.Button(self, text=f"Check Total Stock", command=lambda: self.controller.showFrame(CheckStockPage)).pack()
        # Exit button
        self.exitButton = ttk.Button(self, text="exit", command=self.controller.destroy).pack()

###################
## class AddPage ##
###################
# Frame to display data to construct a query to add data to a sqlite database
class AddPage(ttk.Frame):
    """
    Frame to add stock into the database.
    """    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Datafields to store information for the sqlite query
        self.controller.queryData["type"] = TYPE_STRING_ADD
        self.controller.queryData["parameters"] = {
            "name" : tk.StringVar(),
            "quantity" : tk.IntVar(),
            "deliveryDate" : tk.StringVar(),
            "useByDate" : tk.StringVar(),
        }
        # assign this variable to shorten the path
        parameters = self.controller.queryData["parameters"]
        # datafields to record if the respective variable field is valid
        self.dataValid = {
            "name" : None,
            "quantity" : None,
            "deliveryDate" : None,
            "useByDate" : None,
        }

        # Store for labels for each member of self.data
        self.labels = {
            "name": ttk.Label(self, text="Name/Id Number of Good"),
            "quantity": ttk.Label(self, text="Quantity of good"),
            "deliveryDate": ttk.Label(self, text="Delivery Date (YYYY-MM-DD)"),
            "useByDate": ttk.Label(self, text="Use By Date (YYYY-MM-DD)")
        }
        # store for entries for each member of self.data
        self.entries = {
            "name": ttk.Entry(self, textvariable=parameters["name"]),
            "quantity": ttk.Entry(self, textvariable=parameters["quantity"]),
            "deliveryDate": ttk.Entry(self, textvariable=parameters["deliveryDate"]),
            "useByDate": ttk.Entry(self, textvariable=parameters["useByDate"])
        }
        # store for input error warnings for each member of self.data
        # These will be modified to display text if any fields are found to 
        # contain invalid data
        self.entriesInvalid = {
            "name": ttk.Label(self, text=""),
            "quantity": ttk.Label(self, text=""),
            "deliveryDate": ttk.Label(self, text=""),
            "useByDate": ttk.Label(self, text="")
        }
       
        # Loop to display labels, entries, and invalids
        # I chose to seperate them like this because each type of tkinter 
        # object may need to be displayed in their own style, and this allows 
        # for that.
        for dataField in self.labels:
            self.labels[dataField].pack()
            self.entries[dataField].pack()
            self.entriesInvalid[dataField].pack()

        ttk.Button(self, text="Submit details", command=self.checkValid).pack()

    # make sure that values entered are all valid
    def checkValid(self):
        """
        Check each value in self.data in turn to ensure that it conforms to the
        syntax of the sql database, and mark it as invalid if it does not. If
        all values are valid, then the query is submitted; otherwise, the 
        invalid fields are flagged and the user is asked to re-enter that data.
        """        
        parameters = self.controller.queryData["parameters"]
        # use flag to see if any data are incorrectly formatted
        allValid = True
        # check name is valid by running a quick sqlite query
        conn = sql.connect("dbs/stock_database.db")
        cur = conn.cursor()

        #Check to see if a stock number was entered instead of a name
        # If it was, search for the id, not the name
        if parameters["name"].get().isnumeric():
            cur.execute('SELECT id FROM stock_names WHERE id = ?', (parameters["name"].get(),))
        else:
            cur.execute('SELECT name FROM stock_names WHERE name = ?', (parameters["name"].get().lower(),))
        if len(cur.fetchall()) > 0:
            self.dataValid["name"] = True
        else:
            self.dataValid["name"] = False
            allValid = False
        conn.close()
        
        # Ensure that quantity is an integer and is greater than 0
        # IntVar objects reset their value to 0 if a non-integer is entered, 
        # so this test checks both parameters
        if parameters["quantity"].get() > 0:
            self.dataValid["quantity"] = True
        else:
            self.dataValid["quantity"] = False
            allValid = False

        # Ensure that the delivery date is formatted correctly (yyyy-mm-dd), 
        # that all parts are possible (eg, no 13th month), and that it is not in 
        # the future
        if isDate(parameters["deliveryDate"].get()) and not dateInFuture(parameters["deliveryDate"].get()):
            self.dataValid["deliveryDate"] = True
        else:
            self.dataValid["deliveryDate"] = False
            allValid = False

        # Ensure that the use by date is formatted correctly (yyyy-mm-dd),
        # that all parts are possible (eg, no 13th month), and that it is in 
        # the future
        if isDate(parameters["useByDate"].get()) and dateInFuture(parameters["useByDate"].get()):
            self.dataValid["useByDate"] = True
        else:
            self.dataValid["useByDate"] = False
            allValid = False

        # If all data is valid, display the confirmation screen
        # If some data is invalid, identify the invalid data and highlight 
        # those fields to the user.
        if allValid:
            self.submitQuery()
            self.controller.showFrame(ResultsPage)
        else:
            self.displayInvalid()



    def displayInvalid(self):
        """ 
        Check each datafield in turn, and if it has been flagged as invalid,
        display an error message. Otherwise, remove existing error messages.
        """        
        if not self.dataValid["name"]:
            self.entriesInvalid["name"]["text"] = "Name/id number was not found in database. Please check spelling"
        else:
            self.entriesInvalid["name"]["text"] = ""

        if not self.dataValid["quantity"]:
            self.entriesInvalid["quantity"]["text"]= "Quantity must be a positive whole number"
        else:
            self.entriesInvalid["quantity"]["text"] = ""

        if not self.dataValid["deliveryDate"]:
            self.entriesInvalid["deliveryDate"]["text"] = "Delivery date must be in the form YYYY-MM-DD"
        else:
            self.entriesInvalid["deliveryDate"]["text"] = ""

        if not self.dataValid["useByDate"]:
            self.entriesInvalid["useByDate"]["text"] = "Use by date must be in the form YYYY-MM-DD"
        else:
            self.entriesInvalid["useByDate"]["text"] = ""


    # construct and submit a query to the database
    def submitQuery(self):
        """
        First add a record to the batches database, then add a record to the
        additions database, save results to the controller, and then going to 
        the results page.

        The database updates are transactional. Failure will result in
        successful updates being undone, details of the failure being saved to
        the controller, and then going to the results page.
        """        
        parameters = self.controller.queryData["parameters"]

        # Remove leading zeroes from dates
        deliveryDate = removeLeadingZeroes(parameters["deliveryDate"].get())
        useByDate = removeLeadingZeroes(parameters["useByDate"].get())

        conn = sql.connect("dbs/stock_database.db")
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")

        stockId = parameters["name"].get()
        try:
            # if a name has been used, get the id
            if not parameters["name"].get().isnumeric():
                cur.execute("SELECT id FROM stock_names WHERE name = ?",(parameters["name"].get().lower(),))
                stockId = cur.fetchone()[0]

            # Add the new batch of stock to the batches table
            cur.execute(
                "INSERT INTO batches (stock_id, quantity_initial, quantity_current, delivered_at, use_by) VALUES (?, ?, ?, ?, ?)", 
                (stockId, 
                parameters["quantity"].get(), 
                parameters["quantity"].get(), 
                deliveryDate, 
                useByDate)
            )
        except sql.Error:
            conn.close()
            print("batch query errored")
            # Save details of the error to the controller
            self.controller.queryData["outcome"] = FAILURE_STRING_G
            return
        
        # record the batchId outside of the try except loop to allow the 
        # prior transaction to be undone.
        batchId = cur.lastrowid
        try:
            # Record the addition in the transactions table
            cur.execute(
                "INSERT INTO transactions (transaction_type, batch_id, stock_id, quantity, occured_at) VALUES (?, ?, ?, ?, ?)",
                (                TRANSACTION_TYPE_ADDITION_STRING,
                batchId,
                stockId,
                parameters["quantity"].get(),
                deliveryDate)
            )
        except sql.Error:
            conn.close()
            print("addition query errored")

            # Save details of the failure to the controller
            self.controller.queryData["outcome"] = FAILURE_STRING_G

            # exit the function
            return
        conn.commit()
        conn.close()
        self.controller.queryData["result"].append(batchId)
        self.controller.queryData["outcome"] = SUCCESS_STRING_G



########################
########################
### class RemovePage ###
########################
########################
class RemovePage(ttk.Frame):
    """
    Frame to remove data from the databases
    """    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Datafields to store information for the sqlite query
        self.controller.queryData["type"] = TYPE_STRING_REMOVE
        self.controller.queryData["parameters"] = {
            "batchId" : tk.IntVar(),
            "quantity" : tk.IntVar(),
            "removalDate" : tk.StringVar(),
            "removalReason" : tk.StringVar()
        }
        # assign this variable to shorten the path
        parameters = self.controller.queryData["parameters"]
        # datafields to record if the respective variable field is valid
        self.dataValid = {
            "batchId" : None,
            "quantity" : None,
            "removalDate" : None,
            "removalReason" : None,
        }

        # Store for labels for each member of self.data
        self.labels = {
            "batchId" : ttk.Label(self, text="Batch Number"),
            "quantity": ttk.Label(self, text="Quantity removed"),
            "removalDate": ttk.Label(self, text="Date of removal (YYYY-MM-DD)"),
            "removalReason": ttk.Label(self, text="Reason for removal")
        }
        # store for entries for each member of self.data
        self.entries = {
            "batchId" : ttk.Entry(self, textvariable=parameters["batchId"]),
            "quantity": ttk.Entry(self, textvariable=parameters["quantity"]),
            "removalDate": ttk.Entry(self, textvariable=parameters["removalDate"]),
            "removalReason": []
        }
        self.entries["removalReason"] = [
            ttk.Radiobutton(self, text=f"{RemovalReason[i][0]}", value=f"{RemovalReason[i][1]}", variable=parameters["removalReason"]) for i in range(len(RemovalReason))
        ]
        # store for input error warnings for each member of self.data
        # These will be modified to display text if any fields are found to 
        # contain invalid data
        self.entriesInvalid = {
            "batchId" : ttk.Label(self, text=""),
            "quantity": ttk.Label(self, text=""),
            "removalDate": ttk.Label(self, text=""),
            "removalReason": ttk.Label(self, text="")
        }
       
        # Loop to display labels, entries, and invalids
        # I chose to seperate them like this because each type of tkinter 
        # object may need to be displayed in their own style, and this allows 
        # for that.
        for dataField in self.labels:
            self.labels[dataField].pack()
            entry = self.entries[dataField]
            if isinstance(entry, list):
                for item in entry:
                    item.pack()
            else:
                entry.pack()
            self.entriesInvalid[dataField].pack()

        ttk.Button(self, text="Submit details", command=self.checkValid).pack()

    # make sure that values entered are all valid
    def checkValid(self):
        """
        Check each value in self.data in turn to ensure that it conforms to the
        syntax of the sql database, and mark it as invalid if it does not. If
        all values are valid, then the query is submitted; otherwise, the 
        invalid fields are flagged and the user is asked to re-enter that data.
        """        
        parameters = self.controller.queryData["parameters"]
        # use flag to see if any data are incorrectly formatted
        allValid = True

        #Connect to the database
        conn = sql.connect("dbs/stock_database.db")
        cur = conn.cursor() 

        batchId = parameters["batchId"].get()
        # check batchId exists in batches
        cur.execute('SELECT id FROM batches WHERE id = ?', (batchId,))
        if len(cur.fetchall()) > 0:
            self.dataValid["batchId"] = True
        else:
            self.dataValid["batchId"] = False
            # If batch number is not valid, none of the other checks will return 
            # valid.
            self.displayInvalid()
            return

        
        # Ensure that quantity is an integer is greater than 0, and is not more
        # than the quantity_current in the chosen batch
        # IntVar objects reset their value to 0 if a non-integer is entered, 
        # so this test checks the first two parameters
        cur.execute('SELECT quantity_current FROM batches WHERE id = ?', (batchId,))
        quantity = parameters["quantity"].get()
        if quantity > 0 and int(cur.fetchone()[0]) >= quantity:
            self.dataValid["quantity"] = True
        else:
            self.dataValid["quantity"] = False
            allValid = False

        # Ensure that the removal date is formatted correctly (yyyy-mm-dd), 
        # that all parts are possible (eg, no 13th month), and that it is later than the delivery date on the batch
        cur.execute('SELECT delivered_at FROM batches WHERE id = ?', (batchId,))

        deliveryDate = cur.fetchone()[0]
        print(f"{deliveryDate}")
        removalDate = removeLeadingZeroes(parameters["removalDate"].get())
        print(f"{removalDate}")

        if isDate(removalDate) and not dateInFuture(removalDate) and not dateLessThan(removalDate, deliveryDate):
            self.dataValid["removalDate"] = True
        else:
            self.dataValid["removalDate"] = False
            allValid = False
        conn.close()

        # If all data is valid, display the confirmation screen
        # If some data is invalid, identify the invalid data and highlight 
        # those fields to the user.
        if allValid:
            self.submitQuery()
            self.controller.showFrame(ResultsPage)
        else:
            self.displayInvalid()



    def displayInvalid(self):
        """ 
        Check each datafield in turn, and if it has been flagged as invalid,
        display an error message. Otherwise, remove existing error messages.
        """        
        if not self.dataValid["batchId"]:
            self.entriesInvalid["batchId"]["text"] = "Batch number was not found in database."
        else:
            self.entriesInvalid["batchId"]["text"] = ""

        if not self.dataValid["quantity"]:
            self.entriesInvalid["quantity"]["text"]= "Quantity must be a positive whole number, less than the batches current quantity"
        else:
            self.entriesInvalid["quantity"]["text"] = ""

        if not self.dataValid["removalDate"]:
            self.entriesInvalid["removalDate"]["text"] = "Delivery date must be in the form YYYY-MM-DD"
        else:
            self.entriesInvalid["deliveryDate"]["text"] = ""


    # construct and submit a query to the database
    def submitQuery(self):
        """
        First remove a quantity from the batches database, then add a record to the
        transactions database, save results to the controller, and then go to 
        the results page.

        The database updates are transactional. Failure will result in
        successful updates being undone, details of the failure being saved to
        the controller, and then going to the results page.
        """        
        parameters = self.controller.queryData["parameters"]

        # Remove leading zeroes from dates
        removalDate = removeLeadingZeroes(parameters["removalDate"].get())

        # Connect to database
        conn = sql.connect("dbs/stock_database.db")
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")

        batchId = parameters["batchId"].get()
        try:
            # Get the current quantity of the desired batch
            cur.execute("SELECT quantity_current FROM batches WHERE id = ?", (batchId,))

            # Calculate the new quantity
            currentQuantity = cur.fetchone()[0]
            newQuantity = currentQuantity - parameters["quantity"].get()
            
            # Update the desired batch
            cur.execute("UPDATE batches SET quantity_current = ? WHERE id = ?", (newQuantity, batchId))

        except sql.Error:
            conn.close()
            print("batch query errored")

            # Save details of the error to the controller
            self.controller.queryData["outcome"] = FAILURE_STRING_G
            # exit the function
            return
        
        # Get stockId needed to add to transaction table
        cur.execute("SELECT stock_id FROM batches WHERE id = ?", (batchId,))
        stockId = cur.fetchone()[0]

        try:
            # Record the removal in the transactions table
            cur.execute(
                "INSERT INTO transactions (batch_id, stock_id,transaction_type, quantity, occured_at, removal_reason) VALUES (?, ?, ?, ?, ?, ?)",
                (batchId,
                stockId,
                TRANSACTION_TYPE_REMOVAL_STRING,
                parameters["quantity"].get(),
                removalDate,
                parameters["removalReason"].get())
            )
        except sql.Error:
            conn.close()
            print("addition query errored")
            # Save details of the failure to the controller
            self.controller.queryData["outcome"] = FAILURE_STRING_G
            # exit the function
            return
        
        conn.commit()
        conn.close()
        self.controller.queryData["outcome"] = SUCCESS_STRING_G

class CheckBatchPage(ttk.Frame):
    def __init__(self, parent, controller):
        pass
    
class CheckTransactionPage(ttk.Frame):
    def __init__(self, parent, controller):
        pass

class CheckStockPage(ttk.Frame):
    def __init__(self, parent, controller):
        pass

class ResultsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.header = ttk.Label(self, text="RESULT?").pack()
        # Show the success or failure of the database operation
        queryType = self.controller.queryData["type"]
        outcome = self.controller.queryData["outcome"]
        self.outcomeLabel = ttk.Label(self, text=f"The database operation {outcome}").pack()
        self.parameterLabel = ttk.Label(self, text=f"")
        # If add or remove operations succeeded, show the parameters that were 
        # used. 
        # This gives another opportunity to make sure that the data was 
        # correct, and potentially to correct mistakes.
        if outcome is not FAILURE_STRING_G and queryType is not TYPE_STRING_CHECK: 
            self.parameterLabel["text"] = f"The following data was {OUTCOME_STRINGS[queryType]} the database: "
            for k, v in self.controller.queryData["parameters"].items():
                ttk.Label(self, text=f"{k} : {v.get()}").pack()
            # If the query is an add, displays the new batch ID number to make future removals easier
            if queryType is TYPE_STRING_ADD:
                ttk.Label(self,text=f"The batch ID number is {self.controller.queryData["result"][0]}. Please record this for future transactions.")
        # If the parameter was a database check, and the list of results is not too long, display them on screen.
        elif queryType is TYPE_STRING_CHECK and len(self.controller.queryData["result"] <= MAX_ROWS_TO_DISPLAY):
            pass

        # provide a button to return to the main page
        self.exitButton = ttk.Button(self, text="Return to Main Page", command=lambda: self.controller.showFrame(MainPage)).pack()
        # If the query type was check, provide an option to output the results to a csv file
