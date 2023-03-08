from src.data_store import data_store
from src.error import InputError
from src.user import user_increase_channel_stat_helper, user_involvement_calculator_updater
import time

def channels_list_v1(auth_user_id):
    '''
    Provide a list of all channels that the user is a part of (and their associated details)

    Arguments:
        auth_user_id (integer)  - User ID of person requesting channels_list_v1.

    Exceptions:
        AccessError             - Occurs when ID does not exist in data store.

    Return Value:
        Returns list of all channels and their respective details on the condition that the
        user ID exists and they are a memeber of the channels.
    '''

    # Fetch stored data and initialise empty channel list
    store = data_store.get()
    channels_list = []

    # If auth_user_id exists, return a list with channels they are members of along with details
    for user in store['users']:
        if user['u_id'] == auth_user_id:
            for channel in store['channels']:
                # If auth_user_id is a member of channel, append channel details to channel list
                if auth_user_id in channel['members']:
                    channels_list.append({'name': channel['name'], 'channel_id': channel['channel_id']})
            
    return {
        'channels': channels_list
    }

def channels_listall_v1(auth_user_id):
    '''
    Provide a list of all channels, including private channels, (and their associated details)

    Arguments:
        auth_user_id (integer)  - User ID of person requesting channels_listall_v1.

    Exceptions:
        AccessError             - Occurs when ID does not exist in data store.

    Return Value:
        Returns list of all channels and their respective details on the condition that the
        user ID exists.
    '''

    # Fetch stored data
    store = data_store.get()

    # Initialise empty channel list
    channel_list = []
    # Append channel details to channel list
    for channel in store['channels']:
        channel_list.append({'name': channel['name'], 'channel_id': channel['channel_id']})
            
    return {
        'channels' : channel_list
    }

def channels_create_v1(auth_user_id, name, is_public):
    '''
    This function creates a new SEAMS channel and returns the new channel id on a success.

    Arguments:
        auth_user_id (integer)  - User ID of person requesting a new channel creation.
        name (string)           - The name of the new channel.
        is_public (boolean)     - Specifies whether the created channel will be public or private.

    Exceptions:
        InputError              - Occurs if the channel name is either too short or too long.

    Return Value:
        Returns the ID value of the newly created channel.
    '''

    # Fetch stored data
    store = data_store.get()
    
    # Raise InputError if name is too long or short
    if len(name) <= 0:
        raise InputError("Channel name too short")
    if len(name) > 20:
        raise InputError("Channel name too long")

    # Create new channel with unique channel_id and specified information
    channel_id = len(store['channels'])
    store['channels'].append(
        {
            'channel_id': channel_id,
            'auth_user_id': auth_user_id,
            'owners': [auth_user_id],
            'name': name,
            'is_public': is_public,
            'members': [auth_user_id],
            'messages': [],
            'standup' : {
                'is_active' : False,
                'time_finish' : 0,
                'messages' : [],
            },
        }
    )

    # Get time
    curr_time = int( time.time() )

    # Updates user stats to increase by 1
    store = user_increase_channel_stat_helper(auth_user_id, curr_time, store)

    # Update user involvement_rate
    store = user_involvement_calculator_updater(auth_user_id, store)

    data_store.set(store)

    return {
        'channel_id': channel_id,
    }
