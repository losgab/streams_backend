import json
import pytest
import requests
from src import config
from src.error import InputError, AccessError

@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1')

# Register 2 users
@pytest.fixture
def register_users():
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'christina@domain.com', 'password': 'password', 'name_first': 'christina', 'name_last': 'lee'})
    user_0 = json.loads(user_0_json.text)
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'celina@domain.com', 'password': 'password', 'name_first': 'celina', 'name_last': 'shen'})
    user_1 = json.loads(user_1_json.text)
    user_2_json = requests.post(config.url + 'auth/register/v2', json={'email': 'cengiz@domain.com', 'password': 'password', 'name_first': 'cengiz', 'name_last': 'cimen'})
    user_2 = json.loads(user_2_json.text)
    return (user_0['token'], user_1['token'], user_1['auth_user_id'], user_2['token'])

# Channel_ID does not refer to a valid channel
def test_channel_leave_v1_invalid_channel_id(clear, register_users):
    resp = requests.post(config.url + 'channel/leave/v1', json={'token': register_users[0], 'channel_id': -1})
    # Expected status code (400) InputError
    assert resp.status_code == 400

# Channel_ID is valid and the authorised user is not a member of the channel
def test_channel_leave_v1_not_a_member(clear, register_users):
    # Christina creates a public channel
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': register_users[0], 'name': 'channel0', 'is_public': True})
    channel_0 = json.loads(channel_0_json.text)
    # Celina leaves the channel (not a member)
    resp = requests.post(config.url + 'channel/leave/v1', json={'token': register_users[1], 'channel_id': channel_0['channel_id']})
    # Expected status code (403) AccessError
    assert resp.status_code == 403

# Invalid token
def test_channel_leave_v1_invalid_token(clear, register_users):
    resp = requests.post(config.url + 'channel/leave/v1', json={'token': -1, 'channel_id': -1})
    # Expected status code (403) AccessError
    assert resp.status_code == 403

# One member public channel
def test_channel_leave_v1_one_member_public(clear, register_users):
    # Christina creates a public channel
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': register_users[0], 'name': 'channel0', 'is_public': True})
    channel_0 = json.loads(channel_0_json.text)
    # Christina leaves the channel
    resp = requests.post(config.url + 'channel/leave/v1', json={'token': register_users[0], 'channel_id': channel_0['channel_id']})
    assert resp.status_code == 200
    assert resp.json() == {}
    # Check channel details (behaviour), should be accessError because no longer part of channel
    det = requests.get(config.url + 'channel/details/v2', params={'token': register_users[0], 'channel_id': channel_0['channel_id']})
    det.status_code = 403

# One member private channel
def test_channel_leave_v1_one_member_private(clear, register_users):
    # Celina creates a private channel
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': register_users[1], 'name': 'channel0', 'is_public': False})
    channel_0 = json.loads(channel_0_json.text)
    # Celina leaves the channel
    resp = requests.post(config.url + 'channel/leave/v1', json={'token': register_users[1], 'channel_id': channel_0['channel_id']})
    assert resp.status_code == 200
    assert resp.json() == {}
    # Check channel details (behaviour), should be accessError because no longer part of channel
    det = requests.get(config.url + 'channel/details/v2', params={'token': register_users[1], 'channel_id': channel_0['channel_id']})
    det.status_code = 403

