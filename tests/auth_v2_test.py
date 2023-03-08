import pytest
import requests
import json
from src import config

@pytest.fixture
def user_setup():
    requests.delete(config.url + 'clear/v1')
    requests.post(config.url + 'auth/register/v2', 
    json = {
        'email' : 'celina@domain.com',
        'password': 'password',
        'name_first': 'celina',
        'name_last': 'shen'
    })
    requests.post(config.url + 'auth/register/v2', 
    json = {
        'email' : 'christina@domain.com',
        'password': 'password',
        'name_first': 'christina',
        'name_last': 'lee'
    })
    requests.post(config.url + 'auth/register/v2', 
    json = {
        'email' : 'garbiel@domain.com',
        'password': 'password',
        'name_first': 'gabriel',
        'name_last': 'thien'
    })
    requests.post(config.url + 'auth/register/v2', 
    json = {
        'email' : 'nathan@domain.com',
        'password': 'password',
        'name_first': 'nathan',
        'name_last': 'mu'
    })
    requests.post(config.url + 'auth/register/v2', 
    json = {
        'email' : 'cengiz@domain.com',
        'password': 'password',
        'name_first': 'cengiz',
        'name_last': 'cimen'
    })

@pytest.fixture
def user_setup_data():
    requests.delete(config.url + 'clear/v1')
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'gabriel@domain.com', 'password': 'password', 'name_first': 'gabriel', 'name_last': 'thien'})
    user_0 = json.loads(user_0_json.text)
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'nathan@domain.com', 'password': 'password', 'name_first': 'nathan', 'name_last': 'mu'})
    user_1 = json.loads(user_1_json.text)
    user_2_json = requests.post(config.url + 'auth/register/v2', json={'email': 'celina@domain.com', 'password': 'password', 'name_first': 'celina', 'name_last': 'shen'})
    user_2 = json.loads(user_2_json.text)
    return (user_0['token'], user_1['token'], user_2['token'], user_0['auth_user_id'], user_1['auth_user_id'], user_2['auth_user_id'])
 

def test_auth_register_success_v2():
    requests.delete(config.url + 'clear/v1')
    resp = requests.post(config.url + 'auth/register/v2', 
    json = {
        'email' : 'cengiz@gmai.com',
        'password': 'pasaoieajroiwqejr',
        'name_first': 'cengiz',
        'name_last': 'cimen'
    })
    assert resp.status_code == 200

def test_auth_email_not_valid_v2():
    # requests.delete(config.url + 'clear/v1')
    requests.delete(config.url + 'clear/v1')
    resp = requests.post(config.url + 'auth/register/v2', 
    json = {
        'email' : 'cengzicimenm',
        'password': 'pasaoieajroiwqejr',
        'name_first': 'cengiz',
        'name_last': 'cimen'
    })
    assert resp.status_code == 400

def test_auth_email_in_use_v2():
    requests.delete(config.url + 'clear/v1')
    requests.post(config.url + 'auth/register/v2', 
    json = {
        'email' : 'cengzicimen@gmai.com',
        'password': 'pasaoieajroiwqejr',
        'name_first': 'cengiz',
        'name_last': 'cimen'
    })
    resp = requests.post(config.url + 'auth/register/v2', 
    json = {
        'email' : 'cengzicimen@gmai.com',
        'password': 'pasaoieajroiwqejr',
        'name_first': 'cengiz',
        'name_last': 'cimen'
    })
    assert resp.status_code == 400


def test_last_name_too_long_v2():
    requests.delete(config.url + 'clear/v1')
    resp = requests.post(config.url + 'auth/register/v2', 
    json = {
        'email' : 'cengzicimen@gmai.com',
        'password': 'pasaoieajroiwqejr',
        'name_first': 'cengiz',
        'name_last': 'ewojfqowejrowqijfowiqejfoiqwejfoipqwjfoiqwejoifqwjeofijqweojfqweiojfoqweejfopqweijfweqoi'
    })

    assert resp.status_code == 400


def test_last_name_too_short_v2():
    requests.delete(config.url + 'clear/v1')
    resp = requests.post(config.url + 'auth/register/v2', 
    json = {
        'email' : 'cengzicimen@gmai.com',
        'password': 'pasaoieajroiwqejr',
        'name_first': 'cengiz',
        'name_last': ''
    })

    assert resp.status_code == 400   
    
