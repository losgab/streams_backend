import pytest

from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import clear_v1

# Fixture that clears the data store, registers 5 users.
@pytest.fixture
def auth_registers():
    clear_v1()
    pytest.global_celina = auth_register_v1('celina@domain.com', 'password', 'celina', 'shen')
    pytest.global_christina =  auth_register_v1('christina@domain.com', 'password', 'christina', 'lee')
    pytest.global_gabriel = auth_register_v1('gabriel@domain.com', 'password', 'gabriel', 'thien')
    pytest.global_nathan = auth_register_v1('nathan@domain.com', 'password', 'nathan', 'mu')
    pytest.global_cengiz = auth_register_v1('cengiz@domain.com', 'password', 'cengiz', 'cimen')

# def test_invalid_user_id(): # invalid user ID
#     clear_v1()
#     with pytest.raises(AccessError):
#         channels_create_v1(-1, 'pp', True)

def test_create_no_name_1(auth_registers): # no name public channel
    with pytest.raises(InputError):
        channels_create_v1(pytest.global_celina['auth_user_id'], '', True)

def test_create_long_name_1(auth_registers): # long name public channel
    with pytest.raises(InputError):
        channels_create_v1(pytest.global_christina['auth_user_id'], '098765432109876543210', True)

def test_create_no_name_2(auth_registers): # no name private channel
    with pytest.raises(InputError):
        channels_create_v1(pytest.global_gabriel['auth_user_id'], '', False)

def test_create_long_name_2(auth_registers): # long name private channel
    with pytest.raises(InputError):
        channels_create_v1(pytest.global_nathan['auth_user_id'], 'abcdefghijklmnopqrstuvwxyz', False)
