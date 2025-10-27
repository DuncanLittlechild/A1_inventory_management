CREATE TABLE IF NOT EXISTS stock_names (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL CHECK (LENGTH(name) <= 50)
);

INSERT OR IGNORE INTO stock_names (name)
VALUES
    ('nuts'),
    ('steel plates'),
    ('screws'),
    ('folding chairs')

CREATE TABLE IF NOT EXISTS batches (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  stock_id INTEGER NOT NULL,
  quantity_initial INTEGER NOT NULL CHECK (quantity_initial >= 0),
  quantity_current INTEGER NOT NULL CHECK (quantity_current >= 0),
  delivered_at TEXT CHECK (delivered_at LIKE '%-%-%'),
  recorded_in_database TEXT DEFAULT (datetime('now')),
  use_by TEXT CHECK (use_by LIKE '%-%-%'),
  FOREIGN KEY (stock_id) REFERENCES stock_names(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS transactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  transaction_type TEXT NOT NULL CHECK (transaction_type IN ('addition', 'removal')),
  batch_id INTEGER NOT NULL,
  stock_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL CHECK (quantity >= 0),
  removal_reason TEXT CHECK (removal_reason IN (
                                'N/A',
                                'used',
                                'out_of_date',
                                'returned',
                                'lost',
                                'destroyed')) DEFAULT ('N/A'),
  occured_at TEXT CHECK (occured_at LIKE '%-%-%'),
  recorded_in_database TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE,
  FOREIGN KEY (stock_id) REFERENCES stock_names(id) ON DELETE CASCADE
);