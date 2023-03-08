from src.channels import channels_listall_v1, channels_create_v1
from src.auth import auth_register_v1
from src.channel import channel_join_v1
from src.other import clear_v1
from src.error import AccessError

import pytest

# Fixture that clears the data store, registers 5 users.
@pytest.fixture
def auth_registers():
    clear_v1()
    pytest.global_celina = auth_register_v1('celina@domain.com', 'password', 'celina', 'shen')
    pytest.global_christina =  auth_register_v1('christina@domain.com', 'password', 'christina', 'lee')
    pytest.global_gabriel = auth_register_v1('gabriel@domain.com', 'password', 'gabriel', 'thien')
    pytest.global_nathan = auth_register_v1('nathan@domain.com', 'password', 'nathan', 'mu')
    pytest.global_cengiz = auth_register_v1('cengiz@domain.com', 'password', 'cengiz', 'cimen')

# # Test if input is invalid (id doesn't exist) for channels_listall_v1
# def test_listall_invalid_user_id():
#     clear_v1()
#     with pytest.raises(AccessError):
#         channels_listall_v1(0)

# Tests channels_listall_v2 with no channels
def test_listall_no_channels(auth_registers):
    assert channels_listall_v1(pytest.global_celina['auth_user_id']) == {
        'channels': []
    }

# Tests channels_listall_v1 with one user in channel
def test_listall_one_user(auth_registers):
    # User Celina creates public channel 'lonely', and store channel ID
    channel_lonely_id = channels_create_v1(pytest.global_celina['auth_user_id'], 'lonely', True)
    # Assert channels_listall_v1 functions as expected
    assert channels_listall_v1(pytest.global_celina['auth_user_id']) == {
        'channels': [
            {
                'channel_id': channel_lonely_id['channel_id'],
                'name' : 'lonely',
            }
        ]
    }

# Tests channels_listall_v1 with multiple users joined
def test_listall_multiple_users(auth_registers):
    # User Celina creates public channel 'elephant', and store channel ID
    channel_elephant_id = channels_create_v1(pytest.global_celina['auth_user_id'], 'elephant', True)
    # Users Christina, Gabriel, Nathan and Cengiz join channel 'elephant'
    channel_join_v1(pytest.global_christina['auth_user_id'], channel_elephant_id['channel_id'])
    channel_join_v1(pytest.global_gabriel['auth_user_id'], channel_elephant_id['channel_id'])
    channel_join_v1(pytest.global_nathan['auth_user_id'], channel_elephant_id['channel_id'])
    channel_join_v1(pytest.global_cengiz['auth_user_id'], channel_elephant_id['channel_id'])
    # Assert channels_listall_v1 functions as expected
    assert channels_listall_v1(pytest.global_celina['auth_user_id']) == {
        'channels': [
            {
                'channel_id': channel_elephant_id['channel_id'],
                'name' : 'elephant',
            }
        ]
    }

# Tests channels_listall_v1 with all private channels
def test_listall_private(auth_registers):
    # User Celina creates private channel 'hello', and store channel ID 
    channel_hello_id = channels_create_v1(pytest.global_celina['auth_user_id'], 'hello', False)
    # User Christina creates private channel 'world' and store channel ID 
    channel_world_id = channels_create_v1(pytest.global_christina['auth_user_id'], 'world', False)
    # Assert channels_listall_v1 functions as expected
    assert channels_listall_v1(pytest.global_celina['auth_user_id']) == {
        'channels': [
            {
                'channel_id': channel_hello_id['channel_id'],
                'name' : 'hello',
            },
            {
                'channel_id': channel_world_id['channel_id'],
                'name' : 'world',
            }
        ]
    }

# Tests channels_listall_v1 with all public channels
def test_listall_public(auth_registers):
    # User Gabriel creates public channel 'sushi', and store channel ID 
    channel_sushi_id = channels_create_v1(pytest.global_gabriel['auth_user_id'], 'sushi', True)
    # User Nathan creates public channel 'burger' and store channel ID 
    channel_burger_id = channels_create_v1(pytest.global_nathan['auth_user_id'], 'burger', True)
    # User Cengiz creates a public channel 'nugget' and store channel ID
    channel_nugget_id = channels_create_v1(pytest.global_cengiz['auth_user_id'], 'nugget', True)
    # Assert channels_listall_v1 functions as expected
    assert channels_listall_v1(pytest.global_celina['auth_user_id']) == {
        'channels': [
            {
                'channel_id': channel_sushi_id['channel_id'],
                'name' : 'sushi',
            },
            {
                'channel_id': channel_burger_id['channel_id'],
                'name' : 'burger',
            },
            {
                'channel_id': channel_nugget_id['channel_id'],
                'name' : 'nugget',
            }
        ]
    }

# Tests channels_listall_v1 with a mix of public and private channels
def test_listall_multiple_channels(auth_registers):
    # User Celina creates private channel 'hello', and store channel ID 
    channel_hello_id = channels_create_v1(pytest.global_celina['auth_user_id'], 'hello', False)
    # User Christina creates private channel 'world' and store channel ID 
    channel_world_id = channels_create_v1(pytest.global_christina['auth_user_id'], 'world', False)
    # User Gabriel creates public channel 'sushi', and store channel ID 
    channel_sushi_id = channels_create_v1(pytest.global_gabriel['auth_user_id'], 'sushi', True)
    # User Nathan creates public channel 'burger' and store channel ID 
    channel_burger_id = channels_create_v1(pytest.global_nathan['auth_user_id'], 'burger', True)
    # User Cengiz creates a public channel 'nugget' and store channel ID
    channel_nugget_id = channels_create_v1(pytest.global_cengiz['auth_user_id'], 'nugget', True)
    # Assert channels_listall_v1 functions as expected
    assert channels_listall_v1(pytest.global_celina['auth_user_id']) == {
        'channels': [
            {
                'channel_id': channel_hello_id['channel_id'],
                'name' : 'hello',
            },
            {
                'channel_id': channel_world_id['channel_id'],
                'name' : 'world',
            },
            {
                'channel_id': channel_sushi_id['channel_id'],
                'name' : 'sushi',
            },
            {
                'channel_id': channel_burger_id['channel_id'],
                'name' : 'burger',
            },
            {
                'channel_id': channel_nugget_id['channel_id'],
                'name' : 'nugget',
            }
        ]
    }
