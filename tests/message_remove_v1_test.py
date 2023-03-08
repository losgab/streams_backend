import pytest
import requests
from src import config


@pytest.fixture
# Registers three users and creates a channel; returns a dictionary with relevant tokens, user ids and a channel id
def public_channel():
    # Clear the current datastore file 
    resp_clear = requests.delete(config.url + 'clear/v1')
    assert resp_clear.status_code == 200
    # Register three users
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'gabriel@domain.com', 'password': 'password', 'name_first': 'gabriel', 'name_last': 'thien'})
    user_0 = user_0_json.json()
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'nathan@domain.com', 'password': 'password', 'name_first': 'nathan', 'name_last': 'mu'})
    user_1 = user_1_json.json()
    user_2_json = requests.post(config.url + 'auth/register/v2', json={'email': 'celina@domain.com', 'password': 'password', 'name_first': 'celina', 'name_last': 'shen'})
    user_2 = user_2_json.json()
    # Create a channel with only one user Gabriel
    channel_0 = requests.post(config.url + 'channels/create/v2', json={'token': user_0['token'], 'name': 'bear', 'is_public': True})
    requests.post(config.url + 'channel/join/v2', json={'token': user_1['token'], 'channel_id': channel_0.json()['channel_id']})
    return {
        'tokens' : [user_0['token'], user_1['token'], user_2['token']],
        'u_ids' : [user_0['auth_user_id'], user_1['auth_user_id'], user_2['auth_user_id']],
        'channel_id' : channel_0.json()['channel_id']
    }

@pytest.fixture
# Registers three users and creates a dm; returns a dictionary with relevant tokens, user ids and a dm id
def dm_setup():
    # Clear the current datastore file 
    resp_clear = requests.delete(config.url + 'clear/v1')
    assert resp_clear.status_code == 200
    # Register three users
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'gabriel@domain.com', 'password': 'password', 'name_first': 'gabriel', 'name_last': 'thien'})
    user_0 = user_0_json.json()
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'nathan@domain.com', 'password': 'password', 'name_first': 'nathan', 'name_last': 'mu'})
    user_1 = user_1_json.json()
    user_2_json = requests.post(config.url + 'auth/register/v2', json={'email': 'celina@domain.com', 'password': 'password', 'name_first': 'celina', 'name_last': 'shen'})
    user_2 = user_2_json.json()
    # Gabriel creates a DM and adds Nathan to it 
    dm_data = requests.post(config.url + 'dm/create/v1', json={'token': user_0['token'], 'u_ids': [user_1['auth_user_id']]})
    return {
        'tokens' : [user_0['token'], user_1['token'], user_2['token']],
        'u_ids' : [user_0['auth_user_id'], user_1['auth_user_id'], user_2['auth_user_id']],
        'dm_id' : dm_data.json()['dm_id']
    }

