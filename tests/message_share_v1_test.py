import json
import pytest
import requests
from src import config
from src.error import InputError, AccessError
import time

@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def register_users():
    # register users
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'christina@domain.com', 'password': 'password', 'name_first': 'christina', 'name_last': 'lee'})
    user_0 = json.loads(user_0_json.text)
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'celina@domain.com', 'password': 'password', 'name_first': 'celina', 'name_last': 'shen'})
    user_1 = json.loads(user_1_json.text)
    user_2_json = requests.post(config.url + 'auth/register/v2', json={'email': 'cengiz@domain.com', 'password': 'password', 'name_first': 'cengiz', 'name_last': 'cimen'})
    user_2 = json.loads(user_2_json.text)
    # Christina creates a channel
    channel_json = requests.post(config.url + 'channels/create/v2', json={'token': user_0['token'], 'name': 'channel0', 'is_public': True})
    channel = json.loads(channel_json.text)
    # Celina joins channel
    channel_json = requests.post(config.url + 'channel/join/v2', json={'token': user_1['token'], 'channel_id': channel['channel_id']})
    # create a dm between Christina and Celina
    dm_0_json = requests.post(config.url + 'dm/create/v1', json={'token': user_0['token'], 'u_ids': [user_1['auth_user_id']]})
    dm_0 = json.loads(dm_0_json.text)
    dm_1_json = requests.post(config.url + 'dm/create/v1', json={'token': user_1['token'], 'u_ids': [user_0['auth_user_id']]})
    dm_1 = json.loads(dm_1_json.text)
    # send messages
    message_0_json = requests.post(config.url + 'message/send/v1', json={'token': user_0['token'], 'channel_id': channel['channel_id'], 'message': 'Hello'})
    message_0 = json.loads(message_0_json.text)
    message_1_json = requests.post(config.url + 'message/send/v1', json={'token': user_0['token'], 'channel_id': channel['channel_id'], 'message': 'message'})
    message_1 = json.loads(message_1_json.text)
    dm_message_0_json = requests.post(config.url + 'message/senddm/v1', json={'token': user_0['token'], 'dm_id': dm_0['dm_id'], 'message': 'Hello'})
    dm_message_0 = json.loads(dm_message_0_json.text)
    dm_message_1_json = requests.post(config.url + 'message/senddm/v1', json={'token': user_0['token'], 'dm_id': dm_0['dm_id'], 'message': 'message'})
    dm_message_1 = json.loads(dm_message_1_json.text)
    dm_message_2_json = requests.post(config.url + 'message/senddm/v1', json={'token': user_0['token'], 'dm_id': dm_1['dm_id'], 'message': 'Bye'})
    dm_message_2 = json.loads(dm_message_2_json.text)
    curr_time = int(time.time())
    
    return {
        'time': curr_time,
        'token0': user_0['token'],
        'token1': user_1['token'],
        'token2': user_2['token'],
        'u_id_0': user_0['auth_user_id'],
        'u_id_1': user_1['auth_user_id'],
        'channel_id': channel['channel_id'],
        'channel_message_0': message_0['message_id'],
        'channel_message_1': message_1['message_id'],
        'dm_id': dm_0['dm_id'],
        'dm_message_0': dm_message_0['message_id'],
        'dm_message_1': dm_message_1['message_id'],
        'dm_message_2': dm_message_2['message_id']
    }

# both channel_id and dm_id are invalid
def test_message_share_v1_channel_id_dm_id_invalid(clear, register_users):
    resp0 = requests.post(config.url + 'message/share/v1', json={'token': register_users['token0'], 'og_message_id': register_users['channel_message_0'], 'message': "Hello", 'channel_id': -2, 'dm_id': -2})
    resp1 = requests.post(config.url + 'message/share/v1', json={'token': register_users['token0'], 'og_message_id': register_users['dm_message_0'], 'message': "Hello", 'channel_id': -2, 'dm_id': -2})
    # Expected status code (400) InputError
    assert resp0.status_code == 400
    assert resp1.status_code == 400