# Owner leaves a public channel
def test_channel_leave_v1_owner_leaves_public(clear, register_users):
    # Christina creates a public channel
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': register_users[0], 'name': 'channel0', 'is_public': True})
    channel_0 = json.loads(channel_0_json.text)
    # Celina joins
    requests.post(config.url + 'channel/join/v2', json={'token': register_users[1], 'channel_id': channel_0['channel_id']})
    # Christina leaves the channel
    resp = requests.post(config.url + 'channel/leave/v1', json={'token': register_users[0], 'channel_id': channel_0['channel_id']})
    assert resp.status_code == 200
    assert resp.json() == {}
    # Check channel details (behaviour)
    det = requests.get(config.url + 'channel/details/v2', params={'token': register_users[1], 'channel_id': channel_0['channel_id']})
    assert det.json() == {
        'name': 'channel0',
        'is_public': True,
        'owner_members': [
        ],
        'all_members': [
            {
                'u_id': 1,
                'email': 'celina@domain.com',
                'name_first': 'celina',
                'name_last': 'shen',
                'handle_str': 'celinashen',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ]
    }

# Owner leaves a private channel
def test_channel_leave_v1_owner_leaves_private(clear, register_users):
    # Christina creates a private channel
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': register_users[0], 'name': 'channel0', 'is_public': False})
    channel_0 = json.loads(channel_0_json.text)
    # Celina invited
    requests.post(config.url + 'channel/invite/v2', json={'token': register_users[0], 'channel_id': channel_0['channel_id'], 'u_id': register_users[2]})
    # Christina leaves the channel
    resp = requests.post(config.url + 'channel/leave/v1', json={'token': register_users[0], 'channel_id': channel_0['channel_id']})
    assert resp.status_code == 200
    assert resp.json() == {}
    # Check channel details (behaviour)
    det = requests.get(config.url + 'channel/details/v2', params={'token': register_users[1], 'channel_id': channel_0['channel_id']})
    assert det.json() == {
        'name': 'channel0',
        'is_public': False,
        'owner_members': [
        ],
        'all_members': [
            {
                'u_id': 1,
                'email': 'celina@domain.com',
                'name_first': 'celina',
                'name_last': 'shen',
                'handle_str': 'celinashen',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ]
    }


# A member leaves a public channel
def test_channel_leave_v1_member_leaves_public(clear, register_users):
    # Christina creates public channels 
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': register_users[0], 'name': 'channel0', 'is_public': True})
    channel_0 = json.loads(channel_0_json.text)
    requests.post(config.url + 'channels/create/v2', json={'token': register_users[0], 'name': 'otter', 'is_public': True})
    # Celina joins
    requests.post(config.url + 'channel/join/v2', json={'token': register_users[1], 'channel_id': channel_0['channel_id']})
    # Celina leaves the channel
    resp = requests.post(config.url + 'channel/leave/v1', json={'token': register_users[1], 'channel_id': channel_0['channel_id']})
    assert resp.status_code == 200
    assert resp.json() == {}
    # Check channel details (behaviour)
    det = requests.get(config.url + 'channel/details/v2', params={'token': register_users[0], 'channel_id': channel_0['channel_id']})
    assert det.json() == {
        'name': 'channel0',
        'is_public': True,
        'owner_members': [
            {
                'u_id': 0,
                'email': 'christina@domain.com',
                'name_first': 'christina',
                'name_last': 'lee',
                'handle_str': 'christinalee',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
        'all_members': [
            {
                'u_id': 0,
                'email': 'christina@domain.com',
                'name_first': 'christina',
                'name_last': 'lee',
                'handle_str': 'christinalee',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ]
    }

# A member leaves a private channel
def test_channel_leave_v1_member_leaves_private(clear, register_users):
    # Christina creates a private channel
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': register_users[0], 'name': 'channel0', 'is_public': False})
    channel_0 = json.loads(channel_0_json.text)
    # Celina invited
    requests.post(config.url + 'channel/invite/v2', json={'token': register_users[0], 'channel_id': channel_0['channel_id'], 'u_id': register_users[2]})
    # Celina leaves the channel
    resp = requests.post(config.url + 'channel/leave/v1', json={'token': register_users[1], 'channel_id': channel_0['channel_id']})
    assert resp.status_code == 200
    assert resp.json() == {}
    # Check channel details (behaviour)
    det = requests.get(config.url + 'channel/details/v2', params={'token': register_users[0], 'channel_id': channel_0['channel_id']})
    assert det.json() == {
        'name': 'channel0',
        'is_public': False,
        'owner_members': [
            {
                'u_id': 0,
                'email': 'christina@domain.com',
                'name_first': 'christina',
                'name_last': 'lee',
                'handle_str': 'christinalee',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
        'all_members': [
            {
                'u_id': 0,
                'email': 'christina@domain.com',
                'name_first': 'christina',
                'name_last': 'lee',
                'handle_str': 'christinalee',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ]
    }
