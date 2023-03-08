import json
import requests
import pytest

from src.error import AccessError, InputError
from src import config

@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1')

# Fixture that registers 2 users
@pytest.fixture
def user_setup():
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'gabriel@domain.com', 'password': 'password', 'name_first': 'gabriel', 'name_last': 'thien'})
    user_0 = json.loads(user_0_json.text)
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'nathan@domain.com', 'password': 'password', 'name_first': 'nathan', 'name_last': 'mu'})
    user_1 = json.loads(user_1_json.text)
    return (user_0['token'], user_1['token'])

# Invalid token passed
def test_invalid_token(clear):
    response_data = requests.post(config.url + 'channel/join/v2', json={'token': -1, 'channel_id': -1})
    # AccessError code 403 expected
    assert response_data.status_code == AccessError.code

# Invalid channel_id passed
def test_invalid_channel(clear, user_setup):
    response_data = requests.post(config.url + 'channel/join/v2', json={'token': user_setup[0], 'channel_id': -1})
    # InputError code 400 expected
    assert response_data.status_code == InputError.code

# Tests input error when user is already a member of said channel
def test_alreadymember(clear, user_setup):
    # Public channel is created by Gabriel 
    channel_response = requests.post(config.url + 'channels/create/v2', json={'token': user_setup[0], 'name': 'sushi', 'is_public': True})
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup[0], 'channel_id': channel_response.json()["channel_id"]})
    response_data = requests.post(config.url + 'channel/join/v2', json={'token': user_setup[0], 'channel_id': channel_response.json()['channel_id']})
    assert response_data.status_code == InputError.code 

# Tests what happens when user tries to join a private channel
def test_nopermissions(clear, user_setup):
    # Private channel is created by Gabriel 
    channel_response = requests.post(config.url + 'channels/create/v2', json={'token': user_setup[0], 'name': 'sushi', 'is_public': False})
    response_data = requests.post(config.url + 'channel/join/v2', json={'token': user_setup[1], 'channel_id': channel_response.json()["channel_id"]})
    assert response_data.status_code == AccessError.code

# Tests if global owner can join a private channel
def test_globalowner_privatechannel(clear, user_setup):
    # Private channel is created by Nathan (test w multiple channels)
    requests.post(config.url + 'channels/create/v2', json={'token': user_setup[1], 'name': 'nugget', 'is_public': False})
    # Private channel is created by Nathan
    channel_response = requests.post(config.url + 'channels/create/v2', json={'token': user_setup[1], 'name': 'sushi', 'is_public': False})
    # Global owner Gabriel joins the channel
    response_data = requests.post(config.url + 'channel/join/v2', json={'token': user_setup[0], 'channel_id': channel_response.json()["channel_id"]})
    assert response_data.status_code == 200
    assert response_data.json() == {}