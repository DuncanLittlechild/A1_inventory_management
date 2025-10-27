# This file defines the query classes that will be used to check, construct,
# and execute the sqlite3 queries.

# See the UML diagram for a clearer picture of their relationship to each other
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showerror, showinfo, askyesno
root = tk.Tk()
tk.Label(root, text="Loading modules... please wait").pack()
root.update()
import sqlite3 as sql
import pandas as pd
from pandastable import Table, TableModel

root.destroy()

from A1_inventory_management.utils.datetime_helpers import isDate, dateInFuture, addLeadingZeroes, dateLessThan, getCurrentDateTime

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

REMOVAL_REASON = {
    # Display text  # Database record
    "Used": "used",
    "Out of Date": "out_of_date",
    "Returned": "returned",
    "Lost": "lost",
    "Destroyed": "destroyed"  
}

TRANSACTION_TYPE = [
    TRANSACTION_TYPE_ADDITION_STRING,
    TRANSACTION_TYPE_REMOVAL_STRING
]


###############
## class App ##
###############
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fylde Aero inventory mangement")
        
        # set height and width
        self.width = 300
        self.height = 500

        # Get screen height and width
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        
        #find the offsets needed to centre the window
        offsetX = int(screenWidth/2 - self.width / 2)
        offsetY = int(screenHeight / 2 - self.height / 2)
    
        # Set the window to the centre of the screen
        self.geometry(f'{self.width}x{self.height}+{offsetX}+{offsetY}')

        # Create container for active frames
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand="true")

        # Datafield to contain the fulfilled, returned query
        self.queryData = {
            "type" : "Not started",
            "outcome": "Not started",
            "parameters" : {},
            "result" : None
        }

        self.showFrame(MainPage)

    # Method to display a new frame of a set class
    def showFrame(self, frameClass):
        """Remove a prior frame and display a new one of the class frameClass

        Args:
            frameClass (class <ttk.Frame>): the name of the class of the frame
              to be instantiated
        """        
        # Reset the container to the default size
        self.centreWindow()
        # Clear the current frame from the container
        for widget in self.container.winfo_children():
            widget.destroy()
        # create a new frame attached to the container
        frame = frameClass(self.container, self)
        # display the new frame
        frame.pack(fill="both", expand="true")

    def centreWindow(self, width = None, height = None):
        # Get window height and width
        if width is None:
            width = self.width
        if height is None:
            height = self.height

        # Get screen height and width
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        
        #find the offsets needed to centre the window
        offsetX = int(screenWidth/2 - width / 2)
        offsetY = int(screenHeight / 2 - height / 2)
    
        # Set the window to the centre of the screen
        self.geometry(f'{width}x{height}+{offsetX}+{offsetY}')


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
            "delivered_at" : tk.StringVar(),
            "use_by" : tk.StringVar(),
        }
        # assign this variable to shorten the path
        parameters = self.controller.queryData["parameters"]
        # datafields to record if the respective variable field is valid
        self.dataValid = {
            "name" : None,
            "quantity" : None,
            "delivered_at" : None,
            "use_by" : None,
        }

        # Store for labels for each member of self.data
        self.labels = {
            "name": ttk.Labelframe(self, text="Name/Id Number of Good"),
            "quantity": ttk.Labelframe(self, text="Quantity of good"),
            "delivered_at": ttk.Labelframe(self, text="Delivery Date (YYYY-MM-DD)"),
            "use_by": ttk.Labelframe(self, text="Use By Date (YYYY-MM-DD)")
        }
        # store for entries for each member of self.data
        self.entries = {
            "name": ttk.Entry(self.labels["name"], textvariable=parameters["name"]),
            "quantity": ttk.Entry(self.labels["quantity"], textvariable=parameters["quantity"]),
            "delivered_at": ttk.Entry(self.labels["delivered_at"], textvariable=parameters["delivered_at"]),
            "use_by": ttk.Entry(self.labels["use_by"], textvariable=parameters["use_by"])
        }
        # store for input error warnings for each member of self.data
        # These will be modified to display text if any fields are found to 
        # contain invalid data
        self.entriesInvalid = {
            "name": ttk.Label(self, text=""),
            "quantity": ttk.Label(self, text=""),
            "delivered_at": ttk.Label(self, text=""),
            "use_by": ttk.Label(self, text="")
        }
       
        # Loop to display labels, entries, and invalids
        # I chose to seperate them like this because each type of tkinter 
        # object may need to be displayed in their own style, and this allows 
        # for that.
        for dataField in self.labels:
            self.labels[dataField].pack()
            self.entries[dataField].pack(padx=5, pady=5)
            self.entriesInvalid[dataField].pack()

        ttk.Button(self, text="Submit details", command=self.checkValid).pack()

        # Button to return to main page
        self.backButton = ttk.Button(self, text="Back", command=lambda: self.controller.showFrame(MainPage))

        self.backButton.pack()

    def checkValid(self):
        """
        Check each value in self.data in turn to ensure that it conforms to the
        syntax of the sql database, and mark it as invalid if it does not. If
        all values are valid, then the query is submitted; otherwise, the 
        invalid fields are flagged and the user is asked to re-enter that data.
        """        
        #region checkValid
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
        if isDate(parameters["delivered_at"].get()) and not dateInFuture(parameters["delivered_at"].get()):
            self.dataValid["delivered_at"] = True
        else:
            self.dataValid["delivered_at"] = False
            allValid = False

        # Ensure that the use by date is formatted correctly (yyyy-mm-dd),
        # that all parts are possible (eg, no 13th month), and that it is in 
        # the future
        if isDate(parameters["use_by"].get()) and dateInFuture(parameters["use_by"].get()):
            self.dataValid["use_by"] = True
        else:
            self.dataValid["use_by"] = False
            allValid = False

        # If all data is valid, get user to confirm details then submit
        # If some data is invalid, identify the invalid data and highlight 
        # those fields to the user.
        if allValid:
            self.confirmSubmitQuery()
        else:
            self.displayInvalid()
        #endregion
    
    def confirmSubmitQuery(self):
        """Give the user an opportunity to check the data they are about to add to the database
        """
        #region cSQ       
        parameters = self.controller.queryData["parameters"]

        infoString = "You want to add batch with the following parameters to the database: \n"
        for k, v in parameters.items():
            infoString = infoString + f"{k} : {v.get()}\n"
        infoString = infoString + "\nAre you sure?"
        confirm = askyesno(title="Confirm query submission", message=infoString)
        if confirm:
            self.submitQuery()
        #endregion

    def displayInvalid(self):
        """ 
        Check each datafield in turn, and if it has been flagged as invalid,
        display an error message. Otherwise, remove existing error messages.
        """
        #region dI        S
        if not self.dataValid["name"]:
            self.entriesInvalid["name"]["text"] = "Name/id number was not found in database. Please check spelling"
        else:
            self.entriesInvalid["name"]["text"] = ""

        if not self.dataValid["quantity"]:
            self.entriesInvalid["quantity"]["text"]= "Quantity must be a positive whole number"
        else:
            self.entriesInvalid["quantity"]["text"] = ""

        if not self.dataValid["delivered_at"]:
            self.entriesInvalid["delivered_at"]["text"] = "Delivery date must be in the form YYYY-MM-DD"
        else:
            self.entriesInvalid["delivered_at"]["text"] = ""

        if not self.dataValid["use_by"]:
            self.entriesInvalid["use_by"]["text"] = "Use by date must be in the form YYYY-MM-DD"
        else:
            self.entriesInvalid["use_by"]["text"] = ""
        #endregion

    def submitQuery(self):
        """
        First add a record to the batches database, then add a record to the
        transactions database, save results to the controller, and then go to 
        the results page.

        The database updates are transactional. Failure will result in
        successful updates being undone, details of the failure being saved to
        the controller, and then going to the results page.
        """        
        #region sQ
        parameters = self.controller.queryData["parameters"]


        # Remove leading zeroes from dates
        delivered_at = addLeadingZeroes(parameters["delivered_at"].get())
        use_by = addLeadingZeroes(parameters["use_by"].get())

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
                delivered_at, 
                use_by)
            )
        except sql.Error:
            conn.close()
            showerror(title="Failed to add to batches", message="Query failed to add to batches. The database has not been altered. Please contact your system administrator")
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
                delivered_at)
            )
        except sql.Error:
            conn.close()
            showerror(title="Failed to add to transactions", message="Query failed to add to transactions. The database has not been altered. Please contact your system administrator")

            # Save details of the failure to the controller
            self.controller.queryData["outcome"] = FAILURE_STRING_G

            # exit the function
            return
        conn.commit()
        conn.close()
        infoString = "An entry was added to the batches database with the following parameters: \n"
        for k, v in parameters.items():
            infoString = infoString + f"{k} : {v.get()}\n"
        infoString = infoString + f"\nIt was assigned the batch id {batchId}."
        showinfo(title="Add Successful", message=infoString)
        self.controller.queryData["outcome"] = SUCCESS_STRING_G
        #endregion



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
            ttk.Radiobutton(self, text=f"{k}", value=f"{v}", variable=parameters["removalReason"]) for k, v in REMOVAL_REASON.items()
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

        # Button to return to main page
        self.backButton = ttk.Button(self, text="Back", command=lambda: self.controller.showFrame(MainPage))

        self.backButton.pack()


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

        delivered_at = cur.fetchone()[0]
        removalDate = parameters["removalDate"].get()

        if isDate(removalDate) and not dateInFuture(removalDate) and not dateLessThan(removalDate, delivered_at):
            self.dataValid["removalDate"] = True
        else:
            self.dataValid["removalDate"] = False
            allValid = False
        conn.close()

        # If all data is valid, display the confirmation screen
        # If some data is invalid, identify the invalid data and highlight 
        # those fields to the user.
        if allValid:
            self.confirmSubmitQuery()
        else:
            self.displayInvalid()

    def confirmSubmitQuery(self):
        """Give the user an opportunity to check the data they are about to alter in the database
        """        
        parameters = self.controller.queryData["parameters"]

        infoString = f"You want to remove {parameters["quantity"].get()} units from batch {parameters["batchId"].get()} with the following parameters: \n"
        for k, v in parameters.items():
            if k == "batchId":
                continue
            infoString = infoString + f"{k} : {v.get()}\n"
        infoString = infoString + "\nAre you sure?"
        confirm = askyesno(title="Confirm query submission", message=infoString)
        if confirm:
            self.submitQuery()

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
            self.entriesInvalid["delivered_at"]["text"] = ""


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
        removalDate = addLeadingZeroes(parameters["removalDate"].get())

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
            showerror(title="Failed to update batches", message="Query failed to update batches. The database has not been altered. Please contact your system administrator")

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
            showerror(title="Failed to add to transactions", message="Query failed to add to transactions. The database has not been altered. Please contact your system administrator")
            # Save details of the failure to the controller
            self.controller.queryData["outcome"] = FAILURE_STRING_G
            # exit the function
            return
        
        conn.commit()
        conn.close()

