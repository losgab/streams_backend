import requests
import pytest

from src import config

# Fixture that clears the data store 
@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1')

# Fixture that registers 3 users. returns their tokens and u_ids
@pytest.fixture
def user_setup():
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'gabriel@domain.com', 'password': 'password', 'name_first': 'gabriel', 'name_last': 'thien'})
    user_1_json = requests.post(config.url + 'auth/register/v2', json={'email': 'cengiz@domain.com', 'password': 'password', 'name_first': 'cengiz', 'name_last': 'cimen'})
    user_2_json = requests.post(config.url + 'auth/register/v2', json={'email': 'nathan@domain.com', 'password': 'password', 'name_first': 'nathan', 'name_last': 'mu'})
    return {
        'user0_token': user_0_json.json()['token'],
        'user1_token': user_1_json.json()['token'],
        'user2_token': user_2_json.json()['token'],
        'user0_id': user_0_json.json()['auth_user_id'],
        'user1_id': user_1_json.json()['auth_user_id'],
        'user2_id': user_2_json.json()['auth_user_id'],
    }

# Fixture that creates two test channels, one public and one private 
@pytest.fixture
def channel_setup(user_setup):
    # gabbo creates public channel
    channel0_data = requests.post(config.url + 'channels/create/v2',json={'token': user_setup['user0_token'], 'name': 'public test channel', 'is_public': True})
    # cengiz creates private channel
    channel1_data = requests.post(config.url + 'channels/create/v2',json={'token': user_setup['user1_token'], 'name': 'private test channel', 'is_public': False})
    return {
        'channel0_id': channel0_data.json()['channel_id'],
        'channel1_id': channel1_data.json()['channel_id']
    }
    
# Two test DMs, Gabriel - Cengiz, Cengiz - Nathan
@pytest.fixture
def dm_setup(user_setup):
    # gabbo dms cengiz and nathan
    dm0_data = requests.post(config.url + 'dm/create/v1',json={'token': user_setup['user0_token'], 'u_ids': [user_setup['user1_id'], user_setup['user2_id']]})
    return {
        'dm0_id': dm0_data.json()['dm_id']
    }

