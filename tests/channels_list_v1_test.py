import pytest 

from src.data_store import data_store
from src.other import clear_v1
from src.auth import auth_login_v1, auth_register_v1
from src.error import AccessError
from src.channels import channels_list_v1, channels_listall_v1, channels_create_v1
from src.channel import channel_invite_v1, channel_join_v1

# Register some users first
# Create some channels first

def test_allchannels_public(): #channels_list_v1
    # List of all channels created, only public
    clear_v1()
    auth_register_v1('cengiz@gmail.com', 'password', 'cengiz', 'cimen')
    u_id = auth_register_v1('gabbo@gmail.com', 'password', 'gabriel', 'thien')['auth_user_id']
    channels_create_v1(u_id, 'gabbos couch', True) # Public
    assert channels_list_v1(u_id) == { 
        'channels' : [
            {
                'channel_id': 0,
                'name': 'gabbos couch', 
            }
        ]
    }

def test_all_nochannels(): # All of 0 channels should be visible since 0 channels were created
    clear_v1()
    auth_register_v1('cengiz@gmail.com', 'password', 'cengiz', 'cimen') 
    auth_register_v1('gabbo@gmail.com', 'password', 'gabriel', 'thien')
    assert channels_list_v1(auth_login_v1('cengiz@gmail.com', 'password')['auth_user_id']) == {
        'channels': []
    }

def test_allchannels_mix(): #channels_list_v1
    clear_v1()
    auth_register_v1('cengiz@gmail.com', 'password', 'cengiz', 'cimen') 
    auth_register_v1('gabbo@gmail.com', 'password', 'gabriel', 'thien')
    # Gets ids of users 
    id1 = auth_login_v1('cengiz@gmail.com', 'password')['auth_user_id']
    id2 = auth_login_v1('gabbo@gmail.com', 'password')['auth_user_id']
    # Gets ids of channels 
    channel_id_1 = channels_create_v1(id1, 'cengis couch', True)['channel_id'] # Public
    channel_id_2 = channels_create_v1(id2, 'gabbos bed', False)['channel_id'] # Private
    channel_invite_v1(id2, channel_id_2, id1)
    # Must be able to see both public and private channels since member of both
    assert channels_list_v1(id1) == { 
        'channels' : [ 
            {
                'channel_id': channel_id_1,
                'name': 'cengis couch', 
            }, 
            {
                'channel_id': channel_id_2,
                'name': 'gabbos bed', 
            }
        ]
    }

def test_member_seessomechannels():
    # Show all channels that the user is a member of 
    clear_v1()
    auth_register_v1('cengiz@gmail.com', 'password', 'cengiz', 'cimen') 
    auth_register_v1('gabbo@gmail.com', 'password', 'gabriel', 'thien')
    auth_register_v1('chris@gmail.com', 'password', 'christina', 'lee')
    channels_create_v1(auth_login_v1('cengiz@gmail.com', 'password')['auth_user_id'], 'cengis bed', False) # Private channel
    # Gets channel_id of channel that Gabbo is a member of 
    gabbo_channel_id = channels_create_v1(auth_login_v1('gabbo@gmail.com', 'password')['auth_user_id'], 'gabbos couch', True)['channel_id'] # Public channel
    channels_create_v1(auth_login_v1('chris@gmail.com', 'password')['auth_user_id'], 'christinas shoe', False) # Private channel
    # gabbo should only see his own couch
    assert channels_list_v1(auth_login_v1('gabbo@gmail.com', 'password')['auth_user_id']) == { 
        'channels' : [
            {
                'channel_id': gabbo_channel_id, 
                'name': 'gabbos couch', 
            }
        ]
    }


def test_private_channels(): # channels_list_v1
    clear_v1()
    auth_register_v1('cengiz@gmail.com', 'password', 'cengiz', 'cimen') 
    auth_register_v1('gabbo@gmail.com', 'password', 'gabriel', 'thien')
    # Gabbo creates a private channel
    channels_create_v1(auth_login_v1('gabbo@gmail.com', 'password')['auth_user_id'], 'gabbos couch', False) # private
    # Cengiz should see nothing since not a member of any 
    assert channels_list_v1(auth_login_v1('cengiz@gmail.com', 'password')['auth_user_id']) == {
        'channels' : []
    }
