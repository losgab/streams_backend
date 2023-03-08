import pytest
import requests
import json
import os
from urllib.request import urlretrieve
from src import config

def test_clear_user():
    # clear
    resp_clear = requests.delete(config.url + 'clear/v1')
    assert resp_clear.status_code == 200

    # register user
    resp_register = requests.post(config.url + 'auth/register/v2',
                                  json={'email': 'test@gmail.com', 'password': 'password',
                                        'name_first': 'test', 'name_last': 'acc'})
    assert resp_register.status_code == 200

    # clear
    resp_clear = requests.delete(config.url + 'clear/v1')
    assert resp_clear.status_code == 200
    assert json.loads(resp_clear.text) == {}

    # try to login - user should no longer exist
    resp_login = requests.post(config.url + 'auth/login/v2',
                               json={'email': 'test@gmail.com', 'password': 'password'})
    assert resp_login.status_code == 400 # InputError

def test_clear_channel():
    # clear
    resp_clear = requests.delete(config.url + 'clear/v1')
    assert resp_clear.status_code == 200

    # register user
    resp_register = requests.post(config.url + 'auth/register/v2',
                                  json={'email': 'test@gmail.com', 'password': 'password',
                                        'name_first': 'test', 'name_last': 'acc'})
    assert resp_register.status_code == 200
    resp_register_data = resp_register.json()
    token_old = resp_register_data['token']

    # create channel
    resp_create_channel = requests.post(config.url + 'channels/create/v2',
                                        json={'token': token_old, 'name': 'test channel', 'is_public': True})
    assert resp_create_channel.status_code == 200
    resp_create_channel_data = resp_create_channel.json()
    channel_id = resp_create_channel_data['channel_id']

    # clear
    resp_clear = requests.delete(config.url + 'clear/v1')
    assert resp_clear.status_code == 200
    assert json.loads(resp_clear.text) == {}

    # user and channel should no longer exist

    # register user
    resp_register = requests.post(config.url + 'auth/register/v2',
                                  json={'email': 'test@gmail.com', 'password': 'password',
                                        'name_first': 'test', 'name_last': 'acc'})
    assert resp_register.status_code == 200
    resp_register_data = resp_register.json()
    token_new = resp_register_data['token']

    # user exists now but channel should not exist
    resp_messages = requests.get(config.url + 'channel/messages/v2',
                                 params={'token': token_new, 'channel_id': channel_id, 'start': 0})
    assert resp_messages.status_code == 400 # InputError
    
# Tests whether default_sushi profile picture is the only image present
def test_clear_profile_pictures():
    # Download and save a file
    urlretrieve("http://www.4ingredients.com.au/wp-content/uploads/2018/07/4I-Sushi-sml.jpg", "src/static/img0.jpg")
    assert len(os.listdir(os.getcwd() + "/src/static")) == 2
    assert "img0.jpg" in os.listdir(os.getcwd() + "/src/static")
    resp_clear = requests.delete(config.url + 'clear/v1')
    assert resp_clear.status_code == 200
    assert len(os.listdir(os.getcwd() + "/src/static")) == 1
    assert "default_sushi.jpg" in os.listdir(os.getcwd() + "/src/static")
    
