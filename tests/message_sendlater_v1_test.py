import pytest
import requests
import json
import time
from src import config


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

def test_sendlater_invalid_channel():
    # InputError 400 when channel_id does not refer to a valid channel

    # clear
    resp_clear = requests.delete(config.url + 'clear/v1')
    assert resp_clear.status_code == 200

    # register user
    resp_register = requests.post(config.url + 'auth/register/v2', json = {
        'email': 'user@domain.com',
        'password': 'password',
        'name_first': 'user',
        'name_last': 'zero'
    })
    user = resp_register.json()

    # use sendlater with invalid channel id
    resp_sendlater = requests.post(config.url + 'message/sendlater/v1', json = {
        'token': user['token'],
        'channel_id': 0,
        'message': 'ahhhhhhhhh',
        'time_sent': int(time.time()) + 5
    })
    assert resp_sendlater.status_code == 400

    resp_sendlater = requests.post(config.url + 'message/sendlater/v1', json = {
        'token': user['token'],
        'channel_id': 1,
        'message': 'ahhhhhhhhh',
        'time_sent': int(time.time()) + 5
    })
    assert resp_sendlater.status_code == 400

    resp_sendlater = requests.post(config.url + 'message/sendlater/v1', json = {
        'token': user['token'],
        'channel_id': -1,
        'message': 'ahhhhhhhhh',
        'time_sent': int(time.time()) + 5
    })
    assert resp_sendlater.status_code == 400

def test_sendlater_invalid_channel_two(public_channel):
    # InputError 400 when channel_id does not refer to a valid channel
    resp_sendlater = requests.post(config.url + 'message/sendlater/v1', json = {
        'token': public_channel['owner_token'],
        'channel_id': 1,
        'message': 'ahhhhhhhhh',
        'time_sent': int(time.time()) + 5
    })
    assert resp_sendlater.status_code == 400

def test_sendlater_message_too_short(public_channel):
    # InputError 400 when message length is less than 1 character
    resp_sendlater = requests.post(config.url + 'message/sendlater/v1', json = {
        'token': public_channel['owner_token'],
        'channel_id': public_channel['channel_id'],
        'message': '',
        'time_sent': int(time.time()) + 5
    })
    assert resp_sendlater.status_code == 400

def test_sendlater_message_too_long(public_channel):
    # InputError 400 when message length is greater than 1000 characters (i.e. 1001 or above)

    message = 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Na'

    resp_sendlater = requests.post(config.url + 'message/sendlater/v1', json = {
        'token': public_channel['owner_token'],
        'channel_id': public_channel['channel_id'],
        'message': message,
        'time_sent': int(time.time()) + 5
    })
    assert resp_sendlater.status_code == 400

def test_sendlater_time_passed(public_channel):
    # InputError 400 when time_sent is a time in the past
    resp_sendlater = requests.post(config.url + 'message/sendlater/v1', json = {
        'token': public_channel['owner_token'],
        'channel_id': public_channel['channel_id'],
        'message': 'hello',
        'time_sent': int(time.time()) - 5
    })
    assert resp_sendlater.status_code == 400

def test_sendlater_user_not_channel_member(public_channel):
    # AccessError 403 when channel_id is valid and the authorised user is not a member
    # of a channel they are trying to post to

    # register other user
    resp_register = requests.post(config.url + 'auth/register/v2', json = {
        'email': 'otheruser@domain.com',
        'password': 'password',
        'name_first': 'other',
        'name_last': 'user'
    })
    user = resp_register.json()

    resp_sendlater = requests.post(config.url + 'message/sendlater/v1', json = {
        'token': user['token'],
        'channel_id': public_channel['channel_id'],
        'message': 'hello',
        'time_sent': int(time.time()) + 5
    })
    assert resp_sendlater.status_code == 403

def test_sendlater_invalid_token(public_channel):
    # AccessError 403 when token is invalid
    # is handled by the token functions

    resp_sendlater = requests.post(config.url + 'message/sendlater/v1', json = {
        'token': 1,
        'channel_id': public_channel['channel_id'],
        'message': 'hello',
        'time_sent': int(time.time()) + 5
    })
    assert resp_sendlater.status_code == 403

    resp_sendlater = requests.post(config.url + 'message/sendlater/v1', json = {
        'token': -1,
        'channel_id': public_channel['channel_id'],
        'message': 'hello',
        'time_sent': int(time.time()) + 5
    })
    assert resp_sendlater.status_code == 403

def test_sendlater_success_public(public_channel):
    message = 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. N'

    send_time = int(time.time()) + 1

    resp_sendlater = requests.post(config.url + 'message/sendlater/v1', json = {
        'token': public_channel['owner_token'],
        'channel_id': public_channel['channel_id'],
        'message': message,
        'time_sent': send_time
    })
    assert resp_sendlater.status_code == 200
    assert resp_sendlater.json()['message_id'] == 0

    # verify that the message is sent 1 second later
    time.sleep(1)
    resp_messages = requests.get(config.url + 'channel/messages/v2', params = {
        'token': public_channel['owner_token'],
        'channel_id': public_channel['channel_id'],
        'start': 0
    })
    assert resp_messages.status_code == 200
    message_data = resp_messages.json()
    assert message_data['messages'][0]['message_id'] == 0
    assert message_data['messages'][0]['message'] == message
    assert message_data['messages'][0]['time_sent'] == send_time