class CheckBatchPage(ttk.Frame):
    """
    Page frame used to construct a query to get information from the
    batches table

    """    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.centreWindow(400, 400)
        '''Setup datafields for query'''
        # Datafields to store information for the sqlite query
        self.controller.queryData["type"] = TYPE_STRING_CHECK
        self.controller.queryData["parameters"] = {
            "batchId" : tk.IntVar(),
            "name" : tk.StringVar(),
            "delivered_at" : [tk.StringVar(), tk.StringVar()],
            "use_by" : [tk.StringVar(), tk.StringVar()],
            "recorded_in_database" : [tk.StringVar(), tk.StringVar()],
        }
        # assign this variable to shorten the path
        parameters = self.controller.queryData["parameters"]

        # datafields to record if the respective variable field is used
        # This doubles as a flag to show that partiular field
        self.dataUsed = {
            "batchId" : tk.BooleanVar(),
            "name" : tk.BooleanVar(value=True),
            "delivered_at" : tk.BooleanVar(),
            "use_by" : tk.BooleanVar(),
            "recorded_in_database" : tk.BooleanVar(),
        }

        '''Setup and place primary widgets'''
        # Frames to divide the screen between fields/buttons and the results table
        self.sectionFrames = {
            "main" : ttk.Frame(self),
            "results" : ttk.Frame(self)
        }
        # set up grid on main frame

        self.sectionFrames["main"].columnconfigure(index=0, weight=4)
        self.sectionFrames["main"].columnconfigure(index=1, weight=1)

        self.sectionFrames["main"].rowconfigure(index=0, weight=1)
        self.sectionFrames["main"].rowconfigure(index=1, weight=1)
        self.sectionFrames["main"].rowconfigure(index=2, weight=1)

        # Create large container frame for datafields
        self.dataFieldFrame = ttk.Frame(self.sectionFrames["main"])

        for d in self.sectionFrames.values():
            d.pack(fill="both", expand=True)
        
        self.dataFieldFrame.grid(column=0, row=0, rowspan=3)

        '''Setup widgets'''
        # Frames to seperate the two types of batch query: solely batchId, or
        # other
        self.mainFrames = {
            "batchId" : ttk.Frame(self.dataFieldFrame),
            "other" : ttk.Frame(self.dataFieldFrame)
        }

        # subframes to seperate the different query fields.
        self.subFrames = {
            "name" : ttk.Frame(self.mainFrames["other"]),
            "delivered_at" : ttk.Frame(self.mainFrames["other"]),
            "use_by" : ttk.Frame(self.mainFrames["other"]),
            "recorded_in_database" : ttk.Frame(self.mainFrames["other"])
        }


        # Checkboxes to choose which variables to use for the search
        self.checkBoxes = {
            "batchId" : ttk.Checkbutton(
                self.mainFrames["batchId"],
                text="Search for Specific Batch",
                command= self.toggleBatchSearch,
                variable=self.dataUsed["batchId"]),
            "name" : ttk.Checkbutton(
                self.subFrames["name"], 
                text="Search by Stock Name", 
                command=lambda: self.toggleVar["name"], 
                variable=self.dataUsed["name"]),
            "delivered_at" : ttk.Checkbutton(
                self.subFrames["delivered_at"], 
                text="Search by delivery date", 
                command=lambda: self.toggleVar("delivered_at"), 
                variable=self.dataUsed["delivered_at"]),
            "use_by" : ttk.Checkbutton(
                self.subFrames["use_by"], 
                text="Search by use by date", 
                command=lambda: self.toggleVar("use_by"), 
                variable=self.dataUsed["use_by"]),
            "recorded_in_database" : ttk.Checkbutton(
                self.subFrames["recorded_in_database"], 
                text="Search by date batch recorded", 
                command=lambda: self.toggleVar("recorded_in_database"), 
                variable=self.dataUsed["recorded_in_database"])
        }
       # Labelframes for each field
        self.labels = {
            "batchId": ttk.LabelFrame(self.mainFrames["batchId"], text="Batch ID"),
            "name": ttk.LabelFrame(self.subFrames["name"], text="Name/Id Number of Good"),
            "delivered_at": ttk.LabelFrame(self.subFrames["delivered_at"], text="Delivery Date Range (YYYY-MM-DD)"),
            "use_by": ttk.LabelFrame(self.subFrames["use_by"], text="Use By Date Range (YYYY-MM-DD)"),
            "recorded_in_database": ttk.LabelFrame(self.subFrames["recorded_in_database"], text="Recorded Date Range (YYYY-MM-DD)")
        }

        # Entries for each field, bound to the requisite LabelFrame. The three date ranges have attached labels showig if they are to or from
        self.entries = {
            "batchId": ttk.Entry(self.labels["batchId"], textvariable=parameters["batchId"]),
            "name": ttk.Entry(self.labels["name"], textvariable=parameters["name"]),
            "delivered_at": [
                ttk.Entry(self.labels["delivered_at"], textvariable=parameters["delivered_at"][0]),
                ttk.Entry(self.labels["delivered_at"], textvariable=parameters["delivered_at"][1])
            ],
            "use_by": [
                ttk.Entry(self.labels["use_by"], textvariable=parameters["use_by"][0]),
                ttk.Entry(self.labels["use_by"], textvariable=parameters["use_by"][1])
            ],
            "recorded_in_database": [
                ttk.Entry(self.labels["recorded_in_database"], textvariable=parameters["recorded_in_database"][0]),
                ttk.Entry(self.labels["recorded_in_database"], textvariable=parameters["recorded_in_database"][1])
            ]
        }

        '''
        Place datafield widgets
        '''
        # Place datafields
        for d in self.mainFrames.values():
            d.pack(padx=10, anchor=tk.W)
        for d in self.subFrames.values():
            d.pack(anchor=tk.W)
        for d in self.checkBoxes.values():
            d.pack(anchor=tk.W)
        for d in self.labels.values():
            d.pack(padx=10, anchor=tk.W)
        for k, d in self.entries.items():
            if isinstance(d, list):
                # Set up columns in the daterange box
                self.labels[k].rowconfigure(0, weight=1, pad=5)
                self.labels[k].rowconfigure(1, weight=1, pad=5)
                self.labels[k].columnconfigure(0, weight=1)
                self.labels[k].columnconfigure(1, weight=5)
                #Create the labels and bind them to the right places
                ttk.Label(self.labels[k], text="From").grid(column=0, row=0)
                d[0].grid(column=1, row=0)
                ttk.Label(self.labels[k], text="To").grid(column=0, row=1)
                d[1].grid(column=1, row=1)
            else:
                d.pack(anchor=tk.W, padx=10, pady=10)

        # hide unused datafields
        for d in self.dataUsed:
            if not self.dataUsed[d].get():
                self.labels[d].pack_forget()

        '''Place button widgets'''
        self.submitDetails = ttk.Button(self.sectionFrames["main"], text="Submit details", command=self.submitQuery)
        self.submitDetails.grid(column=1, row=0, padx=10)

        # Construct but do not place Button to export to csv
        self.csvButton = ttk.Button(self.sectionFrames["main"], text="Export results to .csv", command= self.exportToCsv)

        # Button to return to main page
        self.backButton = ttk.Button(self.sectionFrames["main"], text="Back", command=lambda: self.controller.showFrame(MainPage))
        self.backButton.grid(column=1, row=2, padx=10)

        # Frame to hold the results of the last submitted query
        self.resultsFrame = ttk.Frame(self)

        # Datafield that will hold the pandastable to show the results when/if it is generated
        self.resultsTable = None


    # construct and submit a query to the database
    def submitQuery(self):
        """
        Constructs a SELECT query based on the data entered and chosen. If no
        data is found, an error message pops up.

        As these functions do not modify the database in any way, they did not
        need the additional layers of protection provided by the validation 
        step.
        """  
        #region sQ
        # Check to see at least one parameter has been entered. If none have 
        # been entered, exit the function   
        noneUsed = True
        for b in self.dataUsed.values():
            if b.get():
                noneUsed = False
                break
        if noneUsed:
            return
        
        parameters = self.controller.queryData["parameters"]

        conn = sql.connect("dbs/stock_database.db")
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")

        # Builds a sql SELECT string a bit at a time, then a tuple to insert
        # the relevant values
        queryString = "SELECT * FROM batches WHERE ("
        queryParameters = []
        # if batchId is used, then that is the only parameter needed for the query
        if self.dataUsed["batchId"].get():
            queryString = queryString + "id = ?"
            queryParameters.append(parameters["batchId"].get())
        else:
            # Use the addAnd flag to add an AND to the start of every
            # additional prompt except the first
            addAnd = ""

            # if name is used, add to query
            if self.dataUsed["name"].get():
                stockId = parameters["name"].get()
                if not stockId.isnumeric():
                    cur.execute("SELECT id FROM stock_names WHERE name = ?", (parameters["name"].get(),))
                    stockId = cur.fetchone()[0]
                queryString = queryString +"stock_id = ?"
                queryParameters.append(stockId)
                addAnd = " AND "
            
            # Create a subdictionary of ranges to iterate over
            dateRangesToExtract = ["delivered_at", "recorded_in_database", "use_by"]
            dateRanges = {key: self.dataUsed[key] for key in dateRangesToExtract if key in self.dataUsed}

            # Iterate over the dateranges, adding them if they are used
            for r in dateRanges:
                if dateRanges[r].get():
                    queryString = queryString + f"{addAnd}{r} >= ? AND {r} <= ?"
                    queryParameters.append(addLeadingZeroes(parameters[r][0].get()))
                    queryParameters.append(addLeadingZeroes(parameters[r][1].get()))
                    addAnd = " AND "
        #Close off the queryString
        queryString = queryString + ")"

        # Use pandas to read the select query
        parameters["result"] = pd.read_sql_query(queryString, conn, params=tuple(queryParameters))
        if not parameters["result"].empty:
            # show export to csv button
            self.csvButton.grid(column=0, row=1, padx=10)

            # Increase size of parent window to display table
            self.controller.centreWindow(800, 600)
            self.csvButton.grid(column=1, row=1, padx=10)
            # show the results frame
            self.sectionFrames["results"].pack(fill="both", expand=True)
            # Turn result pandas dataframe into a pandastable
            self.resultsTable = Table(self.sectionFrames["results"], dataframe=parameters["result"], editable=False, showstatusbar=True)
            # Ensure that the table has completed all setup before displaying
            self.resultsTable.update_idletasks()
            self.resultsTable.show()
            self.resultsTable.redraw()
            self.resultsTable.autoResizeColumns()
        else:
            showerror(title="Check Failed", message="No data found matching this query")
        conn.close()
        #endregion

    def exportToCsv(self):
        """
        Saves the data currently displayed to a csv at a user-defined location.
        """
        #region eTC
        # open window to choose folder location
        fileName = fd.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save exported query"
        )

        if fileName:
            # save file with set name
            self.resultsTable.model.df.to_csv(fileName, index=False)
            showinfo(title="Export complete", message=f"Query results exported to {fileName}.")
        #endregion

    def toggleBatchSearch(self):
        """
        Toggles the others mainFrame off if searching for specific
        batch, or on if not.
        As each batch number has but one match, refining is not necessary
        """ 
        #region tBS
        # If the batchnumber label is visible, toggle it off and display all
        # subframes
        if self.labels["batchId"].winfo_ismapped():
            self.labels["batchId"].pack_forget()
            for f in self.subFrames.values():
                f.pack()

        # If the batchNumber label is not visible, toggle it on and hide all 
        # subframes
        else:
            self.labels["batchId"].pack(anchor=tk.W)
            for f in self.subFrames.values():
                f.pack_forget()
        

    def toggleVar(self, varName, makeVisible = None):
        """Toggle visibility of a varName on or off

        Args:
            varName (string): string identifying which varName is to be toggled

            makeVisible(bool): Boolean that on None toggles, on True turns 
                        varName on, and on False turns varName off
        """
        # If no mode entered, default to toggle
        if makeVisible is None:
            makeVisible = not self.labels[varName].winfo_ismapped()

        if makeVisible:
            self.labels[varName].pack(anchor=tk.W)
        else:
            self.labels[varName].pack_forget()
    
    
