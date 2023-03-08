import pytest

from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.channel import channel_join_v1, channel_invite_v1
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

# Tests when invalid auth_user_id is passed 
def test_invalid_auth_uid(user_setup):
    # Gabbo creates a public channel
    channelid_banana = channels_create_v1(pytest.global_gabriel['auth_user_id'], 'banana', True)
    # Invalid auth_user_id is passed
    with pytest.raises(AccessError):
        channel_invite_v1(700, channelid_banana['channel_id'], pytest.global_nathan['auth_user_id'])
    with pytest.raises(AccessError):
        channel_invite_v1(-1, channelid_banana['channel_id'], pytest.global_nathan['auth_user_id'])

# Tests when invalid channel_id is passed 
def test_invalid_channel(user_setup): # InputError when channel_id does not refer to a valid channel
    # Gabbo tries to invite Christina to a channel that doesnt exist, should raise InputError
    with pytest.raises(InputError):
        channel_invite_v1(pytest.global_gabriel['auth_user_id'], 3, pytest.global_christina['auth_user_id']) # Bad integer 
    with pytest.raises(InputError):
        channel_invite_v1(pytest.global_gabriel['auth_user_id'], -1, pytest.global_christina['auth_user_id']) # Passing negative

# Tests when invalid u_id is passed 
def test_invalid_uid(user_setup): # InputError when u_id specified is not a user/does not exist 
    # Gabbo creates a public channel
    channelid_banana = channels_create_v1(pytest.global_gabriel['auth_user_id'], 'banana', True)
    # Gabbo tries to invite an invalid user to a channel, should raise InputError
    with pytest.raises(InputError):
        channel_invite_v1(pytest.global_gabriel['auth_user_id'], channelid_banana['channel_id'], 7) # Passing bad integer
    with pytest.raises(InputError):
        channel_invite_v1(pytest.global_gabriel['auth_user_id'], channelid_banana['channel_id'], -1) # Passing negative

# Tests whats happens when u_id is already a member of specified channel 
def test_uid_alreadymember(user_setup): # InputError when u_id specified is already a member of said channel
    # Gabbo creates a public channel
    channelid_banana = channels_create_v1(pytest.global_gabriel['auth_user_id'], 'banana', True)
    # Cengiz joints gabbo's channel
    channel_join_v1(pytest.global_cengiz['auth_user_id'], channelid_banana['channel_id'])
    # Gabbo invites cengiz, who is already a member, should raise InputError
    with pytest.raises(InputError):
        channel_invite_v1(pytest.global_gabriel['auth_user_id'], channelid_banana['channel_id'], pytest.global_cengiz['auth_user_id']) 

# Test what happens when the inviter isnt actually a member of the channel
def test_inviter_notmember(user_setup): # AccessError when the inviter is not a member of the channel they inviting u_id to 
    # Gabbo creates a private channel
    channelid_banana = channels_create_v1(pytest.global_gabriel['auth_user_id'], 'banana', False)
    # Celina tries to invite Nathan
    with pytest.raises(AccessError):
        channel_invite_v1(pytest.global_celina['auth_user_id'], channelid_banana['channel_id'], pytest.global_nathan['auth_user_id'])

