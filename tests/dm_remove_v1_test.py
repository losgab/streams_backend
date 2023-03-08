from isort import code
import pytest
import requests
import json

from src import config
from src.error import AccessError, InputError

# Fixture that clears the data store
@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1')

# Fixture that registers 2 users
@pytest.fixture
def user_setup():
    user_0 = requests.post(config.url + 'auth/register/v2', json={'email': 'gabriel@domain.com', 'password': 'password', 'name_first': 'gabriel', 'name_last': 'thien'})
    user_1 = requests.post(config.url + 'auth/register/v2', json={'email': 'cengiz@domain.com', 'password': 'password', 'name_first': 'cengiz', 'name_last': 'cimen'})
    user_2 = requests.post(config.url + 'auth/register/v2', json={'email': 'nathan@domain.com', 'password': 'password', 'name_first': 'nathan', 'name_last': 'mu'})
    return (user_0.json()['token'], user_1.json()['token'], user_2.json()['token'], user_0.json()['auth_user_id'], user_1.json()['auth_user_id'], user_2.json()['auth_user_id'])

# Invalid dm_id is passed 
def test_invalid_dm_id(clear, user_setup):
    # Negative dm_id passed 
    response_data = requests.delete(config.url + 'dm/remove/v1', json={'token': user_setup[0], 'dm_id': -1})
    assert response_data.status_code == InputError.code
    # Exceed max dm_id passed
    response_data = requests.delete(config.url + 'dm/remove/v1', json={'token': user_setup[0], 'dm_id': 1})
    assert response_data.status_code == InputError.code

# dm_id is valid and authorised user is not the original creator 
def test_not_dm_creator(clear, user_setup):
    # Make a dm first between gabriel and cengiz
    dm_data = requests.post(config.url + 'dm/create/v1', json={'token': user_setup[0], 'u_ids': [user_setup[4]]})
    # Cengiz tries to delete the DM
    resp_data = requests.delete(config.url + 'dm/remove/v1', json={'token': user_setup[1], 'dm_id': dm_data.json()['dm_id']})
    # AccessError code 403 expected
    assert resp_data.status_code == AccessError.code

# dm_id is valid but the authorised user is no longer part of the dm
def test_not_in_dm(clear, user_setup):
    # Make a dm first between Gabriel and Cengiz
    dm_data = requests.post(config.url + 'dm/create/v1', json={'token': user_setup[0], 'u_ids': [user_setup[4]]})
    # Nathan tries to remove the DM 
    resp_data = requests.delete(config.url + 'dm/remove/v1', json={'token': user_setup[2], 'dm_id': dm_data.json()['dm_id']})
    assert resp_data.status_code == AccessError.code

# Tests success case and functionality of command 
def test_success(clear, user_setup):
    # Make a dm first between Gabriel and Cengiz
    dm_data = requests.post(config.url + 'dm/create/v1', json={'token': user_setup[0], 'u_ids': [user_setup[4]]})
    dm_id = dm_data.json()['dm_id']
    # Gabriel removes it 
    requests.delete(config.url + 'dm/remove/v1', json={'token': user_setup[0], 'dm_id': dm_data.json()['dm_id']})
    # Call on dm remove to verify that the dm is now invalid 
    resp_data = requests.delete(config.url + 'dm/remove/v1', json={'token': user_setup[0], 'dm_id': dm_id})
    # InputError code 400 expected since not a valid dm, it was just removed 
    assert resp_data.status_code == InputError.code