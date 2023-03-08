import pytest
import requests

from src import config
from src.error import InputError

# Fixture that clears the data store 
@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1')

# Fixture that registers users
@pytest.fixture
def user_setup():
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'gabriel@domain.com', 'password': 'password', 'name_first': 'gabriel', 'name_last': 'thien'})
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'cengiz@domain.com', 'password': 'password', 'name_first': 'cengiz', 'name_last': 'cimen'})
    user_2_json = requests.post(config.url + 'auth/register/v2', json={'email': 'nathan@domain.com', 'password': 'password', 'name_first': 'nathan', 'name_last': 'mu'})
    return {
        'user0_token': user_0_json.json()['token'],
        'user1_token': user_1_json.json()['token'],
        'user2_token': user_2_json.json()['token'],
        'user0_id': user_0_json.json()['auth_user_id'],
        'user1_id': user_1_json.json()['auth_user_id'],
        'user2_id': user_2_json.json()['auth_user_id'],
    }

# Fixture that registers 2 users and creates a test channel
@pytest.fixture
def channel_setup(user_setup):
    # gabbo creates public channel
    channel0_data = requests.post(config.url + 'channels/create/v2',json={'token': user_setup['user0_token'], 'name': 'public test channel', 'is_public': True})
    # cengiz creates private channel
    channel1_data = requests.post(config.url + 'channels/create/v2',json={'token': user_setup['user1_token'], 'name': 'private test channel', 'is_public': False})
    return {
        'channel0_id': channel0_data.json()['channel_id'],
        'channel1_id': channel1_data.json()['channel_id']
    }
    
@pytest.fixture
def dm_setup(user_setup):
    # gabbo dms cengiz
    dm0_data = requests.post(config.url + 'dm/create/v1',json={'token': user_setup['user0_token'], 'u_ids': [user_setup['user1_id']]})
    # cengiz dms nathan
    dm1_data = requests.post(config.url + 'dm/create/v1',json={'token': user_setup['user1_token'], 'u_ids': [user_setup['user2_id']]})
    return {
        'dm0_id': dm0_data.json()['dm_id'],
        'dm1_id': dm1_data.json()['dm_id']
    }

# Test for less than 1 char query string (empty string)
def test_empty_string(clear, user_setup):
    # Sends in empty string as a query string 
    search_data = requests.get(config.url + 'search/v1', params={'token': user_setup['user0_token'], 'query_str': ''})
    # InputError code is expected 
    assert search_data.status_code == InputError.code
    
# Test for more than 1000 character query string 
def test_string_toolong(clear, user_setup):
    # Sends in large string as a query string 
    search_data = requests.get(config.url + 'search/v1', params={'token': user_setup['user0_token'], 'query_str': 1001*'a'})
    # InputError code is expected 
    assert search_data.status_code == InputError.code

# Global owners should be able to see all messages in all channels but not in dms 
def test_globalowner_messages_success(clear, user_setup, channel_setup, dm_setup):
    # Cengiz joins the public messages 
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel0_id']})
    # Cengiz sends messages in both the public and private channels
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel0_id'], 'message': 'poo poo'})
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel1_id'], 'message': 'poo poo'})
    # Cengiz sends messages in both dms that hes part of 
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user1_token'], 'dm_id': dm_setup['dm0_id'], 'message': 'poo poo'})
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user1_token'], 'dm_id': dm_setup['dm1_id'], 'message': 'poo poo2'})
    # Gabbo should be able to see only the two messages in the channels that cengiz is in, and the dm that gabbo is in
    search_data = requests.get(config.url + 'search/v1', params={'token': user_setup['user0_token'], 'query_str': 'poo'})
    assert search_data.status_code == 200
    assert len(search_data.json()['messages']) == 3
    for message in search_data.json()['messages']:
        assert message['message'] == 'poo poo'

# User should not see matching messages in a channel/dm they are not a member of
def test_no_access_some_messages_(clear, user_setup, channel_setup, dm_setup):
    # Nathan joins the public channel gabbo created 
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup['user2_token'], 'channel_id': channel_setup['channel0_id']})
    # Gabbo sends a message in public channel
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user0_token'], 'channel_id': channel_setup['channel0_id'], 'message': 'poo poo'})
    # Cengiz sends a message in private channel
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel1_id'], 'message': 'poo poo1'})
    # Gabbo sends message in DM to cengiz
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user0_token'], 'dm_id': dm_setup['dm0_id'], 'message': 'poo poo1'})
    # Cengiz sends message in DM to nathan
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user1_token'], 'dm_id': dm_setup['dm1_id'], 'message': 'poo poo'})
    # Nathan should only see Gabbo's message in the channel and Cengiz's message in DM
    search_data = requests.get(config.url + 'search/v1', params={'token': user_setup['user2_token'], 'query_str': 'poo'})
    assert search_data.status_code == 200
    assert len(search_data.json()['messages']) == 2
    for message in search_data.json()['messages']:
        assert message['message'] == 'poo poo'

