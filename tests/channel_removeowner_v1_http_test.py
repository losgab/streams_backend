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
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'gabriel@domain.com', 'password': 'password', 'name_first': 'gabriel', 'name_last': 'thien'})
    user_0 = json.loads(user_0_json.text)
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'nathan@domain.com', 'password': 'password', 'name_first': 'nathan', 'name_last': 'mu'})
    user_1 = json.loads(user_1_json.text)
    user_2_json = requests.post(config.url + 'auth/register/v2', json={'email': 'cengiz@domain.com', 'password': 'password', 'name_first': 'cengiz', 'name_last': 'cimen'})
    user_2 = json.loads(user_2_json.text)
    return (user_0['token'], user_1['token'], user_2['token'], user_0['auth_user_id'], user_1['auth_user_id'], user_2['auth_user_id'])

# Invalid token passed
def test_invalid_token(clear):
    response_data = requests.post(config.url + 'channel/removeowner/v1', json={'token': -1, 'channel_id': -1, 'u_id': -1})
    # AccessError code 403 expected
    assert response_data.status_code == AccessError.code

# Invalid channel_id passed
def test_invalid_channel(clear, user_setup):
    response_data = requests.post(config.url + 'channel/removeowner/v1', json={'token': user_setup[0], 'channel_id': -1, 'u_id': -1})
    # InputError code 400 expected
    assert response_data.status_code == InputError.code

# Invaid u_id passed 
def test_invalid_uid(clear, user_setup):
    channel_response = requests.post(config.url + 'channels/create/v2', json={'token': user_setup[0], 'name': 'sushi', 'is_public': True})
    response_data = requests.post(config.url + 'channel/removeowner/v1', json={'token': user_setup[0], 'channel_id': channel_response.json()['channel_id'], 'u_id': -1})
    # InputError code 400 expected
    assert response_data.status_code == InputError.code

# u_id passed is not an owner of the channel
def test_uid_not_owner(clear, user_setup):
    # Gabbo makes a channel and natho joins 
    channel_response = requests.post(config.url + 'channels/create/v2', json={'token': user_setup[0], 'name': 'sushi', 'is_public': True})
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup[1], 'channel_id': channel_response.json()["channel_id"]})
    # Gabbo removes nathan as an owner of channel
    response_data = requests.post(config.url + 'channel/removeowner/v1', json={'token': user_setup[0], 'channel_id': channel_response.json()['channel_id'], 'u_id': user_setup[4]})
    # InputError code 400 expected
    assert response_data.status_code == InputError.code

# u_id passed is currently the only owner in the channel
def test_only_owner(clear, user_setup):
    # Gabbo makes a channel 
    channel_response = requests.post(config.url + 'channels/create/v2', json={'token': user_setup[0], 'name': 'sushi', 'is_public': True})
    # Gabbo tries to remove himself from channel as owner 
    response_data = requests.post(config.url + 'channel/removeowner/v1', json={'token': user_setup[0], 'channel_id': channel_response.json()['channel_id'], 'u_id': user_setup[3]})
    # InputError code 400 expected
    assert response_data.status_code == InputError.code

# Tests when auth_user_id has no permissions 
def test_nopermissions(clear, user_setup):
    # Gabbo makes a channel and natho joins 
    channel_response = requests.post(config.url + 'channels/create/v2', json={'token': user_setup[0], 'name': 'sushi', 'is_public': True})
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup[1], 'channel_id': channel_response.json()["channel_id"]})
    # natho tries to remove gabbo as owner of channel
    response_data = requests.post(config.url + 'channel/removeowner/v1', json={'token': user_setup[1], 'channel_id': channel_response.json()['channel_id'], 'u_id': user_setup[3]})
    # AccessError code 403 expected
    assert response_data.status_code == AccessError.code

