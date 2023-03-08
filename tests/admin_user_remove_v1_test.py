import pytest
import requests
import json
from src import config, tokens


# Fixture that registers 2 users
@pytest.fixture
def user_setup():
    requests.delete(config.url + 'clear/v1')
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'gabriel@domain.com', 'password': 'password', 'name_first': 'gabriel', 'name_last': 'thien'})
    user_0 = json.loads(user_0_json.text)
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'nathan@domain.com', 'password': 'password', 'name_first': 'nathan', 'name_last': 'mu'})
    user_1 = json.loads(user_1_json.text)
    user_2_json = requests.post(config.url + 'auth/register/v2', json={'email': 'celina@domain.com', 'password': 'password', 'name_first': 'celina', 'name_last': 'shen'})
    user_2 = json.loads(user_2_json.text)
    return (user_0['token'], user_1['token'], user_2['token'], user_0['auth_user_id'], user_1['auth_user_id'], user_2['auth_user_id'])

def test_user_remove_success_case(user_setup):
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={'token': user_setup[0], 'u_id' : user_setup[3]})
    resp.status_code == 200

def test_user_remove_invalid_id(user_setup):
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={'token': user_setup[0], 'u_id' : -1})
    resp1 = requests.delete(config.url + 'admin/user/remove/v1', json={'token': user_setup[0], 'u_id' : 4})
    assert resp1.status_code == 400 and resp.status_code == 400

def test_user_remove_single_admin(user_setup):
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={'token': user_setup[0], 'u_id' : user_setup[3]})
    assert resp.status_code == 400

def test_user_remove_not_owner(user_setup):
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={'token': user_setup[1], 'u_id' : user_setup[3]})
    assert resp.status_code == 403

def test_user_remove_name_changed(user_setup):
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={'token': user_setup[0], 'u_id' : user_setup[5]})
    assert resp.status_code == 200
    assert json.loads(resp.text) == {}
    # test reusable handle
    resp_profile = requests.get(config.url + 'user/profile/v1',
                                params = {'token': user_setup[0], 'u_id': user_setup[5]})
    assert resp_profile.json() == {
        'user': {
            'u_id': user_setup[5],
            'email': 'celina@domain.com',
            'name_first': 'Removed',
            'name_last': 'user',
            'handle_str': 'celinashen',
            'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
        }
    }

def test_user_remove_messages(user_setup):
    # User Nathan creates channel 'bear' and Celina joins
    channel_json = requests.post(config.url + 'channels/create/v2', json={'token': user_setup[1], 'name': 'bear', 'is_public': True})
    channel = json.loads(channel_json.text)
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup[2], 'channel_id': channel['channel_id']})
    # Celina and Nathan sends messages
    requests.post(config.url + 'message/send/v1', json={'token': user_setup[2], 'channel_id': channel['channel_id'], 'message':'hey'})
    requests.post(config.url + 'message/send/v1', json={'token': user_setup[1], 'channel_id': channel['channel_id'], 'message': 'hello'})
    requests.post(config.url + 'message/send/v1', json={'token': user_setup[2], 'channel_id': channel['channel_id'], 'message':'bye'})
    # Remove Nathan
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={'token': user_setup[0], 'u_id': user_setup[4]})
    assert resp.status_code == 200
    assert json.loads(resp.text) == {}
    # Assert behaviour (idk how to view messages)

def test_user_removed_from_dm(user_setup):
    resp0 = requests.post(config.url + 'dm/create/v1', 
        json={
            'token' : user_setup[1],
            'u_ids' : [user_setup[3], user_setup[5]]
        })
    assert resp0.status_code == 200

    resp1 = requests.delete(config.url + 'admin/user/remove/v1', json={'token': user_setup[0], 'u_id' : user_setup[4]})
    
    assert resp1.status_code == 200

