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

def addLeadingZeroes(date):
    """Adds leading zeroes before dates are added to the database to allow them to be compared

    Args:
        date (string): A string in the form "YYYY-M-D"

    Returns:
        string: A String in the form "YYYY-MM-DD"
    """    
    dtList = date.split("-")

    for d in range(len(dtList)):
        if len(dtList[d]) < 2:
            dtList[d] = f"0{dtList[d]}"

    return f"{dtList[0]}-{dtList[1]}-{dtList[2]}"

def dateLessThan(date1, date2):
    return datetime.strptime(date1, "%Y-%m-%d").date() < datetime.strptime(date2, "%Y-%m-%d").date()

def getCurrentDateTime():
    now = datetime.now()
    return now.strftime("%Y_%m_%d_%H_%M_%S")