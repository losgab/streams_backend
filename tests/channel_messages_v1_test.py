import pytest

from src.auth import auth_register_v1, auth_login_v1
from src.channels import channels_create_v1
from src.channel import channel_join_v1, channel_invite_v1, channel_messages_v1
from src.other import clear_v1
from src.error import InputError, AccessError

# for iteration 1, can only test with 0 messages

@pytest.fixture
def no_messages_output():
    returned_dict = {
        'messages': [],
        'start': 0,
        'end': -1
    }
    return returned_dict

def test_messages_negative_inputs():
    # assumption: if auth_user_id, channel_id or start are negative numbers, it will raise an InputError
    clear_v1()
    auth_register_v1('test@gmail.com', 'password', 'test', 'acc')
    channels_create_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 'test channel', True) # public channel
    with pytest.raises(AccessError):
        channel_messages_v1(-1, 0, 0)
        channel_messages_v1(0, -1, 0)
        channel_messages_v1(0, 0, -1)
        channel_messages_v1(-65, -5, -23)

def test_messages_check_users():
    # checks behaviour when invalid user ids are passed into the function
    clear_v1()
    auth_register_v1('test@gmail.com', 'password', 'test', 'acc')
    channels_create_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 'test channel', True) # public channel
    with pytest.raises(AccessError):
        channel_messages_v1(1, 0, 0)
        channel_messages_v1(2, 0, 0)

def test_messages_no_messages_index_zero(no_messages_output):
    # InputError when start is greater than the total number of messages in the channel
    # assumption: if a channel has zero messages, and channel_messages_v1 is called with start 0, it will return an empty messages list
    clear_v1()
    auth_register_v1('test@gmail.com', 'password', 'test', 'acc')
    channels_create_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 'test channel', True) # public channel
    assert channel_messages_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 0, 0) == no_messages_output

def test_messages_no_messages_index_one():
    # InputError when start is greater than the total number of messages in the channel
    clear_v1()
    auth_register_v1('test@gmail.com', 'password', 'test', 'acc')
    channels_create_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 'test channel', True) # public channel
    with pytest.raises(InputError):
        channel_messages_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 0, 1)

def test_messages_no_messages_other_index():
    # InputError when start is greater than the total number of messages in the channel
    clear_v1()
    auth_register_v1('test@gmail.com', 'password', 'test', 'acc')
    channels_create_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 'test channel', True) # public channel
    with pytest.raises(InputError):
        channel_messages_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 0, 99)

def test_messages_no_messages_two_channels(no_messages_output):
    # InputError when start is greater than the total number of messages in the channel
    # will this work? maybe the exeption causes the function to stop?
    clear_v1()
    auth_register_v1('test@gmail.com', 'password', 'test', 'acc')
    channels_create_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 'test channel', True) # public channel
    channels_create_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 'test channel 2', False) # private channel
    assert channel_messages_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 0, 0) == no_messages_output
    with pytest.raises(InputError):
        channel_messages_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 1, 99)

def test_messages_invalid_channel_id_no_channels():
    # InputError when channel_id does not refer to a valid channel
    clear_v1()
    auth_register_v1('test@gmail.com', 'password', 'test', 'acc')
    with pytest.raises(InputError):
        channel_messages_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 0, 0)

def test_messages_invalid_channel_id_one_channel():
    # InputError when channel_id does not refer to a valid channel
    clear_v1()
    auth_register_v1('test@gmail.com', 'password', 'test', 'acc')
    channels_create_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 'test channel', True) # public channel
    with pytest.raises(InputError):
        channel_messages_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 1, 99)

def test_messages_invalid_users():
    # invalid auth_user_id causes AccessError
    clear_v1()
    auth_register_v1('test@gmail.com', 'password', 'test', 'acc')
    channels_create_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 'test channel', True) # public channel
    with pytest.raises(AccessError):
        channel_messages_v1(1, 0, 0)
    auth_register_v1('otheruser@gmail.com', 'password', 'other', 'user') # register second user
    with pytest.raises(AccessError):
        channel_messages_v1(2, 0, 0)
        channel_messages_v1(3, 0, 0)

def test_messages_invalid_user_then_register(no_messages_output):
    # creates a user and channel, then tries to access the channel from invalid user id 1
    # then creates a user with the same id which then joins the channel,
    # then tries to read messages from the channel
    clear_v1()
    auth_register_v1('test@gmail.com', 'password', 'test', 'acc')
    channels_create_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 'test channel', True) # public channel
    with pytest.raises(AccessError):
        channel_messages_v1(1, 0, 0)
    auth_register_v1('otheruser@gmail.com', 'password', 'other', 'user') # register second user
    channel_join_v1(auth_login_v1('otheruser@gmail.com', 'password')['auth_user_id'], 0)
    assert channel_messages_v1(auth_login_v1('otheruser@gmail.com', 'password')['auth_user_id'], 0, 0) == no_messages_output

def test_messages_user_not_member_public():
    # AccessError when channel_id is valid and authorised user is not a member of the channel
    clear_v1()
    auth_register_v1('test@gmail.com', 'password', 'test', 'acc')
    channels_create_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 'test channel', True) # public channel
    auth_register_v1('otheruser@gmail.com', 'password', 'other', 'user') # register second user
    with pytest.raises(AccessError):
        channel_messages_v1(auth_login_v1('otheruser@gmail.com', 'password')['auth_user_id'], 0, 0)

def test_messages_user_not_member_private():
    # AccessError when channel_id is valid and authorised user is not a member of the channel
    clear_v1()
    auth_register_v1('test@gmail.com', 'password', 'test', 'acc')
    channels_create_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 'private channel', False) # private channel
    auth_register_v1('otheruser@gmail.com', 'password', 'other', 'user') # register second user
    with pytest.raises(AccessError):
        channel_messages_v1(auth_login_v1('otheruser@gmail.com', 'password')['auth_user_id'], 0, 0)

def test_messages_no_messages_public_channel_created_by_other_person(no_messages_output):
    clear_v1()
    auth_register_v1('test@gmail.com', 'password', 'test', 'acc')
    channels_create_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 'test channel', True) # public channel
    auth_register_v1('otheruser@gmail.com', 'password', 'other', 'user') # register second user
    channel_join_v1(auth_login_v1('otheruser@gmail.com', 'password')['auth_user_id'], 0)
    assert channel_messages_v1(auth_login_v1('otheruser@gmail.com', 'password')['auth_user_id'], 0, 0) == no_messages_output

def test_messages_no_messages_private_channel_created_by_other_person(no_messages_output):
    clear_v1()
    auth_register_v1('test@gmail.com', 'password', 'test', 'acc')
    channels_create_v1(0, 'test channel', False) # private channel
    auth_register_v1('otheruser@gmail.com', 'password', 'other', 'user') # register second user
    channel_invite_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 0, 1)
    assert channel_messages_v1(auth_login_v1('otheruser@gmail.com', 'password')['auth_user_id'], 0, 0) == no_messages_output

# tests below this point can't be tested bc haven't implemented message creation

# def test_messages_normal():
#     # 10 messages
    
# def test_messages_two_channels():

# def test_messages_fifty():
#     # have more than 50 messages, but it should only return 50 messages

# def test_messages_multiple_users():
#     # have messages from multiple users

# def test_messages_end_negative_one():
#     # if there are no more messages to load, returns -1 in end

# def test_messages_index_zero():
#     # message with index 0 is the most recent message in the channel

# def test_messages_invalid_start():

# def test_messages_valid_channel_id_authorised_user_not_member():
