# This file defines the query classes that will be used to check, construct,
# and execute the sqlite3 queries.

# See the UML diagram for a clearer picture of their relationship to each other
from abc import ABC, abstractmethod
from enum import Enum
import tkinter as tk
from tkinter import ttk
import sqlite3 as sql


from A1_inventory_management.utils.tkinter_tools import clearWindow
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

#####################
## class BaseQuery ##
#####################
# This class creates the template that the other Query classes must follow
class BaseQuery(ABC):
    def __init__(self):
        self.valid = False
        self.__query = ""
        self.__queryAdded = False
        self.__window = tk.Tk()

# These functions are declared here as virtual functions to ensure that they
# are implemented by all children, to ensure that this basic functionality is
# properly implemented across the board.

# displayOptions alters the Tkiter widget to display the options that the user
# has to fine tune the query they want to run
    @abstractmethod
    def displayOptions(self, window):
        pass

# checkValid checks each member variable __x that has a __xValid flag
# attached to it, and makes sure that __x is valid. If it is, then __xValid is
# set to True; if it is not, then _xValid is set to false. If every variable
# that fits this pattern is valid, the overall __valid flag is set to True;
# otherwise, __valid is set to/remains False
    @abstractmethod
    def checkValid(self):
        pass

# displayInvalid alters the Tkinter widget to display those variables __x that
# have their __xValid flag set to false, with information about what a valid
# instance of that variable should be
    @abstractmethod
    def displayInvalid(self):
        pass

# constructQuery is used to construct the sqlite3 query as a string. This part
# does not directly use any user input, but rather uses the data in the class
# instance to construct a query that contains the datafields the user wants
    @abstractmethod
    def constructQuery(self):
        pass

# updateDatabase submits the completed query to the sqlite3 database, and
# checks to make sure that the query was successfully recieved
    @abstractmethod
    def updateDatabase(self):
        pass