# neither channel_id nor dm_id are -1
def test_message_share_v1_channel_id_dm_id_not_sent(clear, register_users):
    resp0 = requests.post(config.url + 'message/share/v1', json={'token': register_users['token0'], 'og_message_id': register_users['channel_message_0'], 'message': "Hello", 'channel_id': register_users['channel_id'], 'dm_id': register_users['dm_id']})
    resp1 = requests.post(config.url + 'message/share/v1', json={'token': register_users['token0'], 'og_message_id': register_users['dm_message_0'], 'message': "Hello", 'channel_id': register_users['channel_id'], 'dm_id': register_users['dm_id']})
    # Expected status code (400) InputError
    assert resp0.status_code == 400
    assert resp1.status_code == 400

# og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined
def test_message_share_v1_og_message_id_invalid(clear, register_users):
    resp_0 = requests.post(config.url + 'message/share/v1', json={'token': register_users['token0'], 'og_message_id': -1, 'message': "Hello", 'channel_id': register_users['channel_id'], 'dm_id': -1})
    resp_1 = requests.post(config.url + 'message/share/v1', json={'token': register_users['token0'], 'og_message_id': 10, 'message': "Hello", 'channel_id': register_users['channel_id'], 'dm_id': -1})
    # Expected status code (400) InputError
    assert resp_0.status_code == 400
    assert resp_1.status_code == 400

# length of message is more than 1000 characters
def test_message_share_v1_message_long(clear, register_users):
    long = "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, \
            nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, \
            vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus \
            elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, \
            feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. \
            Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. N"

    resp0 = requests.post(config.url + 'message/share/v1', json={'token': register_users['token0'], 'og_message_id': register_users['channel_message_0'], 'message': long, 'channel_id': register_users['channel_id'], 'dm_id':-1})
    resp1 = requests.post(config.url + 'message/share/v1', json={'token': register_users['token0'], 'og_message_id': register_users['dm_message_0'], 'message': long, 'channel_id': -1, 'dm_id': register_users['dm_id']})
    # Expected status code (400) InputError
    assert resp0.status_code == 400
    assert resp1.status_code == 400

# the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) 
# and the authorised user has not joined the channel or DM they are trying to share the message to
def test_message_share_v1_not_a_member(clear, register_users):
    # Cengiz tries to share a message
    resp0 = requests.post(config.url + 'message/share/v1', json={'token': register_users['token2'], 'og_message_id': register_users['channel_message_0'], 'message': "Hello", 'channel_id': register_users['channel_id'], 'dm_id': -1})
    resp1 = requests.post(config.url + 'message/share/v1', json={'token': register_users['token2'], 'og_message_id': register_users['dm_message_0'], 'message': "Hello", 'channel_id': -1, 'dm_id': register_users['dm_id']})
    # Expected status code (403) AccessError
    assert resp0.status_code == 403
    assert resp1.status_code == 403

# invalid token
def test_message_share_v1_invalid_token(clear, register_users):
    resp0 = requests.post(config.url + 'message/share/v1', json={'token': -1, 'og_message_id': register_users['channel_message_0'], 'message': "Hello", 'channel_id': -1, 'dm_id': register_users['dm_id']})
    resp1 = requests.post(config.url + 'message/share/v1', json={'token': -1, 'og_message_id': register_users['dm_message_0'], 'message': "Hello", 'channel_id': register_users['channel_id'], 'dm_id': -1})
    # Expected status code (403) AccessError
    assert resp0.status_code == 403
    assert resp1.status_code == 403

# og_message_id, channel_id and dm_id are valid
def test_message_share_v1(clear, register_users):
    # Christina shares a message
    resp0 = requests.post(config.url + 'message/share/v1', json={'token': register_users['token0'], 'og_message_id': register_users['channel_message_0'], 'message': "Hello", 'channel_id': -1, 'dm_id': register_users['dm_id']})
    resp1 = requests.post(config.url + 'message/share/v1', json={'token': register_users['token0'], 'og_message_id': register_users['dm_message_0'], 'message': "Hello", 'channel_id': register_users['channel_id'], 'dm_id':-1})
    assert resp0.status_code == 200
    assert resp1.status_code == 200
