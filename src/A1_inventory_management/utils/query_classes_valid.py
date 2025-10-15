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

def removeLeadingZeroes(date):
    dt = datetime.strptime(date, "%Y-%m-%d").date()
    return f"{dt.year}-{dt.month}-{dt.day}"

def dateLessThan(date1, date2):
    return datetime.strptime(date1, "%Y-%m-%d").date() < datetime.strptime(date2, "%Y-%m-%d").date()