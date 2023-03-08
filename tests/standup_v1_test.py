import pytest
import requests
import time
from src.error import InputError, AccessError
from src import config

@pytest.fixture
def public_channel():
    # clear, register user, create public channel
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

# TESTS FOR STANDUP CREATE

# STATUS 400: The channel ID is invalid
def test_standup_start_invalid_channel_id(public_channel):
    # Create a standup
    req = requests.post(config.url + 'standup/start/v1', json={
                'token': public_channel['owner_token'], 
                'channel_id' : -13213, 
                'length': 1000})
    assert req.status_code == InputError.code


# STATUS 400: The standup length is a negative value
def test_standup_start_negative_length(public_channel):
    # Create a standup
    req = requests.post(config.url + 'standup/start/v1', json={
                'token': public_channel['owner_token'], 
                'channel_id' : public_channel['channel_id'], 
                'length': -2})
    assert req.status_code == InputError.code

# STATUS 400: Another standup is already running
def test_standup_start_active_standup_already_running(public_channel):
    # Create a standup
    requests.post(config.url + 'standup/start/v1', json={
                'token': public_channel['owner_token'], 
                'channel_id' : public_channel['channel_id'], 
                'length': 1000})
    # Create another standup
    req = requests.post(config.url + 'standup/start/v1', json={
                'token': public_channel['owner_token'], 
                'channel_id' : public_channel['channel_id'], 
                'length': 1000})
    assert req.status_code == InputError.code

# STATUS 403: The authorised user is not a member of the channel
def test_standup_start_channel_id_valid_authorised_user_not_member(public_channel):
    # Create a new user that is not a part of the channel
    resp_register = requests.post(config.url + 'auth/register/v2',
                                  json={'email': 'testafeiownwe@gmail.com', 'password': 'password',
                                        'name_first': 'test', 'name_last': 'acc'})
    assert resp_register.status_code == 200
    new_user_token = resp_register.json()['token']

    req = requests.post(config.url + 'standup/start/v1', json={
                'token': new_user_token, 
                'channel_id' : public_channel['channel_id'], 
                'length': 1})
    assert req.status_code == AccessError.code

# STATUS 200: The standup is succesfully created
def test_standup_start_success(public_channel):
    # Register a new user to be added to the DM
    resp_register = requests.post(config.url + 'auth/register/v2',
                                  json={'email': 'testafeiownwe@gmail.com', 'password': 'password',
                                        'name_first': 'test', 'name_last': 'acc'})
    assert resp_register.status_code == 200
    new_user_id = resp_register.json()['auth_user_id']

    # Create a dm (increases coverage for generating the message id of the standup)
    requests.post(config.url + 'dm/create/v1', 
        json={
            'token' : public_channel['owner_token'],
            'u_ids' : [new_user_id]
        })
    # Start the standup
    req = requests.post(config.url + 'standup/start/v1', json={
                'token': public_channel['owner_token'], 
                'channel_id' : public_channel['channel_id'],
                'length': 0})
    assert req.status_code == 200

# TESTS FOR STANDUP ACTIVE

# STATUS 400: The channel ID is invalid
def test_standup_active_invalid_channel_id(public_channel):

    resp = requests.get(config.url + 'standup/active/v1', params={'token': public_channel['owner_token'], 'channel_id': -1}) 
    assert resp.status_code == InputError.code

# STATUS 403: The authorised user is not a member of the channel
def test_standup_active_channel_id_valid_authorised_user_not_member(public_channel):

    # Create a new user that is not a part of the channel
    resp_register = requests.post(config.url + 'auth/register/v2',
                                  json={'email': 'testafeiownwe@gmail.com', 'password': 'password',
                                        'name_first': 'test', 'name_last': 'acc'})
    assert resp_register.status_code == 200
    new_user_token = resp_register.json()['token']
    resp = requests.get(config.url + 'standup/active/v1', params={'token': new_user_token, 'channel_id': public_channel['channel_id']})
    assert resp.status_code == AccessError.code

# STATUS 200: The standup status returns successfully
def test_standup_active_success(public_channel):
    resp = requests.get(config.url + 'standup/active/v1', params={'token': public_channel['owner_token'], 'channel_id': public_channel['channel_id']})
    assert resp.status_code == 200



# TESTS FOR STANDUP SEND

# STATUS 403: Channel ID is valid and the authorised user is not a member of the channel
def test_standup_send_channel_user_id_invalid(public_channel):
    # Register a new user to be added to the DM
    resp_register = requests.post(config.url + 'auth/register/v2',
                                  json={'email': 'aksjnbdasjkbdas@gmail.com', 'password': 'password',
                                        'name_first': 'test', 'name_last': 'acc'})
    assert resp_register.status_code == 200

    # Start a standup
    req = requests.post(config.url + 'standup/start/v1', json={
                'token': public_channel['owner_token'], 
                'channel_id' : public_channel['channel_id'], 
                'length': 1})
    assert req.status_code == 200

    # Attempt invalid user to send message
    req = requests.post(config.url + 'standup/send/v1', json={
                'token': resp_register.json()['token'], 
                'channel_id' : public_channel['channel_id'], 
                'message': "This is a message"})

    assert req.status_code == AccessError.code


# STATUS 400: The length of the message is over 1000 characters
def test_standup_send_channel_id_invalid(public_channel):
    # Start a standup
    req = requests.post(config.url + 'standup/start/v1', json={
                'token': public_channel['owner_token'], 
                'channel_id' : public_channel['channel_id'], 
                'length': 1})
    assert req.status_code == 200

    # Attempt auth user to send to invalid channel
    req = requests.post(config.url + 'standup/send/v1', json={
                'token': public_channel['owner_token'], 
                'channel_id' : -1291203, 
                'message': "This is a message"})

    assert req.status_code == InputError.code

# STATUS 400: An active standup is not currently running in the channel
def test_standup_send_standup_not_active(public_channel):
    # Attempt invalid user to send message
    req = requests.post(config.url + 'standup/send/v1', json={
                'token': public_channel['owner_token'], 
                'channel_id' : public_channel['channel_id'], 
                'message': "This is a message"})

    assert req.status_code == InputError.code


# STATUS 400: The message is longer than 1000 characters
def test_standup_send_message_too_long(public_channel):
    # Start a standup
    req = requests.post(config.url + 'standup/start/v1', json={
                'token': public_channel['owner_token'], 
                'channel_id' : public_channel['channel_id'], 
                'length': 1})
    assert req.status_code == 200

    long = "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, \
            nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, \
            vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus \
            elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, \
            feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. \
            Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. N. Etiam ultricies nisi vel augue. \
            Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. N"

    # Attempt valid user to send invalid message
    req = requests.post(config.url + 'standup/send/v1', json={
                'token': public_channel['owner_token'], 
                'channel_id' : public_channel['channel_id'], 
                'message': long})

    assert req.status_code == InputError.code

# STATUS 200: Message successfully sent
def test_standup_send_message_success(public_channel):
    # Start a standup
    req = requests.post(config.url + 'standup/start/v1', json={
                'token': public_channel['owner_token'], 
                'channel_id' : public_channel['channel_id'], 
                'length': 1})
    assert req.status_code == 200

    # Attempt valid user to send invalid message
    req = requests.post(config.url + 'standup/send/v1', json={
                'token': public_channel['owner_token'], 
                'channel_id' : public_channel['channel_id'], 
                'message': "Hello"})
    
    # Sleep to allow message to send
    time.sleep(2)

    assert req.status_code == 200