def test_sendlater_success_private(private_channel):
    message = 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. N'

    send_time = int(time.time()) + 1

    # Create a channel for coverage
    requests.post(config.url + 'channels/create/v2',
                  json={'token': private_channel['owner_token'], 'name': 'BEAR', 'is_public': True})

    resp_sendlater = requests.post(config.url + 'message/sendlater/v1', json = {
        'token': private_channel['owner_token'],
        'channel_id': private_channel['channel_id'],
        'message': message,
        'time_sent': send_time
    })
    assert resp_sendlater.status_code == 200
    assert resp_sendlater.json()['message_id'] == 0

    # verify that the message is sent 1 second later
    time.sleep(1)
    resp_messages = requests.get(config.url + 'channel/messages/v2', params = {
        'token': private_channel['owner_token'],
        'channel_id': private_channel['channel_id'],
        'start': 0
    })
    assert resp_messages.status_code == 200
    message_data = resp_messages.json()
    assert message_data['messages'][0]['message_id'] == 0
    assert message_data['messages'][0]['message'] == message
    assert message_data['messages'][0]['time_sent'] == send_time

def test_sendlater_and_normal_message(public_channel):
    # send message in 1 second, but before the second has passed, send a normal message
    send_time = int(time.time()) + 1
    resp_sendlater = requests.post(config.url + 'message/sendlater/v1', json = {
        'token': public_channel['owner_token'],
        'channel_id': public_channel['channel_id'],
        'message': 'sendlater message',
        'time_sent': send_time
    })
    assert resp_sendlater.status_code == 200
    assert resp_sendlater.json()['message_id'] == 0

    # the normal message
    resp_send = requests.post(config.url + 'message/send/v1', json = {
        'token': public_channel['owner_token'],
        'channel_id': public_channel['channel_id'],
        'message': 'normal message',
        'time_sent': int(time.time())
    })
    assert resp_send.status_code == 200

    # verify the messages
    time.sleep(1)
    resp_messages = requests.get(config.url + 'channel/messages/v2', params = {
        'token': public_channel['owner_token'],
        'channel_id': public_channel['channel_id'],
        'start': 0
    })
    message_data = resp_messages.json()

    assert message_data['messages'][0]['message_id'] == 0
    assert message_data['messages'][0]['message'] == 'sendlater message'
    assert message_data['messages'][0]['time_sent'] == send_time

    assert message_data['messages'][1]['message_id'] == 1
    assert message_data['messages'][1]['message'] == 'normal message'

def test_sendlater_multiple_channels(public_channel):
    # create second channel
    resp_create_channel = requests.post(config.url + 'channels/create/v2', json = {
        'token': public_channel['owner_token'],
        'name': 'second channel',
        'is_public': False
    })
    assert resp_create_channel.status_code == 200
    channel_id2 = resp_create_channel.json()['channel_id']

    # put some messages in second channel
    resp_send = requests.post(config.url + 'message/send/v1', json = {
        'token': public_channel['owner_token'],
        'channel_id': channel_id2,
        'message': 'second channel message 1',
        'time_sent': int(time.time())
    })
    assert resp_send.status_code == 200

    resp_send = requests.post(config.url + 'message/send/v1', json = {
        'token': public_channel['owner_token'],
        'channel_id': channel_id2,
        'message': 'second channel message 2',
        'time_sent': int(time.time())
    })
    assert resp_send.status_code == 200

    # put some messages in first channel
    resp_send = requests.post(config.url + 'message/send/v1', json = {
        'token': public_channel['owner_token'],
        'channel_id': public_channel['channel_id'],
        'message': 'first channel message 1',
        'time_sent': int(time.time())
    })
    assert resp_send.status_code == 200

    resp_send = requests.post(config.url + 'message/send/v1', json = {
        'token': public_channel['owner_token'],
        'channel_id': public_channel['channel_id'],
        'message': 'first channel message 2',
        'time_sent': int(time.time())
    })
    assert resp_send.status_code == 200

    send_time = int(time.time()) + 1

    resp_sendlater = requests.post(config.url + 'message/sendlater/v1', json = {
        'token': public_channel['owner_token'],
        'channel_id': public_channel['channel_id'],
        'message': 'sendlater message',
        'time_sent': send_time
    })
    assert resp_sendlater.status_code == 200
    assert resp_sendlater.json()['message_id'] == 4

    # verify messages in first channel 1 second later
    time.sleep(1)
    resp_messages = requests.get(config.url + 'channel/messages/v2', params = {
        'token': public_channel['owner_token'],
        'channel_id': public_channel['channel_id'],
        'start': 0
    })
    assert resp_messages.status_code == 200
    message_data = resp_messages.json()
    assert message_data['messages'][0]['message_id'] == 4
    assert message_data['messages'][0]['message'] == 'sendlater message'
    assert message_data['messages'][0]['time_sent'] == send_time
