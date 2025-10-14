CREATE TABLE IF NOT EXISTS stock_names (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL CHECK (LENGTH(name) <= 50)
);

CREATE TABLE IF NOT EXISTS batches (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  stock_id INTEGER NOT NULL,
  quantity_initial INTEGER NOT NULL,
  quantity_current INTEGER NOT NULL,
  delivered_at TEXT CHECK (delivered_at LIKE '%-%-%'),
  recorded_in_database TEXT DEFAULT (datetime('now')),
  use_by TEXT CHECK (use_by LIKE '%-%-%'),
  FOREIGN KEY (stock_id) REFERENCES stock_names(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS additions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  batch_id INTEGER NOT NULL,
  stock_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL,
  added_at TEXT CHECK (added_at LIKE '%-%-%'),
  recorded_in_database TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE,
  FOREIGN KEY (stock_id) REFERENCES stock_names(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS removals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  batch_id INTEGER NOT NULL,
  stock_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL,
  reason TEXT CHECK (reason IN ('used',
                                'out_of_date',
                                'returned',
                                'lost',
                                'destroyed')),
  removed_at TEXT CHECK (removed_at LIKE '%-%-%'),
  recorded_in_database TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE,
  FOREIGN KEY (stock_id) REFERENCES stock_names(id) ON DELETE CASCADE
);