# Tests when a global owner removes an owner from a channel
def test_globalowner_removesowner(clear, user_setup):
    # Natho makes a channel and Cengiz, Gabbo joins 
    channel_response = requests.post(config.url + 'channels/create/v2', json={'token': user_setup[1], 'name': 'sushi', 'is_public': True})
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup[2], 'channel_id': channel_response.json()["channel_id"]})
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup[0], 'channel_id': channel_response.json()["channel_id"]})
    # Nathan adds cengiz as owner
    requests.post(config.url + 'channel/addowner/v1', json={'token': user_setup[1], 'channel_id': channel_response.json()["channel_id"], 'u_id': user_setup[5]})
    # Gabbo doesnt like cengiz and removes him as an owner of the channel
    response_data = requests.post(config.url + 'channel/removeowner/v1', json={'token': user_setup[0], 'channel_id': channel_response.json()["channel_id"], 'u_id': user_setup[5]})
    assert response_data.status_code == 200
    assert response_data.json() == {}
    # Confirming 
    details_data = requests.get(config.url + 'channel/details/v2', params={'token': user_setup[1], 'channel_id': channel_response.json()["channel_id"]})
    assert details_data.json() == {
        'name': 'sushi', 
        'is_public': True, 
        'owner_members': [
            {
                "u_id": 1, 
                "email": "nathan@domain.com",
                "name_first": "nathan", 
                "name_last": "mu", 
                "handle_str": "nathanmu",
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
        'all_members': [
            {
                "u_id": 1, 
                "email": "nathan@domain.com",
                "name_first": "nathan", 
                "name_last": "mu", 
                "handle_str": "nathanmu",
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
            {  
                "u_id": 2, 
                "email": "cengiz@domain.com",
                "name_first": "cengiz", 
                "name_last": "cimen", 
                "handle_str": "cengizcimen",
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
            {  
                "u_id": 0, 
                "email": "gabriel@domain.com",
                "name_first": "gabriel", 
                "name_last": "thien", 
                "handle_str": "gabrielthien",
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ]
    }

# Tests whether the global owner can remove the only owner in a channel
def test_globalowner_removeonlyowner(clear, user_setup):
    # Natho makes a channel & Gabbo joins
    channel_response = requests.post(config.url + 'channels/create/v2', json={'token': user_setup[1], 'name': 'sushi', 'is_public': True})
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup[0], 'channel_id': channel_response.json()["channel_id"]})
    # Gabbo tries to remove natho as an owner but should fail since hes the only owner 
    response_data = requests.post(config.url + 'channel/removeowner/v1', json={'token': user_setup[0], 'channel_id': channel_response.json()["channel_id"], 'u_id': user_setup[4]})
    # InputError code 400 expected
    assert response_data.status_code == InputError.code

# Tests success case and behaviour with details call
def test_successcase(clear, user_setup):
    # Gabbo makes a channel and natho joins 
    channel_response = requests.post(config.url + 'channels/create/v2', json={'token': user_setup[0], 'name': 'sushi', 'is_public': True})
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup[1], 'channel_id': channel_response.json()["channel_id"]})
    # Nathan is added as an owner 
    requests.post(config.url + 'channel/addowner/v1', json={'token': user_setup[0], 'channel_id': channel_response.json()["channel_id"], 'u_id': user_setup[4]})
    # Gabbo is now removed as an owner 
    response_data = requests.post(config.url + 'channel/removeowner/v1', json={'token': user_setup[1], 'channel_id': channel_response.json()["channel_id"], 'u_id': user_setup[3]})
    assert response_data.status_code == 200
    assert response_data.json() == {}
    details_data = requests.get(config.url + 'channel/details/v2', params={'token': user_setup[0], 'channel_id': channel_response.json()["channel_id"]})
    assert details_data.json() == {
        'name': 'sushi', 
        'is_public': True, 
        'owner_members': [
            {
                "u_id": 1, 
                "email": "nathan@domain.com",
                "name_first": "nathan", 
                "name_last": "mu", 
                "handle_str": "nathanmu",
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
        'all_members': [
            {
                "u_id": 0, 
                "email": "gabriel@domain.com",
                "name_first": "gabriel", 
                "name_last": "thien", 
                "handle_str": "gabrielthien",
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }, 
            {
                "u_id": 1, 
                "email": "nathan@domain.com",
                "name_first": "nathan", 
                "name_last": "mu", 
                "handle_str": "nathanmu",
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ]
    }