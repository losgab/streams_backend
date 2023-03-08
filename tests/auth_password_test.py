import pytest
import requests
from src import config, auth
import json

@pytest.fixture
def user_setup():
    requests.delete(config.url + 'clear/v1')
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'gabriel@domain.com', 'password': 'password', 'name_first': 'gabriel', 'name_last': 'thien'})
    user_0 = json.loads(user_0_json.text)
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'nathan@domain.com', 'password': 'password', 'name_first': 'nathan', 'name_last': 'mu'})
    user_1 = json.loads(user_1_json.text)
    user_2_json = requests.post(config.url + 'auth/register/v2', json={'email': 'celina@domain.com', 'password': 'password', 'name_first': 'celina', 'name_last': 'shen'})
    user_2 = json.loads(user_2_json.text)
    return (user_0['token'], user_1['token'], user_2['token'], 'gabriel@domain.com', 'nathan@domain.com', 'celina@domain.com')

# STATUS 200 There are users and user in collection
def test_password_request_with_users(user_setup):
    req = requests.post(config.url + 'auth/passwordreset/request/v1', json={'email': user_setup[4]})
    assert req.status_code == 200

# STATUS 200 There are no users
def test_password_request_no_users():
    requests.delete(config.url + 'clear/v1')
    req = requests.post(config.url + 'auth/passwordreset/request/v1', json={'email': 'celina@domain.com'})
    assert req.status_code == 200

# STATUS 200 There are users and user not in collectiion
def test_password_request_not_in_users(user_setup):
    req = requests.post(config.url + 'auth/passwordreset/request/v1', json={'email': 'audhiuqhwed@domain.com'})
    assert req.status_code == 200


# Test invalid code
def test_password_reset_invalid_code(user_setup):
    req = requests.post(config.url + 'auth/passwordreset/reset/v1', json={'reset_code': 'invalidcodeinvaliccodeinvalidcode', 'new_password' : 'newpassword'})
    assert req.status_code == 400

# Test password too short
def test_password_reset_new_password_too_short(user_setup):
    req = requests.post(config.url + 'auth/passwordreset/reset/v1', json={'reset_code': 'invalidcodeinvaliccodeinvalidcode', 'new_password' : 'new'})
    assert req.status_code == 400
