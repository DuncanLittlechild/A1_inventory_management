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

# Test that window exists
def test_window_exists(root):
    assert root.container is not None



# Test that the pages exist and can be instantiated
@pytest.mark.parametrize("page_class", [
    qc.AddPage,
    qc.RemovePage,
    qc.CheckBatchPage,
    qc.CheckStockPage,
    qc.CheckTransactionPage,
])
def test_page_exists(root, page_class):
    page = page_class(root.container, root)
    assert page is not None

# Test that the read pages have the appropriate variables attached
# Set up the values that need to be checked for each read page
@pytest.mark.parametrize("page_class_dict", [
    [qc.AddPage, {
        "name" : tk.StringVar,
        "quantity" : tk.IntVar,
        "delivered_at" : tk.StringVar,
        "use_by" : tk.StringVar
    
    }],
    [qc.RemovePage, {
        "batchId" : tk.IntVar,
        "quantity" : tk.IntVar,
        "removalDate" : tk.StringVar,
        "removalReason" : tk.StringVar
    }],
    [qc.CheckBatchPage, {
            "batchId" : tk.IntVar,
            "name" : tk.StringVar,
            "delivered_at" : [tk.StringVar, tk.StringVar],
            "use_by" : [tk.StringVar, tk.StringVar],
            "recorded_in_database" : [tk.StringVar, tk.StringVar],
    }],
    [qc.CheckTransactionPage, {
        "transaction_type" : tk.StringVar,
        "stock_id" : tk.StringVar,
        "occured_at" : [tk.StringVar, tk.StringVar],
        "recorded_in_database" : [tk.StringVar, tk.StringVar],
        "removal_reason" : tk.StringVar
    }],
    [qc.CheckStockPage, {
        "stock_id" : tk.StringVar,
    }]
], ids=["AddPage", "RemovePage", "CheckBatchPage", "CheckTransactionPage", "CheckStockPage"]
)
def test_write_page_data(root, page_class_dict):
    # Create a page of the chosen class
    page = page_class_dict[0](root.container, root)

    # Check to make sure the parameters are of the correct type
    var_list = page_class_dict[1]
    parameter_dict = root.queryData["parameters"]
    for k, v in var_list.items():
        assert k in parameter_dict
        if isinstance(v, list):
            for index, value in enumerate(v):
                assert isinstance(parameter_dict[k][index], value)
        else:
            assert isinstance(parameter_dict[k], v)


    # Only write types have dataValid fields
    if hasattr(page, "dataValid"):
        # Check to make sure the dataValid checks are of the correct type
        valid_dict = page.dataValid
        for k in var_list.keys():
            assert k in valid_dict
            assert valid_dict[k] is None
    
    # Only read types have dataUsed Fields
    if hasattr(page, "dataUsed"):
        # Check to ake sure the dataUsed checks are of the correct type
        used_dict = page.dataUsed
        for k in var_list.keys():
            assert k in used_dict
            assert isinstance(used_dict[k], tk.BooleanVar)


# test AddPages checkvalid to make sure that it correctly recognises correct 
# and incorrect data
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

