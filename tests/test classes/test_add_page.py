import pytest
from unittest.mock import patch, Mock
import tkinter as tk
from tkinter import ttk
import A1_inventory_management.query_classes as qc

@pytest.mark.parametrize("test_data",[
    {"name" : ["nuts", True],
    "quantity" : [45, True],
    "delivered_at" : ["2025-6-4", True],
    "use_by" : ["2030-5-4", True]},
], ids=["All_Valid"]
)
@patch("sqlite3.connect")
@patch("A1_inventory_management.query_classes.AddPage.confirmSubmitQuery")
@patch("A1_inventory_management.query_classes.AddPage.displayInvalid")
def test_add_page_checkValid(mock_display_invalid, mock_confirm_query, mock_connect, root, test_data):
    page = qc.AddPage(root.container, root)

    # Create mocks to imitate the database conection and cursor
    mock_cur = Mock()
    mock_connect.cursor.return_value = mock_cur
    mock_cur.fetchone.return_value = ("screws")

    # Set addpage parameters to test data
    parameters = root.queryData["parameters"]
    for k, v in test_data.items():
        parameters[k].set(v[0])

    expectedResults = {k: v[1] for k, v in test_data.items()}
    # run checkValid
    page.checkValid()

    # check that the results are what they should be
    assert list(page.dataValid) == list(expectedResults)

