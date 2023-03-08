from src.channel import channel_details_v1, channel_join_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.other import clear_v1
from src.error import InputError, AccessError

import pytest

# Fixture that clears the data store, registers 5 users.
@pytest.fixture
def auth_registers():
    clear_v1()
    user1 = auth_register_v1('celina@domain.com', 'password', 'celina', 'shen')
    user2 =  auth_register_v1('christina@domain.com', 'password', 'christina', 'lee')
    user3 = auth_register_v1('gabriel@domain.com', 'password', 'gabriel', 'thien')
    user4 = auth_register_v1('nathan@domain.com', 'password', 'nathan', 'mu')
    user5 = auth_register_v1('cengiz@domain.com', 'password', 'cengiz', 'cimen')
    return (user1['auth_user_id'], user2['auth_user_id'], user3['auth_user_id'], user4['auth_user_id'], user5['auth_user_id'])

# # Tests channel_details_v1 with an invalid user id
# def test_channel_details_invalid_user_id():
#     clear_v1()
#     with pytest.raises(AccessError):
#         channel_details_v1(-1, -1)

# Tests channel_details_v1 with a valid user and invalid channel_id
def test_channel_details_invalid_channel_id(auth_registers):
    with pytest.raises(InputError):
        channel_details_v1(auth_registers[0], -1) 

# Tests channel_details_v1 with a valid user, but not a member of valid channel
def test_channel_details_not_member(auth_registers):
    # User Christina makes public channel 'panda'
    channel_panda_id = channels_create_v1(auth_registers[1], 'panda', True)
    with pytest.raises(AccessError):
        channel_details_v1(auth_registers[0], channel_panda_id['channel_id'])

# Tests channel_details_v1 with a valid user and valid public channel
def test_channel_details_public(auth_registers):
    # User Celina creates public channel 'bear', and store channel ID
    channel_bear_id = channels_create_v1(auth_registers[0], 'bear', True)
    # Assert channels_details_v1 functions as expected
    assert channel_details_v1(auth_registers[0], channel_bear_id['channel_id']) == {
        'name': 'bear',
        'is_public': True,
        'owner_members': [
            {
                'u_id': auth_registers[0],
                'email': 'celina@domain.com',
                'name_first': 'celina',
                'name_last': 'shen',
                'handle_str': 'celinashen',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
        'all_members': [
            {
                'u_id': auth_registers[0],
                'email': 'celina@domain.com',
                'name_first': 'celina',
                'name_last': 'shen',
                'handle_str': 'celinashen',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
    }

# Tests channel_details_v1 with a valid user and valid private channel  
def test_channel_details_private(auth_registers):
    # User Nathan creates private channel 'otter', and store channel ID
    channels_create_v1(auth_registers[3], 'bear', True)
    channel_otter_id = channels_create_v1(auth_registers[3], 'otter', False)
    # Assert channels_details_v1 functions as expected
    assert channel_details_v1(auth_registers[3], channel_otter_id['channel_id']) == {
        'name': 'otter',
        'is_public': False,
        'owner_members': [
            {
                'u_id': auth_registers[3],
                'email': 'nathan@domain.com',
                'name_first': 'nathan',
                'name_last': 'mu',
                'handle_str': 'nathanmu',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
        'all_members': [
            {
                'u_id': auth_registers[3],
                'email': 'nathan@domain.com',
                'name_first': 'nathan',
                'name_last': 'mu',
                'handle_str': 'nathanmu',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
    }

# Tests channel_details_v1 with multiple users in a public channel
def test_channel_details_multiple_members(auth_registers):
    # User Christina creates public channel 'seal', and store channel ID
    channel_seal_id = channels_create_v1(auth_registers[1], 'seal', True)
    # Users Gabriel and Cengiz join channel 'seal'
    channel_join_v1(auth_registers[2], channel_seal_id['channel_id'])
    channel_join_v1(auth_registers[4], channel_seal_id['channel_id'])
    # Assert channels_details_v1 functions as expected
    assert channel_details_v1(auth_registers[1], channel_seal_id['channel_id']) == {
        'name': 'seal',
        'is_public': True,
        'owner_members': [
            {
                'u_id': auth_registers[1],
                'email': 'christina@domain.com',
                'name_first': 'christina',
                'name_last': 'lee',
                'handle_str': 'christinalee',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
        'all_members': [
            {
                'u_id': auth_registers[1],
                'email': 'christina@domain.com',
                'name_first': 'christina',
                'name_last': 'lee',
                'handle_str': 'christinalee',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
            {
                'u_id': auth_registers[2],
                'email': 'gabriel@domain.com',
                'name_first': 'gabriel',
                'name_last': 'thien',
                'handle_str': 'gabrielthien',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            },
            {
                'u_id': auth_registers[4],
                'email': 'cengiz@domain.com',
                'name_first': 'cengiz',
                'name_last': 'cimen',
                'handle_str': 'cengizcimen',
                'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg'
            }
        ],
    }
