import re
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
def registered():
    # Register users Celina (global owner), Christina and Gabriel
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'celina@domain.com', 'password': 'password', 'name_first': 'celina', 'name_last': 'shen'})
    user_0 = json.loads(user_0_json.text)
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'christina@domain.com', 'password': 'password', 'name_first': 'christina', 'name_last': 'lee'})
    user_1 = json.loads(user_1_json.text)
    user_2_json = requests.post(config.url + 'auth/register/v2', json={'email': 'gabriel@domain.com', 'password': 'password', 'name_first': 'gabriel', 'name_last': 'thien'})
    user_2 = json.loads(user_2_json.text)
    # Return tuple of user tokens and user id
    return (user_0['token'], user_1['token'], user_2['token'], user_0['auth_user_id'], user_1['auth_user_id'], user_2['auth_user_id'])

# AccessError (403), invalid user token input
def test_channel_addowner_v1_invalid_token(clear, registered):
    # User Celina creates PUBLIC channel bear
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': registered[0], 'name': 'bear', 'is_public': True})
    channel_0 = json.loads(channel_0_json.text)
    # Invalid token
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': -1, 'channel_id': channel_0['channel_id'], 'u_id': registered[2]})
    # Expected status code (403) AccessError
    assert resp.status_code == 403

# InputError (400), invalid channel id
def test_channel_addowner_v2_invalid_channel(clear, registered):
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': registered[0], 'channel_id': -1, 'u_id': registered[2]})
    # Expected status code (400) InputError
    assert resp.status_code == 400

# InputError (400), invalid u_id
def test_channel_addowner_v2_invalid_u_id(clear, registered):
    # User Celina creates PUBLIC channel bear
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': registered[0], 'name': 'bear', 'is_public': True})
    channel_0 = json.loads(channel_0_json.text)
    # Invalid user id
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': registered[0], 'channel_id': channel_0['channel_id'], 'u_id': -1})
    # Expected status code (400) InputError
    assert resp.status_code == 400

# InputError (400), u_id is not a member of the channel 
def test_channel_addowner_v2_not_member(clear, registered):
    # User Celina creates PUBLIC channel bear
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': registered[0], 'name': 'bear', 'is_public': True})
    channel_0 = json.loads(channel_0_json.text)
    # User Celina makes Chrstina (not a member) owner 
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': registered[0], 'channel_id': channel_0['channel_id'], 'u_id': registered[4]})
    # Expected status code (400) InputError 
    assert resp.status_code == 400

# InputError (400), u_id is already an owner of the channel
def test_channel_addowner_v2_already_owner(clear, registered):
    # User Celina creates PUBLIC channel bear
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': registered[0], 'name': 'bear', 'is_public': True})
    channel_0 = json.loads(channel_0_json.text)
    # User Celina is made owner of channel bear, however already is an owner
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': registered[0], 'channel_id': channel_0['channel_id'], 'u_id': registered[3]})
    # Expected status code (400) InputError
    assert resp.status_code == 400

# All input is valid, but the auth user does not have owner permissions (non channel owner + non global owner)
def test_channel_addowner_v2_no_permissions(clear, registered):
    # User Celina creates PUBLIC channel bear
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': registered[0], 'name': 'bear', 'is_public': True})
    channel_0 = json.loads(channel_0_json.text)
    # Users Gabriel and Christina join channel bear
    requests.post(config.url + 'channel/join/v2', json={'token': registered[1], 'channel_id': channel_0['channel_id']})
    requests.post(config.url + 'channel/join/v2', json={'token': registered[2], 'channel_id': channel_0['channel_id']})
    # User Christina (no-perms) tries to make Gabriel channel owner 
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': registered[1], 'channel_id': channel_0['channel_id'], 'u_id': registered[5]})
    # Excpected status code (403) AccessError
    assert resp.status_code == 403