def test_first_name_too_long_v2():
    requests.delete(config.url + 'clear/v1')
    resp = requests.post(config.url + 'auth/register/v2', 
    json = {
        'email' : 'cengzicimen@gmai.com',
        'password': 'pasaoieajroiwqejr',
        'name_first': 'ewojfqowejrowqijfowiqejfoiqwejfoipqwjfoiqwejoifqwjeofijqweojfqweiojfoqweejfopqweijfweqoi',
        'name_last': 'cimen'
    })

    assert resp.status_code == 400

def test_first_name_too_short_v2():
    requests.delete(config.url + 'clear/v1')
    resp = requests.post(config.url + 'auth/register/v2', 
    json = {
        'email' : 'cengzicimen@gmai.com',
        'password': 'pasaoieajroiwqejr',
        'name_first': '',
        'name_last': 'cimen'
    })

    assert resp.status_code == 400

def test_password_length_too_short_v2():
    requests.delete(config.url + 'clear/v1')
    resp = requests.post(config.url + 'auth/register/v2', 
    json = {
        'email' : 'cengzicimen@gmai.com',
        'password': '12',
        'name_first': 'cengiz',
        'name_last': 'cimen'
    })

    assert resp.status_code == 400

def test_removed_user_handle_reusable_v2(user_setup_data):
    # test reusable email
    requests.delete(config.url + 'admin/user/remove/v1', json={'token': user_setup_data[0], 'u_id' : user_setup_data[5]})
    resp = requests.post(config.url + 'auth/register/v2', json={'email': 'casaaas@domain.com', 'password': 'password', 'name_first': 'celina', 'name_last': 'shen'})
    assert resp.status_code == 200

    # test reusable handle
    resp_profile = requests.get(config.url + 'user/profile/v1',
                                params = {'token': user_setup_data[0], 'u_id': resp.json()['auth_user_id']})
    assert resp_profile.json() == {
        'user': {
            'u_id': resp.json()['auth_user_id'],
            'email': 'casaaas@domain.com',
            'name_first': 'celina',
            'name_last': 'shen',
            'handle_str': 'celinashen',
            'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
        }
    }

def test_removed_user_email_reusable_v2(user_setup_data):
    # test reusable email
    requests.delete(config.url + 'admin/user/remove/v1', json={'token': user_setup_data[0], 'u_id' : user_setup_data[5]})
    resp = requests.post(config.url + 'auth/register/v2', json={'email': 'celina@domain.com', 'password': 'password', 'name_first': 'celina', 'name_last': 'shen'})
    assert resp.status_code == 200

    # test reusable handle
    resp_profile = requests.get(config.url + 'user/profile/v1',
                                params = {'token': user_setup_data[0], 'u_id': resp.json()['auth_user_id']})
    assert resp_profile.json() == {
        'user': {
            'u_id': resp.json()['auth_user_id'],
            'email': 'celina@domain.com',
            'name_first': 'celina',
            'name_last': 'shen',
            'handle_str': 'celinashen',
            'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
        }
    }


###### TESTS FOR AUTH LOGIN BELOW #######
def test_email_not_in_database_v2(user_setup):
    resp = requests.post(config.url + 'auth/login/v2', 
    json = {
        'email' : 'celia@domain.com',
        'password': 'password'
    })
    assert resp.status_code == 400


def test_password_incorrect_v2(user_setup):
    resp = requests.post(config.url + 'auth/login/v2', 
    json = {
        'email' : 'celina@domain.com',
        'password': '123122233',
    })
    assert resp.status_code == 400

def test_login_success_v2(user_setup):
    resp0 = requests.post(config.url + 'auth/login/v2', 
    json = {
        'email' : 'cengiz@domain.com',
        'password': 'password',
    })
    assert resp0.status_code == 200

    resp1 = requests.post(config.url + 'auth/login/v2', 
    json = {
        'email' : 'cengiz@domain.com',
        'password': 'password',
    })
    assert resp1.status_code == 200

    assert resp0.json()['token'] != resp1.json()['token']
    assert resp0.json()['auth_user_id'] == resp1.json()['auth_user_id']

def test_login_user_has_been_removed(user_setup_data):
    resp0 = requests.post(config.url + 'auth/login/v2', 
    json = {
        'email' : 'nathan@domain.com',
        'password': 'password'
    })
    assert resp0.status_code == 200

    requests.delete(config.url + 'admin/user/remove/v1', json={'token': user_setup_data[0], 'u_id' : resp0.json()['auth_user_id']})

    resp1 = requests.post(config.url + 'auth/login/v2', 
    json = {
        'email' : 'nathan@domain.com',
        'password': 'password'
    })

    assert resp1.status_code == 400
    
