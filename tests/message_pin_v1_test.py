import pytest
import requests
import json
from src import config
import time

# Fixture that clears the data store
@pytest.fixture
def clear():
    requests.delete(config.url  + 'clear/v1')

# Fixture that registers 2 users and sends a few messages
@pytest.fixture
def register():
    # register users celina and christina
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'celina@domain.com', 'password': 'password', 'name_first': 'celina', 'name_last': 'shen'})
    user_0 = json.loads(user_0_json.text)
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'christina@domain.com', 'password': 'password', 'name_first': 'christina', 'name_last': 'lee'})
    user_1 = json.loads(user_1_json.text)
    user_2_json = requests.post(config.url + 'auth/register/v2', json={'email': 'cengiz@domain.com', 'password': 'password', 'name_first': 'cengiz', 'name_last': 'cimen'})
    user_2 = json.loads(user_2_json.text)
    # Create channel to send msgs in
    channel_json = requests.post(config.url + 'channels/create/v2', json={'token': user_0['token'], 'name': 'test channel', 'is_public': True})
    channel = json.loads(channel_json.text)
    # Christina joins channel
    channel_json = requests.post(config.url + 'channel/join/v2', json={'token': user_1['token'], 'channel_id': channel['channel_id'], })
    # Create dm with members celina and christina
    dm_1_json = requests.post(config.url + 'dm/create/v1', json={'token': user_0['token'], 'u_ids': [user_1['auth_user_id']]})
    dm_1 = json.loads(dm_1_json.text)
    # Create a dm with Christina and Celina (Christina is owner)
    dm_2_json = requests.post(config.url + 'dm/create/v1', json={'token': user_1['token'], 'u_ids': [user_0['auth_user_id']]})
    dm_2 = json.loads(dm_2_json.text)
    # Send messages in channel and dms
    msg_0_json = requests.post(config.url + 'message/send/v1', json={'token': user_0['token'], 'channel_id': channel['channel_id'], 'message': 'hello'})
    msg_0 = json.loads(msg_0_json.text)
    msg_1_json = requests.post(config.url + 'message/send/v1', json={'token': user_0['token'], 'channel_id': channel['channel_id'], 'message': 'bye'})
    msg_1 = json.loads(msg_1_json.text)
    dm_msg_0_json = requests.post(config.url + 'message/senddm/v1', json={'token': user_0['token'], 'dm_id': dm_1['dm_id'], 'message': 'hello'})
    dm_msg_0 = json.loads(dm_msg_0_json.text)
    dm_msg_1_json = requests.post(config.url + 'message/senddm/v1', json={'token': user_0['token'], 'dm_id': dm_1['dm_id'], 'message': "hello !!"})
    dm_msg_1 = json.loads(dm_msg_1_json.text)
    dm_msg_2_json = requests.post(config.url + 'message/senddm/v1', json={'token': user_0['token'], 'dm_id': dm_2['dm_id'], 'message': "Hi c:"})
    dm_msg_2 = json.loads(dm_msg_2_json.text)
    curr_time = int( time.time() )
    # return dictionary of tokens and message id's
    return {
        'time':  curr_time,
        'token0': user_0['token'],
        'token1': user_1['token'],
        'token2': user_2['token'],
        'u_id_0': user_0['auth_user_id'],
        'u_id_1': user_1['auth_user_id'],
        'channel_id': channel['channel_id'],
        'channel_msg_0': msg_0['message_id'],
        'channel_msg_1': msg_1['message_id'],
        'dm_id': dm_1['dm_id'],
        'dm_msg_0': dm_msg_0['message_id'],
        'dm_msg_1': dm_msg_1['message_id'],
        'dm_msg_2': dm_msg_2['message_id']
    }

# AccessError (403), invalid token input
def test_message_pin_invalid_token(clear, register):
    resp_0 = requests.post(config.url + 'message/pin/v1', json={'token': -1, 'message_id': register['channel_msg_0']})
    resp_1 = requests.post(config.url + 'message/pin/v1', json={'token': 10, 'message_id': register['dm_msg_0']})
    # Assert expected status code (403) AccessError
    assert resp_0.status_code == 403
    assert resp_1.status_code == 403

# AccessError (403), not owner / global owner of channel 
def test_message_pin_no_permissions_channel(clear, register):
    resp_0 = requests.post(config.url + 'message/pin/v1', json={'token': register['token1'], 'message_id': register['channel_msg_0']})
    resp_1 = requests.post(config.url + 'message/pin/v1', json={'token': register['token1'], 'message_id': register['channel_msg_1']})
    # Assert expected status code (403) AccesssError
    assert resp_0.status_code == 403
    assert resp_1.status_code == 403

# AccessError (403), not owner of DM
def test_message_pin_no_permissions_dm(clear, register):
    # Member but not Owner of dm
    resp_0 = requests.post(config.url + 'message/pin/v1', json={'token': register['token1'], 'message_id': register['dm_msg_0']})
    resp_1 = requests.post(config.url + 'message/pin/v1', json={'token': register['token1'], 'message_id': register['dm_msg_1']})
    # Global owner but not owner of dm
    resp_2 = requests.post(config.url + 'message/pin/v1', json={'token': register['token0'], 'message_id': register['dm_msg_2']})
    # Assert expected status code (403) AccesssError
    assert resp_0.status_code == 403
    assert resp_1.status_code == 403
    assert resp_2.status_code == 403

