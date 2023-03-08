import json
import requests
import pytest

from src.error import AccessError, InputError
from src import config

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
    response_data = requests.post(config.url + 'dm/leave/v1', json={'token': user_setup[0], 'dm_id': -1})
    assert response_data.status_code == InputError.code
    # Exceed max dm_id passed
    response_data = requests.post(config.url + 'dm/leave/v1', json={'token': user_setup[0], 'dm_id': 1})
    assert response_data.status_code == InputError.code

# dm_id is valid but the person isnt a member of the dm lmao
def test_not_member(clear, user_setup):
    # Gabbo DMs cengiz
    dm_data = requests.post(config.url + 'dm/create/v1', json={'token': user_setup[0], 'u_ids': [user_setup[4]]})
    # Cengiz leaves
    response_data = requests.post(config.url + 'dm/leave/v1', json={'token': user_setup[0], 'dm_id': dm_data.json()['dm_id']})
    # Successfully leaves the DM
    assert response_data.status_code == 200
    # Cengiz leaves again?
    response_data = requests.post(config.url + 'dm/leave/v1', json={'token': user_setup[0], 'dm_id': dm_data.json()['dm_id']})
    # AccessError code 400 expected 
    assert response_data.status_code == AccessError.code

# tests success functionality
def test_success(clear, user_setup):
    # Gabbo DMs cengiz
    dm_data = requests.post(config.url + 'dm/create/v1', json={'token': user_setup[0], 'u_ids': [user_setup[4]]})
    # Cengiz leaves
    response_data = requests.post(config.url + 'dm/leave/v1', json={'token': user_setup[1], 'dm_id': dm_data.json()['dm_id']})
    # Success code expected
    assert response_data.status_code == 200
    # Call dm list to check whether cengiz is still a member of the dm
    success_data = requests.get(config.url + 'dm/list/v1', params={'token': user_setup[1]})
    assert success_data.status_code == 200
    # Cengiz should have no dms that he is part of 
    assert success_data.json() == {
        'dms': [] # Should be an empty list, since he left the one dm he was part of 
    }