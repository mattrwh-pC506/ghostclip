import pytest
from pytest_mock import mocker
import plaid


@pytest.fixture
def plaid_client_factory(db, mocker):
    mocker.patch('plaid.Client')
