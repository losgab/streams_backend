from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import channel_member_added_notification
from src.user import user_increase_channel_stat_helper, user_decrease_channel_stat_helper, user_involvement_calculator_updater
import time

def channel_invite_v1(auth_user_id, channel_id, u_id):
    '''
    channel_invite_v1

    Given an a valid auth_user_id (the inviter), the channel_id to be invited to, and a valid u_id 
    (the invitee), the invitee is immediately added to the channel as a member 

    Arguments:
        auth_user_id (integer) - The id of an existing (registered) user
        channel_id (integer)   - The id of an existing channel
        u_id (integer)         - The id of another existing (registered) user
        
    Exceptions:
        InputError  - Occurs when channel_id does not refer to a valid channel or is not an integer,
                    - Occurs when u_id is already a member of specified channel
                    - Occurs when u_id does not refer to a a valid registered user

        AccessError - Occurs when auth_user_id is invalid
                    - Occurs when the inviter isnt already a member of the channel

    Return Value:
        None
    '''

    # Fetch data from data_store
    store = data_store.get()

    # Checks if u_id is valid
    if u_id < 0 or u_id >= len(store['users']):
        raise InputError("Invalid User ID")

    # Checks if channel_id is valid
    if channel_id < 0 or channel_id >= len(store['channels']):
        raise InputError("Invalid Channel ID")

    # Checks if inviter is in channel, ie. has permission to invite 
    if auth_user_id not in store['channels'][channel_id]['members']:
        raise AccessError("Auth User does not have permission!")

    # Checks if member is already in channel
    if u_id in store['channels'][channel_id]['members']:
        raise InputError("User is already in channel!")

    # If u_id is not in channel, and all checks have passed then add them to channel
    store['channels'][channel_id]['members'].append(u_id)

    # Get time
    curr_time = int( time.time() )

    # Updates user stats to increase by 1
    store = user_increase_channel_stat_helper(u_id, curr_time, store)

    # Helper function for adding a channel added notification to u_id
    store = channel_member_added_notification(auth_user_id, channel_id, u_id, store)

    # Update user involvement_rate
    store = user_involvement_calculator_updater(u_id, store)

    data_store.set(store)
    return {}

def channel_details_v1(auth_user_id, channel_id):
    '''
    channel_details_v1

    Given a channel with ID channel_id that the authorised user is a member of, provide basic details 
    about the channel.

    Arguments:
        auth_user_id (integer) - The id of an existing (registered) user
        channel_id (integer)   - The id of an existing channel
        
    Exceptions:
        InputError  - Occurs when channel_id does not refer to a valid channel or is not an integer,

        AccessError - Occurs when auth_user_id is invalid
                    - Occurs when the auth_user_id is not a member of channel_id

    Return Value:
        { name, is_public, owner_members, all_members }, where name is a string, is_public is a boolean,
        owner_members is a list of dictionaries of type user, all_members is a list of dictionaries of
        type user

    '''

    # Fetch stored data
    store = data_store.get()

    # Raise InputError if the channel id to join is invalid 
    if channel_id < 0 or channel_id >= len(store['channels']):
        raise InputError("Invalid channel ID")

    # Initialise empty dictionary
    channel_details = {
        'name': 'temp_name',
        'is_public': True,
        'owner_members': [],
        'all_members': []
    }

    for channel in store['channels']:
        # Channel corresponds to given channel_id
        if channel['channel_id'] == channel_id:
            # Set name and is_public to channel's details
            channel_details['name'] = channel['name']
            channel_details['is_public'] = channel['is_public']
            # Check if auth_user_id is in member list of channel_id
            if auth_user_id not in channel['members']:
                raise AccessError('User ID is not a member of given channel ID')
            for member in channel['members']:
                # If auth_user_id is found in member list loop through the member and owner list and append user information
                if member == auth_user_id:
                    for member_id in channel['members']:
                        user = store['users'][member_id]
                        # Make a new dictionary for the member that is to be appended
                        user_member = {
                            'u_id' : user['u_id'], 
                            'email' : user['email'], 
                            'name_first' : user['name_first'],  
                            'name_last' : user['name_last'],  
                            'handle_str' : user['handle_str'],
                            'profile_img_url': user['profile_img_url']
                        }
                        # Append members user details to members list
                        channel_details['all_members'].append(user_member)
                        # If member is an owner, append user information to owners list
                        if member_id in channel['owners']:
                            channel_details['owner_members'].append(user_member)
                
    return channel_details
            