# InputError (400), the message_id does not exist
def test_pin_invalid_message_id(clear, register):
    resp_0 = requests.post(config.url + 'message/pin/v1', json={'token': register['token0'], 'message_id': -1})
    resp_1 = requests.post(config.url + 'message/pin/v1', json={'token': register['token0'], 'message_id': 10})
    # Assert expected status code (400) InputError
    assert resp_0.status_code == 400
    assert resp_1.status_code == 400

# InputError (400), the authorised user not in channel with message id
def test_pin_not_member_channel(clear, register):
    resp_0 = requests.post(config.url + 'message/pin/v1', json={'token': register['token2'], 'message_id': register['channel_msg_0']})
    resp_1 = requests.post(config.url + 'message/pin/v1', json={'token': register['token2'], 'message_id': register['channel_msg_1']})
    # Assert expected status code (400) InputError
    assert resp_0.status_code == 400
    assert resp_1.status_code == 400

# InputError (400), the authorised user not in dm with message id
def test_pin_not_member_dm(clear, register):
    resp_0 = requests.post(config.url + 'message/pin/v1', json={'token': register['token2'], 'message_id': register['dm_msg_0']})
    resp_1 = requests.post(config.url + 'message/pin/v1', json={'token': register['token2'], 'message_id': register['dm_msg_1']})
    # Assert expected status code (400) InputError
    assert resp_0.status_code == 400
    assert resp_1.status_code == 400

# InputError (400), the message is already pinned (channels + dms)
def test_pin_already_pinned(clear, register):
    # Celina tries to pin messages twice
    resp_0 = requests.post(config.url + 'message/pin/v1', json={'token': register['token0'], 'message_id': register['channel_msg_0']})
    resp_1 = requests.post(config.url + 'message/pin/v1', json={'token': register['token0'], 'message_id': register['channel_msg_0']})
    resp_2 = requests.post(config.url + 'message/pin/v1', json={'token': register['token0'], 'message_id': register['dm_msg_0']})
    resp_3 = requests.post(config.url + 'message/pin/v1', json={'token': register['token0'], 'message_id': register['dm_msg_0']})

    # Assert expected status code (400) InputError
    assert resp_0.status_code == 200
    assert resp_1.status_code == 400
    assert resp_2.status_code == 200
    assert resp_3.status_code == 400

# Test successful case channels
def test_pin_successful_channel(clear, register):
    # Celina pins both messages in channel
    resp_0 = requests.post(config.url + 'message/pin/v1', json={'token': register['token0'], 'message_id': register['channel_msg_0']})
    resp_1 = requests.post(config.url + 'message/pin/v1', json={'token': register['token0'], 'message_id': register['channel_msg_1']})
    # Expected status code (200), successful
    assert resp_0.status_code == 200
    assert resp_1.status_code == 200
    # Assert expected output
    assert resp_0.json() == {}
    assert resp_1.json() == {}
    # Expected behaviour
    channel_messages = requests.get(config.url + 'channel/messages/v2', params={'token': register['token1'], 'channel_id': register['channel_id'], 'start': 0})
    assert channel_messages.json() == {
        'messages': [
            {
                'message_id': register['channel_msg_1'],
                'u_id': register['u_id_0'],
                'message': 'bye',
                'time_sent': register['time'],
                'reacts': [
                    {
                        'react_id': 1,
                        'u_ids': [],
                        'is_this_user_reacted': False,
                    }
                ],
                'is_pinned': True,
            },
            {
                'message_id': register['channel_msg_0'],
                'u_id': register['u_id_0'],
                'message': 'hello',
                'time_sent': register['time'],
                'reacts': [
                    {
                        'react_id': 1,
                        'u_ids': [],
                        'is_this_user_reacted': False,
                    }
                ],
                'is_pinned': True,
            },
            
        ],
        'start': 0,
        'end': -1,
    }

# Test successful case channels
def test_pin_successful_dm(clear, register):
    # Celina pins both messages in channel
    resp_0 = requests.post(config.url + 'message/pin/v1', json={'token': register['token0'], 'message_id': register['dm_msg_0']})
    resp_1 = requests.post(config.url + 'message/pin/v1', json={'token': register['token0'], 'message_id': register['dm_msg_1']})
    # Expected status code (200), successful
    assert resp_0.status_code == 200
    assert resp_1.status_code == 200
    # Assert expected output
    assert resp_0.json() == {}
    assert resp_1.json() == {}
    # Expected behaviour
    dm_messages = requests.get(config.url + 'dm/messages/v1', params={'token': register['token0'], 'dm_id': register['dm_id'], 'start': 0})
    assert dm_messages.json() == {
        'messages': [
            {
                'message_id': register['dm_msg_1'],
                'u_id': register['u_id_0'],
                'message': 'hello !!',
                'time_sent': register['time'],
                'reacts': [
                    {
                        'react_id': 1,
                        'u_ids': [],
                        'is_this_user_reacted': False,
                    }
                ],
                'is_pinned': True,
            },
            {
                'message_id': register['dm_msg_0'],
                'u_id': register['u_id_0'],
                'message': 'hello',
                'time_sent': register['time'],
                'reacts': [
                    {
                        'react_id': 1,
                        'u_ids': [],
                        'is_this_user_reacted': False,
                    }
                ],
                'is_pinned': True,
            },
        ],
        'start': 0,
        'end': -1,
    }
