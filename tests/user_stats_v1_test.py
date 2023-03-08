import pytest
import requests
from src import config

# Fixture that clears the data store 
@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1')

# Fixture that registers 3 users. returns their tokens and u_ids
@pytest.fixture
def user_setup():
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'gabriel@domain.com', 'password': 'password', 'name_first': 'gabriel', 'name_last': 'thien'})
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'christina@domain.com', 'password': 'password', 'name_first': 'christina', 'name_last': 'lee'})
    user_2_json = requests.post(config.url + 'auth/register/v2', json={'email': 'celina@domain.com', 'password': 'password', 'name_first': 'celina', 'name_last': 'shen'})
    return {
        'user0_token': user_0_json.json()['token'],
        'user1_token': user_1_json.json()['token'],
        'user2_token': user_2_json.json()['token'],
        'user0_id': user_0_json.json()['auth_user_id'],
        'user1_id': user_1_json.json()['auth_user_id'],
        'user2_id': user_2_json.json()['auth_user_id'],
    }

# Fixture that creates two test channels, both public
@pytest.fixture
def channel_setup(user_setup):
    # gabbo creates public channel
    channel0_data = requests.post(config.url + 'channels/create/v2',json={'token': user_setup['user0_token'], 'name': 'public test channel0', 'is_public': True})
    # christina creates public channel
    channel1_data = requests.post(config.url + 'channels/create/v2',json={'token': user_setup['user1_token'], 'name': 'public test channel1', 'is_public': True})
    return {
        'channel0_id': channel0_data.json()['channel_id'],
        'channel1_id': channel1_data.json()['channel_id']
    }

# Two test DMs, Gabriel - Christina, Christina - Celina
@pytest.fixture
def dm_setup(user_setup):
    # gabbo dms christina
    dm0_data = requests.post(config.url + 'dm/create/v1',json={'token': user_setup['user0_token'], 'u_ids': [user_setup['user1_id']]})
    # christina dms celina
    dm1_data = requests.post(config.url + 'dm/create/v1',json={'token': user_setup['user1_token'], 'u_ids': [user_setup['user2_id']]})
    return {
        'dm0_id': dm0_data.json()['dm_id'],
        'dm1_id': dm1_data.json()['dm_id']
    }