def channel_messages_v1(auth_user_id, channel_id, start):
    '''
    channel_messages_v1

    Given a auth_user_id, channel_id and start, this function displays up to 50 messages
    in reverse order from a channel that the user is a member of. The messages displayed
    begin from the specified start value.

    Arguments:
        auth_user_id (integer)  - The id of an existing (registered) user
        channel_id (integer)    - The id of an existing channel
        start (integer)         - The message to start displaying messages from,
                                  with 0 being the most recent, 1 being the second most recent

    Exceptions:
        InputError  - Occurs when channel_id does not refer to a valid channel,
                      start is greater than the total number of messages in the channel,
                      or any of the inputs are negative numbers
        AccessError - Occurs when auth_user_id is invalid, or
                      channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns { messages, start, end } where messages is an output type,
        start is an integer and end is an integer
        If there are 50 messages to return, then end = start + 50.
        If the function has returned the least recent messages in the channel, then end = -1
    '''

    # get users and channels
    store = data_store.get()

    channels = store['channels']
        
    # Raise InputError if the channel id to join is invalid 
    if channel_id < 0 or channel_id >= len(channels):
        raise InputError("Invalid channel ID")
    
    # check if user is in the channel
    if auth_user_id not in channels[channel_id]['members'] and auth_user_id not in channels[channel_id]['owners']:
        raise AccessError("User is not a member of the channel")

    unsorted_messages = [{
        'message_id': message['message_id'],
        'u_id': message['u_id'],
        'message': message['message'],
        'time_sent': message['time_sent'],
        'reacts': [
            {
                'react_id': 1,
                'u_ids': message['reacts'],
                'is_this_user_reacted': True if auth_user_id in message['reacts'] else False
            }
        ],
        'is_pinned': message['is_pinned'], 
        } for message in channels[channel_id]['messages'] if message['message'] != '']
    messages_list = sorted(unsorted_messages, key=lambda d: d['time_sent'])
    messages_list.reverse()
    
    # check if start is greater than total messages
    if start > len(messages_list) or start < 0:
        raise InputError("start is greater than total messages")

    end = start + 50
    return {
        'messages': messages_list[start : end],
        'start': start,
        'end': -1 if len(messages_list) <= end else end,
    }


def channel_join_v1(auth_user_id, channel_id):
    '''
    channel_join_v1

    Given an auth_user_id and the channel id to be joined, the user is immediately added to the channel 
    as a member. Users can only join public channels using this command unless they are an owner 

    Arguments:
        auth_user_id (integer) - the id of an existing (registered) user
        channel_id (integer)   - the id of an existing channel

    Exceptions:
        InputError  - Occurs when channel_id does not refer to a valid channel or is not an integer,
                    - Occurs when user is already a member of specified channel

        AccessError - Occurs when auth_user_id is invalid
                    - Occurs when the user tries to join a private channel 

    Return Value:
        None
    '''

    # Fetch stored data
    store = data_store.get()

    # Raise InputError if the channel id to join is invalid 
    if channel_id < 0 or channel_id >= len(store['channels']):
        raise InputError("Channel ID is invalid")
    
    # Gets the specific channel data
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            # Raise InputError if user is already a member
            if auth_user_id in channel['members']:
                raise InputError("User is already a member in channel")

            # Raise AccessError if channel is private and user is not a global owner
            if not channel['is_public'] and store['users'][auth_user_id]['permission_id'] == 2:
                raise AccessError("Channel is private")

            # Add user to members list of the channel if not
            channel['members'].append(auth_user_id)
     
    # Get time
    curr_time = int( time.time() )

    # Updates user stats to increase by 1
    store = user_increase_channel_stat_helper(auth_user_id, curr_time, store)

    # Update user involvement_rate
    store = user_involvement_calculator_updater(auth_user_id, store)

    data_store.set(store)

    return {}
    
