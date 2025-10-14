# This file defines the query classes that will be used to check, construct,
# and execute the sqlite3 queries.

# See the UML diagram for a clearer picture of their relationship to each other
from abc import ABC, abstractmethod
from enum import Enum
import tkinter as tk
from tkinter import ttk
import sqlite3 as sql

from A1_inventory_management.utils.query_classes_valid import isDate, dateInFuture


########################
## enum RemovalReason ##
########################
# Enum used to record the reason for goods being removed from a batch
class RemovalReason(Enum):
    USED        = 0
    OUT_OF_DATE = 1
    RETURNED    = 2
    LOST        = 3
    DESTROYED   = 4

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
        self.data = {
            "query" : ""
        }

        self.showFrame(MainPage)
        
    # Method to display a new frame of a set class
    def showFrame(self, frameClass):
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
        self.exitButton = ttk.Button(self, text="exit", command=self.destroy).pack()

###################
## class AddPage ##
###################
# Frame to display data to construct a query to add data to a sqlite database
class AddPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Datafields to store information for the sqlite query
        self.data = {
            "name" : tk.StringVar(),
            "quantity" : tk.IntVar(),
            "deliveryDate" : tk.StringVar(),
            "useByDate" : tk.StringVar(),
            "batchNumber" : tk.IntVar(),
        }
        # datafields to record if the respective variable field is valid
        self.dataValid = {
            "name" : None,
            "quantity" : None,
            "deliveryDate" : None,
            "useByDate" : None,
            "batchNumber" : None,
        }

        # Store for labels for each member of self.data
        self.labels = {
            "name": ttk.Label(self, text="Name of Good"),
            "batchNumber": ttk.Label(self, text="Batch Number(optional)"),
            "quantity": ttk.Label(self, text="Quantity of good"),
            "deliveryDate": ttk.Label(self, text="Delivery Date (YYYY-MM-DD)"),
            "useByDate": ttk.Label(self, text="Use By Date (YYYY-MM-DD)")
        }
        # store for entries for each member of self.data
        self.entries = {
            "name": ttk.Entry(self, textvariable=self.data["name"]),
            "batchNumber": ttk.Entry(self, textvariable=self.data["batchNumber"]),
            "quantity": ttk.Entry(self, textvariable=self.data["quantity"]),
            "deliveryDate": ttk.Entry(self, textvariable=self.data["deliveryDate"]),
            "useByDate": ttk.Entry(self, textvariable=self.data["useByDate"])
        }
        # store for input error warnings for each member of self.data
        # These will be modified to display text if any fields are found to 
        # contain invalid data
        self.entriesInvalid = {
            "name": ttk.Label(self, text=""),
            "batchNumber": ttk.Label(self, text=""),
            "quantity": ttk.Label(self, text=""),
            "deliveryDate": ttk.Label(self, text=""),
            "useByDate": ttk.Label(self, text="")
        }
        self.submitButton = ttk.Button(self, text="Submit details", command=self.checkValid)
        # Loop to display labels, entries, and invalids
        # I chose to seperate them like this because each type of tkinter 
        # object may need to be displayed in their own style, and this allows 
        # for that.
        for dataField in self.labels:
            self.labels[dataField].pack()
            self.entries[dataField].pack()
            self.entriesInvalid[dataField].pack()

        self.submitButton.pack()


    # make sure that values entered are all valid
    def checkValid(self):
        # use flag to see if any data are incorrectly formatted
        allValid = True
        # check name is valid by running a quick sqlite query
        conn = sql.connect("dbs/stock_database.db")
        cur = conn.cursor()
        cur.execute('SELECT name FROM stock_names WHERE name = ?', (self.data["name"].get().lower(),))
        if len(cur.fetchall()) > 0:
            self.dataValid["name"] = True
        else:
            self.dataValid["name"] = False
            allValid = False

         # If they have set the batch number to anything, then check to see that it exists in the database
         # This is placed here so the connection can be closed as soon as possible
         # batchNumberUsed is used to tell displayInvalid if the batchNumber was used
        batchNumberUsed = False
        if self.data["batchNumber"] != 0:
            batchNumberUsed = True
            cur.execute('SELECT id FROM batches WHERE id = ?', (self.data["batchNumber"].get(),))
            if len(cur.fetchall()) > 0:
                self.dataValid["batchNumber"] = True
            else:
                self.dataValid["batchNumber"] = False
                allValid = False
        conn.close()
        
        # Ensure that quantity is an integer and is greater than 0
        # IntVar objects reset their value to 0 if a non-integer is entered, 
        # so this test checks both parameters
        if self.data["quantity"].get() > 0:
            self.dataValid["quantity"] = True
        else:
            self.dataValid["quantity"] = False
            allValid = False

        # Ensure that the delivery date is formatted correctly (yyyy-mm-dd), 
        # that all parts are possible (eg, no 13th month), and that it is not in 
        # the future
        if isDate(self.data["deliveryDate"].get()) and not dateInFuture(self.data["deliveryDate"].get()):
            self.dataValid["deliveryDate"] = True
        else:
            self.dataValid["deliveryDate"] = False
            allValid = False

        # Ensure that the use by date is formatted correctly (yyyy-mm-dd),
        # that all parts are possible (eg, no 13th month), and that it is in 
        # the future
        if isDate(self.data["useByDate"].get()) and dateInFuture(self.data["useByDate"].get()):
            self.dataValid["useByDate"] = True
        else:
            self.dataValid["useByDate"] = False
            allValid = False

        if allValid:
            self.submitQuery(batchNumberUsed)
            self.controller.showFrame(ResultsPage)
        else:
            self.displayInvalid(batchNumberUsed)

    # Display error messages for incorrectly entered datafields
    def displayInvalid(self, batchNumberUsed):
        # Check each datafield in turn, and if it has been flagged as invalid, 
        # display an error message
        if not self.dataValid["name"]:
            self.entriesInvalid["name"]["text"] = "Name was invalid. Ensure that name is present in the database and check spelling"
        if not self.dataValid["batchNumber"] and batchNumberUsed:
            self.entriesInvalid["batchNumber"]["text"] ="Batch Number was invalid. If not using, set to zero, or ensure that batch number is present in the database"
        if not self.dataValid["quantity"]:
            self.entriesInvalid["quantity"]["text"]= "Quantity is invalid. Ensure that it is a positive whole number"
        if not self.dataValid["deliveryDate"]:
            self.entriesInvalid["deliveryDate"]["text"] = "Delivery date was invalid. Ensure that it is in the form YYYY-MM-DD, that it is a possible date, and that it is not in the future"
        if not self.dataValid["useByDate"]:
            self.entriesInvalid["useByDate"]["text"] = "Use by date was invalid. Ensure that it is in the form YYYY-MM-DD, that it is a possible date, and that it is in the future"

    # construct and submit a query to the database
    def submitQuery(self, batchNumberUsed):
        conn = sql.connect("dbs/stock_database.db")
        cur = conn.cursor()
        if batchNumberUsed is True:
            pass
            # get current quantity
            # update quantity
        else:
            pass


