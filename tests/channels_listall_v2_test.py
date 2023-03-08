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
def registered_users():
    # register users celina and christina
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'celina@domain.com', 'password': 'password', 'name_first': 'celina', 'name_last': 'shen'})
    user_0 = json.loads(user_0_json.text)
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'christina@domain.com', 'password': 'password', 'name_first': 'christina', 'name_last': 'lee'})
    user_1 = json.loads(user_1_json.text)
    # return tuple of user tokens
    return (user_0['token'], user_1['token'])

# AccessError (403), invalid token input
def test_channels_listall_v2_invalid_token(clear):
    resp = requests.get(config.url + 'channels/listall/v2', params={'token': -1}) 
    # Expected status code (403) AccessError
    assert resp.status_code == 403

# Given a valid token, user calls channel_listall_v2 for no created channels (empty)
def test_channels_listall_v2_no_channels(clear, registered_users):
    resp = requests.get(config.url + 'channels/listall/v2', params={'token': registered_users[0]})
    assert json.loads(resp.text) == {
        'channels': []
    }
    # Expected status code (200) successful
    assert resp.status_code == 200
    
# Given a valid token, owner calls channel_listall_v2 to list PUBLIC channels
def test_channels_listall_v2_successful_public(clear, registered_users):
    # User Celina creates PUBLIC channels bear and otter
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'bear', 'is_public': True})
    channel_0 = json.loads(channel_0_json.text)
    channel_1_json = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'otter', 'is_public': True})
    channel_1 = json.loads(channel_1_json.text)
    # Assert expected output of valid token
    resp = requests.get(config.url + 'channels/listall/v2', params={'token': registered_users[0]})
    assert json.loads(resp.text) == {
        'channels': [
            {
                'name' : 'bear',
                'channel_id': channel_0['channel_id']
            },
            {
                'name' : 'otter',
                'channel_id': channel_1['channel_id'],
                
            }
        ]
    }
    # Expected status code (200) successful
    assert resp.status_code == 200

# Given a valid token, owner calls channel_listall_v2 to list PRIVATE channels
def test_channels_listall_v2_successful_private(clear, registered_users):
    # User Celina creates PRIVATE channels bear and otter
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'bear', 'is_public': False})
    channel_0 = json.loads(channel_0_json.text)
    channel_1_json = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'otter', 'is_public': False})
    channel_1 = json.loads(channel_1_json.text)
    # Assert expected output of valid token
    resp = requests.get(config.url + 'channels/listall/v2', params={'token': registered_users[0]})
    assert json.loads(resp.text) == {
        'channels': [
            {
                'channel_id': channel_0['channel_id'],
                'name' : 'bear',
            },
            {
                'channel_id': channel_1['channel_id'],
                'name' : 'otter', 
            }
        ]
    }
    # Expected status code (200) successful
    assert resp.status_code == 200

# Given a valid token, a non-member calls channel_listall_v2 to list channels
def test_channels_listall_v2_not_member(clear, registered_users):
    # User Celina creates PUBLIC channel giraffe
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'giraffe', 'is_public': True})
    channel_0 = json.loads(channel_0_json.text)
    # User Christina calls channel_listall_v2; Assert expected output
    resp = requests.get(config.url + 'channels/listall/v2', params={'token': registered_users[1]})
    assert json.loads(resp.text) == {
        'channels': [
            {
                'channel_id': channel_0['channel_id'],
                'name' : 'giraffe',
            }
        ]
    }
    # Expected status code (200) successful
    assert resp.status_code == 200