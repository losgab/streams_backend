import json
import pytest
import requests
from src import config

@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1')

# Register users
@pytest.fixture
def register_users():
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'christina@domain.com', 'password': 'password', 'name_first': 'christina', 'name_last': 'lee'})
    user_0 = json.loads(user_0_json.text)
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'celina@domain.com', 'password': 'password', 'name_first': 'celina', 'name_last': 'shen'})
    user_1 = json.loads(user_1_json.text)
    user_2_json = requests.post(config.url + 'auth/register/v2', json={'email': 'cengiz@domain.com', 'password': 'password', 'name_first': 'cengiz', 'name_last': 'cimen'})
    user_2 = json.loads(user_2_json.text)
    return (user_0['token'], user_1['token'], user_2['token'], user_0['auth_user_id'], user_1['auth_user_id'], user_2['auth_user_id'])

# dm_id does not refer to a valid dm
def test_dm_details_v1_invalid_dm_id(clear, register_users):
    resp = requests.get(config.url + 'dm/details/v1', params={'token': register_users[0], 'dm_id': -1})
    # Expected status code (400) InputError
    assert resp.status_code == 400

# dm_id is valid and the authorised user is not a member of the DM
def test_dm_details_v1_not_a_member(clear, register_users):
    # Create a dm between Christina and Celina
    dm = requests.post(config.url + 'dm/create/v1', json={'token': register_users[0], 'u_ids': [register_users[4]]})
    # Cengiz tries to access the dm
    resp = requests.get(config.url + 'dm/details/v1', params={'token': register_users[2], 'dm_id': dm.json()['dm_id']})
    # Expected status code (403) AccessError
    assert resp.status_code == 403

# dm_id is valid and the authorised user is a member of the DM
def test_dm_details_v1(clear, register_users):
    # Create a dm between Christina and Celina
    dm = requests.post(config.url + 'dm/create/v1', json={'token': register_users[0], 'u_ids': [register_users[4]]})
    # Christina access dm
    resp = requests.get(config.url + 'dm/details/v1', params={'token': register_users[0], 'dm_id': dm.json()['dm_id']})
    assert resp.status_code == 200
    # Check dm details behaviour
    det = requests.get(config.url + 'dm/details/v1', params={'token': register_users[0], 'dm_id': dm.json()['dm_id']})
    assert det.json() == {
        'name': "celinashen, christinalee",
        'members': [
            {
                'u_id': register_users[4],
                'name_first': 'celina',
                'name_last': 'shen',
                'email': 'celina@domain.com',
                'handle_str': 'celinashen',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
            {
                'u_id': register_users[3],
                'name_first': 'christina',
                'name_last': 'lee',
                'email': 'christina@domain.com',
                'handle_str': 'christinalee',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
        ],
    }

def test_dem_details_multiple_dms_created(clear, register_users):
    requests.post(config.url + 'dm/create/v1', json={'token': register_users[0], 'u_ids': [register_users[4]]})
    requests.post(config.url + 'dm/create/v1', json={'token': register_users[0], 'u_ids': [register_users[4]]})
    dm = requests.post(config.url + 'dm/create/v1', json={'token': register_users[0], 'u_ids': [register_users[4]]})

    det = requests.get(config.url + 'dm/details/v1', params={'token': register_users[0], 'dm_id': dm.json()['dm_id']})

    assert det.json() == {
        'name': "celinashen, christinalee",
        'members': [
            {
                'u_id': register_users[4],
                'name_first': 'celina',
                'name_last': 'shen',
                'email': 'celina@domain.com',
                'handle_str': 'celinashen',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
            {
                'u_id': register_users[3],
                'name_first': 'christina',
                'name_last': 'lee',
                'email': 'christina@domain.com',
                'handle_str': 'christinalee',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
        ],
    }
