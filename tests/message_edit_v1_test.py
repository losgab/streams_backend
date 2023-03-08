import pytest
import requests
from src import config
import json

# Fixture that registers 2 users
@pytest.fixture
def public_channel():
    resp_clear = requests.delete(config.url + 'clear/v1')
    assert resp_clear.status_code == 200

    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'gabriel@domain.com', 'password': 'password', 'name_first': 'gabriel', 'name_last': 'thien'})
    user_0 = user_0_json.json()
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'nathan@domain.com', 'password': 'password', 'name_first': 'nathan', 'name_last': 'mu'})
    user_1 = user_1_json.json()
    user_2_json = requests.post(config.url + 'auth/register/v2', json={'email': 'celina@domain.com', 'password': 'password', 'name_first': 'celina', 'name_last': 'shen'})
    user_2 = user_2_json.json()

    channel_0 = requests.post(config.url + 'channels/create/v2', json={'token': user_0['token'], 'name': 'bear', 'is_public': True})
    requests.post(config.url + 'channel/join/v2', json={'token': user_1['token'], 'channel_id': channel_0.json()['channel_id']})
    return {
        'tokens' : [user_0['token'], user_1['token'], user_2['token']],
        'u_ids' : [user_0['auth_user_id'], user_1['auth_user_id'], user_2['auth_user_id']],
        'channel_id' : channel_0.json()['channel_id']
    }

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

