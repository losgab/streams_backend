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
def test_channels_create_v2_invalid_token(clear):
    resp = requests.post(config.url + 'channels/create/v2', json={'token': -1, 'name': 'bear', 'is_public': True})
    # Expected status code (403) AccessError
    assert resp.status_code == 403

# Test invalid channel name, length less than 1 for PUBLIC channel
def test_channels_create_v2_short_name_public(clear, registered_users):
    resp = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': '', 'is_public': True})
    # Expected status code (400) InputError
    assert resp.status_code == 400

# Test invalid channel name, length less than 1 for PRIVATE channel
def test_channels_create_v2_short_name_private(clear, registered_users):
    resp = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': '', 'is_public': False})
    # Expected status code (400) InputError
    assert resp.status_code == 400

# Test invalid channel name, length more than 20 for PUBLIC channel
def test_channels_create_v2_long_name_public(clear, registered_users):
    resp = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'channelnamewaytoolong', 'is_public': True})
    # Expected status code (400) InputError
    assert resp.status_code == 400

# Test invalid channel name, length more than 20 for PRIVATE channel
def test_channels_create_v2_long_name_private(clear, registered_users):
    resp = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'channelnamewaytoolong', 'is_public': False})
    # Expected status code (400) InputError
    assert resp.status_code == 400

# Test valid input for PUBLIC channel
def test_channels_create_v2_public(clear, registered_users):
    # User Celina creates PUBLI8C channel bear
    resp = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'bear', 'is_public': True})
    channel = json.loads(resp.text)
    # Assert expected output of channel create v2
    assert json.loads(resp.text) == {
        'channel_id' : channel['channel_id'],
    }
    # Expected status code (200) successful
    assert resp.status_code == 200
    # Test behaviour with channel listall
    listall = requests.get(config.url + 'channels/listall/v2', params={'token': registered_users[0]})
    assert json.loads(listall.text) == {
        'channels': [
            {
                'name': 'bear',
                'channel_id': channel['channel_id'],
            }
        ]
    }

# Test valid input for PRIVATE channel
def test_channels_create_v2_private(clear, registered_users):
    # User Celina creates PUBLIC channel otter
    resp = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'otter', 'is_public': False})
    channel = json.loads(resp.text)
    # Assert expected output of channel create v2
    assert json.loads(resp.text) == {
        'channel_id' : channel['channel_id'],
    }
    # Expected status code (200) successful
    assert resp.status_code == 200
    # Test behaviour with channel listall
    listall = requests.get(config.url + 'channels/listall/v2', params={'token': registered_users[0]})
    assert json.loads(listall.text) == {
        'channels': [
            {
                'name': 'otter',
                'channel_id': channel['channel_id'],
            }
        ]
    }

# Test valid input and create two channels
def test_channels_create_v2_multiple_channels(clear, registered_users):
    # User Celina creates PUBLIC channel seal
    resp_0 = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'seal', 'is_public': False})
    channel_0 = json.loads(resp_0.text)
    # Assert expected output of channel create v2
    assert json.loads(resp_0.text) == {
        'channel_id' : channel_0['channel_id'],
    }
    # User Christina creates PRIVATE channel giraffe
    resp_1 = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'giraffe', 'is_public': True})
    channel_1 = json.loads(resp_1.text)
    # Assert expected output of channel create v2
    assert json.loads(resp_1.text) == {
        'channel_id' : channel_1['channel_id'],
    }
    # Expected status codes (200) successful
    assert resp_0.status_code == 200
    assert resp_1.status_code == 200
    # Test behaviour with channel listall
    listall = requests.get(config.url + 'channels/listall/v2', params={'token': registered_users[0]})
    assert json.loads(listall.text) == {
        'channels': [
            {
                'name': 'seal',
                'channel_id': channel_0['channel_id'],
            },
            {
                'name': 'giraffe',
                'channel_id': channel_1['channel_id'],
            }
        ]
    }