# STATUS 200: The message is successfully removed from the channel where user is owner
def test_message_remove_channel_owner_remove(public_channel):
    # Gabriel sends a message on a newly created channel
    message_0 = requests.post(config.url + 'message/send/v1', json = {
        'token': public_channel['tokens'][0],
        'channel_id': public_channel['channel_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })
    #  Gabriel removes his own message as an owner
    resp_remove = requests.delete(config.url + 'message/remove/v1', json = {
        'token': public_channel['tokens'][0],
        'message_id': message_0.json()['message_id']
    })
    # Checks if this request went through succesfully
    assert resp_remove.status_code == 200

    # Gabriel requests for a list of messsages in 
    resp = requests.get(config.url + 'channel/messages/v2',
                        params={'token': public_channel['tokens'][0], 'channel_id': public_channel['channel_id'], 'start': 0})

    # Checks if this request went through succesfully
    assert resp.status_code == 200
    # Messages list should be empty
    assert resp.json()['messages'] == []
    

# STATUS 400: The message id is invalid
def test_message_remove_channel_invalid_message_id(public_channel):
    # Gabriel sends a message to the channel
    requests.post(config.url + 'message/send/v1', json = {
        'token': public_channel['tokens'][0],
        'channel_id': public_channel['channel_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })
    # Gabriel requests for that message to be removed with and INVALID ID
    resp_remove = requests.delete(config.url + 'message/remove/v1', json = {
        'token': public_channel['tokens'][0],
        'message_id': 112830912
    })
    # Check if that raises an INPUTERROR(400)
    assert resp_remove.status_code == 400

def test_message_remove_dm_invalid_message_id(dm_setup):
    # Gabriel sends a message to a dm
    requests.post(config.url + 'message/senddm/v1', json = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_setup['dm_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })
    # Gabriel requests for that message to be removed with and INVALID ID
    resp_remove = requests.delete(config.url + 'message/remove/v1', json = {
        'token': dm_setup['tokens'][0],
        'message_id': 112830912
    })
    # Check if that raises an INPUTERROR(400)
    assert resp_remove.status_code == 400

# STATUS 400: The message id is invalid
def test_message_remove_invalid_message_id_dm(dm_setup):
    requests.post(config.url + 'message/senddm/v1', json = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_setup['dm_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })

    resp_remove = requests.delete(config.url + 'message/remove/v1', json = {
        'token': dm_setup['tokens'][0],
        'message_id': 112830912
    })
    
    assert resp_remove.status_code == 400

# STATUS 200: The message is deleted where the user is dm owner
def test_message_remove_dm_owner(dm_setup):
    # Gabriel sends a message to the new DM
    message_0 = requests.post(config.url + 'message/senddm/v1', json = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_setup['dm_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })
    # Nathan sends a message to the new DM
    requests.post(config.url + 'message/senddm/v1', json = {
        'token': dm_setup['tokens'][1],
        'dm_id': dm_setup['dm_id'],
        'message': 'MESSAGE 1 asdfiuag'
    })
    # Gabriel sends another message to the new DM
    requests.post(config.url + 'message/senddm/v1', json = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_setup['dm_id'],
        'message': 'MESSAGE 2 fiaheuwg'
    })
    # Gabriel requests to delete the first message from his dm as an owner
    resp_remove = requests.delete(config.url + 'message/remove/v1', json = {
        'token': dm_setup['tokens'][0],
        'message_id': message_0.json()['message_id']
    })
    
    assert resp_remove.status_code == 200
    
    # Gabriel checks whether the message was properly deleted
    resp = requests.get(config.url + 'dm/messages/v1',
                        params={'token': dm_setup['tokens'][0], 'dm_id': dm_setup['dm_id'], 'start': 0})

    assert len(resp.json()['messages']) == 2
    assert resp.json()['messages'][0]['message'] == 'MESSAGE 2 fiaheuwg'
    assert resp.json()['end'] == -1

# STATUS 200: The message is deleted where the user is dm member (not dm owner)
def test_message_remove_success_member_dm(dm_setup):
    # Nathan sends a message to the dm as a member of the dm
    requests.post(config.url + 'message/senddm/v1', json = {
        'token': dm_setup['tokens'][1],
        'dm_id': dm_setup['dm_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })
    # Nathan sends another message to the dm as a member of the dm
    message_0 = requests.post(config.url + 'message/senddm/v1', json = {
        'token': dm_setup['tokens'][1],
        'dm_id': dm_setup['dm_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })

    # Nathan sends another message to the dm as a member of the dm
    requests.post(config.url + 'message/senddm/v1', json = {
        'token': dm_setup['tokens'][1],
        'dm_id': dm_setup['dm_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })

    # Nathan requests for the message to be deleted
    resp_remove = requests.delete(config.url + 'message/remove/v1', json = {
        'token': dm_setup['tokens'][1],
        'message_id': message_0.json()['message_id']
    })
    
    assert resp_remove.status_code == 200

    # Gabriel checks that the message was deleted
    resp = requests.get(config.url + 'dm/messages/v1',
                        params={'token': dm_setup['tokens'][0], 'dm_id': dm_setup['dm_id'], 'start': 0})
    
    assert len(resp.json()['messages']) == 2
    assert resp.json()['end'] == -1


# STATUS 200: The message is successfully removed from the channel where user is member
def test_message_remove_channel_member_own_message(public_channel):
    # Gabriel creates a channel
    requests.post(config.url + 'channels/create/v2', json={'token': public_channel['tokens'][0], 'name': 'splear', 'is_public': True})
    # Nathan sends a message to the first channel
    message_0 = requests.post(config.url + 'message/send/v1', json = {
        'token': public_channel['tokens'][1],
        'channel_id': public_channel['channel_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })
    # Nathan removes his message in the first channel (the code skips over second channel)
    resp_remove = requests.delete(config.url + 'message/remove/v1', json = {
        'token': public_channel['tokens'][1],
        'message_id': message_0.json()['message_id']
    })
    
    assert resp_remove.status_code == 200

# STATUS 403: The message is sent by someone else and member (not channel owner) tries to delete it
def test_message_remove_not_own_message_member_channel(public_channel):
    message_0 = requests.post(config.url + 'message/send/v1', json = {
        'token': public_channel['tokens'][0],
        'channel_id': public_channel['channel_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })

    # Nathan tries to removes a message from another user
    resp_remove = requests.delete(config.url + 'message/remove/v1', json = {
        'token': public_channel['tokens'][1],
        'message_id': message_0.json()['message_id']
    })
    assert resp_remove.status_code == 403

# STATUS 403: The message is sent by someone else and member (not dm owner) tries to delete it
def test_message_remove_not_own_message_member_dm(dm_setup):
    message_0 = requests.post(config.url + 'message/senddm/v1', json = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_setup['dm_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })

    resp_remove = requests.delete(config.url + 'message/remove/v1', json = {
        'token': dm_setup['tokens'][1],
        'message_id': message_0.json()['message_id']
    })
    assert resp_remove.status_code == 403

# STATUS 200: Test case where message is removed in one with multiple channels existing
def test_message_remove_two_channels(public_channel):
    # create second channel
    resp_create = requests.post(config.url + 'channels/create/v2', json={'token': public_channel['tokens'][1], 'name': 'blear', 'is_public': True})
    other_channel_id = resp_create.json()['channel_id']

    # send a message in the first channel
    message_first_channel = requests.post(config.url + 'message/send/v1', json = {
        'token': public_channel['tokens'][1],
        'channel_id': public_channel['channel_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })

    # send a message in the second channel
    requests.post(config.url + 'message/send/v1', json = {
        'token': public_channel['tokens'][1],
        'channel_id': other_channel_id,
        'message': 'other channel hi'
    })

    resp_remove = requests.delete(config.url + 'message/remove/v1', json = {
        'token': public_channel['tokens'][1],
        'message_id': message_first_channel.json()['message_id']
    })
    assert resp_remove.status_code == 200

    # test that the correct message was removed
    first_channel_messages = requests.get(config.url + 'channel/messages/v2', params = {
        'token': public_channel['tokens'][0],
        'channel_id': public_channel['channel_id'],
        'start': 0
    })
    assert first_channel_messages.status_code == 200
    assert first_channel_messages.json() == {
            'messages': [],
            'start': 0,
            'end': -1
    }

    second_channel_messages = requests.get(config.url + 'channel/messages/v2', params = {
        'token': public_channel['tokens'][1],
        'channel_id': other_channel_id,
        'start': 0
    })
    assert second_channel_messages.status_code == 200
    assert second_channel_messages.json()['messages'][0]['message'] == 'other channel hi'

# STATUS 400: Message id exists but the user requesting remove is not in any dms
def test_message_remove_not_dm_member(dm_setup):
    # Three dms are created
    requests.post(config.url + 'dm/create/v1', json={'token': dm_setup['tokens'][0], 'u_ids': []})
    requests.post(config.url + 'dm/create/v1', json={'token': dm_setup['tokens'][1], 'u_ids': []})

    message_0 = requests.post(config.url + 'message/senddm/v1', json = {
        'token': dm_setup['tokens'][0],
        'dm_id': dm_setup['dm_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })
    
    resp_remove = requests.delete(config.url + 'message/remove/v1', json = {
        'token': dm_setup['tokens'][2],
        'message_id': message_0.json()['message_id']
    })
    
    assert resp_remove.status_code == 400

# STATUS 400: Message id exists but the user requesting remove is not in any channels
def test_message_remove_not_a_channel_member(public_channel):
    message_0 = requests.post(config.url + 'message/send/v1', json = {
        'token': public_channel['tokens'][0],
        'channel_id': public_channel['channel_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })
    
    resp_remove = requests.delete(config.url + 'message/remove/v1', json = {
        'token': public_channel['tokens'][2],
        'message_id': message_0.json()['message_id']
    })
    
    assert resp_remove.status_code == 400

# STATUS 200: Channel owner removes the message of a member
def test_message_remove_channel_owner_remove_other(public_channel):
    message_0 = requests.post(config.url + 'message/send/v1', json = {
        'token': public_channel['tokens'][1],
        'channel_id': public_channel['channel_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })
    
    resp_remove = requests.delete(config.url + 'message/remove/v1', json = {
        'token': public_channel['tokens'][0],
        'message_id': message_0.json()['message_id']
    })
    
    assert resp_remove.status_code == 200


# STATUS 400: Try to remove an already-removed message - the message_id is not valid
def test_message_remove_twice_channel(public_channel):
    message_0 = requests.post(config.url + 'message/send/v1', json = {
        'token': public_channel['tokens'][0],
        'channel_id': public_channel['channel_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })

    resp_remove = requests.delete(config.url + 'message/remove/v1', json = {
        'token': public_channel['tokens'][0],
        'message_id': message_0.json()['message_id']
    })
    
    assert resp_remove.status_code == 200

# STATUS 200: DM creator removes the message of a member
def test_message_remove_dm_owner_remove_other(dm_setup):
    message_0 = requests.post(config.url + 'message/senddm/v1', json = {
        'token': dm_setup['tokens'][1],
        'dm_id': dm_setup['dm_id'],
        'message': 'MESSAGE 0 asdfiuag'
    })
    
    resp_remove = requests.delete(config.url + 'message/remove/v1', json = {
        'token': dm_setup['tokens'][0],
        'message_id': message_0.json()['message_id']
    })
    
    assert resp_remove.status_code == 200

    resp_remove_again = requests.delete(config.url + 'message/remove/v1', json = {
        'token': dm_setup['tokens'][1],
        'message_id': message_0.json()['message_id']
    })
    assert resp_remove_again.status_code == 400

