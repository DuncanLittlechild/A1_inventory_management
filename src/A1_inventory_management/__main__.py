import A1_inventory_management.query_classes as qc
from A1_inventory_management.core import initialiseDb

if __name__ == "__main__":
    initialiseDb()
    app = qc.App()
    app.mainloop()