def test_user_removed_from_channel(user_setup):
    # Create channel with user
    resp0 = requests.post(config.url + 'channels/create/v2', json={'token': user_setup[1], 'name': 'seal', 'is_public': True})
    assert resp0.status_code == 200

    channel_data0 = resp0.json()

    resp = requests.post(config.url + 'channel/join/v2', json={'token': user_setup[2], 'channel_id': resp0.json()['channel_id']})
    assert resp.status_code == 200

    resp = requests.post(config.url + 'message/send/v1', json={
        'token': user_setup[1],
        'channel_id' : channel_data0['channel_id'],
        'message' : 'This is a message!'})

    assert resp.status_code == 200

    resp = requests.post(config.url + 'message/send/v1', json={
        'token': user_setup[1],
        'channel_id' : channel_data0['channel_id'],
        'message' : 'This is a message!'})

    assert resp.status_code == 200

    resp = requests.post(config.url + 'message/send/v1', json={
        'token': user_setup[2],
        'channel_id' : channel_data0['channel_id'],
        'message' : 'This is a message!'})
    
    resp = requests.post(config.url + 'message/send/v1', json={
        'token': user_setup[2],
        'channel_id' : channel_data0['channel_id'],
        'message' : 'This is a message!'})

    assert resp.status_code == 200

    # Assert expected output of channel create v2
    resp5 = requests.delete(config.url + 'admin/user/remove/v1', json={'token': user_setup[0], 'u_id' : user_setup[4]})
    assert resp5.status_code == 200

    resp6 = requests.delete(config.url + 'admin/user/remove/v1', json={'token': user_setup[0], 'u_id' : user_setup[5]})
    assert resp6.status_code == 200

# Create message in channel

def test_user_removed_from_dms(user_setup):
    # Create channel with user
    requests.post(config.url + 'dm/create/v1', 
        json={
            'token' : user_setup[0],
            'u_ids' : [user_setup[3]]
        })

    dm = requests.post(config.url + 'dm/create/v1', 
        json={
            'token' : user_setup[0],
            'u_ids' : [user_setup[4]]
        })
    
    requests.post(config.url + 'dm/create/v1', 
        json={
            'token' : user_setup[1],
            'u_ids' : [user_setup[5], user_setup[3]]
        })

    resp1 = requests.post(config.url + 'message/senddm/v1', json={'token': user_setup[1], 'dm_id': dm.json()['dm_id'], 'message': "hello"})
    assert resp1.status_code == 200

    resp1 = requests.post(config.url + 'message/senddm/v1', json={'token': user_setup[0], 'dm_id': dm.json()['dm_id'], 'message': "hello"})
    assert resp1.status_code == 200

    resp2 = requests.post(config.url + 'message/senddm/v1', json={'token': user_setup[1], 'dm_id': dm.json()['dm_id'], 'message': "hello"})
    assert resp2.status_code == 200

    # Assert expected output of channel create v2
    resp3 = requests.delete(config.url + 'admin/user/remove/v1', json={'token': user_setup[0], 'u_id' : user_setup[4]})
    assert resp3.status_code == 200

def test_user_removed_from_channel_members(user_setup):
    resp0 = requests.post(config.url + 'channels/create/v2', json={'token': user_setup[1], 'name': 'seal', 'is_public': True})
    assert resp0.status_code == 200

    resp1 = requests.post(config.url + 'channels/create/v2', json={'token': user_setup[0], 'name': 'dingo', 'is_public': True})
    assert resp1.status_code == 200

    resp2 = requests.post(config.url + 'channel/join/v2', json={'token': user_setup[2], 'channel_id': resp0.json()['channel_id']})
    assert resp2.status_code == 200

    resp3 = requests.delete(config.url + 'admin/user/remove/v1', json={'token': user_setup[0], 'u_id' : user_setup[5]})
    assert resp3.status_code == 200


def test_user_removed_from_dm_creator(user_setup):
    requests.post(config.url + 'dm/create/v1', 
        json={
            'token' : user_setup[0],
            'u_ids' : [user_setup[4]]
        })
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={'token': user_setup[0], 'u_id' : user_setup[4]})
    assert resp.status_code == 200

def test_user_removed_from_dm_not_member(user_setup):
    requests.post(config.url + 'dm/create/v1', 
        json={
            'token' : user_setup[0],
            'u_ids' : []
        })
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={'token': user_setup[0], 'u_id' : user_setup[4]})
    assert resp.status_code == 200