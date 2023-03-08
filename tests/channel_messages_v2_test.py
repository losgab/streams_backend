import pytest
import requests
from src import config


@pytest.fixture
def no_messages_output():
    return {
        'messages': [],
        'start': 0,
        'end': -1
    }

@pytest.fixture
def public_channel():
    # clear, register user, create public channel

    # clear
    resp_clear = requests.delete(config.url + 'clear/v1')
    assert resp_clear.status_code == 200

    # register user
    resp_register = requests.post(config.url + 'auth/register/v2',
                                  json={'email': 'test@gmail.com', 'password': 'password',
                                        'name_first': 'test', 'name_last': 'acc'})
    assert resp_register.status_code == 200
    token = resp_register.json()['token']

    # create public channel
    resp_create_channel = requests.post(config.url + 'channels/create/v2',
                                        json={'token': token, 'name': 'test channel', 'is_public': True})
    assert resp_create_channel.status_code == 200
    channel_id = resp_create_channel.json()['channel_id']

    return {
        'owner_token': token,
        'channel_id': channel_id
    }

@pytest.fixture
def private_channel():
    # clear, register user, create private channel

    # clear
    resp_clear = requests.delete(config.url + 'clear/v1')
    assert resp_clear.status_code == 200

    # register user
    resp_register = requests.post(config.url + 'auth/register/v2',
                                  json={'email': 'test@gmail.com', 'password': 'password',
                                        'name_first': 'test', 'name_last': 'acc'})
    assert resp_register.status_code == 200
    resp_register_data = resp_register.json()
    token = resp_register_data['token']

    # create private channel
    resp_create_channel = requests.post(config.url + 'channels/create/v2',
                                        json={'token': token, 'name': 'test channel', 'is_public': False})
    assert resp_create_channel.status_code == 200
    resp_create_channel_data = resp_create_channel.json()
    channel_id = resp_create_channel_data['channel_id']

    return {
        'owner_token': token,
        'channel_id': channel_id
    }

def test_messages_negative_inputs():
    # if token is invalid, then it raises an AccessError
    # assumption: if any of the other inputs are negative numbers, it will raise an InputError
    resp_clear = requests.delete(config.url + 'clear/v1')
    assert resp_clear.status_code == 200

    resp = requests.get(config.url + 'channel/messages/v2',
                        params={'token': -1, 'channel_id': 0, 'start': 0})
    assert resp.status_code == 403 # AccessError

    # register user
    resp_register = requests.post(config.url + 'auth/register/v2',
                                  json={'email': 'test@gmail.com', 'password': 'password',
                                        'name_first': 'test', 'name_last': 'acc'})
    assert resp_register.status_code == 200

    token = resp_register.json()['token']

    resp = requests.get(config.url + 'channel/messages/v2',
                        params={'token': token, 'channel_id': -1, 'start': 0})
    assert resp.status_code == 400 # InputError

    resp = requests.get(config.url + 'channel/messages/v2',
                        params={'token': token, 'channel_id': 0, 'start': -1})
    assert resp.status_code == 400 # InputError

    resp = requests.get(config.url + 'channel/messages/v2',
                        params={'token': -65, 'channel_id': -5, 'start': -23})
    assert resp.status_code == 403 # AccessError

def test_messages_check_users(public_channel):
    # try to access a channel from invalid users
    resp = requests.get(config.url + 'channel/messages/v2',
                        params={'token': 10, 'channel_id': public_channel['channel_id'], 'start': 0})
    assert resp.status_code == 403 # AccessError

    resp = requests.get(config.url + 'channel/messages/v2',
                        params={'token': 1, 'channel_id': public_channel['channel_id'], 'start': 0})
    assert resp.status_code == 403 # AccessError

    resp = requests.get(config.url + 'channel/messages/v2',
                        params={'token': 999, 'channel_id': public_channel['channel_id'], 'start': 0})
    assert resp.status_code == 403 # AccessError

def test_messages_no_messages_start_zero(public_channel, no_messages_output):
    # InputError when start is greater than the total number of messages in the channel
    # assumption: if a channel has zero messages, and channel_messages_v1 is called with start 0, it will return an empty messages list
    resp_messages = requests.get(config.url + 'channel/messages/v2',
                                 params={'token': public_channel['owner_token'],
                                         'channel_id': public_channel['channel_id'],
                                         'start': 0})
    resp_messages_data = resp_messages.json()
    assert resp_messages_data == no_messages_output

def test_messages_no_messages_start_one(public_channel):
    # InputError when start is greater than the total number of messages in the channel
    resp_messages = requests.get(config.url + 'channel/messages/v2',
                                 params={'token': public_channel['owner_token'],
                                         'channel_id': public_channel['channel_id'],
                                         'start': 1})
    assert resp_messages.status_code == 400 # InputError

def test_messages_no_messages_start_99(public_channel):
    # InputError when start is greater than the total number of messages in the channel
    resp_messages = requests.get(config.url + 'channel/messages/v2',
                                 params={'token': public_channel['owner_token'],
                                         'channel_id': public_channel['channel_id'],
                                         'start': 99})
    assert resp_messages.status_code == 400 # InputError

