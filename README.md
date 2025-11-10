# A1-inventory-management
Inventory management system to track new stock and removal of stock. It uses tkinter to display pages where stock can be added, removed, or checked against a sqlite3 database. It is verified for python 3.12 onwards, and can run on either windows or linux.

The project stores stock data in batches, which have a stock type, an initial quantity, a current quantity and a use by date. The date and time of database changes is also stored for auditing purposes. Batches can be added, and then have their current quantity modified, with the information of when and why the removal was performed recorded.

To enter a stock type, it must be known by the database. Currently there is no way to add additional stock types directly, however the database setup comes with four stock types built in: 'nuts', 'steel plates', 'screws', and 'folding chairs'.

## How to install
1. Download the zip and extract to a location of your choice
2. Navigate to that folder and open a command line prompt in it by typing cmd and enter into the address bar
3. Set up a virtual environment using python3 -m venv .venv
4. Activate it with .venv\Scripts\activate (windows) or source .venv/bin/activate (linux)
5. Run the project using using "python3 main.py" in the command line