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
    user_2_json = requests.post(config.url + 'auth/register/v2', json={'email': 'celina@domain.com', 'password': 'password', 'name_first': 'celina', 'name_last': 'shen'})
    user_2 = json.loads(user_2_json.text)
    return (user_0['token'], user_1['token'], user_2['token'], user_0['auth_user_id'], user_1['auth_user_id'], user_2['auth_user_id'])

# Invalid token passed
def test_invalid_token(clear):
    response_data = requests.post(config.url + 'channel/invite/v2', json={'token': -1, 'channel_id': -1, 'u_id': -1})
    # AccessError code 403 expected
    assert response_data.status_code == AccessError.code
    
# Invalid channel_id passed
def test_invalid_channel(clear, user_setup):
    response_data = requests.post(config.url + 'channel/invite/v2', json={'token': user_setup[0], 'channel_id': -1, 'u_id': user_setup[4]})
    # InputError code 400 expected
    assert response_data.status_code == InputError.code

# Invalid channel_id passed too big
def test_invalid_channel_too_big(clear, user_setup):
    response_data = requests.post(config.url + 'channel/invite/v2', json={'token': user_setup[0], 'channel_id': -1, 'u_id': user_setup[4]})
    # InputError code 400 expected
    assert response_data.status_code == InputError.code
    
# Invalid u_id of user to invite passed     
def test_invalid_u_id(clear, user_setup):
    # Gabbo creates a channel
    channel_response = requests.post(config.url + 'channels/create/v2', json={'token': user_setup[0], 'name': 'sushi', 'is_public': True})
    response_data = requests.post(config.url + 'channel/invite/v2', json={'token': user_setup[0], 'channel_id': channel_response.json()['channel_id'], 'u_id': -1}) 
    assert response_data.status_code == InputError.code
    
# Tests when specified user is already a member of the channel
def test_already_member(clear, user_setup):
    # Gabbo creates a channel
    channel_response = requests.post(config.url + 'channels/create/v2', json={'token': user_setup[0], 'name': 'sushi', 'is_public': True})
    # Nathan joins
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup[1], 'channel_id': channel_response.json()['channel_id']})
    # Gabbo tries to invite nathan to join the channel 
    invite_response_data = requests.post(config.url + 'channel/invite/v2', json={'token': user_setup[0], 'channel_id': channel_response.json()['channel_id'], 'u_id': user_setup[3]})
    assert invite_response_data.status_code == InputError.code

# Tests what happens when the inviter isnt a member of the channel
def test_inviter_notmember(clear, user_setup):
    # Gabbo creates a public channel
    channel_response = requests.post(config.url + 'channels/create/v2', json={'token': user_setup[0], 'name': 'sushi', 'is_public': True})
    # Celina tries to invite nathan to the channel
    invite_response = requests.post(config.url + 'channel/invite/v2', json={'token': user_setup[2], 'channel_id': channel_response.json()['channel_id'], 'u_id': user_setup[4]})
    assert invite_response.status_code == AccessError.code