# STATUS 400: The message id is invalid
def test_message_edit_invalid_message_id_channel(public_channel):
    requests.post(config.url + 'message/send/v1', json = {
        'token': public_channel['tokens'][0],
        'channel_id': public_channel['channel_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })

    resp_edit = requests.put(config.url + 'message/edit/v1', json = {
        'token': public_channel['tokens'][0],
        'message_id': 23987984712983,
        'message' : 'Message updated'
    })
    assert resp_edit.status_code == 400

# STATUS 400: The message id is invalid
def test_message_edit_invalid_message_id_dm(dm_setup):
    requests.post(config.url + 'message/senddm/v1', json = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_setup['dm_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })

    resp_edit = requests.put(config.url + 'message/edit/v1', json = {
        'token': dm_setup['tokens'][0],
        'message_id': 23987984712983,
        'message' : 'Message updated'
    })
    assert resp_edit.status_code == 400

# STATUS 400: The message id is successful for a channel owner
def test_message_edit_success_channel_owner(public_channel):
    message_0 = requests.post(config.url + 'message/send/v1', json = {
        'token': public_channel['tokens'][0],
        'channel_id': public_channel['channel_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })

    message_0_data = message_0.json()

    resp_edit = requests.put(config.url + 'message/edit/v1', json = {
        'token': public_channel['tokens'][0],
        'message_id': message_0_data['message_id'],
        'message' : 'Message updated'
    })
    assert resp_edit.status_code == 200

# STATUS 400: The message text is too long
def test_message_edit_text_too_long(public_channel):
    long = "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, \
            nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, \
            vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus \
            elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, \
            feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. \
            Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. N"
    
    message_0 = requests.post(config.url + 'message/send/v1', json = {
        'token': public_channel['tokens'][0],
        'channel_id': public_channel['channel_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })

    message_0_data = message_0.json()

    resp_edit = requests.put(config.url + 'message/edit/v1', json = {
        'token': public_channel['tokens'][0],
        'message_id': message_0_data['message_id'],
        'message' : long
    })

    assert resp_edit.status_code == 400

# STATUS 200: Successfully delete a message by editing the text
def test_message_edit_text_delete_success(public_channel):
    
    message_0 = requests.post(config.url + 'message/send/v1', json = {
        'token': public_channel['tokens'][0],
        'channel_id': public_channel['channel_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })

    message_0_data = message_0.json()

    resp_edit = requests.put(config.url + 'message/edit/v1', json = {
        'token': public_channel['tokens'][0],
        'message_id': message_0_data['message_id'],
        'message' : ""
    })
    assert resp_edit.status_code == 200

    resp = requests.get(config.url + 'channel/messages/v2', params={'token': public_channel['tokens'][0], 'channel_id': public_channel['channel_id'], 'start': 0})
    assert resp.status_code == 200

    assert len(resp.json()['messages']) == 0

# STATUS 200: Successfully edit a message
def test_message_edit_success_dm(dm_setup):
    message_0 = requests.post(config.url + 'message/senddm/v1', json = {
        'token': dm_setup['tokens'][1],
        'dm_id': dm_setup['dm_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })

    message_0_data = message_0.json()

    resp_edit = requests.put(config.url + 'message/edit/v1', json = {
        'token': dm_setup['tokens'][1],
        'message_id': message_0_data['message_id'],
        'message' : "Update message"
    })
    assert resp_edit.status_code == 200

    resp = requests.get(config.url + 'dm/messages/v1', params={'token': dm_setup['tokens'][0], 'dm_id': dm_setup['dm_id'], 'start': 0})
    resp_data = json.loads(resp.text)
    assert resp_data['messages'][0]['message'] == "Update message"

# STATUS 200: Edit someone else's message as a channel owner
def test_message_edit_not_own_message_owner_channel(public_channel):
    message_0 = requests.post(config.url + 'message/send/v1', json = {
        'token': public_channel['tokens'][1],
        'channel_id': public_channel['channel_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })

    message_0_data = message_0.json()

    resp_edit = requests.put(config.url + 'message/edit/v1', json = {
        'token': public_channel['tokens'][0],
        'message_id': message_0_data['message_id'],
        'message' : 'Message updated'
    })
    assert resp_edit.status_code == 200

# STATUS 200: Edit someone else's message as a DM owner
def test_message_edit_not_own_message_owner_dm(dm_setup):
    message_0 = requests.post(config.url + 'message/senddm/v1', json = {
        'token': dm_setup['tokens'][1],
        'dm_id': dm_setup['dm_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })

    message_0_data = message_0.json()

    resp_edit = requests.put(config.url + 'message/edit/v1', json = {
        'token': dm_setup['tokens'][0],
        'message_id': message_0_data['message_id'],
        'message' : "Update message"
    })
    assert resp_edit.status_code == 200

    resp = requests.get(config.url + 'dm/messages/v1', params={'token': dm_setup['tokens'][0], 'dm_id': dm_setup['dm_id'], 'start': 0})
    resp_data = json.loads(resp.text)
    assert resp_data['messages'][0]['message'] == "Update message"

# STATUS 403: Try to edit a message sent by another user
def test_message_edit_not_own_message_member_channel(public_channel):
    message_0 = requests.post(config.url + 'message/send/v1', json = {
        'token': public_channel['tokens'][0],
        'channel_id': public_channel['channel_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })

    message_0_data = message_0.json()

    resp_edit = requests.put(config.url + 'message/edit/v1', json = {
        'token': public_channel['tokens'][1],
        'message_id': message_0_data['message_id'],
        'message' : 'Message updated'
    })
    assert resp_edit.status_code == 403

# STATUS 403: Try to edit a message sent by another user
def test_message_edit_not_own_message_member_dm(dm_setup):
    message_0 = requests.post(config.url + 'message/senddm/v1', json = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_setup['dm_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })

    message_0_data = message_0.json()

    resp_edit = requests.put(config.url + 'message/edit/v1', json = {
        'token': dm_setup['tokens'][1],
        'message_id': message_0_data['message_id'],
        'message' : "Update message"
    })
    assert resp_edit.status_code == 403

# STATUS 400: Message id exists but the user requesting edit is not in any channels
def test_message_edit_not_channel_member(public_channel):
    message_0 = requests.post(config.url + 'message/send/v1', json = {
        'token': public_channel['tokens'][0],
        'channel_id': public_channel['channel_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })
    
    resp_edit = requests.put(config.url + 'message/edit/v1', json = {
        'token': public_channel['tokens'][2],
        'message_id': message_0.json()['message_id'],
        'message': 'asdyugfauiyosdeg'
    })
    assert resp_edit.status_code == 400

# STATUS 400: Message id exists but the user requesting edit is not in any dms
def test_message_edit_not_dm_member(dm_setup):
    message_0 = requests.post(config.url + 'message/senddm/v1', json = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_setup['dm_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })
    
    resp_edit = requests.put(config.url + 'message/edit/v1', json = {
        'token': dm_setup['tokens'][2],
        'message_id': message_0.json()['message_id'],
        'message': 'update message'
    })
    assert resp_edit.status_code == 400
