import pytest
import requests
import json
from src import config


@pytest.fixture
def public_channel():
    # clear, register user, create public channel

    # clear
    resp_clear = requests.delete(config.url + 'clear/v1')
    assert resp_clear.status_code == 200

    # register user
    resp_register = requests.post(config.url + 'auth/register/v2',
                                  json={'email': 'test@gmail.com', 'password': 'password',
                                        'name_first': 'test', 'name_last': 'acc'})
    assert resp_register.status_code == 200
    token = resp_register.json()['token']

    # create public channel
    resp_create_channel = requests.post(config.url + 'channels/create/v2',
                                        json={'token': token, 'name': 'test channel', 'is_public': True})
    assert resp_create_channel.status_code == 200
    channel_id = resp_create_channel.json()['channel_id']

    return {
        'owner_token': token,
        'channel_id': channel_id
    }

@pytest.fixture
def private_channel():
    # clear
    resp_clear = requests.delete(config.url + 'clear/v1')
    assert resp_clear.status_code == 200

    # register user
    resp_register = requests.post(config.url + 'auth/register/v2',
                                  json={'email': 'test@gmail.com', 'password': 'password',
                                        'name_first': 'test', 'name_last': 'acc'})
    assert resp_register.status_code == 200
    resp_register_data = resp_register.json()
    token = resp_register_data['token']

    # create private channel
    resp_create_channel = requests.post(config.url + 'channels/create/v2',
                                        json={'token': token, 'name': 'test channel', 'is_public': False})
    assert resp_create_channel.status_code == 200
    resp_create_channel_data = resp_create_channel.json()
    channel_id = resp_create_channel_data['channel_id']

    return {
        'owner_token': token,
        'channel_id': channel_id
    }

@pytest.fixture
def user_setup():
    # requests.delete(config.url + 'clear/v1')
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'gabriel@domain.com', 'password': 'password', 'name_first': 'gabriel', 'name_last': 'thien'})
    user_0 = json.loads(user_0_json.text)
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'nathan@domain.com', 'password': 'password', 'name_first': 'nathan', 'name_last': 'mu'})
    user_1 = json.loads(user_1_json.text)
    user_2_json = requests.post(config.url + 'auth/register/v2', json={'email': 'celina@domain.com', 'password': 'password', 'name_first': 'celina', 'name_last': 'shen'})
    user_2 = json.loads(user_2_json.text)
    return (user_0['token'], user_1['token'], user_2['token'], user_0['auth_user_id'], user_1['auth_user_id'], user_2['auth_user_id'])


# STATUS 400: Test using an invalid channel id (public)
def test_message_send_invalid_channel_id_public(public_channel):
    resp = requests.post(config.url + 'message/send/v1', json={
        'token': public_channel['owner_token'],
        'channel_id' : -1,
        'message' : 'This is a message!'})

    assert resp.status_code == 400

# STATUS 400: Test using an invalid channel id (private)
def test_message_send_invalid_channel_id_private(private_channel):

    resp = requests.post(config.url + 'message/send/v1', json={
        'token': private_channel['owner_token'],
        'channel_id' : -1,
        'message' : 'This is a message!'})

    assert resp.status_code == 400

# STATUS 403: Check if the user not valid (public)
def test_message_send_user_not_in_channel_public(public_channel):
    new_user = requests.post(config.url + 'auth/register/v2',
                                  json={'email': 'aeworij@gmail.com', 'password': 'password',
                                        'name_first': 'test', 'name_last': 'acc'})
    new_user_data = new_user.json()
    new_user_token = new_user_data['token']

    resp = requests.post(config.url + 'message/send/v1', json={
        'token': new_user_token,
        'channel_id' : public_channel['channel_id'],
        'message' : 'This is a message!'})

    assert resp.status_code == 403

# STATUS 403: Check if the user not valid (private)
def test_message_send_user_not_in_channel_private(private_channel):
    new_user = requests.post(config.url + 'auth/register/v2',
                                  json={'email': 'aeworij@gmail.com', 'password': 'password',
                                        'name_first': 'test', 'name_last': 'acc'})
    new_user_data = new_user.json()
    new_user_token = new_user_data['token']

    resp = requests.post(config.url + 'message/send/v1', json={
        'token': new_user_token,
        'channel_id' : private_channel['channel_id'],
        'message' : 'This is a message!'})

    assert resp.status_code == 403

# STATUS 400: If the message is too short an error is raised
def test_message_too_short(public_channel):
    resp = requests.post(config.url + 'message/send/v1', json={
        'token': public_channel['owner_token'],
        'channel_id' : public_channel['channel_id'],
        'message' : ''})
    assert resp.status_code == 400