# Test successful public channel
def test_channel_addowner_v2_public(clear, registered):
    # User Celina creates PUBLIC channel otter and giraffe (test multiple channels)
    requests.post(config.url + 'channels/create/v2', json={'token': registered[0], 'name': 'otter', 'is_public': True})
    requests.post(config.url + 'channels/create/v2', json={'token': registered[0], 'name': 'giraffe', 'is_public': True})
    # User Celina creates PUBLIC channel bear
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': registered[0], 'name': 'bear', 'is_public': True})
    channel_0 = json.loads(channel_0_json.text)
    # Users Gabriel and Christina join channel bear
    requests.post(config.url + 'channel/join/v2', json={'token': registered[1], 'channel_id': channel_0['channel_id']})
    requests.post(config.url + 'channel/join/v2', json={'token': registered[2], 'channel_id': channel_0['channel_id']})
    # User Celina (perms) adds Christina as channel owner
    resp_0 = requests.post(config.url + 'channel/addowner/v1', json={'token': registered[0], 'channel_id': channel_0['channel_id'], 'u_id': registered[4]})
    # Assert return and status code (200) successful
    assert json.loads(resp_0.text) == {}
    assert resp_0.status_code == 200 
    # Assert expected output of channel details (list of owners)
    details_0 = requests.get(config.url + 'channel/details/v2', params={'token': registered[0], 'channel_id': channel_0['channel_id']})
    assert json.loads(details_0.text) == {
        'name': 'bear',
        'is_public': True,
        'owner_members': [
            {
                'u_id': registered[3],
                'email': 'celina@domain.com',
                'name_first': 'celina',
                'name_last': 'shen',
                'handle_str': 'celinashen',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
            {
                'u_id': registered[4],
                'email': 'christina@domain.com',
                'name_first': 'christina',
                'name_last': 'lee',
                'handle_str': 'christinalee',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
        'all_members': [
            {
                'u_id': registered[3],
                'email': 'celina@domain.com',
                'name_first': 'celina',
                'name_last': 'shen',
                'handle_str': 'celinashen',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
            {
                'u_id': registered[4],
                'email': 'christina@domain.com',
                'name_first': 'christina',
                'name_last': 'lee',
                'handle_str': 'christinalee',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
            {
                'u_id': registered[5],
                'email': 'gabriel@domain.com',
                'name_first': 'gabriel',
                'name_last': 'thien',
                'handle_str': 'gabrielthien',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
    }
    # User Christina (perms) adds Gabriel as channel owner
    resp_1 = requests.post(config.url + 'channel/addowner/v1', json={'token': registered[1], 'channel_id': channel_0['channel_id'], 'u_id': registered[5]})
    # Assert return and status code (200) successful
    assert json.loads(resp_1.text) == {}
    assert resp_1.status_code == 200 
    # Assert expected output of channel details (list of owners)
    details_1 = requests.get(config.url + 'channel/details/v2', params={'token': registered[0], 'channel_id': channel_0['channel_id']})
    assert json.loads(details_1.text) == {
        'name': 'bear',
        'is_public': True,
        'owner_members': [
            {
                'u_id': registered[3],
                'email': 'celina@domain.com',
                'name_first': 'celina',
                'name_last': 'shen',
                'handle_str': 'celinashen',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
            {
                'u_id': registered[4],
                'email': 'christina@domain.com',
                'name_first': 'christina',
                'name_last': 'lee',
                'handle_str': 'christinalee',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
            {
                'u_id': registered[5],
                'email': 'gabriel@domain.com',
                'name_first': 'gabriel',
                'name_last': 'thien',
                'handle_str': 'gabrielthien',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
        'all_members': [
            {
                'u_id': registered[3],
                'email': 'celina@domain.com',
                'name_first': 'celina',
                'name_last': 'shen',
                'handle_str': 'celinashen',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
            {
                'u_id': registered[4],
                'email': 'christina@domain.com',
                'name_first': 'christina',
                'name_last': 'lee',
                'handle_str': 'christinalee',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
            {
                'u_id': registered[5],
                'email': 'gabriel@domain.com',
                'name_first': 'gabriel',
                'name_last': 'thien',
                'handle_str': 'gabrielthien',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
    }

# Test successful private channel
def test_channel_addowner_v2_private(clear, registered):
    # User Celina creates PRIVATE channel bear
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': registered[0], 'name': 'bear', 'is_public': False})
    channel_0 = json.loads(channel_0_json.text)
    # Users Gabriel and Christina join channel bear
    requests.post(config.url + 'channel/invite/v2', json={'token': registered[0], 'channel_id': channel_0['channel_id'], 'u_id': registered[4]})
    requests.post(config.url + 'channel/invite/v2', json={'token': registered[0], 'channel_id': channel_0['channel_id'], 'u_id': registered[5]})
    # User Celina (perms) adds Christina as channel owner
    resp_0 = requests.post(config.url + 'channel/addowner/v1', json={'token': registered[0], 'channel_id': channel_0['channel_id'], 'u_id': registered[4]})
    # Assert return value and status code (200) successful
    assert json.loads(resp_0.text) == {}
    assert resp_0.status_code == 200 
    # Assert expected output of channel details (list of owners) (behaviour)
    details_0 = requests.get(config.url + 'channel/details/v2', params={'token': registered[0], 'channel_id': channel_0['channel_id']})
    assert json.loads(details_0.text) == {
        'name': 'bear',
        'is_public': False,
        'owner_members': [
            {
                'u_id': registered[3],
                'email': 'celina@domain.com',
                'name_first': 'celina',
                'name_last': 'shen',
                'handle_str': 'celinashen',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
            {
                'u_id': registered[4],
                'email': 'christina@domain.com',
                'name_first': 'christina',
                'name_last': 'lee',
                'handle_str': 'christinalee',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
        'all_members': [
            {
                'u_id': registered[3],
                'email': 'celina@domain.com',
                'name_first': 'celina',
                'name_last': 'shen',
                'handle_str': 'celinashen',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
            {
                'u_id': registered[4],
                'email': 'christina@domain.com',
                'name_first': 'christina',
                'name_last': 'lee',
                'handle_str': 'christinalee',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
            {
                'u_id': registered[5],
                'email': 'gabriel@domain.com',
                'name_first': 'gabriel',
                'name_last': 'thien',
                'handle_str': 'gabrielthien',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
    }
    # User Christina (perms) adds Gabriel as channel owner
    resp_1 = requests.post(config.url + 'channel/addowner/v1', json={'token': registered[1], 'channel_id': channel_0['channel_id'], 'u_id': registered[5]})
    # Assert return and status code (200) successful
    assert json.loads(resp_1.text) == {}
    assert resp_1.status_code == 200 
    # Assert expected output of channel details (list of owners) (behaviour)
    details_1 = requests.get(config.url + 'channel/details/v2', params={'token': registered[0], 'channel_id': channel_0['channel_id']})
    assert json.loads(details_1.text) == {
        'name': 'bear',
        'is_public': False,
        'owner_members': [
            {
                'u_id': registered[3],
                'email': 'celina@domain.com',
                'name_first': 'celina',
                'name_last': 'shen',
                'handle_str': 'celinashen',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
            {
                'u_id': registered[4],
                'email': 'christina@domain.com',
                'name_first': 'christina',
                'name_last': 'lee',
                'handle_str': 'christinalee',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
            {
                'u_id': registered[5],
                'email': 'gabriel@domain.com',
                'name_first': 'gabriel',
                'name_last': 'thien',
                'handle_str': 'gabrielthien',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
        'all_members': [
            {
                'u_id': registered[3],
                'email': 'celina@domain.com',
                'name_first': 'celina',
                'name_last': 'shen',
                'handle_str': 'celinashen',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
            {
                'u_id': registered[4],
                'email': 'christina@domain.com',
                'name_first': 'christina',
                'name_last': 'lee',
                'handle_str': 'christinalee',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
            {
                'u_id': registered[5],
                'email': 'gabriel@domain.com',
                'name_first': 'gabriel',
                'name_last': 'thien',
                'handle_str': 'gabrielthien',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
    }

def test_addowner_global_not_member_public(clear, registered):
    # User Christina creates PRIVATE channel bear
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': registered[1], 'name': 'bear', 'is_public': True})
    channel_0 = json.loads(channel_0_json.text)
    # User Celina (global owner but not member) adds Christina as channel owner
    resp_0 = requests.post(config.url + 'channel/addowner/v1', json={'token': registered[0], 'channel_id': channel_0['channel_id'], 'u_id': registered[4]})
    assert resp_0.status_code == 403

def test_addowner_global_not_member_private(clear, registered):
    # User Christina creates PRIVATE channel bear
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': registered[1], 'name': 'bear', 'is_public': False})
    channel_0 = json.loads(channel_0_json.text)
    # User Celina (global owner but not member) adds Christina as channel owner
    resp_0 = requests.post(config.url + 'channel/addowner/v1', json={'token': registered[0], 'channel_id': channel_0['channel_id'], 'u_id': registered[4]})
    assert resp_0.status_code == 403
