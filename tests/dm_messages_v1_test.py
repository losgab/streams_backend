import json
import requests
import pytest

from src.error import AccessError, InputError
from src import config

# Fixture that clears the data store 
@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1')

# Fixture that registers 2 users
@pytest.fixture
def user_setup():
    user_0 = requests.post(config.url + 'auth/register/v2', json={'email': 'gabriel@domain.com', 'password': 'password', 'name_first': 'gabriel', 'name_last': 'thien'})
    user_1 = requests.post(config.url + 'auth/register/v2', json={'email': 'cengiz@domain.com', 'password': 'password', 'name_first': 'cengiz', 'name_last': 'cimen'})
    user_2 = requests.post(config.url + 'auth/register/v2', json={'email': 'nathan@domain.com', 'password': 'password', 'name_first': 'nathan', 'name_last': 'mu'})
    return (user_0.json()['token'], user_1.json()['token'], user_2.json()['token'], user_0.json()['auth_user_id'], user_1.json()['auth_user_id'], user_2.json()['auth_user_id'])

# Invalid dm_id is passed 
def test_invalid_dm_id(clear, user_setup):
    # Negative dm_id passed 
    response_data = requests.get(config.url + 'dm/messages/v1', params={'token': user_setup[0], 'dm_id': -1, 'start': 0})
    assert response_data.status_code == InputError.code
    # Exceed max dm_id passed
    response_data = requests.get(config.url + 'dm/messages/v1', params={'token': user_setup[0], 'dm_id': 1, 'start': 0})
    assert response_data.status_code == InputError.code
    
# start passed is larger than the number of messages in the channel
def test_invalid_start(clear, user_setup): 
    # Make a dm first between gabriel and cengiz
    dm_data = requests.post(config.url + 'dm/create/v1', json={'token': user_setup[0], 'u_ids': [user_setup[4]]})
    # Start index is too big 
    response_data = requests.get(config.url + 'dm/messages/v1', params={'token': user_setup[0], 'dm_id': dm_data.json()['dm_id'], 'start': 1})
    # InputError code 403 expected
    assert response_data.status_code == InputError.code
    # Start index is negative >:(
    response_data = requests.get(config.url + 'dm/messages/v1', params={'token': user_setup[0], 'dm_id': dm_data.json()['dm_id'], 'start': -1})
    # InputError code 403 expected
    assert response_data.status_code == InputError.code

# User is not a member of the dm but they know the dm_id
def test_user_noperms(clear, user_setup):
    # Make a dm first between gabriel and cengiz
    dm_data = requests.post(config.url + 'dm/create/v1', json={'token': user_setup[0], 'u_ids': [user_setup[4]]})
    # Third person tries to gabbo and cengiz's messages
    response_data = requests.get(config.url + 'dm/messages/v1', params={'token': user_setup[2], 'dm_id': dm_data.json()['dm_id'], 'start': 0})
    # Should raise an access error
    assert response_data.status_code == AccessError.code

# Test success case and whether the returns are correct or not in a zero message environment
def test_success_zero_no_messages(clear, user_setup):
    # Make a dm first between gabriel and cengiz
    dm_data = requests.post(config.url + 'dm/create/v1', json={'token': user_setup[0], 'u_ids': [user_setup[4]]})
    # Gets the messages which should be none 
    response_data = requests.get(config.url + 'dm/messages/v1', params={'token': user_setup[0], 'dm_id': dm_data.json()['dm_id'], 'start': 0})
    # Success code expected
    assert response_data.status_code == 200 

# Test success case, correct returns with 10 messages and no more messages to request
def test_success_no_more_messages(clear, user_setup):
    # Make a dm first between gabriel and cengiz
    dm_data = requests.post(config.url + 'dm/create/v1', json={'token': user_setup[0], 'u_ids': [user_setup[4]]})
    # Adds 9 messages
    for message in range(9):
        message = str(message)
        requests.post(config.url + 'message/senddm/v1', json={'token': user_setup[0], 'dm_id': dm_data.json()['dm_id'], 'message': 'bruh'})
    # Adds a 10th msg
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup[0], 'dm_id': dm_data.json()['dm_id'], 'message': '10th msg'})
    # Gets the messages starting from index 0
    response_data = requests.get(config.url + 'dm/messages/v1', params={'token': user_setup[0], 'dm_id': dm_data.json()['dm_id'], 'start': 0})
    assert response_data.status_code == 200
    assert len(response_data.json()['messages']) == 10
    assert response_data.json()['messages'][0]['message'] == '10th msg'
    assert response_data.json()['start'] == 0
    assert response_data.json()['end'] == -1

