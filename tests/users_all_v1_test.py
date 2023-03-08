import pytest
import requests
from src import config

@pytest.fixture
def user_tokens():
    # register four users and return their tokens in a tuple

    # clear
    resp_clear = requests.delete(config.url + 'clear/v1')
    assert resp_clear.status_code == 200

    # register first user
    resp_register0 = requests.post(config.url + 'auth/register/v2',
                                  json = {'email': 'test@gmail.com', 'password': 'password',
                                        'name_first': 'test', 'name_last': 'acc'})
    assert resp_register0.status_code == 200
    token0 = resp_register0.json()['token']

    # register second user
    resp_register1 = requests.post(config.url + 'auth/register/v2',
                                  json = {'email': 'second@user.com', 'password': 'awleiuufadsf',
                                          'name_first': 'second', 'name_last': 'user'})
    assert resp_register1.status_code == 200
    token1 = resp_register1.json()['token']

    # register third user with same name as first user
    resp_register2 = requests.post(config.url + 'auth/register/v2',
                                  json = {'email': 'third@user.com', 'password': 'awieogf',
                                          'name_first': 'test', 'name_last': 'acc'})
    assert resp_register2.status_code == 200
    token2 = resp_register2.json()['token']

    # register fourth user which will be removed
    resp_register3 = requests.post(config.url + 'auth/register/v2',
                                  json = {'email': 'fourth@user.com', 'password': 'auikwyegyf',
                                          'name_first': 'good', 'name_last': 'bye'})
    assert resp_register3.status_code == 200
    token3 = resp_register3.json()['token']
    u_id3 = resp_register3.json()['auth_user_id']
    
    # remove fourth user
    resp_remove = requests.delete(config.url + 'admin/user/remove/v1',
                                  json = {'token': token0, 'u_id': u_id3})
    assert resp_remove.status_code == 200

    return (token0, token1, token2, token3)

@pytest.fixture
def userdata():
    user0 = {
        'u_id': 0,
        'email': 'test@gmail.com',
        'name_first': 'test',
        'name_last': 'acc',
        'handle_str': 'testacc',
        'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
    }

    user1 = {
        'u_id': 1,
        'email': 'second@user.com',
        'name_first': 'second',
        'name_last': 'user',
        'handle_str': 'seconduser',
        'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
    }

    user2 = {
        'u_id': 2,
        'email': 'third@user.com',
        'name_first': 'test',
        'name_last': 'acc',
        'handle_str': 'testacc1',
        'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
    }

    user3 = {
        'u_id': 3,
        'email': 'fourth@user.com',
        'name_first': 'Removed',
        'name_last': 'user',
        'handle_str': 'goodbye',
        'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
    }

    return (user0, user1, user2, user3)

def test_all_normal(user_tokens, userdata):
    # calls users/all/v1 with all valid tokens
    # note that the third user details should not be returned 

    # calling from token of first user
    resp_all = requests.get(config.url + 'users/all/v1',
                            params = {'token': user_tokens[0]})
    assert resp_all.status_code == 200
    assert resp_all.json() == {'users' : [userdata[0], userdata[1], userdata[2]] } 

    # calling from token of second user
    resp_all = requests.get(config.url + 'users/all/v1',
                            params = {'token': user_tokens[1]})
    assert resp_all.status_code == 200
    assert resp_all.json() ==  {'users' : [userdata[0], userdata[1], userdata[2]] } 

    # calling from token of third user
    resp_all = requests.get(config.url + 'users/all/v1',
                            params = {'token': user_tokens[2]})
    assert resp_all.status_code == 200
    assert resp_all.json() ==  {'users' : [userdata[0], userdata[1], userdata[2]] } 

def test_all_invalid_token(user_tokens):
    # calls users/all/v1 from invalid tokens
    # note that invalid tokens are not handled by user/all/v1,
    # but rather the decode_session_token function in src/tokens.py
    # this includes the handling of calling functions from removed users

    resp_all = requests.get(config.url + 'users/all/v1',
                            params = {'token': 'aaaa'})
    assert resp_all.status_code == 403 # AccessError

    resp_all = requests.get(config.url + 'users/all/v1',
                            params = {'token': 0})
    assert resp_all.status_code == 403 # AccessError

    resp_all = requests.get(config.url + 'users/all/v1',
                            params = {'token': ''})
    assert resp_all.status_code == 403 # AccessError