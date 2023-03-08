import pytest
import requests
import json
import time
from src import config


@pytest.fixture
def dm_setup():
    resp_clear = requests.delete(config.url + 'clear/v1')
    assert resp_clear.status_code == 200

    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'gabriel@domain.com', 'password': 'password', 'name_first': 'gabriel', 'name_last': 'thien'})
    user_0 = user_0_json.json()
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'nathan@domain.com', 'password': 'password', 'name_first': 'nathan', 'name_last': 'mu'})
    user_1 = user_1_json.json()
    user_2_json = requests.post(config.url + 'auth/register/v2', json={'email': 'celina@domain.com', 'password': 'password', 'name_first': 'celina', 'name_last': 'shen'})
    user_2 = user_2_json.json()

    dm_data = requests.post(config.url + 'dm/create/v1', json={'token': user_0['token'], 'u_ids': [user_1['auth_user_id']]})
    return {
        'tokens' : [user_0['token'], user_1['token'], user_2['token']],
        'u_ids' : [user_0['auth_user_id'], user_1['auth_user_id'], user_2['auth_user_id']],
        'dm_id' : dm_data.json()['dm_id']
    }

def test_sendlaterdm_invalid_dm():
    # InputError 400 when dm_id does not refer to a valid dm

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
    resp_sendlaterdm = requests.post(config.url + 'message/sendlaterdm/v1', json = {
        'token': user['token'],
        'dm_id': 0,
        'message': 'ahhhhhhhhh',
        'time_sent': int(time.time()) + 5
    })
    assert resp_sendlaterdm.status_code == 400

    resp_sendlaterdm = requests.post(config.url + 'message/sendlaterdm/v1', json = {
        'token': user['token'],
        'dm_id': 1,
        'message': 'ahhhhhhhhh',
        'time_sent': int(time.time()) + 5
    })
    assert resp_sendlaterdm.status_code == 400

    resp_sendlaterdm = requests.post(config.url + 'message/sendlaterdm/v1', json = {
        'token': user['token'],
        'dm_id': -1,
        'message': 'ahhhhhhhhh',
        'time_sent': int(time.time()) + 5
    })
    assert resp_sendlaterdm.status_code == 400

def test_sendlaterdm_invalid_dm_two(dm_setup):
    # InputError 400 when dm_id does not refer to a valid channel
    resp_sendlaterdm = requests.post(config.url + 'message/sendlaterdm/v1', json = {
        'token': dm_setup['tokens'][0],
        'dm_id': 1,
        'message': 'ahhhhhhhhh',
        'time_sent': int(time.time()) + 5
    })
    assert resp_sendlaterdm.status_code == 400

def test_sendlaterdm_message_too_short(dm_setup):
    # InputError 400 when message length is less than 1 character
    resp_sendlaterdm = requests.post(config.url + 'message/sendlaterdm/v1', json = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_setup['dm_id'],
        'message': '',
        'time_sent': int(time.time()) + 5
    })
    assert resp_sendlaterdm.status_code == 400

def test_sendlaterdm_message_too_long(dm_setup):
    # InputError 400 when message length is greater than 1000 characters (i.e. 1001 or above)

    message = 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Na'

    resp_sendlaterdm = requests.post(config.url + 'message/sendlaterdm/v1', json = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_setup['dm_id'],
        'message': message,
        'time_sent': int(time.time()) + 5
    })
    assert resp_sendlaterdm.status_code == 400

def test_sendlaterdm_time_passed(dm_setup):
    # InputError 400 when time_sent is a time in the past
    resp_sendlaterdm = requests.post(config.url + 'message/sendlaterdm/v1', json = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_setup['dm_id'],
        'message': 'hello',
        'time_sent': int(time.time()) - 5
    })
    assert resp_sendlaterdm.status_code == 400

def test_sendlaterdm_user_not_dm_member(dm_setup):
    # AccessError 403 when dm_id is valid and the authorised user is not a member
    # of the DM they are trying to post to

    resp_sendlaterdm = requests.post(config.url + 'message/sendlaterdm/v1', json = {
        'token': dm_setup['tokens'][2],
        'dm_id': dm_setup['dm_id'],
        'message': 'hello?',
        'time_sent': int(time.time()) + 5
    })
    assert resp_sendlaterdm.status_code == 403

