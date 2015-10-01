import pytest
import requests
from requests.auth import HTTPBasicAuth


def test_get_api():
    response = requests.get('http://localhost:8000/users/', auth=HTTPBasicAuth('admin', 'admin'))
    assert response.json()['count'] == 1
