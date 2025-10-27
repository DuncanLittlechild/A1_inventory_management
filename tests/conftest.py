import pytest
import A1_inventory_management.core as qc

@pytest.fixture(scope="session")
def root():
    root = qc.App()
    root.withdraw()
    yield root