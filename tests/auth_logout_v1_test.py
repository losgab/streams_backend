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
    
def test_successfull_logout(registered_users):
    # Assert expected output of valid token
    resp = requests.post(config.url + "auth/logout/v1", json={'token': registered_users[0]})
    # Expected status code (400) successful
    assert resp.status_code == 200
    assert resp.json() == {}
    # Test behaviour
    resp = requests.post(config.url + 'channel/invite/v2', json={'token': registered_users[0], 'channel_id': 0, 'u_id': 0})
    # AccessError code 403 expected
    assert resp.status_code == 403
    
def test_logout_not_in_session(registered_users):
    # Assert expected output of invalid token
    resp_0 = requests.post(config.url + "auth/logout/v1", json={'token': -1})
    resp_1 = requests.post(config.url + "auth/logout/v1", json={'token': 10})
    # Expected status code (403) AccessError
    assert resp_0.status_code == 403
    assert resp_1.status_code == 403
    