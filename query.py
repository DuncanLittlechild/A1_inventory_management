# This file defines the query classes that will be used to check, construct,
# and execute the sqlite3 queries.

# See the UML diagram for a clearer picture of their relationship to each other

#####################
## class BaseQuery ##
#####################
# This class creates the template that the other Query classes must follow

# These functions are declared here as virtual functions to ensure that they
# are implemented by all children, to ensure that this basic functionality is
# properly implemented across the board.


####################
## class AddQuery ##
####################
# Class used to add new batches, or to increase the quantity recorded in a
# batch.
# The ability to increase quantity in a batch was added to account for lost 
# or incorrectly entered inventory.


#######################
## class RemoveQuery ##
#######################
# Class used to remove quantity from batches
# Does not currently remove batches, as the current architecture holds on to
# batch information for archival and auditing purposes - removal of batches is
# a planned feature to add in subsequent updates.


######################
## class CheckQuery ##
######################
# Abstract class that serves to add the displayOptions() abstract function to
# the three (as of 08/10/2025) children of this class. As above, this is
# primarily done to ensure that the class is actually implemented, and not
# neglected.


#################################
## class TransactionCheckQuery ##
#################################
# Class used to get information about specific transations


###########################
## class BatchCheckQuery ##
###########################
# Class used to get information about specific batches, or to get a batch
# number.


###########################
## class StockCheckQuery ##
###########################
# Class used to get information about stock at various points in time.