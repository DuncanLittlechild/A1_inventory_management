import A1_inventory_management.query_classes as qc

'''
These dicts are used as a centralised list of all current query objects. 

To add new query objects, first instantiate them as children of BaseQuery 
or CheckQuery depending on if they write or read to the database 
respectively, and then add them to the respective dictionary using the text 
you want to appear on the button as the key and the class as the value.
'''
alterStockClassesList = {
    "add"              : qc.AddQuery,
    "remove"           : qc.RemoveQuery,
}

checkStockClassesList = {
    "checkBatches"       : qc.BatchCheckQuery,
    "checkTransactions" : qc.TransactionCheckQuery,
    "checkStock"       : qc.StockCheckQuery
}
