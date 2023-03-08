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

# AccessError (403), invalid user token input
def test_channel_details_v2_invalid_token(clear, registered_users):
    # User Celina creates channel bear 
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'bear', 'is_public': True})
    channel_0 = json.loads(channel_0_json.text)
    # Invalid user token 
    resp = requests.get(config.url + 'channel/details/v2', params={'token': -1, 'channel_id': channel_0['channel_id']})
    # Expected status code (403) AccessError
    assert resp.status_code == 403

# InputError (400), invalid channel_id with valid user token
def test_channel_details_v2_invalid_channel(clear, registered_users):
    resp = requests.get(config.url +'channel/details/v2', params={'token': registered_users[0], 'channel_id': -1})
    # Expected status code (400) InputError
    assert resp.status_code == 400

# Valid token and valid channel id of public channel, status should be 200
def test_channel_details_v2_successful_public(clear, registered_users):
    # User Celina creates PRIVATE channels otter and giraffe (test loop)
    requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'otter', 'is_public': False})
    requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'giraffe', 'is_public': False}) 
    # User Celina creates PUBLIC channel bear
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'bear', 'is_public': True})
    channel_0 = json.loads(channel_0_json.text)
    # Assert expected output of valid token and channel bear id
    resp = requests.get(config.url + 'channel/details/v2', params={'token': registered_users[0], 'channel_id': channel_0['channel_id']})
    assert json.loads(resp.text) == {
        'name': 'bear',
        'is_public': True,
        'owner_members': [
            {
                'u_id': 0,
                'email': 'celina@domain.com',
                'name_first': 'celina',
                'name_last': 'shen',
                'handle_str': 'celinashen',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
        'all_members': [
            {
                'u_id': 0,
                'email': 'celina@domain.com',
                'name_first': 'celina',
                'name_last': 'shen',
                'handle_str': 'celinashen',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
    }
    # Expected status code (200) successful
    assert resp.status_code == 200

# Valid token and valid channel id of private channel, status should be 200
def test_channel_details_v2_successful_private(clear, registered_users):
    # User Celina creates PRIVATE channel otter
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'otter', 'is_public': False})
    channel_0 = json.loads(channel_0_json.text)
    # Assert expected output of valid token and channel otter id
    resp = requests.get(config.url + 'channel/details/v2', params={'token': registered_users[0], 'channel_id': channel_0['channel_id']})
    assert json.loads(resp.text) == {
        'name': 'otter',
        'is_public': False,
        'owner_members': [
            {
                'u_id': 0,
                'email': 'celina@domain.com',
                'name_first': 'celina',
                'name_last': 'shen',
                'handle_str': 'celinashen',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
        'all_members': [
            {
                'u_id': 0,
                'email': 'celina@domain.com',
                'name_first': 'celina',
                'name_last': 'shen',
                'handle_str': 'celinashen',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
    }
    # Expected status code (200) successful
    assert resp.status_code == 200

# Valid token and valid channel id, but user requesting is not a member of channel; status should be AccessError (403)
def test_channel_details_v2_not_member(clear, registered_users):
    # User Celina creates PUBLIC channel seal
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'seal', 'is_public': True})
    channel_0 = json.loads(channel_0_json.text)
    # User Christina requests channel details (should create AccessError)
    resp = requests.get(config.url + 'channel/details/v2', params={'token': registered_users[1], 'channel_id': channel_0['channel_id']})
    # Expected status code (403) AccessError
    assert resp.status_code == 403

# # Tests channel details v2 with multiple users in public channel
def test_channel_details_v2_multiple_members(clear, registered_users):
    # User Celina creates PUBLIC channel giraffe
    channel_0_json = requests.post(config.url + 'channels/create/v2', json={'token': registered_users[0], 'name': 'giraffe', 'is_public': True})
    channel_0 = json.loads(channel_0_json.text)
    # User Christina joins channel giraffe
    requests.post(config.url + 'channel/join/v2', json={'token': registered_users[1], 'channel_id': channel_0['channel_id']})
    # Assert expected output of valid token and channel id
    resp = requests.get(config.url + 'channel/details/v2', params={'token': registered_users[0], 'channel_id': channel_0['channel_id']})
    assert json.loads(resp.text) == {
        'name' : 'giraffe',
        'is_public': True,
        'owner_members': [
            {
                'u_id': 0,
                'email': 'celina@domain.com',
                'name_first': 'celina',
                'name_last': 'shen',
                'handle_str': 'celinashen',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
        'all_members': [
            {
                'u_id': 0,
                'email': 'celina@domain.com',
                'name_first': 'celina',
                'name_last': 'shen',
                'handle_str': 'celinashen',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
            {
                'u_id': 1,
                'email': 'christina@domain.com',
                'name_first': 'christina',
                'name_last': 'lee',
                'handle_str': 'christinalee',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
    }
    # Expected status code (200) successful
    assert resp.status_code == 200