# Tests whether notifications are generated when user is no longer in a channel
# Could be from their own message or in a tagged message
def test_user_not_in_channeldm(clear, user_setup, channel_setup, dm_setup):
    # Cengiz & nathan join gabbos channel
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel0_id']})
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup['user2_token'], 'channel_id': channel_setup['channel0_id']})
    # Cengiz sends a message to channel and dm
    message0_data = requests.post(config.url + 'message/send/v1', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel0_id'], 'message': 'poo poo'})
    message1_data = requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user1_token'], 'dm_id': dm_setup['dm0_id'], 'message': 'poo poo'})
    # Gabbo reacts to it
    requests.post(config.url + 'message/react/v1', json={'token': user_setup['user0_token'], 'message_id': message0_data.json()['message_id'], 'react_id': 1})
    requests.post(config.url + 'message/react/v1', json={'token': user_setup['user0_token'], 'message_id': message1_data.json()['message_id'], 'react_id': 1})
    # Cengiz gets notifications, should see gabbos reaction x2
    notif_data = requests.get(config.url + 'notifications/get/v1', params={'token': user_setup['user1_token']})
    assert notif_data.status_code == 200
    assert len(notif_data.json()['notifications']) == 3
    assert notif_data.json()['notifications'][:-1] == [
        {
            'channel_id': -1,
            'dm_id': dm_setup['dm0_id'],
            'notification_message': 'gabrielthien reacted to your message in cengizcimen, gabrielthien, nathanmu'
        },{
            'channel_id': channel_setup['channel0_id'],
            'dm_id': -1,
            'notification_message': 'gabrielthien reacted to your message in public test channel'
        }
    ]
    # Cengiz leaves the channel
    requests.post(config.url + 'channel/leave/v1', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel0_id']})
    requests.post(config.url + 'dm/leave/v1', json={'token': user_setup['user1_token'], 'dm_id': dm_setup['dm0_id']})
    # Nathan reacts to the messages
    requests.post(config.url + 'message/react/v1', json={'token': user_setup['user2_token'], 'message_id': message0_data.json()['message_id'], 'react_id': 1})
    requests.post(config.url + 'message/react/v1', json={'token': user_setup['user2_token'], 'message_id': message1_data.json()['message_id'], 'react_id': 1})
    # Gabbo tags cengiz in both channel and dm
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user0_token'], 'channel_id': channel_setup['channel0_id'], 'message': '@cengizcimen'})
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user0_token'], 'dm_id': dm_setup['dm0_id'], 'message': '@cengizcimen'})
    # Cengiz gets notifications, should see no difference
    notif_data = requests.get(config.url + 'notifications/get/v1', params={'token': user_setup['user1_token']})
    assert notif_data.status_code == 200
    assert len(notif_data.json()['notifications']) == 3 # No new notifications should have been added

# Tests whether only 1 notification is generated when user is tagged multiple times in a single message
def test_multiple_tags_onenotif(clear, user_setup, channel_setup, dm_setup):
    # Cengiz join gabbos channel
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel0_id']})
    # Gabbo sends a message into the channel and dm tagging cengiz three times
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user0_token'], 'channel_id': channel_setup['channel0_id'], 'message': '@cengizcimen how u doing @cengizcimen @cengizcimen'})
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user0_token'], 'dm_id': dm_setup['dm0_id'], 'message': '@cengizcimen how u doing @cengizcimen @cengizcimen'})
    # Cengiz gets notifications, should see only two related notifs, one each for the channel and dm
    notif_data = requests.get(config.url + 'notifications/get/v1', params={'token': user_setup['user1_token']})
    assert notif_data.status_code == 200
    assert len(notif_data.json()['notifications']) == 3
    assert notif_data.json()['notifications'][:-1] == [
        {
            'channel_id': -1,
            'dm_id': dm_setup['dm0_id'],
            'notification_message': 'gabrielthien tagged you in cengizcimen, gabrielthien, nathanmu: @cengizcimen how u d'
        },{
            'channel_id': channel_setup['channel0_id'],
            'dm_id': -1,
            'notification_message': 'gabrielthien tagged you in public test channel: @cengizcimen how u d'
        } 
    ]

# Tests when multiple users are tagged in a post, whether all of them receive a notification
def test_multiple_tags_notify_each_user(clear, user_setup, channel_setup, dm_setup):
    # Cengiz & nathan join gabbos channel
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel0_id']})
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup['user2_token'], 'channel_id': channel_setup['channel0_id']})
    # Gabbo tags both nathan and cengiz in a message in a channel and dm
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user0_token'], 'channel_id': channel_setup['channel0_id'], 'message': '@cengizcimen @nathanmu how we doing'})
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user0_token'], 'dm_id': dm_setup['dm0_id'], 'message': '@cengizcimen @nathanmu how we doing'})
    # Cengiz gets notifications and should see the tags
    notif_data = requests.get(config.url + 'notifications/get/v1', params={'token': user_setup['user1_token']})
    assert notif_data.status_code == 200
    assert len(notif_data.json()['notifications']) == 3
    assert notif_data.json()['notifications'][:-1] == [
        {
            'channel_id': -1,
            'dm_id': dm_setup['dm0_id'],
            'notification_message': 'gabrielthien tagged you in cengizcimen, gabrielthien, nathanmu: @cengizcimen @nathan'
        },{
            'channel_id': channel_setup['channel0_id'],
            'dm_id': -1,
            'notification_message': 'gabrielthien tagged you in public test channel: @cengizcimen @nathan'
        }
    ]
    # Nathan gets notifications and should also see the tags
    notif_data = requests.get(config.url + 'notifications/get/v1', params={'token': user_setup['user2_token']})
    assert notif_data.status_code == 200
    assert len(notif_data.json()['notifications']) == 3
    assert notif_data.json()['notifications'][:-1] == [
        {
            'channel_id': -1,
            'dm_id': dm_setup['dm0_id'],
            'notification_message': 'gabrielthien tagged you in cengizcimen, gabrielthien, nathanmu: @cengizcimen @nathan'
        },{
            'channel_id': channel_setup['channel0_id'],
            'dm_id': -1,
            'notification_message': 'gabrielthien tagged you in public test channel: @cengizcimen @nathan'
        }
    ]

