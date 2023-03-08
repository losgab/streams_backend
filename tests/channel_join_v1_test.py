import pytest

from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.channel import channel_join_v1
from src.other import clear_v1
from src.data_store import data_store
from src.error import InputError, AccessError

@pytest.fixture
def user_setup():
    clear_v1()
    pytest.global_celina = auth_register_v1('celina@domain.com', 'password', 'celina', 'shen')
    pytest.global_christina =  auth_register_v1('christina@domain.com', 'password', 'christina', 'lee')
    pytest.global_gabriel = auth_register_v1('gabriel@domain.com', 'password', 'gabriel', 'thien')
    pytest.global_nathan = auth_register_v1('nathan@domain.com', 'password', 'nathan', 'mu')
    pytest.global_cengiz = auth_register_v1('cengiz@domain.com', 'password', 'cengiz', 'cimen')

# def test_invalid_auth_uid(user_setup):
#     # Gabbo creates a public channel
#     channelid_banana = channels_create_v1(pytest.global_gabriel['auth_user_id'], 'banana', True)
#     # Invalid auth_user_id is passed
#     with pytest.raises(AccessError):
#         channel_join_v1(700, channelid_banana['channel_id'])
#         channel_join_v1('bruh', channelid_banana['channel_id'])

def test_invalidchannel(user_setup): # Channel specified to join does not exist or invalid input
    with pytest.raises(InputError): # Channel doesnt exist
        channel_join_v1(pytest.global_celina['auth_user_id'], 2)
        channel_join_v1(pytest.global_nathan['auth_user_id'], 'bruh')

def test_alreadymember(user_setup): # Tests what happens when a member who is already a member in a channel, tries to join the channel again
    channels_create_v1(pytest.global_cengiz['auth_user_id'], 'channel 0', True) # Cengiz creates a public channel
    channel_join_v1(pytest.global_gabriel['auth_user_id'], 0) # Gabbo joins channel
    with pytest.raises(InputError):
        channel_join_v1(pytest.global_gabriel['auth_user_id'], 0) # Gabbo tries to join channel again

def test_nopermissions(user_setup): # Tests what happens when a user tries to join a private channel
    channels_create_v1(pytest.global_cengiz['auth_user_id'], 'channel 0', False) # Private channel created 
    with pytest.raises(AccessError):
        channel_join_v1(pytest.global_gabriel['auth_user_id'], 0) # Gabbo tries to join private channel
        
def test_globalowners_join_privatechannel(user_setup): # Tests if a global owner can access a private channel
    channel_id = channels_create_v1(pytest.global_cengiz['auth_user_id'], 'channel 0', False) # Private channel created 
    channel_join_v1(pytest.global_celina['auth_user_id'], channel_id['channel_id'])