def channel_leave_v1(auth_user_id, channel_id):
    '''
    channel_leave_v1

    Given a channel with ID channel_id that the authorised user is a member of,
    remove them as a member of the channel.

    Arguments:

        auth_user_id (integer) - the id of an existing (registered) user
        channel_id (integer) - the id of an existing channel

    Exceptions:

        InputError - Occurs when channel_id does not refer to a valid channel

        AccessError - Occurs when channel_id is valid and the authorised user is not a member of the channel
                    - Occurs when auth_user_id is invalid

    Return Value:
        None

    '''

    # Fetch stored data
    store = data_store.get()
    
    # Raise InputError if the channel id to join is invalid
    if channel_id < 0 or channel_id >= len(store['channels']):
        raise InputError("Invalid channel ID")

    # Fetch channel data
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            # Raise AccessError if user is not a member
            if auth_user_id not in channel['members']:
                raise AccessError("User is not a member")

            # Remove user from members list
            store['channels'][channel_id]['members'].remove(auth_user_id)
            
            # Remove user from owners list
            if auth_user_id in channel['owners']:
                store['channels'][channel_id]['owners'].remove(auth_user_id)

    # Get time
    curr_time = int( time.time() )

    # Updates user stats to increase by 1
    store = user_decrease_channel_stat_helper(auth_user_id, curr_time, store)

    # Update user involvement_rate
    store = user_involvement_calculator_updater(auth_user_id, store)

    data_store.set(store)
    
    return {}

def channel_removeowner_v1(auth_user_id, channel_id, u_id):
    '''
    channel_removeowner_v1

    Assuming valid inputs, auth_user_id has the permission to remove the ownership status of u_id in said channel back to member

    Arguments:
        auth_user_id (integer) - the id of an existing (registered) user with owner permissions 
        channel_id (integer)   - the id of an existing channel
        u_id (integer)         - the id of an existing user also with owner permissions 

    Exceptions:
        InputError  - Occurs when channel_id does not refer to a valid channel or is not an integer,
                    - Occurs when invalid u_id is passed 
                    - Occurs when u_id passed is not an owner of the channel 
                    - Occurs when u_id passed is the only owner of the channel

        AccessError - Occurs when auth_user_id is invalid
                    - Occurs when auth_user_id has no permission/is not an owner of channel to remove an owner's permissions

    Return Value:
        None
    '''
    # Fetch stored data
    store = data_store.get()

    # Raise InputError if the channel id to join is invalid 
    if channel_id < 0 or channel_id >= len(store['channels']):
        raise InputError("Channel ID is invalid")

    # Raise InputError if the user id to join is invalid 
    if u_id < 0 or u_id >= len(store['users']):
        raise InputError("User ID is invalid")

    # Raise InputError if the u_id is not an owner of the channel
    if u_id not in store['channels'][channel_id]['owners']:
        raise InputError("User ID is not an owner of the channel")
    
    # Raise Access Error when auth_user_id has no permissions and is not a global owner
    if auth_user_id not in store['channels'][channel_id]['owners'] and store['users'][auth_user_id]['permission_id'] == 2:
        raise AccessError("No permission to remove an owner")

    # Raise InputError if u_id is currently the owner of the channel 
    if len(store['channels'][channel_id]['owners']) == 1:
        raise InputError("User ID is currently the only owner of channel")

    # Removes u_id from owners list 
    store['channels'][channel_id]['owners'].remove(u_id)
    
    data_store.set(store)
    
    return {}
    
    

def channel_addowner(auth_user_id, channel_id, u_id):
    '''
    channel_addowner

    Make user with user id u_id an owner of the channel.

    Arguments:
        auth_user_id (integer) - the id of an existing (registered) user
        channel_id (integer)   - the id of an existing channel
        u_id (integer)         - the id of the user to be added

    Exceptions:
        InputError  - Occurs when channel_id does not refer to a valid channel,
                    - Occurs when u_id does not refer to a valid user id,
                    - Occurs when u_id is already an owner,
                    - Occurs when u_id is not a member of channel

        AccessError - Occurs when auth_user_id is invalid
                    - Occurs when auth_user_id does not have owner permissions

    Return Value:
        None
    '''

    # Fetch stored data
    store = data_store.get()
    
    # Check if channel id is valid
    if channel_id < 0 or channel_id >= len(store['channels']):
        raise InputError("Invalid channel ID")
    
    # Check if user_id is valid
    if u_id < 0 or u_id >= len(store['users']):
        raise InputError("Invalid user ID")

    for channel in store['channels']:
        # Channel corresponds to given channel_id
        if channel['channel_id'] == channel_id: 
            # Check if auth user has owner permissions
            if auth_user_id not in channel['owners'] and store['users'][auth_user_id]['permission_id'] == 2:
                raise AccessError("Auth User does not have permission")

            # Check if global owner is a member
            if auth_user_id not in channel['members']:
                raise AccessError("Not a member")

            # Check if user ID is already an owner
            if u_id in channel['owners']:
                raise InputError("User is already an owner")

            # Check if user ID is a member
            if u_id not in channel['members']:
                raise InputError("User ID is not a member of channel")

            # Add user to owners likst of channel
            channel['owners'].append(u_id)

    data_store.set(store)

    return {
    }