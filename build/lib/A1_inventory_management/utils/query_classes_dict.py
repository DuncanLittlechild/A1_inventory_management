import A1_inventory_management.query_classes as qc

checkStockClassesList = {
    "batchCheck"       : qc.BatchCheckQuery,
    "transactionCheck" : qc.TransactionCheckQuery,
    "stockCheck"       : qc.StockCheckQuery
}

alterStockClassesList = {
    "remove"           : qc.RemoveQuery,
    "add"              : qc.AddQuery,
}