class RemovePage(ttk.Frame):
    def __init__(self, parent, controller):
        pass

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
        pass
#######################
## class RemoveQuery ##
#######################
# Class used to remove quantity from batches
# Does not currently remove batches, as the current architecture holds on to
# batch information for archival and auditing purposes - removal of batches is
# a planned feature to add in subsequent updates.
class RemoveQuery():
    def __init__(self):
        super().__init__()
        self.__batchNumber = -1
        self.__batchNumberValid = False
        self.__quantity = -1
        self.__quantityValid = False
        self.__removalDate = ""
        self.__removalDateValid = False
        self.__removalReason = RemovalReason.USED
        self.__removalReasonValid = False


    def displayOptions(self, window):
        raise NotImplementedError("RemoveQuery.displayOptions not implemented")

    def checkValid(self):
        raise NotImplementedError("RemoveQuery.checkValid not implemented")
    
    def displayInvalid(self):
        raise NotImplementedError("RemoveQuery.displayInvalid not implemented")
    
    def constructQuery(self):
        raise NotImplementedError("RemoveQuery.constructQuery not implemented")

    def updateDatabase(self):
        raise NotImplementedError("RemoveQuery.updateDatabase not implemented")


######################
## class CheckQuery ##
######################
# Abstract class used to add the outputToCSV method to the 3 (as of 9/10/25)
# xCheckQuery classes
class CheckQuery():
    @abstractmethod
    def outputToCSV(self):
        pass