####################
## class AddQuery ##
####################
# Class used to add new batches, or to increase the quantity recorded in a
# batch.
# The ability to increase quantity in a batch was added to account for lost 
# or incorrectly entered inventory.
class AddQuery(BaseQuery):
    def __init__(self):
        super().__init__()
        self.__name = ""
        self.__nameValid = False
        self.__quantity = -1
        self.__quantityValid = False
        self.__deliveryDate = ""
        self.__deliveryDateValid = False
        self.__useByDate = ""
        self.__useByDateValid = False
        self.__batchNumber = -1
        self.__batchNumberValid = False


    def displayOptions(self, window):
        clearWindow(window)
        # Allow users to enter the relevant details about the stock to be added
        window.title('Enter data about new stock')

        nameLabel = ttk.Label(window, text="Name of Good").pack()
        nameVar = tk.StringVar()
        nameEntry = ttk.Entry(window, textvariable=nameVar).pack()

        batchNumberLabel = ttk.Label(window, text="Batch Number(optional, only for adding missed goods to existing batch)").pack()
        batchNumberVar = tk.StringVar()
        batchNumberEntry = ttk.Entry(window, textvariable=batchNumberVar).pack()

        quantityLabel = ttk.Label(window, text="Quantity of good").pack()
        quantityVar = tk.IntVar()
        quantityEntry = ttk.Entry(window, textvariable=quantityVar).pack()

        deliveryDateLabel = ttk.Label(window, text="Delivery Date (YYYY-MM-DD)").pack()
        deliveryDateVar = tk.StringVar()
        deliveryDateEntry = ttk.Entry(window, textvariable=deliveryDateVar).pack()

        useByDateLabel = ttk.Label(window, text="Use By Date (YYYY-MM-DD)").pack()
        useByDateVar = tk.StringVar()
        useByDateEntry = ttk.Entry(window, textvariable=useByDateVar).pack()


        # On submission, check to make sure all values are valid before adding them to the object.
        submitButton = ttk.Button(window, text="Submit details", command=lambda: self.checkValid(nameVar.get(), quantityVar.get(), deliveryDateVar.get(), useByDateVar.get(), batchNumberVar.get(), window)).pack()

    def checkValid(self, nameVar, quantityVar, deliveryDateVar, useByDateVar, batchNumberVar, window):
        # check name is valid by running a quick sqlite query
        conn = sql.connect("dbs/stock_database.db")
        cur = conn.cursor()
        cur.execute('SELECT name FROM stock_names WHERE name = ?', (nameVar.lower(),))
        if len(cur.fetchall()) > 0:
            self.__name = nameVar.lower()
            self.__nameValid = True
            print("name valid")
        else:
            print("name not valid")
            self.__nameValid = False
            self.valid = False

         # If they have set the batch number to anything, then check to see that it exists in the database
         # This is placed here so the connection can be closed as soon as possible
         # batchNumberUsed is used to tell displayInvalid if the batchNumber was used
        batchNumberUsed = False
        if batchNumberVar != 0:
            batchNumberUsed = True
            cur.execute('SELECT id FROM batches WHERE id = ?', (batchNumberVar,))
            if len(cur.fetchall()) > 0:
                self.__batchNumber = batchNumberVar
                self.__batchNumberValid = True
                print("Batch number valid")
            else:
                print("batch number not valid")
                self.__batchNumberValid = False
                self.valid = False
        conn.close()
        
        # Ensure that quantity is an integer and is greater than 0
        # IntVar objects reset their value to 0 if a non-integer is entered, 
        # so this test checks both parameters
        if quantityVar > 0:
            self.__quantity = quantityVar
            self.__quantityValid = True
            print("quantity valid")
        else:
            print("quantity not valid")
            self.__quantityValid = False
            self.valid = False

        # Ensure that the delivery date is formatted correctly (yyyy-mm-dd), 
        # that all parts are possible (eg, no 13th month), and that it is not in 
        # the future
        if isDate(deliveryDateVar) and not dateInFuture(deliveryDateVar):
            self.__deliveryDate = deliveryDateVar
            self.__deliveryDateValid = True
            print("delivery date valid")
        else:
            print("delivery date not valid")
            self.__deliveryDateValid = False
            self.valid = False

        # Ensure that the use by date is formatted correctly (yyyy-mm-dd),
        # that all parts are possible (eg, no 13th month), and that it is in 
        # the future
        if isDate(useByDateVar) and dateInFuture(useByDateVar):
            self.__useByDate = deliveryDateVar
            self.__useByDateValid = True
            print("use by date valid")
        else:
            print("use by date not valid")
            self.__deliveryDateValid = False
            self.valid = False

        if not self.valid:
            self.displayInvalid(window, batchNumberUsed)

        

    def displayInvalid(self, window, batchNumberUsed):
        clearWindow(window)
        invalidLabel = ttk.Label(window, text="You entered invalid data").pack()
        nameInvalidLabel = None
        batchNumberInvalidLabel = None
        quantityInvalidLabel = None
        deliveryDateInvalidLabel = None
        useByDateInvalidLabel = None
        if not self.__nameValid:
            nameInvalidLabel = ttk.Label(window, text="Name was invalid. Ensure that name is present in the database and check spelling").pack()
        if not self.__batchNumberValid and batchNumberUsed:
            batchNumberInvalidLabel = ttk.Label(window, text="Batch Number was invalid. If not using, set to zero, or ensure that batch number is present in the database").pack()
        if not self.__quantityValid:
            quantityInvalidLabel = ttk.Label(window, text="Quantity is invalid. Ensure that it is a positive whole number").pack()
        if not self.__deliveryDateValid:
            deliveryDateInvalidLabel = ttk.Label(window, text="Delivery date was invalid. Ensure that it is in the form YYYY-MM-DD, that it is a possible date, and that it is not in the future").pack()
        if not self.__useByDateValid:
            useByDateInvalidLabel = ttk.Label(window, text="Use by date was invalid. Ensure that it is in the form YYYY-MM-DD, that it is a possible date, and that it is in the future").pack()
        return

    def constructQuery(self):
        raise NotImplementedError("AddQuery.constructQuery not implemented")

    def updateDatabase(self):
        raise NotImplementedError("AddQuery.updateDatabase not implemented")


#######################
## class RemoveQuery ##
#######################
# Class used to remove quantity from batches
# Does not currently remove batches, as the current architecture holds on to
# batch information for archival and auditing purposes - removal of batches is
# a planned feature to add in subsequent updates.
class RemoveQuery(BaseQuery):
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
class CheckQuery(BaseQuery):
    @abstractmethod
    def outputToCSV(self):
        pass


#################################
## class TransactionCheckQuery ##
#################################
# Class used to get information about specific transations
class TransactionCheckQuery(CheckQuery):
    def __init__(self):
        BaseQuery.__init__(self)
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
        BaseQuery.__init__(self)
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
        BaseQuery.__init__(self)
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
    
    