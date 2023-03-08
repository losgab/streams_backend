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
    # return tuple of user tokens
    return (user_0['token'], user_1['token'], user_0['auth_user_id'])

# AccessError (403), invalid token input
def test_user_profile_setemail_v1_invalid_token(clear):
    resp = requests.put(config.url + 'user/profile/setemail/v1', json={'token': -1, 'email': 'shen@domain.com'})
    # Expected status code (403) AccessError
    assert resp.status_code == 403

# InputError (400), invalid email (no @)
def test_user_profile_setemail_v1_invalid_email_no_at(clear, register):
    resp = requests.put(config.url + 'user/profile/setemail/v1', json={'token': register[0], 'email': 'invaliddomain.com'})
    # Expected status code (400) InputError
    assert resp.status_code == 400

# InputError (400), invalid email (no .)
def test_user_profile_setemail_v1_invalid_email_no_fullstop(clear, register):
    resp = requests.put(config.url + 'user/profile/setemail/v1', json={'token': register[0], 'email': 'invalid@domaincom'})
    # Expected status code (400) InputError
    assert resp.status_code == 400

# InputError (400), empty email address
def test_user_profile_setemail_v1_invalid_email_empty(clear, register):
    resp = requests.put(config.url + 'user/profile/setemail/v1', json={'token': register[0], 'email': ''})
    # Expected status code (400) InputError
    assert resp.status_code == 400

# InputError (400), email is being used by another user
def test_user_profile_setemail_v1_email_used_another(clear, register):
    resp = requests.put(config.url + 'user/profile/setemail/v1', json={'token': register[0], 'email': 'christina@domain.com'})
    # Expected status code (400) InputError
    assert resp.status_code == 400

# InputError (400), email is being used by user calling function
def test_user_profile_setemail_v1_email_used_self(clear, register):
    resp = requests.put(config.url + 'user/profile/setemail/v1', json={'token': register[0], 'email': 'celina@domain.com'})
    # Expected status code (400) InputError
    assert resp.status_code == 400

# Successful email set, check return value + behaviour + response code
def test_user_profile_setemail_v1_successful(clear, register):
    resp = requests.put(config.url + 'user/profile/setemail/v1', json={'token': register[0], 'email': 'lina@domain.com'})
    # Expected return value and status code (200) successful
    assert json.loads(resp.text) == {}
    assert resp.status_code == 200
    # Assert correct behaviour using user profile v1
    profile = requests.get(config.url + 'user/profile/v1', params={'token': register[0], 'u_id': register[2]})
    assert json.loads(profile.text) == {
        'user': {
            'u_id': 0,
            'email': 'lina@domain.com',
            'name_first': 'celina',
            'name_last': 'shen',
            'handle_str': 'celinashen',
            'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
        }
    }
