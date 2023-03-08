import pytest
import requests
import json
from src import config

# Fixture that clears the data store
@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1')

# Fixture that clears the data store and registers 2 users
@pytest.fixture
def register():
    # register users celina and christina
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'celina@domain.com', 'password': 'password', 'name_first': 'celina', 'name_last': 'shen'})
    user_0 = json.loads(user_0_json.text)
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'christina@domain.com', 'password': 'password', 'name_first': 'christina', 'name_last': 'lee'})
    user_1 = json.loads(user_1_json.text)
    user_2_json = requests.post(config.url + 'auth/register/v2', json={'email': 'nathan@domain.com', 'password': 'password', 'name_first': 'nathan', 'name_last': 'mu'})
    user_2 = json.loads(user_2_json.text)
    # dm with members celina and christina
    dm_1_json = requests.post(config.url + 'dm/create/v1', json={'token': user_0['token'], 'u_ids': [user_1['auth_user_id']]})
    dm_1 = json.loads(dm_1_json.text)
    # dm with christina and nathan
    dm_2_json = requests.post(config.url + 'dm/create/v1', json={'token': user_1['token'], 'u_ids': [user_2['auth_user_id']]})
    dm_2 = json.loads(dm_2_json.text)
    # return tuple of user tokens
    return {
        'token1': user_0['token'], 
        'token2': user_1['token'],
        'token3': user_2['token'],
        'dm_id1': dm_1['dm_id'],
        'dm_id2': dm_2['dm_id'],
    }

# STATUS 403: Test invalid token
def test_dm_list_invalid_token(clear):
    resp = requests.get(config.url + 'dm/list/v1', params={'token': -1})
    assert resp.status_code == 403

# STATUS 200: Test success case default
def test_dm_list_correct_list_celina(clear, register):
    # Call dm list endpoint
    resp = requests.get(config.url + 'dm/list/v1', params={'token' : register['token1']})
    assert resp.status_code == 200
    assert resp.json() == {'dms':
    [
        {
        'name' : 'celinashen, christinalee',
        'dm_id' : register['dm_id1']
        }
    ]
    }

# STATUS CODE 200: Test success for user Christina
def test_dm_list_correct_list_christina(clear, register):
    # Call dm list endpoint
    resp = requests.get(config.url + 'dm/list/v1', params={'token' : register['token2']})
    assert resp.status_code == 200
    assert resp.json() == {'dms':
    [
        {
        'name' : 'celinashen, christinalee',
        'dm_id' : register['dm_id1']
        },
        {
        'name' : 'christinalee, nathanmu',
        'dm_id' : register['dm_id2']
        },
    ]
    }

# STATUS CODE 200: Test success for user Nathan
def test_dm_list_correct_list_nathan(clear, register):
    # Call dm list endpoint
    resp = requests.get(config.url + 'dm/list/v1', params={'token' : register['token3']})
    assert resp.status_code == 200
    assert resp.json() == {'dms':
    [
        {
        'name' : 'christinalee, nathanmu',
        'dm_id' : register['dm_id2']
        }
    ]
    }

# STATUS 200: Test success after removed (need dm remove)
def test_dm_list_removed(clear, register):
    # Celina removes the DM to Christina
    requests.delete(config.url + 'dm/remove/v1', json={'token': register['token1'], 'dm_id': register['dm_id1']})
    # Call dm_list to see if Christina still sees the stuff 
    resp = requests.get(config.url + 'dm/list/v1', params={'token': register['token1']})
    assert resp.status_code == 200
    assert resp.json() == {
        'dms': []
    }