# STATUS 400: If the message is too long an error is raised
def test_message_too_long(public_channel):
    resp = requests.post(config.url + 'message/send/v1', json={
        'token': public_channel['owner_token'],
        'channel_id' : public_channel['channel_id'],
        'message' :     "ZnZvsV%#r09xY9EZ=acwaXB2q4h*Z&tK12K7xP*gQqOG3jEG8ShOgNq0AM0DWkgx%wb9g4ysK8Jc2!@b6k=2v&Vuc6zbBRWpg#tF\
                        E9FXYUGDRA1qmt6TRhoSA!ku6u+m4m%rCYv9m#UYkRWmnSw+4x%F8WD#MVkHwrUK*fftMJj+6ogUYgON+KtsOJsABA#vpKseCaMB\
                        VKb0OAOn!7tvgcoSF6Z022GDye4ZWCD%C*zvHa*DD89OjEPdfuw1aTXuf$J&KKCH#C#u8aHyTxBbGDk5cVQaUvO0GgFRcCz5dKFY\
                        f$9ydOfzae@ ZQc8NB6FxzhRW2rEJW6wd=ZrGK0O1b@r7#CgPnKxF$We7pOe5wc1cKPF*v8SSSW=Yxt23AJwap#k&Ukd&54TWGJ$@\
                        JeOWtfU@e6nOFgf9&W*J6otWgBZbxTVcKJ@OgQ!+bT%+#wkD3X+7Y9363+%k+wdS4CW29ocoDs18utyE1P3k#QBoVcdH9oAvHgtj\
                        7@HY@VRcbH&tK1D03H7WWY4!KN$mff6YqRJp*rBm*yT9Mr$cN9dHSPQwdhfWBxn2Yyr9Qqf1g$RgmrJEhY1APrFSnQoUQm90hvPF\
                        PWj3rG2xyuMXHZbJ+QP74W92t0naUMkUB6@coKOwhddftWUGyn68rz%EsWc3U=Z3=%pbUU39*@2n@FY9&6kCz7h$=4AYQoHv6eNn\
                        sY%gk+NS*Kkh5o%&R=bQAxbXooKf#5ew&%fNd#*@W5zVn3y80fU37PsqoZg%wZHG5SEPwq5rhtTxXpnno$2XC&9Hdo4o!250TX8+\
                        *MSr@urWNQOWs*QnQOCxrFAUYNPCHO*gNTbBueS8K+&0dfmnR1CgXmjyU3w*FC%99YH2mwdobTKFQ0CEZMPXWvAO$A3VkGZZge9b\
                        fVnKAA@%WYSjuRvtD%8NQ!vWVa=@VcFxTcbqm+mx+ZY9o22BSp87DAVygexu$XoE2F1cQ8*##=YWapk=rfKw@#AcVuU05C!SO*Vu\
                        sY%gk+NS*Kkh5o%&R=bQAxbXooKf#5ew&%fNd#*@W5zVn3y80fU37PsqoZg%wZHG5SEPwq5rhtTxXpnno$2XC&9Hdo4o!250TX8+\
                        *MSr@urWNQOWs*QnQOCxrFAUYNPCHO*gNTbBueS8K+&0dfmnR1CgXmjyU3w*FC%99YH2mwdobTKFQ0CEZMPXWvAO$A3VkGZZge9b\
                        fVnKAA@%WYSjuRvtD%8NQ!vWVa=@VcFxTcbqm+mx+ZY9o22BSp87DAVygexu$XoE2F1cQ8*##=YWapk=rfKw@#AcVuU05C!SO*Vu\
                        77@JSvngPge=*dcvHzyVFhuYAJFE$vzBwvwwm7@Zr6e4xGSXe493t1p5gN=OtY&YY$eFr1fpOQRRhVUJG!B%%Qq0H=bujUV#Gyxh"
            
        })
    assert resp.status_code == 400

# STATUS 200: Message sent with no errors on private channel
def test_message_success_private(private_channel):
    resp = requests.post(config.url + 'message/send/v1', json={
        'token': private_channel['owner_token'],
        'channel_id' : private_channel['channel_id'],
        'message' : 'This is a message!!'})
    assert resp.status_code == 200

# STATUS 200: Message sent with no errors on public channel
def test_message_success_public(public_channel):
    resp = requests.post(config.url + 'message/send/v1', json={
        'token': public_channel['owner_token'],
        'channel_id' : public_channel['channel_id'],
        'message' : 'This is a message!!'})
    assert resp.status_code == 200

# STATUS 200: Several messages sent and contents observed using channel/messages/v2
def test_message_send_channel_messages_success(public_channel, user_setup):
    # Message sent by owner
    resp = requests.post(config.url + 'message/send/v1', json={
        'token': public_channel['owner_token'],
        'channel_id' : public_channel['channel_id'],
        'message' : 'This is a message!!'})
    assert resp.status_code == 200
    
    # Message sent by owner
    resp = requests.post(config.url + 'message/send/v1', json={
        'token': public_channel['owner_token'],
        'channel_id' : public_channel['channel_id'],
        'message' : 'This is another message!!'})
    assert resp.status_code == 200

    # Message sent by owner
    resp = requests.post(config.url + 'message/send/v1', json={
        'token': public_channel['owner_token'],
        'channel_id' : public_channel['channel_id'],
        'message' : 'This is an another another message!!'})
    assert resp.status_code == 200
    
    # Request for list of messages on channel
    resp_messages = requests.get(config.url + 'channel/messages/v2',
                                 params={'token': public_channel['owner_token'],
                                         'channel_id': public_channel['channel_id'],
                                      'start': 0})

    # Assert contents of channel match messages taht were sent
    assert resp_messages.status_code == 200
    assert resp_messages.json()['messages'][2]['message'] == "This is a message!!"
    assert resp_messages.json()['messages'][1]['message'] == "This is another message!!"
    assert resp_messages.json()['messages'][0]['message'] == "This is an another another message!!"
    assert resp_messages.json()['end'] == -1
    # Clear data
    requests.delete(config.url + 'clear/v1')