import pytest
import requests
import json
from src import config

# Fixture that clears the data store
@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1')

# Fixture that clears the data store and registers 2 users
@pytest.fixture
def register():
    # register users celina and christina
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'celina@domain.com', 'password': 'password', 'name_first': 'celina', 'name_last': 'shen'})
    user_0 = json.loads(user_0_json.text)
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'christina@domain.com', 'password': 'password', 'name_first': 'christina', 'name_last': 'lee'})
    user_1 = json.loads(user_1_json.text)
    user_2_json = requests.post(config.url + 'auth/register/v2', json={'email': 'nathan@domain.com', 'password': 'password', 'name_first': 'nathan', 'name_last': 'mu'})
    user_2 = json.loads(user_2_json.text)
    # dm with members celina and christina
    dm_1_json = requests.post(config.url + 'dm/create/v1', json={'token': user_0['token'], 'u_ids': [user_1['auth_user_id']]})
    dm_1 = json.loads(dm_1_json.text)
    # dm with christina and nathan
    dm_2_json = requests.post(config.url + 'dm/create/v1', json={'token': user_1['token'], 'u_ids': [user_2['auth_user_id']]})
    dm_2 = json.loads(dm_2_json.text)
    # return tuple of user tokens
    return {
        'token1': user_0['token'], 
        'token2': user_1['token'],
        'token3': user_2['token'],
        'dm_id1': dm_1['dm_id'],
        'dm_id2': dm_2['dm_id'],
    }

# AccessError (403), invalid token input
def test_senddm_v1_invalid_token(clear, register):
    resp_0 = requests.post(config.url + 'message/senddm/v1', json={'token': -1, 'dm_id': register['dm_id1'], 'message': "hello"})
    resp_1 = requests.post(config.url + 'message/senddm/v1', json={'token': 10, 'dm_id': register['dm_id1'], 'message': "hello"})
    # Expected status code (403) AccessError
    assert resp_0.status_code == 403
    assert resp_1.status_code == 403

# InputError (400), invalid dm id
def test_senddm_v1_invalid_dm_id(clear, register):
    resp_0 = requests.post(config.url + 'message/senddm/v1', json={'token': register['token1'], 'dm_id': -1, 'message': "hello"})
    resp_1 = requests.post(config.url + 'message/senddm/v1', json={'token': register['token2'], 'dm_id': 10, 'message': "hello"})
    # Expected status code (400) InputError
    assert resp_0.status_code == 400
    assert resp_1.status_code == 400

# InputError (400), length of message is less than 1 or over 1000 characters
def test_senddm_v1_invalid_msg_length(clear, register):
    long = "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, \
            nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, \
            vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus \
            elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, \
            feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. \
            Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. N"
    
    resp_0 = requests.post(config.url + 'message/senddm/v1', json={'token': register['token1'], 'dm_id': register['dm_id1'], 'message': ""})
    resp_1 = requests.post(config.url + 'message/senddm/v1', json={'token': register['token2'], 'dm_id': register['dm_id1'], 'message':long})
    # Expected status code (400) InputError
    assert resp_0.status_code == 400
    assert resp_1.status_code == 400

# AccessError (403), dm_id is valid and the authorised user is not a member of the DM
def test_senddm_v1_invalid_not_member(clear, register):
    resp_0 = requests.post(config.url + 'message/senddm/v1', json={'token': register['token3'], 'dm_id': register['dm_id1'], 'message': "hello"})
    resp_1 = requests.post(config.url + 'message/senddm/v1', json={'token': register['token1'], 'dm_id': register['dm_id2'], 'message': "hello"})
    # Expected status code (403), AccessError
    assert resp_0.status_code == 403
    assert resp_1.status_code == 403

# Success case
def test_senddm_v1_successsful(clear, register):
    # Create channel to send msgs in (test message id)
    channel_json = requests.post(config.url + 'channels/create/v2', json={'token': register['token1'], 'name': 'test channel', 'is_public': True})
    channel = json.loads(channel_json.text)
    # Send messages in channel and dms
    requests.post(config.url + 'message/send/v1', json={'token': register['token1'], 'channel_id': channel['channel_id'], 'message': 'hello'})
    requests.post(config.url + 'message/send/v1', json={'token': register['token1'], 'channel_id': channel['channel_id'], 'message': 'bye'})
    resp_0 = requests.post(config.url + 'message/senddm/v1', json={'token': register['token1'], 'dm_id': register['dm_id1'], 'message': 'hello'})
    resp_1 = requests.post(config.url + 'message/senddm/v1', json={'token': register['token2'], 'dm_id': register['dm_id1'], 'message': "hello !!"})
    resp_2 = requests.post(config.url + 'message/senddm/v1', json={'token': register['token3'], 'dm_id': register['dm_id2'], 'message': "heyy"})
    resp_3 = requests.post(config.url + 'message/senddm/v1', json={'token': register['token2'], 'dm_id': register['dm_id2'], 'message': "aot is the best"})
    # Expected status code (200), success
    assert resp_0.status_code == 200
    assert resp_1.status_code == 200
    assert resp_2.status_code == 200
    assert resp_3.status_code == 200
    # Assert expected return
    assert json.loads(resp_0.text) == {
        'message_id': 2
    }
    assert json.loads(resp_1.text) == {
        'message_id': 3
    }
    assert json.loads(resp_2.text) == {
        'message_id': 4
    }
    assert json.loads(resp_3.text) == {
        'message_id': 5
    }
