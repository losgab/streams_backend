import pytest

from src.auth import auth_register_v1, auth_login_v1
from src.channels import channels_create_v1
from src.channel import channel_messages_v1
from src.other import clear_v1
from src.error import InputError, AccessError

# def test_clear_user():
#     clear_v1()
#     auth_register_v1('test@gmail.com', 'password', 'test', 'acc')
#     user_id = auth_login_v1('test@gmail.com', 'password')['auth_user_id']
#     clear_v1()
#     # user should no longer exist
#     with pytest.raises(AccessError):
#         channels_create_v1(user_id, 'test channel', True)

def test_clear_channel():
    clear_v1()
    auth_register_v1('test@gmail.com', 'password', 'test', 'acc')
    channels_create_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 'test channel', True)
    clear_v1()
    # user and channel should no longer exist
    auth_register_v1('test@gmail.com', 'password', 'test', 'acc')
    # user exists but channel should not exist
    with pytest.raises(InputError):
        channel_messages_v1(auth_login_v1('test@gmail.com', 'password')['auth_user_id'], 0, 0)