def test_sendlaterdm_success(dm_setup):
    message = 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. N'

    send_time = int(time.time()) + 1

    resp_sendlaterdm = requests.post(config.url + 'message/sendlaterdm/v1', json = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_setup['dm_id'],
        'message': message,
        'time_sent': send_time
    })
    assert resp_sendlaterdm.status_code == 200
    assert resp_sendlaterdm.json()['message_id'] == 0

    # verify that the message is sent 1 second later
    time.sleep(1)
    resp_messages = requests.get(config.url + 'dm/messages/v1', params = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_setup['dm_id'],
        'start': 0
    })
    assert resp_messages.status_code == 200
    message_data = resp_messages.json()
    assert message_data['messages'][0]['message_id'] == 0
    assert message_data['messages'][0]['message'] == message
    assert message_data['messages'][0]['time_sent'] == send_time

def test_sendlaterdm_and_normal_message(dm_setup):
    # send message in 1 second, but before the second has passed, send a normal message
    send_time = int(time.time()) + 1
    resp_sendlaterdm = requests.post(config.url + 'message/sendlaterdm/v1', json = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_setup['dm_id'],
        'message': 'sendlater message',
        'time_sent': send_time
    })
    assert resp_sendlaterdm.status_code == 200
    assert resp_sendlaterdm.json()['message_id'] == 0

    # the normal message
    resp_senddm = requests.post(config.url + 'message/senddm/v1', json = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_setup['dm_id'],
        'message': 'normal message',
        'time_sent': int(time.time())
    })
    assert resp_senddm.status_code == 200

    # verify the messages
    time.sleep(1)
    resp_messages = requests.get(config.url + 'dm/messages/v1', params = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_setup['dm_id'],
        'start': 0
    })
    message_data = resp_messages.json()

    assert message_data['messages'][0]['message_id'] == 0
    assert message_data['messages'][0]['message'] == 'sendlater message'
    assert message_data['messages'][0]['time_sent'] == send_time

    assert message_data['messages'][1]['message_id'] == 1
    assert message_data['messages'][1]['message'] == 'normal message'

def test_sendlaterdm_multiple_dms(dm_setup):
    # create second dm
    resp_create_dm = requests.post(config.url + 'dm/create/v1', json = {
        'token': dm_setup['tokens'][0],
        'u_ids': [dm_setup['u_ids'][1]],
    })
    assert resp_create_dm.status_code == 200
    dm_id2 = resp_create_dm.json()['dm_id']

    # put some messages in second dm
    resp_senddm = requests.post(config.url + 'message/senddm/v1', json = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_id2,
        'message': 'second dm message 1',
        'time_sent': int(time.time())
    })
    assert resp_senddm.status_code == 200

    resp_senddm = requests.post(config.url + 'message/senddm/v1', json = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_id2,
        'message': 'second dm message 2',
        'time_sent': int(time.time())
    })
    assert resp_senddm.status_code == 200

    # put some messages in first dm
    resp_senddm = requests.post(config.url + 'message/senddm/v1', json = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_setup['dm_id'],
        'message': 'first dm message 1',
        'time_sent': int(time.time())
    })
    assert resp_senddm.status_code == 200

    resp_senddm = requests.post(config.url + 'message/senddm/v1', json = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_setup['dm_id'],
        'message': 'first dm message 2',
        'time_sent': int(time.time())
    })
    assert resp_senddm.status_code == 200

    send_time = int(time.time()) + 1

    resp_sendlaterdm = requests.post(config.url + 'message/sendlaterdm/v1', json = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_setup['dm_id'],
        'message': 'sendlater message',
        'time_sent': send_time
    })
    assert resp_sendlaterdm.status_code == 200
    assert resp_sendlaterdm.json()['message_id'] == 4

    # verify messages in first dm 1 second later
    time.sleep(1)
    resp_messages = requests.get(config.url + 'dm/messages/v1', params = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_setup['dm_id'],
        'start': 0
    })
    assert resp_messages.status_code == 200
    message_data = resp_messages.json()
    assert message_data['messages'][0]['message_id'] == 4
    assert message_data['messages'][0]['message'] == 'sendlater message'
    assert message_data['messages'][0]['time_sent'] == send_time
