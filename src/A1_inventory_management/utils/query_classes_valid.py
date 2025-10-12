from datetime import datetime

def isDate(date):
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False
    
def dateInFuture(date):
    dateCompare = datetime.strptime(date, "%Y-%m-%d").date()
    return dateCompare > datetime.now().date()