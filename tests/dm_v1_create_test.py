import pytest
import requests
import json
from src import config

@pytest.fixture
def user_setup():
    # Clear the data_store and register 3 users
    requests.delete(config.url + 'clear/v1')
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'gabriel@domain.com', 'password': 'password', 'name_first': 'gabriel', 'name_last': 'thien'})
    user_0 = json.loads(user_0_json.text)
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'nathan@domain.com', 'password': 'password', 'name_first': 'nathan', 'name_last': 'mu'})
    user_1 = json.loads(user_1_json.text)
    user_2_json = requests.post(config.url + 'auth/register/v2', json={'email': 'celina@domain.com', 'password': 'password', 'name_first': 'celina', 'name_last': 'shen'})
    user_2 = json.loads(user_2_json.text)
    return (user_0['token'], user_1['token'], user_2['token'], user_0['auth_user_id'], user_1['auth_user_id'], user_2['auth_user_id'])
 
# STATUS CODE 400: Create a DM with invalid user IDs
def test_dm_create_uids_invalid(user_setup):
    # Create a new DM
    resp = requests.post(config.url + 'dm/create/v1', 
        json={
            'token' : user_setup[0],
            'u_ids' : [-1, 1, -30]
        })
    assert resp.status_code == 400

# STATUS CODE 400: Create a DM with duplicate user IDs
def test_dm_create_duplicate_uid(user_setup):
    # Create a new DM
    resp = requests.post(config.url + 'dm/create/v1', 
        json={
            'token' : user_setup[0],
            'u_ids' : [user_setup[4], user_setup[4]]
        })
    assert resp.status_code == 400


# STATUS CODE 400: Success case for creating DMs
def test_dm_create_success(user_setup):
    # Create a new DM
    resp = requests.post(config.url + 'dm/create/v1', 
        json={
            'token' : user_setup[0],
            'u_ids' : [user_setup[4], user_setup[5]]
        })
    assert resp.status_code == 200
    # Check if the dm_id is correct
    assert resp.json() == {
        'dm_id': 0
    }

# STATUS CODE 403: Attempt to create a DM with an invalid token
def test_dm_create_invalid_token(user_setup):
    # Create a new DM
    resp = requests.post(config.url + 'dm/create/v1', 
        json={
            'token' : 'qwehqqow',
            'u_ids' : [user_setup[3], user_setup[4], user_setup[5]]
        })
    assert resp.status_code == 403

