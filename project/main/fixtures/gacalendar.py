import pytest
from pytest_mock import mocker
from googleapiclient.discovery import build
from google.oauth2 import service_account


@pytest.fixture
def gacalendar(db, mocker):
    mocker.patch('service_account.Credentials.from_service_account_file')
    mocker.patch('build')