# Tests when no messages are meant to be returned
def test_emptyreturn_success(clear, user_setup, channel_setup, dm_setup):
    # Cengiz sends a message in his private channel
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel1_id'], 'message': 'poo poo'})
    # Nathan should see nothing
    search_data = requests.get(config.url + 'search/v1', params={'token': user_setup['user2_token'], 'query_str': 'poo'})
    assert search_data.status_code == 200
    assert search_data.json() == {
        'messages': []
    }

# Tests successful searching of all messages involving query string
def test_all_success_search(clear, user_setup, channel_setup, dm_setup):
    # Nathan joins the public channel gabbo created 
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup['user2_token'], 'channel_id': channel_setup['channel0_id']})
    # Gabbo sends a message in public channel
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user0_token'], 'channel_id': channel_setup['channel0_id'], 'message': 'poo poo1'})
    # Cengiz sends a message in private channel
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel1_id'], 'message': 'poo poo'})
    # Gabbo sends message in DM to cengiz
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user0_token'], 'dm_id': dm_setup['dm0_id'], 'message': 'poo poo'})
    # Cengiz sees all messages except for gabbo's channel message
    search_data = requests.get(config.url + 'search/v1', params={'token': user_setup['user1_token'], 'query_str': 'poo'})
    assert search_data.status_code == 200
    assert len(search_data.json()['messages']) == 2
    for message in search_data.json()['messages']:
        assert message['message'] == 'poo poo'
    # Nathan only sees gabbos channel message 
    search_data = requests.get(config.url + 'search/v1', params={'token': user_setup['user2_token'], 'query_str': 'poo'})
    assert search_data.status_code == 200
    assert len(search_data.json()['messages']) == 1
    for message in search_data.json()['messages']:
        assert message['message'] == 'poo poo1'

# Tests whether messages that dont contain query string are returned 
def test_assorted_success(clear, user_setup, channel_setup, dm_setup):
    # Gabbo sends a message in public channel
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user0_token'], 'channel_id': channel_setup['channel0_id'], 'message': 'poo poo1'})
    # Cengiz sends messages in private channel
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel1_id'], 'message': 'poo poo'})
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel1_id'], 'message': 'i like children'})
    # Cengiz sends message in DM to nathan
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user1_token'], 'dm_id': dm_setup['dm1_id'], 'message': 'poo poo'})
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user1_token'], 'dm_id': dm_setup['dm1_id'], 'message': 'nathan likes children'})
    # Cengiz should only see 2 messages, 1 from the channel and one from the dm
    search_data = requests.get(config.url + 'search/v1', params={'token': user_setup['user1_token'], 'query_str': 'poo'})
    assert search_data.status_code == 200
    assert len(search_data.json()['messages']) == 2
    for message in search_data.json()['messages']:
        assert message['message'] == 'poo poo'
    # Nathan only sees cengi's DM
    search_data = requests.get(config.url + 'search/v1', params={'token': user_setup['user2_token'], 'query_str': 'children'})
    assert search_data.status_code == 200
    assert len(search_data.json()['messages']) == 1
    for message in search_data.json()['messages']:
        assert message['message'] == 'nathan likes children'

# Tests whether query string is case sensitive
def test_case_insensitive(clear, user_setup, channel_setup, dm_setup):
    # Cengiz sends messages in private channel
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel1_id'], 'message': 'POO POO'})
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel1_id'], 'message': 'Poo Poo'})
    # Cengiz sends message in DM to nathan
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user1_token'], 'dm_id': dm_setup['dm1_id'], 'message': 'POO POO'})
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user1_token'], 'dm_id': dm_setup['dm1_id'], 'message': 'Poo Poo'})
    # Cengiz should see all 4 messages
    search_data = requests.get(config.url + 'search/v1', params={'token': user_setup['user1_token'], 'query_str': 'POo'})
    assert search_data.status_code == 200
    assert len(search_data.json()['messages']) == 4
    for message in search_data.json()['messages']:
        assert message['message'] == 'POO POO' or message['message'] == 'Poo Poo'
