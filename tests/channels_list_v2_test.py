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
def test_channels_list_v2_invalid_token(clear):
    resp = requests.get(config.url + 'channels/list/v2', params={'token': -1}) 
    # Expected status code (403) AccessError
    assert resp.status_code == 403

# No channels created
def test_channels_list_v2_nochannels(clear, registered_users):
    resp = requests.get(config.url + 'channels/list/v2', params={'token': registered_users[0]})
    assert json.loads(resp.text) == {
        'channels': [
        ]
    }
    # Expected status code (200) successful
    assert resp.status_code == 200

# List of all channels created, only public
def test_channels_list_v2_allchannels_public(clear, registered_users):
    # Celina creates public channels 'gabbos couch' and 'cengis couch'
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'gabbos couch', 'is_public': True})
    channel_0 = json.loads(channel_0_json.text)
    channel_1_json = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'cengis couch', 'is_public': True})
    channel_1 = json.loads(channel_1_json.text)
    # Assert expected output of valid token
    resp = requests.get(config.url + 'channels/list/v2', params={'token': registered_users[0]})
    assert json.loads(resp.text) == {
        'channels': [
            {
                'name' : 'gabbos couch',
                'channel_id': channel_0['channel_id']
            },
            {
                'name' : 'cengis couch',
                'channel_id': channel_1['channel_id']
                
            }
        ]
    }
    # Expected status code (200) successful
    assert resp.status_code == 200

# Private channels
def test_channels_list_v2_private_channels(clear, registered_users):
    # Celina creates a private channel 'gabbos couch'
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'gabbos couch', 'is_public': False})
    channel_0 = json.loads(channel_0_json.text)
    # Assert expected output of valid token
    # Celina should see 'gabbos couch'
    resp = requests.get(config.url + 'channels/list/v2', params={'token': registered_users[0]})
    assert json.loads(resp.text) == {
        'channels': [
            {
                'name' : 'gabbos couch',
                'channel_id': channel_0['channel_id']
            }
        ]
    }
    # Expected status code (200) successful
    assert resp.status_code == 200
    # Christina should see nothing since not a member
    resp = requests.get(config.url + 'channels/list/v2', params={'token': registered_users[1]})
    assert json.loads(resp.text) == {
        'channels': [
        ]
    }
    # Expected status code (200) successful
    assert resp.status_code == 200

# Show all channels that the user is a member of
def test_channels_list_v2_member_sees_some_channels(clear, registered_users):
    # Celina creates a private channels 'cengis bed' and 'celinas chair'
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'cengis bed', 'is_public': False})
    channel_0 = json.loads(channel_0_json.text)
    channel_2_json = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'celinas chair', 'is_public': False})
    channel_2 = json.loads(channel_2_json.text)
    # Christina creates a public channel 'gabbos couch'
    channel_1_json = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[1], 'name': 'gabbos couch', 'is_public': True})
    channel_1 = json.loads(channel_1_json.text)
    # Celina should see 'cengis bed' and 'gabbos couch'
    resp = requests.get(config.url + 'channels/list/v2', params={'token': registered_users[0]})
    assert json.loads(resp.text) == {
        'channels': [
            {
                'name' : 'cengis bed',
                'channel_id': channel_0['channel_id']
            },
            {
                'name': 'celinas chair',
                'channel_id': channel_2['channel_id']
            }
        ]
    }
    # Expected status code (200) successful
    assert resp.status_code == 200
    # Christina should only see 'gabbos couch'
    resp = requests.get(config.url + 'channels/list/v2', params={'token': registered_users[1]})
    assert json.loads(resp.text) == {
        'channels': [
            {
                'name' : 'gabbos couch',
                'channel_id': channel_1['channel_id']
            }
        ]
    }
    # Expected status code (200) successful
    assert resp.status_code == 200
