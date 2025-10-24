import pytest
import A1_inventory_management.query_classes as qc

@pytest.fixture(scope="session")
def root():
    root = qc.App()
    root.withdraw()
    yield root