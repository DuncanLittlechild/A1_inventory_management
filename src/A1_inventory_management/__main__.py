import A1_inventory_management.core as qc
from A1_inventory_management.database_init import initialiseDb

if __name__ == "__main__":
    initialiseDb()
    app = qc.App()
    app.mainloop()