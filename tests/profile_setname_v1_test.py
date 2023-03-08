import json
import pytest
import requests

from src.user import profile_setname_v1

from src import config
from src.error import AccessError, InputError

# Fixture that clears the data store 
@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1')

# Fixture that registers 2 users
@pytest.fixture
def user_setup():
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'gabriel@domain.com', 'password': 'password', 'name_first': 'gabriel', 'name_last': 'thien'})
    return (user_0_json.json()['token'], user_0_json.json()['auth_user_id'])
    
# Empty string passed as name_first
def test_first_name_too_short(clear, user_setup):
    response_data = requests.put(config.url + 'user/profile/setname/v1', json={'token': user_setup[0], 'name_first': '', 'name_last': 'cimen'})
    # InputError code 400 expected 
    assert response_data.status_code == InputError.code

# > 50 character string passed as name_first
def test_first_name_too_long(clear, user_setup):
    response_data = requests.put(config.url + 'user/profile/setname/v1', json={'token': user_setup[0], 'name_first': 'cengizcengizcengizcengizcengizcengizcengizcengizcengiz', 'name_last': 'cimen'})
    # InputError code 400 expected
    assert response_data.status_code == InputError.code
    
# Empty string passed as name_last
def test_last_name_too_short(clear, user_setup):
    response_data = requests.put(config.url + 'user/profile/setname/v1', json={'token': user_setup[0], 'name_first': 'cengiz', 'name_last': ''})
    # InputError code 400 expected
    assert response_data.status_code == InputError.code

# > 50 character string passed as name_last
def test_last_name_too_long(clear, user_setup):
    response_data = requests.put(config.url + 'user/profile/setname/v1', json={'token': user_setup[0], 'name_first': 'cengiz', 'name_last': 'cimencimencimencimencimencimencimencimencimencimencimen'})
    # InputError code 400 expected
    assert response_data.status_code == InputError.code

# Tests success case to ensure things actually go right 
def test_success_names_changed(clear, user_setup):
    # Gabbo changes his name from gabriel thien ->  garbo bin
    response_data = requests.put(config.url + 'user/profile/setname/v1', json={'token': user_setup[0], 'name_first': 'garbo', 'name_last': 'bin'})
    # Success code 200 expected
    assert response_data.status_code == 200
    assert response_data.json() == {}
    # Nathan sees Garbo's details 
    user_data = requests.get(config.url + 'user/profile/v1', params={'token': user_setup[0], 'u_id': user_setup[1]})
    # Confirming actual name change 
    assert user_data.json()['user']['name_first'] == 'garbo'
    assert user_data.json()['user']['name_last'] == 'bin'