def test_messages_no_messages_start_negative_1(public_channel):
    # InputError when start is greater than the total number of messages in the channel
    resp_messages = requests.get(config.url + 'channel/messages/v2',
                                 params={'token': public_channel['owner_token'],
                                         'channel_id': public_channel['channel_id'],
                                         'start': -1})
    assert resp_messages.status_code == 400 # InputError

def test_messages_invalid_channel_id_no_channels():
    # InputError when channel_id does not refer to a valid channel

    # clear
    resp_clear = requests.delete(config.url + 'clear/v1')
    assert resp_clear.status_code == 200

    # register user
    resp_register = requests.post(config.url + 'auth/register/v2',
                                  json={'email': 'test@gmail.com', 'password': 'password',
                                        'name_first': 'test', 'name_last': 'acc'})
    assert resp_register.status_code == 200
    resp_register_data = resp_register.json()
    token = resp_register_data['token']

    # channel messages
    resp_messages = requests.get(config.url + 'channel/messages/v2',
                                 params={'token': token, 'channel_id': 0, 'start': 0})
    assert resp_messages.status_code == 400 # InputError

def test_messages_invalid_channel_id_one_channel(public_channel):
    # InputError when channel_id does not refer to a valid channel
    # channel messages
    resp_messages = requests.get(config.url + 'channel/messages/v2',
                                 params={'token': public_channel['owner_token'],
                                         'channel_id': 999999999999, 'start': 0})
    assert resp_messages.status_code == 400 # InputError

def test_messages_user_not_member_public(public_channel):
    # AccessError when channel_id is valid and authorised user is not a member of the channel

    # register second user
    resp_register = requests.post(config.url + 'auth/register/v2',
                                  json={'email': 'otheruser@gmail.com', 'password': 'password',
                                        'name_first': 'other', 'name_last': 'user'})
    assert resp_register.status_code == 200
    resp_register_data = resp_register.json()
    otheruser_token = resp_register_data['token']

    # channel messages
    resp_messages = requests.get(config.url + 'channel/messages/v2',
                                 params={'token': otheruser_token,
                                         'channel_id': public_channel['channel_id'],
                                         'start': 0})
    assert resp_messages.status_code == 403 # AccessError

def test_messages_user_not_member_private(private_channel):
    # AccessError when channel_id is valid and authorised user is not a member of the channel

    # register second user
    resp_register = requests.post(config.url + 'auth/register/v2',
                                  json={'email': 'otheruser@gmail.com', 'password': 'password',
                                        'name_first': 'other', 'name_last': 'user'})
    assert resp_register.status_code == 200
    resp_register_data = resp_register.json()
    otheruser_token = resp_register_data['token']

    # channel messages
    resp_messages = requests.get(config.url + 'channel/messages/v2',
                                 params={'token': otheruser_token,
                                         'channel_id': private_channel['channel_id'],
                                         'start': 0})
    assert resp_messages.status_code == 403 # AccessError

def test_messages_no_messages_public_channel_created_by_other_person(public_channel, no_messages_output):
    # register second user
    resp_register = requests.post(config.url + 'auth/register/v2',
                                  json={'email': 'otheruser@gmail.com', 'password': 'password',
                                        'name_first': 'other', 'name_last': 'user'})
    assert resp_register.status_code == 200
    resp_register_data = resp_register.json()
    otheruser_token = resp_register_data['token']

    # second user joins the channel
    resp_join = requests.post(config.url + 'channel/join/v2',
                              json={'token': otheruser_token,
                                    'channel_id': public_channel['channel_id']})
    assert resp_join.status_code == 200

    # channel messages called by second user
    resp_messages = requests.get(config.url + 'channel/messages/v2',
                                 params={'token': otheruser_token,
                                         'channel_id': public_channel['channel_id'],
                                         'start': 0})
    resp_messages_data = resp_messages.json()
    assert resp_messages_data == no_messages_output

def test_messages_no_messages_private_channel_created_by_other_person(private_channel, no_messages_output):
    # register second user
    resp_register = requests.post(config.url + 'auth/register/v2',
                                  json={'email': 'otheruser@gmail.com', 'password': 'password',
                                        'name_first': 'other', 'name_last': 'user'})
    assert resp_register.status_code == 200
    resp_register_data = resp_register.json()
    otheruser_token = resp_register_data['token']
    u_id = resp_register_data['auth_user_id']

    # second user is invited to the channel
    resp_invite = requests.post(config.url + 'channel/invite/v2',
                                json={'token': private_channel['owner_token'],
                                      'channel_id': private_channel['channel_id'],
                                      'u_id': u_id})
    assert resp_invite.status_code == 200

    # channel messages called by second user
    resp_messages = requests.get(config.url + 'channel/messages/v2',
                                 params={'token': otheruser_token,
                                         'channel_id': private_channel['channel_id'],
                                         'start': 0})
    resp_messages_data = resp_messages.json()
    assert resp_messages_data == no_messages_output