#################################
## class TransactionCheckQuery ##
#################################
# Class used to get information about specific transations
class TransactionCheckQuery(CheckQuery):
    def __init__(self):
        super().__init__(self)
        self.__transactionType = TransactionType.ADD
        self.__batchNumber = -1
        self.__batchNumberValid = False
        self.__stockName = ""
        self.__stockNameValid = False
        self.__dateRange = ["", ""]
        self.__dateRangeValid = False
        self.__removalReason = RemovalReason.USED
        self.__removalReasonValid = False

    def displayOptions(self, window):
        raise NotImplementedError("TransactionCheckQuery.displayOptions not implemented")

    def checkValid(self):
        raise NotImplementedError("TransactionCheckQuery.checkValid not implemented")
    
    def displayInvalid(self):
        raise NotImplementedError("TransactionCheckQuery.displayInvalid not implemented")
    
    def constructQuery(self):
        raise NotImplementedError("TransactionCheckQuery.constructQuery not implemented")

    def updateDatabase(self):
        raise NotImplementedError("TransactionCheckQuery.updateDatabase not implemented")
    
    def outputToCSV(self):
        raise NotImplementedError("TransactionCheckQuery.outputToCSV not implemented")


###########################
## class BatchCheckQuery ##
###########################
# Class used to get information about specific batches, or to get a batch
# number.
class BatchCheckQuery(CheckQuery):
    def __init__(self):
        super().__init__(self)
        self.__batchNumber = -1
        self.__batchNumberValid = False
        self.__stockName = ""
        self.__stockNameValid = False
        self.__dateRange = ["", ""]
        self.__dateRangeValid = False

    def displayOptions(self, window):
        raise NotImplementedError("BatchCheckQuery.displayOptions not implemented")

    def checkValid(self):
        raise NotImplementedError("BatchCheckQuery.checkValid not implemented")
    
    def displayInvalid(self):
        raise NotImplementedError("BatchCheckQuery.displayInvalid not implemented")
    
    def constructQuery(self):
        raise NotImplementedError("BatchCheckQuery.constructQuery not implemented")

    def updateDatabase(self):
        raise NotImplementedError("BatchCheckQuery.updateDatabase not implemented")
    
    def outputToCSV(self):
        raise NotImplementedError("BatchCheckQuery.outputToCSV not implemented")

###########################
## class StockCheckQuery ##
###########################
# Class used to get information about stock at various points in time.
class StockCheckQuery(CheckQuery):
    def __init__(self):
        super().__init__(self)
        self.__allStock = False
        self.__stockList = [""]
        self.__stockListValid = False
        self.__atDate = ""
        self.__atDateValid = False

    def displayOptions(self, window):
        raise NotImplementedError("StockCheckQuery.displayOptions not implemented")

    def checkValid(self):
        raise NotImplementedError("StockCheckQuery.checkValid not implemented")
    
    def displayInvalid(self):
        raise NotImplementedError("StockCheckQuery.displayInvalid not implemented")
    
    def constructQuery(self):
        raise NotImplementedError("StockCheckQuery.constructQuery not implemented")

    def updateDatabase(self):
        raise NotImplementedError("StockCheckQuery.updateDatabase not implemented")
    
    def outputToCSV(self):
        raise NotImplementedError("StockCheckQuery.outputToCSV not implemented")
    
    