# Test success case, correct returns with perfect 50 messages and no more messages to request
def test_success_perfect_no_more_messages(clear, user_setup):
    # Make a dm first between gabriel and cengiz
    dm_data = requests.post(config.url + 'dm/create/v1', json={'token': user_setup[0], 'u_ids': [user_setup[4]]})
    # Adds 49 messages
    for message in range(49):
        message = str(message)
        requests.post(config.url + 'message/senddm/v1', json={'token': user_setup[0], 'dm_id': dm_data.json()['dm_id'], 'message': 'bruh'})
    # Adds a 50th msg
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup[0], 'dm_id': dm_data.json()['dm_id'], 'message': '50th msg'})
    # Gets the messages starting from index 0
    response_data = requests.get(config.url + 'dm/messages/v1', params={'token': user_setup[0], 'dm_id': dm_data.json()['dm_id'], 'start': 0})
    assert response_data.status_code == 200
    assert len(response_data.json()['messages']) == 50
    assert response_data.json()['messages'][49]['message'] == 'bruh'
    assert response_data.json()['messages'][1]['message'] == 'bruh'
    assert response_data.json()['messages'][0]['message'] == '50th msg'
    assert response_data.json()['start'] == 0
    assert response_data.json()['end'] == -1

#  Test success case, correct returns, requesting middle of msgs
def test_success_middle_messages(clear, user_setup):
    # Make a dm first between gabriel and cengiz
    dm_data = requests.post(config.url + 'dm/create/v1', json={'token': user_setup[0], 'u_ids': [user_setup[4]]})
    # Adding 52 messages, we only getting the middle stuff 
    # Adds 1 message index 0 
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup[0], 'dm_id': dm_data.json()['dm_id'], 'message': 'bruh'})
    # Adds index 1 - 50 msgs
    for message in range(50):
        message = str(message)
        requests.post(config.url + 'message/senddm/v1', json={'token': user_setup[0], 'dm_id': dm_data.json()['dm_id'], 'message': 'middle msg'})
    # Adds last message
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup[0], 'dm_id': dm_data.json()['dm_id'], 'message': 'bruh'})
    # Gets the messages starting from index 1
    response_data = requests.get(config.url + 'dm/messages/v1', params={'token': user_setup[0], 'dm_id': dm_data.json()['dm_id'], 'start': 1})
    assert response_data.status_code == 200
    assert len(response_data.json()['messages']) == 50
    assert response_data.json()['messages'][0]['message'] == 'middle msg'
    assert response_data.json()['messages'][49]['message'] == 'middle msg'
    assert response_data.json()['start'] == 1
    assert response_data.json()['end'] == 51

#  Test success case, correct returns, requesting middle to end messages
def test_success_middle_to_end_messages(clear, user_setup):
    # Make a dm first between gabriel and cengiz
    dm_data = requests.post(config.url + 'dm/create/v1', json={'token': user_setup[0], 'u_ids': [user_setup[4]]})
    # Adds 5 messages
    for message in range(5):
        message = str(message)
        requests.post(config.url + 'message/senddm/v1', json={'token': user_setup[0], 'dm_id': dm_data.json()['dm_id'], 'message': 'bruh'})
    # Adds index 5 - 7 msgs
    for message in range(3):
        message = str(message)
        requests.post(config.url + 'message/senddm/v1', json={'token': user_setup[0], 'dm_id': dm_data.json()['dm_id'], 'message': 'middle msg'})
    # Adds last 5 messages
    for message in range(5):
        message = str(message)
        requests.post(config.url + 'message/senddm/v1', json={'token': user_setup[0], 'dm_id': dm_data.json()['dm_id'], 'message': 'bruh'})
    # Gets the messages starting from index 5
    response_data = requests.get(config.url + 'dm/messages/v1', params={'token': user_setup[0], 'dm_id': dm_data.json()['dm_id'], 'start': 5})
    assert response_data.status_code == 200
    assert len(response_data.json()['messages']) == 8
    assert response_data.json()['messages'][0]['message'] == 'middle msg' # First message in the middle 
    assert response_data.json()['messages'][1]['message'] == 'middle msg'
    assert response_data.json()['messages'][2]['message'] == 'middle msg' # Last message in the middle 
    assert response_data.json()['messages'][3]['message'] == 'bruh' # First of last few messages
    assert response_data.json()['messages'][7]['message'] == 'bruh' # Last message
    assert response_data.json()['start'] == 5
    assert response_data.json()['end'] == -1
