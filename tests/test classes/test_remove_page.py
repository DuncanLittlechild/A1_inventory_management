import pytest
from unittest.mock import patch, Mock
import tkinter as tk
from tkinter import ttk
import A1_inventory_management.query_classes as qc

@pytest.fixture(scope="module")
def root():
    root = qc.App()
    root.withdraw()
    yield root
    root.destroy()

@pytest.mark.parametrize("test_data",[
    # Test with all valid data 
    [{"batchId" : [1, True],
    "quantity" : [45, True],
    "removalDate" : ["2025-6-4", True],
    "removalReason" : ["", None]},
    # Returns a batch number,
    # a greater quantity than will be removed,
    # and a delivered_at date that is earlier than the removalDate 
    {"batchId": 1,
     "quantity" : 100,
     "delivered_at": "2024-5-4" 
      }],
], ids=["All_Valid"]
)
@patch("sqlite3.connect")
@patch("A1_inventory_management.query_classes.AddPage.confirmSubmitQuery")
@patch("A1_inventory_management.query_classes.AddPage.displayInvalid")
def test_remove_page_checkValid(mock_display_invalid, mock_confirm_query, mock_connect, root, test_data):
    page = qc.RemovePage(root.container, root)

    # Create mocks to imitate the database conection and cursor
    mock_cur = Mock()
    mock_connect.cursor.return_value = mock_cur

    mock_returns = test_data[1]
    # The iterable here sets the fetchall call to a length greater than 0
    mock_cur.fetchall.return_value.side_effect = [mock_returns["batchId"]]
    # Fetchone returns the date and quantity needed for comparison
    mock_cur.fetchone.return_value.side_effect = [mock_returns["quantity"], mock_returns["delivered_at"]]

    # Set addpage parameters to test data
    parameters = root.queryData["parameters"]
    for k, v in test_data[0].items():
        parameters[k].set(v[0])

    # set up expected results dictionary
    expected_results = {k: v[1] for k, v in test_data[0].items()}
    # run checkValid
    page.checkValid()

    # check that the results are what they should be
    assert list(page.dataValid) == list(expected_results)