# Tests for success case
def test_success_case(clear, user_setup, channel_setup, dm_setup):
    # Prep work
    # Celina joins Gabbo's channel (Gabbo & Celina)
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup['user2_token'], 'channel_id': channel_setup['channel0_id']})
    # Celina joins Christina's channel (Christina & Celina)
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup['user2_token'], 'channel_id': channel_setup['channel1_id']})
    # Sending some spam
    # Gabbo sends one message in dm to Christina (1)
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user0_token'], 'dm_id': dm_setup['dm0_id'], 'message': 'message to christina'})
    stat_data = requests.get(config.url + "user/stats/v1", params={'token': user_setup['user1_token']})
    assert stat_data.status_code == 200
    # Christina sends one message to each dm and one to channel (3)
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel1_id'], 'message': 'channel message2'})
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user1_token'], 'dm_id': dm_setup['dm1_id'], 'message': 'dm to celina0'})
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user1_token'], 'dm_id': dm_setup['dm1_id'], 'message': 'dm to celina1'})
    # Celina sends one message to each channel and one to dm  (3)
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user2_token'], 'channel_id': channel_setup['channel0_id'], 'message': 'channel message0'})
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user2_token'], 'channel_id': channel_setup['channel1_id'], 'message': 'channel message1'})
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user2_token'], 'dm_id': dm_setup['dm1_id'], 'message': 'dm to christina'})
    # Should be 3 messages in Christina - Celina DM, 1 in Gabbo - Christina DM, 1 in Gabbo Channel, 2 in Christina channel
    # Gabbo gets his stats
    stat_data = requests.get(config.url + "user/stats/v1", params={'token': user_setup['user0_token']})
    assert stat_data.status_code == 200
    # START
    assert stat_data.json()['user_stats']['channels_joined'][0]['num_channels_joined'] == 0
    assert stat_data.json()['user_stats']['dms_joined'][0]['num_dms_joined'] == 0
    assert stat_data.json()['user_stats']['messages_sent'][0]['num_messages_sent'] == 0
    assert stat_data.json()['user_stats']['involvement_rate'] == 0
    # Gabbo created a channel
    assert stat_data.json()['user_stats']['channels_joined'][-1]['num_channels_joined'] == 1
    # Gabbo created a dm
    assert stat_data.json()['user_stats']['dms_joined'][-1]['num_dms_joined'] == 1
    # Gabbo's last message
    assert stat_data.json()['user_stats']['messages_sent'][-1]['num_messages_sent'] == 1
    # Gabbo's involvement rate
    assert stat_data.json()['user_stats']['involvement_rate'] == float(3 / 11)
    # Christina gets her stats
    # START
    assert stat_data.json()['user_stats']['channels_joined'][0]['num_channels_joined'] == 0
    assert stat_data.json()['user_stats']['dms_joined'][0]['num_dms_joined'] == 0
    assert stat_data.json()['user_stats']['messages_sent'][0]['num_messages_sent'] == 0
    assert stat_data.json()['user_stats']['involvement_rate'] == 0
    # Christina created a channel
    assert stat_data.json()['user_stats']['channels_joined'][-1]['num_channels_joined'] == 1
    # Christina creates and joins a dm
    assert stat_data.json()['user_stats']['dms_joined'][-1]['num_dms_joined'] == 2
    # Christina's last message
    assert stat_data.json()['user_stats']['messages_sent'][-1]['num_messages_sent'] == 3
    # Christina's involvement rate
    assert stat_data.json()['user_stats']['involvement_rate'] == float
    # Celina gets her stats
    stat_data = requests.get(config.url + "user/stats/v1", params={'token': user_setup['user2_token']})
    assert stat_data.status_code == 200
    # START
    assert stat_data.json()['user_stats']['channels_joined'][0]['num_channels_joined'] == 0
    assert stat_data.json()['user_stats']['dms_joined'][0]['num_dms_joined'] == 0
    assert stat_data.json()['user_stats']['messages_sent'][0]['num_messages_sent'] == 0
    assert stat_data.json()['user_stats']['involvement_rate'] == 0
    # Celina joins a channel
    assert stat_data.json()['user_stats']['channels_joined'][-1]['num_channels_joined'] == 1
    # Celina is dmed
    assert stat_data.json()['user_stats']['dms_joined'][-1]['num_dms_joined'] == 1
    # Celina's last message
    assert stat_data.json()['user_stats']['messages_sent'][-1]['num_messages_sent'] == 3
    # Celina's involvement rate
    assert stat_data.json()['user_stats']['involvement_rate'] == float
 
def test_success_zero(clear, user_setup):
   # Gabbo gets his stats
    stat_data = requests.get(config.url + "user/stats/v1", params={'token': user_setup['user0_token']})
    assert stat_data.status_code == 200
    assert stat_data.json()['user_stats']['channels_joined'][0]['num_channels_joined'] == 0
    assert stat_data.json()['user_stats']['dms_joined'][0]['num_dms_joined'] == 0
    assert stat_data.json()['user_stats']['messages_sent'][0]['num_messages_sent'] == 0
    assert stat_data.json()['user_stats']['involvement_rate'] == 0
   # Christina gets her stats
    stat_data = requests.get(config.url + "user/stats/v1", params={'token': user_setup['user1_token']})
    assert stat_data.status_code == 200
    assert stat_data.json()['user_stats']['channels_joined'][0]['num_channels_joined'] == 0
    assert stat_data.json()['user_stats']['dms_joined'][0]['num_dms_joined'] == 0
    assert stat_data.json()['user_stats']['messages_sent'][0]['num_messages_sent'] == 0
    assert stat_data.json()['user_stats']['involvement_rate'] == 0
   # Celina gets her stats
    stat_data = requests.get(config.url + "user/stats/v1", params={'token': user_setup['user2_token']})
    assert stat_data.status_code == 200
    assert stat_data.json()['user_stats']['channels_joined'][0]['num_channels_joined'] == 0
    assert stat_data.json()['user_stats']['dms_joined'][0]['num_dms_joined'] == 0
    assert stat_data.json()['user_stats']['messages_sent'][0]['num_messages_sent'] == 0
    assert stat_data.json()['user_stats']['involvement_rate'] == 0