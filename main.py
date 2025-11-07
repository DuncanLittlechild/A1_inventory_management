import subprocess
import sys

try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
except:
    print("Error installing core requirements")

import A1_inventory_management.core as core
import A1_inventory_management.database_init as db

db.initialiseDb()
app = core.App()
app.mainloop()

