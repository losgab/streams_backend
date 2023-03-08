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
    return (user_0['token'], user_1['token'], user_0['auth_user_id'], user_1['auth_user_id'])

# AccessError (403), invalid token input
def test_permission_change_v1_invalid_token(clear, register):
    resp_0 = requests.post(config.url + 'admin/userpermission/change/v1', json={'token': -1, 'u_id': register[2], 'permission_id': 2})
    resp_1 = requests.post(config.url + 'admin/userpermission/change/v1', json={'token': 10, 'u_id': register[2], 'permission_id': 2})
    # Expected status code (403) AccessError
    assert resp_0.status_code == 403
    assert resp_1.status_code == 403

# InputError (400), user id is invalid
def test_permission_change_v1_invalid_uid(clear, register):
    resp_0 = requests.post(config.url + 'admin/userpermission/change/v1', json={'token': register[0], 'u_id': -1, 'permission_id': 2})
    resp_1 = requests.post(config.url + 'admin/userpermission/change/v1', json={'token': register[0], 'u_id': 10, 'permission_id': 2}) 
    # Expected status code (400) InputError
    assert resp_0.status_code == 400
    assert resp_1.status_code == 400

# user id regers to the only global owner, inwhich they demote themselves (InputError)
def test_permission_change_v1_only_globalowner(clear, register):
    resp = requests.post(config.url + 'admin/userpermission/change/v1', json={'token': register[0], 'u_id': register[2], 'permission_id': 2})
    # Expected status code (400) InputError
    assert resp.status_code == 400

# InputError (400), invalid permission id
def test_permission_change_v1_invalid_permissionid(clear, register):
    resp_0 = requests.post(config.url + 'admin/userpermission/change/v1', json={'token': register[0], 'u_id': register[3], 'permission_id': 3})
    resp_1 = requests.post(config.url + 'admin/userpermission/change/v1', json={'token': register[0], 'u_id': register[2], 'permission_id': 0})
    # Expected status code (400), InputError
    assert resp_0.status_code == 400
    assert resp_1.status_code == 400

# User already has permission id, InputError
def test_permission_change_v1_already_has_perm(clear, register):
    resp_0 = requests.post(config.url + 'admin/userpermission/change/v1', json={'token': register[0], 'u_id': register[2], 'permission_id': 1})
    resp_1 = requests.post(config.url + 'admin/userpermission/change/v1', json={'token': register[0], 'u_id': register[3], 'permission_id': 2})
    # Expected status code (400) InputError
    assert resp_0.status_code == 400
    assert resp_1.status_code == 400

def test_permission_change_v1_not_globalowner(clear, register):
    resp = requests.post(config.url + 'admin/userpermission/change/v1', json={'token': register[1], 'u_id': register[2], 'permission_id': 2})
    # Expected status code (403), AccessError
    assert resp.status_code == 403

def test_permission_change_v1_successful(clear, register):
    # Celina changes Christina to global owner
    resp_0 = requests.post(config.url + 'admin/userpermission/change/v1', json={'token': register[0], 'u_id': register[3], 'permission_id': 1})
    assert resp_0.status_code == 200
    assert json.loads(resp_0.text) == {}
    # Christina changes Celina to member
    resp_1 = requests.post(config.url + 'admin/userpermission/change/v1', json={'token': register[1], 'u_id': register[2], 'permission_id': 2})
    assert resp_1.status_code == 200
    assert json.loads(resp_1.text) == {} 
    # Celina tries to make Christina a member (403 AccessError)
    resp_2 = requests.post(config.url + 'admin/userpermission/change/v1', json={'token': register[0], 'u_id': register[3], 'permission_id': 2})
    assert resp_2.status_code == 403
