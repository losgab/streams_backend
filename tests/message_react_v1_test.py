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
    # Send messages in channel and dms
    msg_0_json = requests.post(config.url + 'message/send/v1', json={'token': user_0['token'], 'channel_id': channel['channel_id'], 'message': 'hello'})
    msg_0 = json.loads(msg_0_json.text)
    msg_1_json = requests.post(config.url + 'message/send/v1', json={'token': user_0['token'], 'channel_id': channel['channel_id'], 'message': 'bye'})
    msg_1 = json.loads(msg_1_json.text)
    dm_msg_0_json = requests.post(config.url + 'message/senddm/v1', json={'token': user_0['token'], 'dm_id': dm_1['dm_id'], 'message': 'hello'})
    dm_msg_0 = json.loads(dm_msg_0_json.text)
    dm_msg_1_json = requests.post(config.url + 'message/senddm/v1', json={'token': user_0['token'], 'dm_id': dm_1['dm_id'], 'message': "hello !!"})
    dm_msg_1 = json.loads(dm_msg_1_json.text)
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
        'dm_msg_1': dm_msg_1['message_id']
    }

# AccessError (403), invalid token input
def test_react_invalid_token(clear, register):
    resp_0 = requests.post(config.url + 'message/react/v1', json={'token': -1, 'message_id': register['dm_msg_0'], 'react_id': 1})
    resp_1 = requests.post(config.url + 'message/react/v1', json={'token': 10, 'message_id': register['dm_msg_0'], 'react_id': 1})
    # Expected status code (403) AccessError
    assert resp_0.status_code == 403
    assert resp_1.status_code == 403

def test_react_invalid_message_id(clear, register):
# InputError (400), message_id does not exist
    resp_0 = requests.post(config.url + 'message/react/v1', json={'token': register['token0'], 'message_id': -1, 'react_id': 1})
    resp_1 = requests.post(config.url + 'message/react/v1', json={'token': register['token0'], 'message_id': 10, 'react_id': 1})
    # Expected status code (400) InputError
    assert resp_0.status_code == 400
    assert resp_1.status_code == 400

# InputError (400), authorised user not in channel
def test_react_not_member_channel(clear, register):
    # Cengiz tries to react to a message in a channel hes not in
    resp_0 = requests.post(config.url + 'message/react/v1', json={'token': register['token2'], 'message_id': register['channel_msg_0'], 'react_id': 1})
    resp_1 = requests.post(config.url + 'message/react/v1', json={'token': register['token2'], 'message_id': register['channel_msg_1'], 'react_id': 1})
    # Expected status code (400) InputError
    assert resp_0.status_code == 400
    assert resp_1.status_code == 400

# InputError (400), authorised user not in dm
def test_react_not_member_dm(clear, register):
    # Cengiz tries to react to a message in a dm hes not in
    resp_0 = requests.post(config.url + 'message/react/v1', json={'token': register['token2'], 'message_id': register['dm_msg_0'], 'react_id': 1})
    resp_1 = requests.post(config.url + 'message/react/v1', json={'token': register['token2'], 'message_id': register['dm_msg_1'], 'react_id': 1})
    # Expected status code (400) InputError
    assert resp_0.status_code == 400
    assert resp_1.status_code == 400

# InputError (400), invalid react ID (currently only 1 is valid)
def test_react_invalid_react_id(clear, register):
    # Christina tries to react with react id 0 and 2
    resp_0 = requests.post(config.url + 'message/react/v1', json={'token': register['token1'], 'message_id': register['dm_msg_0'], 'react_id': 0})
    resp_1 = requests.post(config.url + 'message/react/v1', json={'token': register['token1'], 'message_id': register['dm_msg_1'], 'react_id': 2})
    # Expected status code (400) InputError
    assert resp_0.status_code == 400
    assert resp_1.status_code == 400

# InputError (400), the auth user already reacted to the message (dm + channel)
def test_react_already_reacted(clear, register):
    # Celina tries to react to messages twice
    resp_0 = requests.post(config.url + 'message/react/v1', json={'token': register['token0'], 'message_id': register['dm_msg_0'], 'react_id': 1})
    resp_1 = requests.post(config.url + 'message/react/v1', json={'token': register['token0'], 'message_id': register['dm_msg_0'], 'react_id': 1})
    resp_2 = requests.post(config.url + 'message/react/v1', json={'token': register['token0'], 'message_id': register['channel_msg_0'], 'react_id': 1})
    resp_3 = requests.post(config.url + 'message/react/v1', json={'token': register['token0'], 'message_id': register['channel_msg_0'], 'react_id': 1})
    # Expected status code (400) InputError
    assert resp_0.status_code == 200
    assert resp_1.status_code == 400
    assert resp_2.status_code == 200
    assert resp_3.status_code == 400

# Test successful case
def test_react_successful_channel(clear, register):
    # Celina reacts (1) to all messages in channels and dms
    resp_0 = requests.post(config.url + 'message/react/v1', json={'token': register['token0'], 'message_id': register['dm_msg_0'], 'react_id': 1})
    resp_1 = requests.post(config.url + 'message/react/v1', json={'token': register['token0'], 'message_id': register['dm_msg_1'], 'react_id': 1})
    resp_2 = requests.post(config.url + 'message/react/v1', json={'token': register['token0'], 'message_id': register['channel_msg_0'], 'react_id': 1})
    resp_3 = requests.post(config.url + 'message/react/v1', json={'token': register['token0'], 'message_id': register['channel_msg_1'], 'react_id': 1})
    resp_4 = requests.post(config.url + 'message/react/v1', json={'token': register['token1'], 'message_id': register['channel_msg_1'], 'react_id': 1})
    # Expected status code (200), successful
    assert resp_0.status_code == 200
    assert resp_1.status_code == 200
    assert resp_2.status_code == 200
    assert resp_3.status_code == 200
    assert resp_4.status_code == 200
    # Expected output
    assert resp_0.json() == {}
    assert resp_1.json() == {}
    assert resp_2.json() == {}
    assert resp_3.json() == {}
    assert resp_4.json() == {}
    # Expected behaviour
    dm_messages = requests.get(config.url + 'dm/messages/v1', params={'token': register['token0'], 'dm_id': register['dm_id'], 'start': 0})
    channel_messages = requests.get(config.url + 'channel/messages/v2', params={'token': register['token1'], 'channel_id': register['channel_id'], 'start': 0})
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
                        'u_ids': [register['u_id_0']],
                        'is_this_user_reacted': True,
                    }
                ],
                'is_pinned': False,
            },
            {
                'message_id': register['dm_msg_0'],
                'u_id': register['u_id_0'],
                'message': 'hello',
                'time_sent': register['time'],
                'reacts': [
                    {
                        'react_id': 1,
                        'u_ids': [register['u_id_0']],
                        'is_this_user_reacted': True,
                    }
                ],
                'is_pinned': False,
            },
        ],
        'start': 0,
        'end': -1,
    }
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
                        'u_ids': [register['u_id_0'], register['u_id_1']],
                        'is_this_user_reacted': True,
                    }
                ],
                'is_pinned': False,
            },
            {
                'message_id': register['channel_msg_0'],
                'u_id': register['u_id_0'],
                'message': 'hello',
                'time_sent': register['time'],
                'reacts': [
                    {
                        'react_id': 1,
                        'u_ids': [register['u_id_0']],
                        'is_this_user_reacted': False,
                    }
                ],
                'is_pinned': False,
            },
            
        ],
        'start': 0,
        'end': -1,
    }
    