class CheckTransactionPage(ttk.Frame):
    """
    Page frame used to construct a query to get information from the
    transactions table

    """    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.centreWindow(400, 600)
        '''Setup datafields for query'''
        # Datafields to store information for the sqlite query
        self.controller.queryData["type"] = TYPE_STRING_CHECK
        self.controller.queryData["parameters"] = {
            "transaction_type" : tk.StringVar(),
            "stock_id" : tk.StringVar(),
            "occured_at" : [tk.StringVar(), tk.StringVar()],
            "recorded_in_database" : [tk.StringVar(), tk.StringVar()],
            "removal_reason" : tk.StringVar()
        }
        # assign this variable to shorten the path
        parameters = self.controller.queryData["parameters"]

        # datafields to record if the respective variable field is used
        # This doubles as a flag to show that partiular field
        self.dataUsed = {
            "transaction_type" : tk.BooleanVar(value=True),
            "stock_id" : tk.BooleanVar(),
            "occured_at" : tk.BooleanVar(),
            "recorded_in_database" : tk.BooleanVar(),
            "removal_reason" : tk.BooleanVar(),
        }

        '''Setup and place primary widgets'''
        # Frames to divide the screen between fields/buttons and the results table
        self.sectionFrames = {
            "main" : ttk.Frame(self),
            "results" : ttk.Frame(self)
        }
        # set up grid on main frame

        self.sectionFrames["main"].columnconfigure(index=0, weight=4)
        self.sectionFrames["main"].columnconfigure(index=1, weight=1)

        self.sectionFrames["main"].rowconfigure(index=0, weight=1)
        self.sectionFrames["main"].rowconfigure(index=1, weight=1)
        self.sectionFrames["main"].rowconfigure(index=2, weight=1)

        # Create large container frame for datafields
        self.dataFieldFrame = ttk.Frame(self.sectionFrames["main"])

        for d in self.sectionFrames.values():
            d.pack(fill="both", expand=True)
        
        self.dataFieldFrame.grid(column=0, row=0, rowspan=3)

        '''Setup widgets'''
        # subframes to seperate the different query fields.
        self.subFrames = {
            "transaction_type" : ttk.Frame(self.dataFieldFrame),
            "stock_id" : ttk.Frame(self.dataFieldFrame),
            "occured_at" : ttk.Frame(self.dataFieldFrame),
            "recorded_in_database" : ttk.Frame(self.dataFieldFrame),
            "removal_reason" : ttk.Frame(self.dataFieldFrame)
        }


        # Checkboxes to choose which variables to use for the search
        self.checkBoxes = {
            "transaction_type" : ttk.Checkbutton(
                self.subFrames["transaction_type"],
                text="Search by Transaction Type",
                command=lambda: self.toggleVar("transaction_type"),
                variable=self.dataUsed["transaction_type"]),
            "stock_id" : ttk.Checkbutton(
                self.subFrames["stock_id"],
                text="Search by Stock Name/id",
                command=lambda: self.toggleVar("stock_id"),
                variable=self.dataUsed["stock_id"]),
            "occured_at" : ttk.Checkbutton(
                self.subFrames["occured_at"], 
                text="Search by date transaction occured", 
                command=lambda: self.toggleVar("occured_at"), 
                variable=self.dataUsed["occured_at"]),
            "recorded_in_database" : ttk.Checkbutton(
                self.subFrames["recorded_in_database"], 
                text="Search by date transaction recorded", 
                command=lambda: self.toggleVar("recorded_in_database"), 
                variable=self.dataUsed["recorded_in_database"]),
            "removal_reason" : ttk.Checkbutton(
                self.subFrames["removal_reason"], 
                text="Search by Reason Removed", 
                command=lambda: self.toggleVar("removal_reason"), 
                variable=self.dataUsed["removal_reason"]),
        }
       # Labelframes for each field
        self.labels = {
            "transaction_type": ttk.LabelFrame(self.subFrames["transaction_type"], text="Transaction type"),
            "stock_id": ttk.LabelFrame(self.subFrames["stock_id"], text="Name/Id Number of Good"),
            "occured_at": ttk.LabelFrame(self.subFrames["occured_at"], text="Transaction Date Range (YYYY-MM-DD)"),
            "recorded_in_database": ttk.LabelFrame(self.subFrames["recorded_in_database"], text="Recorded Date Range (YYYY-MM-DD)"),
            "removal_reason": ttk.LabelFrame(self.subFrames["removal_reason"], text="Removal Reason"),
        }

        # Entries for each field, bound to the requisite LabelFrame. The two date ranges have attached labels showig if they are to or from
        self.entries = {
            "transaction_type": [
                ttk.Radiobutton(self.labels["transaction_type"], text=f"{v}", value=f"{v}", variable=parameters["transaction_type"])
                for v in TRANSACTION_TYPE
            ],
            "stock_id": ttk.Entry(self.labels["stock_id"], textvariable=parameters["stock_id"]),
            "occured_at": [
                ttk.Entry(self.labels["occured_at"], textvariable=parameters["occured_at"][0]),
                ttk.Entry(self.labels["occured_at"], textvariable=parameters["occured_at"][1])
            ],
            "recorded_in_database": [
                ttk.Entry(self.labels["recorded_in_database"], textvariable=parameters["recorded_in_database"][0]),
                ttk.Entry(self.labels["recorded_in_database"], textvariable=parameters["recorded_in_database"][1])
            ],
            "removal_reason": [
                ttk.Radiobutton(self.labels["removal_reason"], text=f"{k}", value=f"{v}", variable=parameters["removal_reason"])
                for k, v in REMOVAL_REASON.items()
            ]
        }

        '''
        Place datafield widgets
        '''
        # Place datafields
        for d in self.subFrames.values():
            d.pack(anchor=tk.W)
        for d in self.checkBoxes.values():
            d.pack(anchor=tk.W)
        for d in self.labels.values():
            d.pack(padx=10, anchor=tk.W)
        for k, d in self.entries.items():
            # If it's a list
            if isinstance(d, list):
                # Check to see if its a list of radiobuttons
                if isinstance(d[0], ttk.Radiobutton):
                    for item in d:
                        item.pack(anchor=tk.W)
                else:
                    # Set up columns in the daterange boxes
                    self.labels[k].rowconfigure(0, weight=1, pad=5)
                    self.labels[k].rowconfigure(1, weight=1, pad=5)
                    self.labels[k].columnconfigure(0, weight=1)
                    self.labels[k].columnconfigure(1, weight=5)
                    #Create the labels and bind them to the right places
                    ttk.Label(self.labels[k], text="From").grid(column=0, row=0)
                    d[0].grid(column=1, row=0)
                    ttk.Label(self.labels[k], text="To").grid(column=0, row=1)
                    d[1].grid(column=1, row=1)
            else:
                d.pack(anchor=tk.W, padx=10, pady=10)

        # hide unused datafields
        for d in self.dataUsed:
            if not self.dataUsed[d].get():
                self.labels[d].pack_forget()

        '''Place button widgets'''
        self.submitDetails = ttk.Button(self.sectionFrames["main"], text="Submit details", command=self.submitQuery)
        self.submitDetails.grid(column=1, row=0, padx=10)

        # Construct but do not place Button to export to csv
        self.csvButton = ttk.Button(self.sectionFrames["main"], text="Export results to .csv", command= self.exportToCsv)

        # Button to return to main page
        self.backButton = ttk.Button(self.sectionFrames["main"], text="Back", command=lambda: self.controller.showFrame(MainPage))
        self.backButton.grid(column=1, row=2, padx=10)

        # Frame to hold the results of the last submitted query
        self.resultsFrame = ttk.Frame(self)

        # Datafield that will hold the pandastable to show the results when/if it is generated
        self.resultsTable = None


    # construct and submit a query to the database
    def submitQuery(self):
        """
        Constructs a SELECT query based on the data entered and chosen. If no
        data is found, an error message pops up. If data is found, a results table
        is displayed.

        As these functions do not modify the database in any way, they did not
        need the additional layers of protection provided by the validation 
        step.
        """  
        #region sQ
        # Check to see at least one parameter has been entered. If none have 
        # been entered, exit the function   
        noneUsed = True
        for b in self.dataUsed.values():
            if b.get():
                noneUsed = False
                break
        if noneUsed:
            return
        
        parameters = self.controller.queryData["parameters"]

        conn = sql.connect("dbs/stock_database.db")
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")

        # Builds a sql SELECT string a bit at a time, then a tuple to insert
        # the relevant values
        queryString = "SELECT * FROM transactions WHERE ("
        queryParameters = []
        # if batchId is used, then that is the only parameter needed for the query

        # Use the addAnd flag to add an AND to the start of every
        # additional prompt except the first
        addAnd = ""


        # if transaction_type is used, add to query
        if self.dataUsed["transaction_type"].get():
            queryString = queryString +"transaction_type = ?"
            queryParameters.append(parameters["transaction_type"].get())
            addAnd = " AND "
        
        # if stock_id is used, add to query
        if self.dataUsed["stock_id"].get():
            stockId = parameters["stock_id"].get()
            if not stockId.isnumeric():
                cur.execute("SELECT id FROM stock_names WHERE name = ?", (parameters["stock_id"].get(),))
                stockId = cur.fetchone()[0]
            queryString = queryString +"stock_id = ?"
            queryParameters.append(stockId)
            addAnd = " AND "
        
        # Create a subdictionary of ranges to iterate over
        dateRangesToExtract = ["delivered_at", "occured_at"]
        dateRanges = {key: self.dataUsed[key] for key in dateRangesToExtract if key in self.dataUsed}

        # Iterate over the dateranges, adding them if they are used
        for r in dateRanges:
            if dateRanges[r].get():
                queryString = queryString + f"{addAnd}{r} >= ? AND {r} <= ?"
                queryParameters.append(addLeadingZeroes(parameters[r][0].get()))
                queryParameters.append(addLeadingZeroes(parameters[r][1].get()))
                addAnd = " AND "
                
        # If removal_reason has been used, add it to the query
        if self.dataUsed["removal_reason"].get():
            queryString = queryString +"removal_reason = ?"
            queryParameters.append(parameters["removal_reason"].get())
            addAnd = " AND "

        #Close off the queryString
        queryString = queryString + ")"

        # Use pandas to read the select query
        parameters["result"] = pd.read_sql_query(queryString, conn, params=tuple(queryParameters))
        if not parameters["result"].empty:
            # show export to csv button
            self.csvButton.grid(column=0, row=1, padx=10)

            # Increase size of parent window to display table
            self.controller.centreWindow(800, 600)
            self.csvButton.grid(column=1, row=1, padx=10)
            # show the results frame
            self.sectionFrames["results"].pack(fill="both", expand=True)
            # Turn result pandas dataframe into a pandastable
            self.resultsTable = Table(self.sectionFrames["results"], dataframe=parameters["result"], editable=False, showstatusbar=True)
            # Ensure that the table has completed all setup before displaying
            self.resultsTable.update_idletasks()
            self.resultsTable.show()
            self.resultsTable.redraw()
            self.resultsTable.autoResizeColumns()
        else:
            showerror(title="Check Failed", message="No data found matching this query")
        conn.close()
        #endregion

    def exportToCsv(self):
        """
        Saves the data currently displayed to a csv at a user-defined location.
        """
        #region eTC
        # open window to choose folder location
        fileName = fd.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save exported query"
        )

        if fileName:
            # save file with set name
            self.resultsTable.model.df.to_csv(fileName, index=False)
            showinfo(title="Export complete", message=f"Query results exported to {fileName}.")
        #endregion


    def toggleVar(self, varName, makeVisible = None):
        """Toggle visibility of a varName on or off

        Args:
            varName (string): string identifying which varName is to be toggled

            makeVisible(bool): Boolean that on None toggles, on True turns 
                        varName on, and on False turns varName off
        """
        #region tV
        # If no mode entered, default to toggle
        if makeVisible is None:
            makeVisible = not self.labels[varName].winfo_ismapped()

        if makeVisible:
            self.labels[varName].pack(anchor=tk.W)
        else:
            self.labels[varName].pack_forget()
        #endregion
  

