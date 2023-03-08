import pytest

from src.auth import auth_register_v1, auth_login_v1
from src.other import clear_v1
from src.error import InputError
from src.data_store import data_store


## Registering new account tests
def test_invalid_email():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('hmm', 'pssword', 'cengiz', 'cimen')

def test_no_duplicates():
    clear_v1()
    auth_register_v1('cengiz@gmail.com', 'password', 'cengiz', 'cimen') 
    with pytest.raises(InputError):
        auth_register_v1('cengiz@gmail.com', 'pssword', 'cengiz', 'cimen')

def test_first_name_length_too_short():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('cengiz@gmail.com', 'pssword', '', 'cimen')

def test_first_name_length_too_long():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('cengiz@gmail.com', 'pssword', 'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh', 'cimen')

def test_last_name_length_too_short():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('cengiz@gmail.com', 'pssword', 'cengiz', '')

def test_last_name_length_too_long():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('cengiz@gmail.com', 'pssword', 'cengiz', 'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')

def test_password_too_short():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('cengiz@gmail.com', '1', 'cengiz', 'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')

def test_auth_user_id():
    clear_v1()
    id1 = auth_register_v1('cengiz@gmail.com', 'pssword', 'cengiz', 'cimen')['auth_user_id']
    id2 = auth_register_v1('gab@gmail.com', 'pssword', 'gab', 'thein')['auth_user_id']
    assert id1 == auth_login_v1('cengiz@gmail.com', 'pssword')['auth_user_id'] and id2 == auth_login_v1('gab@gmail.com', 'pssword')['auth_user_id']

## Logging into account tests
def test_login_not_existing_email():
    clear_v1()
    with pytest.raises(InputError):
        auth_login_v1('cengiz@gmail.com', 'pssword')

def test_incorrect_password_pssword():
    clear_v1()
    auth_register_v1('cengiz@gmail.com', 'pssword', 'cengiz', 'cimen')
    with pytest.raises(InputError):
        auth_login_v1('cengiz@gmail.com', 'notpassword')

def test_incorrect_password_1234784():
    clear_v1()
    auth_register_v1('logicaltomato@gmail.com', '1234784', 'tomato', 'salad')
    with pytest.raises(InputError):
        auth_login_v1('logicaltomato@gmail.com', '1234512348')

def test_correct_login_id():
    clear_v1()
    auth_register_v1('logicaltomato@gmail.com', '1234245', 'tomato', 'salad')
    auth_register_v1('cengiz@gmail.com', 'pssword', 'cengiz', 'cimen')

    id1 = auth_login_v1('logicaltomato@gmail.com', '1234245')['auth_user_id']
    id2 =  auth_login_v1('cengiz@gmail.com', 'pssword')['auth_user_id']

    assert id1 == 0 and id2 == 1
