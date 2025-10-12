# This file defines the query classes that will be used to check, construct,
# and execute the sqlite3 queries.

# See the UML diagram for a clearer picture of their relationship to each other
from abc import ABC, abstractmethod
from enum import Enum
import tkinter as tk


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
        self.__valid = False
        self.__query = ""
        self.__queryAdded = False
        self.__window = tk.Tk()

# These functions are declared here as virtual functions to ensure that they
# are implemented by all children, to ensure that this basic functionality is
# properly implemented across the board.

# displayOptions alters the Tkiter widget to display the options that the user
# has to fine tune the query they want to run
    @abstractmethod
    def displayOptions(self):
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
        super().__init__
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


    def displayOptions(self):
        raise NotImplementedError("AddQuery.displayOptions not implemented")

    def checkValid(self):
        raise NotImplementedError("AddQuery.checkValid not implemented")
    
    def displayInvalid(self):
        raise NotImplementedError("AddQuery.displayInvalid not implemented")
    
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
        super().__init__
        self.__batchNumber = -1
        self.__batchNumberValid = False
        self.__quantity = -1
        self.__quantityValid = False
        self.__removalDate = ""
        self.__removalDateValid = False
        self.__removalReason = RemovalReason.USED
        self.__removalReasonValid = False


    def displayOptions(self):
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

    def displayOptions(self):
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

    def displayOptions(self):
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

    def displayOptions(self):
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
    
    