# Tests whether unreacting a message affects the original notification
def test_reaction_notification_persistence(clear, user_setup, channel_setup, dm_setup):
    # Cengiz join gabbos channel
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel0_id']})
    # Cengiz sends a message in the channel
    message0_data = requests.post(config.url + 'message/send/v1', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel0_id'], 'message': 'poo poo'})
    message1_data = requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user1_token'], 'dm_id': dm_setup['dm0_id'], 'message': 'poo poo'})
    # Gabbo reacts to it
    requests.post(config.url + 'message/react/v1', json={'token': user_setup['user0_token'], 'message_id': message0_data.json()['message_id'], 'react_id': 1})
    requests.post(config.url + 'message/react/v1', json={'token': user_setup['user0_token'], 'message_id': message1_data.json()['message_id'], 'react_id': 1})
    # Cengiz gets notifications, should see only see two react notifications
    notif_data = requests.get(config.url + 'notifications/get/v1', params={'token': user_setup['user1_token']})
    assert notif_data.status_code == 200
    assert len(notif_data.json()['notifications']) == 3
    assert notif_data.json()['notifications'][:-1] == [
        {
            'channel_id': -1,
            'dm_id': dm_setup['dm0_id'],
            'notification_message': 'gabrielthien reacted to your message in cengizcimen, gabrielthien, nathanmu'
        },{
            'channel_id': channel_setup['channel0_id'],
            'dm_id': -1,
            'notification_message': 'gabrielthien reacted to your message in public test channel'
        }
    ]
    # Gabbo unreacts
    requests.post(config.url + 'message/unreact/v1', json={'token': user_setup['user0_token'], 'message_id': message0_data.json()['message_id'], 'react_id': 1})
    requests.post(config.url + 'message/unreact/v1', json={'token': user_setup['user0_token'], 'message_id': message1_data.json()['message_id'], 'react_id': 1})
    # Cengiz gets notifications, should still see only the two original tags
    notif_data = requests.get(config.url + 'notifications/get/v1', params={'token': user_setup['user1_token']})
    assert notif_data.status_code == 200
    assert len(notif_data.json()['notifications']) == 3

# Tests whether editing a message with a tag for a user affects original notification
def test_tag_notification_persistence(clear, user_setup, channel_setup, dm_setup):
    # Cengiz join gabbos channel
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel0_id']})
    # Gabbo sends a message and tags cengiz
    message0_data = requests.post(config.url + 'message/send/v1', json={'token': user_setup['user0_token'], 'channel_id': channel_setup['channel0_id'], 'message': '@cengizcimen how u doing'})
    message1_data = requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user0_token'], 'dm_id': dm_setup['dm0_id'], 'message': '@cengizcimen how u doing'})
    # Cengiz gets notifications, should see two tags
    notif_data = requests.get(config.url + 'notifications/get/v1', params={'token': user_setup['user1_token']})
    assert notif_data.status_code == 200
    assert len(notif_data.json()['notifications']) == 3
    assert notif_data.json()['notifications'][:-1] == [
        {
            'channel_id': -1,
            'dm_id': dm_setup['dm0_id'],
            'notification_message': 'gabrielthien tagged you in cengizcimen, gabrielthien, nathanmu: @cengizcimen how u d'
        },{
            'channel_id': channel_setup['channel0_id'],
            'dm_id': -1,
            'notification_message': 'gabrielthien tagged you in public test channel: @cengizcimen how u d'
        }
    ]
    # Gabbo edits the message to not include cengiz's tag 
    requests.put(config.url + 'message/edit/v1', json={'token': user_setup['user0_token'], 'message_id': message0_data.json()['message_id'], 'message': 'how we doing'})
    requests.put(config.url + 'message/edit/v1', json={'token': user_setup['user0_token'], 'message_id': message1_data.json()['message_id'], 'message': 'how we doing'})
    # Cengiz gets notifications, should still see only one
    notif_data = requests.get(config.url + 'notifications/get/v1', params={'token': user_setup['user1_token']})
    assert notif_data.status_code == 200
    assert len(notif_data.json()['notifications']) == 3

# Tests whether removing a message containing a tag affects original notification
def test_tag_message_removed_persistence(clear, user_setup, channel_setup, dm_setup):
    # Cengiz join gabbos channel
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel0_id']})
    # Gabbo sends a message and tags cengiz
    message0_data = requests.post(config.url + 'message/send/v1', json={'token': user_setup['user0_token'], 'channel_id': channel_setup['channel0_id'], 'message': '@cengizcimen how u doing'})
    message1_data = requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user0_token'], 'dm_id': dm_setup['dm0_id'], 'message': '@cengizcimen how u doing'})
    # Cengiz gets notifications, should see two tags
    notif_data = requests.get(config.url + 'notifications/get/v1', params={'token': user_setup['user1_token']})
    assert notif_data.status_code == 200
    assert len(notif_data.json()['notifications']) == 3
    assert notif_data.json()['notifications'][:-1] == [
        {
            'channel_id': -1,
            'dm_id': dm_setup['dm0_id'],
            'notification_message': 'gabrielthien tagged you in cengizcimen, gabrielthien, nathanmu: @cengizcimen how u d'
        },{
            'channel_id': channel_setup['channel0_id'],
            'dm_id': -1,
            'notification_message': 'gabrielthien tagged you in public test channel: @cengizcimen how u d'
        }
    ]
    # Gabbo removes the message
    requests.delete(config.url + 'message/remove/v1', json={'token': user_setup['user0_token'], 'message_id': message0_data.json()['message_id']})
    requests.delete(config.url + 'message/remove/v1', json={'token': user_setup['user0_token'], 'message_id': message1_data.json()['message_id']})
    # Cengiz gets notifications, should still see original tags
    notif_data = requests.get(config.url + 'notifications/get/v1', params={'token': user_setup['user1_token']})
    assert notif_data.status_code == 200
    assert len(notif_data.json()['notifications']) == 3

# Tests whether a message containing a tag is edited to still contain a tag generates a new notification
def test_tag_message_edited_same_tag(clear, user_setup, channel_setup, dm_setup):
    # Cengiz join gabbos channel
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel0_id']})
    # Gabbo sends a message and tags cengiz
    message0_data = requests.post(config.url + 'message/send/v1', json={'token': user_setup['user0_token'], 'channel_id': channel_setup['channel0_id'], 'message': '@cengizcimen how u doing'})
    message1_data = requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user0_token'], 'dm_id': dm_setup['dm0_id'], 'message': '@cengizcimen how u doing'})
    # Cengiz gets notifications, should see the two tags
    notif_data = requests.get(config.url + 'notifications/get/v1', params={'token': user_setup['user1_token']})
    assert notif_data.status_code == 200
    assert len(notif_data.json()['notifications']) == 3
    assert notif_data.json()['notifications'][:-1] == [
        {
            'channel_id': -1,
            'dm_id': dm_setup['dm0_id'],
            'notification_message': 'gabrielthien tagged you in cengizcimen, gabrielthien, nathanmu: @cengizcimen how u d'
        },{
            'channel_id': channel_setup['channel0_id'],
            'dm_id': -1,
            'notification_message': 'gabrielthien tagged you in public test channel: @cengizcimen how u d'
        }
    ]
    # Gabbo edits the message to still tag cengiz 
    requests.put(config.url + 'message/edit/v1', json={'token': user_setup['user0_token'], 'message_id': message0_data.json()['message_id'], 'message': '@cengizcimen i asked bitch @cengizcimen'})
    requests.put(config.url + 'message/edit/v1', json={'token': user_setup['user0_token'], 'message_id': message1_data.json()['message_id'], 'message': '@cengizcimen i asked bitch @cengizcimen'})
    # Cengiz gets notifications, should still see see original two tags
    notif_data = requests.get(config.url + 'notifications/get/v1', params={'token': user_setup['user1_token']})
    assert notif_data.status_code == 200
    assert len(notif_data.json()['notifications']) == 3

# Tests whether a notification is generated when a message is edited to contain a tag
def test_tag_message_edited_new_tag(clear, user_setup, channel_setup, dm_setup):
    # Cengiz join gabbos channel
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel0_id']})
    # Gabbo sends a message into the channel
    message0_data = requests.post(config.url + 'message/send/v1', json={'token': user_setup['user0_token'], 'channel_id': channel_setup['channel0_id'], 'message': 'how we doing'})
    message1_data = requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user0_token'], 'dm_id': dm_setup['dm0_id'], 'message': 'how we doing'})
    # Cengiz gets notifications, should see no tags
    notif_data = requests.get(config.url + 'notifications/get/v1', params={'token': user_setup['user1_token']})
    assert notif_data.status_code == 200
    assert len(notif_data.json()['notifications']) == 1
    # Gabbo edits the message to tag cengiz
    requests.put(config.url + 'message/edit/v1', json={'token': user_setup['user0_token'], 'message_id': message0_data.json()['message_id'], 'message': '@cengizcimen how u doing'})
    requests.put(config.url + 'message/edit/v1', json={'token': user_setup['user0_token'], 'message_id': message1_data.json()['message_id'], 'message': '@cengizcimen how u doing'})
    # Cengiz gets notifications, should see new notifications
    notif_data = requests.get(config.url + 'notifications/get/v1', params={'token': user_setup['user1_token']})
    assert notif_data.status_code == 200
    assert len(notif_data.json()['notifications']) == 3
    assert notif_data.json()['notifications'][:-1] == [
        {
            'channel_id': -1,
            'dm_id': dm_setup['dm0_id'],
            'notification_message': 'gabrielthien tagged you in cengizcimen, gabrielthien, nathanmu: @cengizcimen how u d'
        },{
            'channel_id': channel_setup['channel0_id'],
            'dm_id': -1,
            'notification_message': 'gabrielthien tagged you in public test channel: @cengizcimen how u d'
        }
    ]

# Tests a range of valid/invalid tagging (tagging recognition)
def test_valid_tagging_recognition(clear, user_setup, channel_setup, dm_setup):
    # Cengiz join gabbos channel
    requests.post(config.url + 'channel/join/v2', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel0_id']})
    # Gabbo sends messages into the channel
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user0_token'], 'channel_id': channel_setup['channel0_id'], 'message': '@cengizcimen how we doing'}) # YES
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user0_token'], 'channel_id': channel_setup['channel0_id'], 'message': '@cengizcimen@cengizcimen@cengizcimen bruh'}) # YES
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user0_token'], 'channel_id': channel_setup['channel0_id'], 'message': '@cengizcimen?'}) # YES
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user0_token'], 'channel_id': channel_setup['channel0_id'], 'message': '@cengizcimenbruh'})
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user0_token'], 'channel_id': channel_setup['channel0_id'], 'message': 'hi@cengizcimen'}) # YES
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user0_token'], 'channel_id': channel_setup['channel0_id'], 'message': 'hi@cengizcimenhi'})
    # Gabbo sends messages into the dm
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user0_token'], 'dm_id': dm_setup['dm0_id'], 'message': '@cengizcimen how we doing'}) # YES
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user0_token'], 'dm_id': dm_setup['dm0_id'], 'message': '@cengizcimen@cengizcimen@cengizcimen bruh'}) # YES
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user0_token'], 'dm_id': dm_setup['dm0_id'], 'message': '@cengizcimen?'}) # YES
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user0_token'], 'dm_id': dm_setup['dm0_id'], 'message': '@cengizcimenbruh'})
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user0_token'], 'dm_id': dm_setup['dm0_id'], 'message': 'hi@cengizcimen'}) # YES
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user0_token'], 'dm_id': dm_setup['dm0_id'], 'message': 'hi@cengizcimenhi'})
    # Cengiz gets notifications, should see 8 tags
    notif_data = requests.get(config.url + 'notifications/get/v1', params={'token': user_setup['user1_token']})
    assert notif_data.status_code == 200
    assert len(notif_data.json()['notifications']) == 9
    assert notif_data.json()['notifications'][:-1] == [
        {
            'channel_id': -1,
            'dm_id': dm_setup['dm0_id'],
            'notification_message': 'gabrielthien tagged you in cengizcimen, gabrielthien, nathanmu: hi@cengizcimen'
        },{
            'channel_id': -1,
            'dm_id': dm_setup['dm0_id'],
            'notification_message': 'gabrielthien tagged you in cengizcimen, gabrielthien, nathanmu: @cengizcimen?'
        },{
            'channel_id': -1,
            'dm_id': dm_setup['dm0_id'],
            'notification_message': 'gabrielthien tagged you in cengizcimen, gabrielthien, nathanmu: @cengizcimen@cengizc'
        },{
            'channel_id': -1,
            'dm_id': dm_setup['dm0_id'],
            'notification_message': 'gabrielthien tagged you in cengizcimen, gabrielthien, nathanmu: @cengizcimen how we '
        },{
            'channel_id': channel_setup['channel0_id'],
            'dm_id': -1,
            'notification_message': 'gabrielthien tagged you in public test channel: hi@cengizcimen'
        },{
            'channel_id': channel_setup['channel0_id'],
            'dm_id': -1,
            'notification_message': 'gabrielthien tagged you in public test channel: @cengizcimen?'
        },{
            'channel_id': channel_setup['channel0_id'],
            'dm_id': -1,
            'notification_message': 'gabrielthien tagged you in public test channel: @cengizcimen@cengizc'
        },{
            'channel_id': channel_setup['channel0_id'],
            'dm_id': -1,
            'notification_message': 'gabrielthien tagged you in public test channel: @cengizcimen how we '
        }
    ]

# Tests whether reacting to own message will generate a notification for the owner of message
def test_react_own_message(clear, user_setup, channel_setup, dm_setup):
    # Gabbo sends a message into the channel and dm
    message0_data = requests.post(config.url + 'message/send/v1', json={'token': user_setup['user0_token'], 'channel_id': channel_setup['channel0_id'], 'message': 'how we doing'})
    message1_data = requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user0_token'], 'dm_id': dm_setup['dm0_id'], 'message': 'how we doing'})
    # Gabbo reacts to own messages
    requests.post(config.url + 'message/react/v1', json={'token': user_setup['user0_token'], 'message_id': message0_data.json()['message_id'], 'react_id': 1})
    requests.post(config.url + 'message/react/v1', json={'token': user_setup['user0_token'], 'message_id': message1_data.json()['message_id'], 'react_id': 1})
    # Gabbo gets notifications and should not see a react notification
    notif_data = requests.get(config.url + 'notifications/get/v1', params={'token': user_setup['user0_token']})
    assert notif_data.status_code == 200
    assert len(notif_data.json()['notifications']) == 1

# Tests whether tagging yourself in a message will generate a notification for the owner of message
# It should yes, ASSUMPTION: since its present in discord and microsoft teams
def test_self_tag(clear, user_setup, channel_setup, dm_setup):
    # Gabbo sends a message into the channel
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user0_token'], 'channel_id': channel_setup['channel0_id'], 'message': '@gabrielthien how we doing'})
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user0_token'], 'dm_id': dm_setup['dm0_id'], 'message': '@gabrielthien how we doing'})
    # Gabbo gets notifications and should see both tag notifications
    notif_data = requests.get(config.url + 'notifications/get/v1', params={'token': user_setup['user0_token']})
    assert notif_data.status_code == 200
    assert len(notif_data.json()['notifications']) == 3
    assert notif_data.json()['notifications'][:-1] == [
        {
            'channel_id': -1,
            'dm_id': dm_setup['dm0_id'],
            'notification_message': 'gabrielthien tagged you in cengizcimen, gabrielthien, nathanmu: @gabrielthien how we'
        },{
            'channel_id': channel_setup['channel0_id'],
            'dm_id': -1,
            'notification_message': 'gabrielthien tagged you in public test channel: @gabrielthien how we'
        }
    ]

# Tests success case for the three types of notifications
def test_triple_success_case(clear, user_setup, channel_setup, dm_setup):
    # Gabbo invites cengiz to his channel
    requests.post(config.url + 'channel/invite/v2', json={'token': user_setup['user0_token'], 'channel_id': channel_setup['channel0_id'], 'u_id': user_setup['user1_id']})
    # Gabbo sends a message into dm and channel and tags cengiz
    requests.post(config.url + 'message/send/v1', json={'token': user_setup['user0_token'], 'channel_id': channel_setup['channel0_id'], 'message': '@cengizcimen how u doing'})
    requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user0_token'], 'dm_id': dm_setup['dm0_id'], 'message': '@cengizcimen how u doing'})
    # Cengiz sends a message into the channel and dm
    message0_data = requests.post(config.url + 'message/send/v1', json={'token': user_setup['user1_token'], 'channel_id': channel_setup['channel0_id'], 'message': 'im good bro'})
    message1_data = requests.post(config.url + 'message/senddm/v1', json={'token': user_setup['user1_token'], 'dm_id': dm_setup['dm0_id'], 'message': 'im good bro'})
    # Gabbo reacts to the message in the channel
    requests.post(config.url + 'message/react/v1', json={'token': user_setup['user0_token'], 'message_id': message0_data.json()['message_id'], 'react_id': 1})
    requests.post(config.url + 'message/react/v1', json={'token': user_setup['user0_token'], 'message_id': message1_data.json()['message_id'], 'react_id': 1})
    # Cengiz gets notifications, should see six
    notif_data = requests.get(config.url + 'notifications/get/v1', params={'token': user_setup['user1_token']})
    assert notif_data.status_code == 200
    assert len(notif_data.json()['notifications']) == 6
    assert notif_data.json()['notifications'] == [
        {
            'channel_id': -1,
            'dm_id': dm_setup['dm0_id'],
            'notification_message': 'gabrielthien reacted to your message in cengizcimen, gabrielthien, nathanmu'
        },{
            'channel_id': channel_setup['channel0_id'],
            'dm_id': -1,
            'notification_message': 'gabrielthien reacted to your message in public test channel'
        },{
            'channel_id': -1,
            'dm_id': dm_setup['dm0_id'],
            'notification_message': 'gabrielthien tagged you in cengizcimen, gabrielthien, nathanmu: @cengizcimen how u d'
        },{
            'channel_id': channel_setup['channel0_id'],
            'dm_id': -1,
            'notification_message': 'gabrielthien tagged you in public test channel: @cengizcimen how u d'
        },{
            'channel_id': channel_setup['channel0_id'],
            'dm_id': -1,
            'notification_message': 'gabrielthien added you to public test channel'
        },{
            'channel_id': -1,
            'dm_id': dm_setup['dm0_id'],
            'notification_message': 'gabrielthien added you to cengizcimen, gabrielthien, nathanmu'
        }
]