class CheckStockPage(ttk.Frame):
    """
    Page frame used to construct a query to get information from the
    batches table

    """    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.centreWindow(400, 400)
        '''Setup datafields for query'''
        # Datafields to store information for the sqlite query
        self.controller.queryData["type"] = TYPE_STRING_CHECK
        self.controller.queryData["parameters"] = {
            "stock_id" : tk.StringVar(),
        }
        # assign this variable to shorten the path
        parameters = self.controller.queryData["parameters"]

        # datafields to record if the respective variable field is used
        # This doubles as a flag to show that partiular field
        self.dataUsed = {
            "full_inventory" : tk.BooleanVar(value=True),
            "stock_id" : tk.BooleanVar(),
        }

        '''Setup and place primary widgets'''
        # Frames to divide the screen between fields/buttons and the results table
        self.sectionFrames = {
            "main" : ttk.Frame(self),
            "results" : ttk.Frame(self)
        }
        # set up grid on main frame

        self.sectionFrames["main"].columnconfigure(index=0, weight=4)
        self.sectionFrames["main"].columnconfigure(index=1, weight=1)

        self.sectionFrames["main"].rowconfigure(index=0, weight=1)
        self.sectionFrames["main"].rowconfigure(index=1, weight=1)
        self.sectionFrames["main"].rowconfigure(index=2, weight=1)

        # Create large container frame for datafields
        self.dataFieldFrame = ttk.Frame(self.sectionFrames["main"])

        for d in self.sectionFrames.values():
            d.pack(fill="both", expand=True)
        
        self.dataFieldFrame.grid(column=0, row=0, rowspan=3)

        '''Setup widgets'''
        # Frames to seperate the two types of batch query: solely fullInventory, or
        # other
        self.mainFrames = {
            "full_inventory" : ttk.Frame(self.dataFieldFrame),
            "other" : ttk.Frame(self.dataFieldFrame)
        }

        # subframes to seperate the different query fields.
        self.subFrames = {
            "stock_id" : ttk.Frame(self.mainFrames["other"]),
        }


        # Checkboxes to choose which variables to use for the search
        self.checkBoxes = {
            "full_inventory" : ttk.Checkbutton(
                self.mainFrames["full_inventory"],
                text="Show full inventory",
                variable=self.dataUsed["full_inventory"]),
            "stock_id" : ttk.Checkbutton(
                self.subFrames["stock_id"], 
                text="Search by Stock Name", 
                command=lambda: self.toggleVar("stock_id"), 
                variable=self.dataUsed["stock_id"]),
        }
       # Labelframes for each field
        self.labels = {
            "stock_id": ttk.LabelFrame(self.subFrames["stock_id"], text="Name/Id Number of Good"),
        }

        # Entries for each field, bound to the requisite LabelFrame. The three date ranges have attached labels showig if they are to or from
        self.entries = {
            "stock_id": ttk.Entry(self.labels["stock_id"], textvariable=parameters["stock_id"]),
        }

        '''
        Place datafield widgets
        '''
        # Place datafields
        for d in self.mainFrames.values():
            d.pack(padx=10, anchor=tk.W)
        for d in self.subFrames.values():
            d.pack(anchor=tk.W)
        for d in self.checkBoxes.values():
            d.pack(anchor=tk.W)
        for d in self.labels.values():
            d.pack(padx=10, anchor=tk.W)
        for k, d in self.entries.items():
            d.pack(anchor=tk.W, padx=10, pady=10)

        # hide unused datafields
        for d in self.dataUsed:
            if not self.dataUsed[d].get():
                self.labels[d].pack_forget()

        '''Place button widgets'''
        self.submitDetails = ttk.Button(self.sectionFrames["main"], text="Submit details", command=self.submitQuery)
        self.submitDetails.grid(column=1, row=0, padx=10)

        # Construct but do not place Button to export to csv
        self.csvButton = ttk.Button(self.sectionFrames["main"], text="Export results to .csv", command= self.exportToCsv)

        # Button to return to main page
        self.backButton = ttk.Button(self.sectionFrames["main"], text="Back", command=lambda: self.controller.showFrame(MainPage))
        self.backButton.grid(column=1, row=2, padx=10)

        # Frame to hold the results of the last submitted query
        self.resultsFrame = ttk.Frame(self)

        # Datafield that will hold the pandastable to show the results when/if it is generated
        self.resultsTable = None


    # construct and submit a query to the database
    def submitQuery(self):
        """
        Constructs a SELECT query based on the data entered and chosen. If no
        data is found, an error message pops up.

        As these functions do not modify the database in any way, they did not
        need the additional layers of protection provided by the validation 
        step.
        """  
        # Check to see at least one parameter has been entered. If none have 
        # been entered, exit the function   
        noneUsed = True
        for b in self.dataUsed.values():
            if b.get():
                noneUsed = False
                break
        if noneUsed:
            return
        
        parameters = self.controller.queryData["parameters"]

        conn = sql.connect("dbs/stock_database.db")
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")

        queryString = "SELECT * FROM stock_names"
        # If the search is of one specific stock, add that stock onto the end 
        # of this query and execute. 
        # Otherwise, select the whole table
        query = None
        if self.dataUsed["stock_id"].get():
            stockId = parameters["stock_id"].get()
            if not stockId.isnumeric():
                cur.execute("SELECT id FROM stock_names WHERE name = ?", (parameters["stock_id"].get(),))
                stockId = cur.fetchone()[0]
            queryString = queryString +" WHERE (id = ?)"
            query = pd.read_sql_query(queryString, conn, params=(stockId,))
        else:
            query = pd.read_sql_query(queryString, conn)
        
        quantities = []
        # Iterate over the list of stock. Get the name, use it to run a search 
        # of batches of that stock. Tally up the total quantity_current, and
        # append that to quantities.
        for row in query.itertuples(index=False):
            batches = pd.read_sql_query("SELECT quantity_current FROM batches WHERE stock_id = ?", conn, params=(row.id,))
            quantity = 0
            # Get current stock remaining in batches
            for q in batches.itertuples(index=False):
                print(f"{q}")
                quantity = quantity + int(q.quantity_current)
            quantities.append(quantity)
        
        query["quantity"] = quantities
        parameters["result"] = query
        if not parameters["result"].empty:
            # show export to csv button
            self.csvButton.grid(column=0, row=1, padx=10)

            # Increase size of parent window to display table
            self.controller.centreWindow(800, 600)
            self.csvButton.grid(column=1, row=1, padx=10)
            # show the results frame
            self.sectionFrames["results"].pack(fill="both", expand=True)
            # Turn result pandas dataframe into a pandastable
            self.resultsTable = Table(self.sectionFrames["results"], dataframe=parameters["result"], editable=False, showstatusbar=True)
            # Ensure that the table has completed all setup before displaying
            self.resultsTable.update_idletasks()
            self.resultsTable.show()
            self.resultsTable.redraw()
            self.resultsTable.autoResizeColumns()
        else:
            showerror(title="Check Failed", message="No data found matching this query")
        conn.close()

    def exportToCsv(self):
        # open window to choose folder location
        fileName = fd.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save exported query"
        )

        if fileName:
            # save file with set name
            self.resultsTable.model.df.to_csv(fileName, index=False)
            showinfo(title="Export complete", message=f"Query results exported to {fileName}.")
            

    def toggleVar(self, varName, makeVisible = None):
        """Toggle visibility of a varName on or off

        Args:
            varName (string): string identifying which varName is to be toggled

            makeVisible(bool): Boolean that on None toggles, on True turns 
                        varName on, and on False turns varName off
        """
        # If no mode entered, default to toggle
        if makeVisible is None:
            makeVisible = not self.labels[varName].winfo_ismapped()

        if makeVisible:
            self.labels[varName].pack(anchor=tk.W)
        else:
            self.labels[varName].pack_forget()
    