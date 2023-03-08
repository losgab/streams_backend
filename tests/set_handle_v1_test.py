import pytest
import requests
import json
from src import config

@pytest.fixture
def registered_users():
    requests.delete(config.url + 'clear/v1')
    user0 = requests.post(config.url + 'auth/register/v2', 
    json = {
        'email' : 'celina@domain.com',
        'password': 'password',
        'name_first': 'celina',
        'name_last': 'shen'
    })
    user1 = requests.post(config.url + 'auth/register/v2', 
    json = {
        'email' : 'christina@domain.com',
        'password': 'password',
        'name_first': 'christina',
        'name_last': 'lee'
    })
    user2 = requests.post(config.url + 'auth/register/v2', 
    json = {
        'email' : 'garbiel@domain.com',
        'password': 'password',
        'name_first': 'gabriel',
        'name_last': 'thien'
    })
    user_0 = json.loads(user0.text)
    user_1 = json.loads(user1.text)
    user_2 = json.loads(user2.text)

    return (user_0['token'], user_1['token'],user_2['token'])
    

def test_set_handle_length_too_short(registered_users):
    # Assert expected output of valid token and channel bear id
    resp = requests.put(config.url + "user/profile/sethandle/v1", json={'token': registered_users[0], 'handle_str': "p"})
    # Expected status code (400) successful
    assert resp.status_code == 400


def test_set_handle_length_too_long(registered_users):
    # Assert expected output of valid token and channel bear id
    resp = requests.put(config.url + "user/profile/sethandle/v1", json={'token': registered_users[0], 'handle_str': "pppppppppppppppppppppppppppppp"})
    # Expected status code (400) successful
    assert resp.status_code == 400

def test_set_handle_already_in_use(registered_users):
    # Assert expected output of valid token and channel bear id
    resp = requests.put(config.url + "user/profile/sethandle/v1", json={'token': registered_users[0], 'handle_str': "gabrielthien"})
    # Expected status code (400) successful
    assert resp.status_code == 400

def test_set_handle_not_alphanumeric(registered_users):
# Assert expected output of valid token and channel bear id
    resp = requests.put(config.url +"user/profile/sethandle/v1", json={'token': registered_users[0], 'handle_str': "!*@*&^*&!@#^"})
    # Expected status code (400) successful
    assert resp.status_code == 400


def test_set_handle_succesfully(registered_users):
    resp = requests.put(config.url + "user/profile/sethandle/v1", json={'token': registered_users[0], 'handle_str': "HappyCamper345"})
    # Expected status code (400) successful
    assert resp.status_code == 200