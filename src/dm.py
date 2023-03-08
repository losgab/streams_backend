from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import dm_member_added_notification
from src.user import user_decrease_dm_stat_helper, user_increase_dm_stat_helper, user_involvement_calculator_updater
import time

def dm_create_v1(auth_id, u_ids):
    '''
    Arguments:
        auth_id (integer)   - creator of the dm
        u_ids   (list)      - list of ids that are top be added to the dm
    Exceptions:
        InputError          - Occurs when given ids are invalid
                            - Occurs when duplicate ids in u_ids

    Returns:
        A new dm ID ('dm_id') for the new dm
    '''
    # Fetch data from data store
    store = data_store.get()

    # Check if valid user id (auth_id cant be invalid because token)
    for u_id in u_ids:
        if u_id < 0 or u_id > len(store['users']) or u_id == auth_id:
            raise InputError(description="One or more IDS of given users are not valid")

    # Check for duplicates
    if len(u_ids) > len(set(u_ids)):
        raise InputError(description="Duplicate IDs given")

    # Generate dm name alphabetically sorted, comma and space seperated
    user_handles = []
    user_handles.append(store['users'][auth_id]['handle_str'])
    for user in store ['users']:
        if user['u_id'] in u_ids:
            user_handles.append(user['handle_str'])
    dm_name = ", ".join(sorted(user_handles))

    # Generate id for dm
    dm_id = len(store['dms'])

    u_ids.append(auth_id)

    store['dms'].append(
        {
            'dm_id': dm_id,
            'owner': auth_id,
            'name': dm_name,
            'members': u_ids,
            'messages': [],
            'removed': False
        }
    )

    # Get time
    curr_time = int( time.time() )

    # Updates user stats to increase by 1
    for u_id in u_ids:
        store = user_increase_dm_stat_helper(u_id, curr_time, store)

    # Helper function for adding notification to the users that were added to the dm
    store = dm_member_added_notification(auth_id, u_ids, dm_id, store)

    # Update user involvement_rate
    for u_id in u_ids:
        store = user_involvement_calculator_updater(u_id, store)

    data_store.set(store)
    
    return {
        'dm_id' : dm_id
    }


def dm_messages_v1(auth_user_id, dm_id, start):
    '''
    Arguments:
        auth_id (integer)   - creator of the dm
        dm_id   (integer)   - list of ids that are top be added to the dm
        start   (integer)   - index of messages in dm to return
    
    Exceptions:
        InputError          - Occurs when dm_id passed is invalid 
                            - Occurs when start index is invalid 
        AccessError         - Occurs when user is no a member of the DM 

    Returns:
        messages (list)
        start    (starting index of messages returned)
        end      (end index of messages returned, -1 if no more to return)
    '''
    
    # Fetch stored data
    store = data_store.get()

    # Checks to ensure that dm_id is valid
    if dm_id < 0 or dm_id >= len(store['dms']) or store['dms'][dm_id]['removed']:
        raise InputError("Invalid dm_id")
    
    # Checks to ensure that auth_user_id is a member of the dm 
    if auth_user_id not in store['dms'][dm_id]['members']:
        raise AccessError("No access to dm messages.")

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
    } for message in store['dms'][dm_id]['messages'] if message['message'] != '']
    messages_list = sorted(unsorted_messages, key=lambda d: d['time_sent'])
    messages_list.reverse()
    
    # Checks if start is a valid index 
    if start < 0 or start > len(messages_list):
        raise InputError("Invalid start index.")

    return {
            'messages': messages_list[start : start + 50],
            'start': start,
            'end': -1 if len(messages_list) <= start + 50 else start + 50,
        }

def dm_remove_v1(auth_user_id, dm_id):
    '''
    Arguments:
        auth_id (integer)   - creator of the dm
        dm_id   (integer)   - list of ids that are top be added to the dm
    
    Exceptions:
        InputError          - Occurs when dm_id passed is invalid 
        AccessError         - Occurs when user is not a member of the DM 
                            - dm_id is valid but the user is not the creator of the dm

    Returns:
        None
    '''
    # Fetch stored data
    store = data_store.get()

    # Checks to ensure that dm_id is valid
    if dm_id < 0 or dm_id >= len(store['dms']) or store['dms'][dm_id]['removed']:
        raise InputError("Invalid dm_id")

    # Checks to ensure that auth_user_id is a member of the dm 
    if auth_user_id not in store['dms'][dm_id]['members']:
        raise AccessError("No access to DM.")

    # Checks whether the authorised user is the original creator of the DM
    if auth_user_id is not store['dms'][dm_id]['owner']:
        raise AccessError("No access to delete the DM.")

    # Get time
    curr_time = int( time.time() )

    dm_members = store['dms'][dm_id]['members']
    # Updates user stats to increase by 1
    for u_id in dm_members:
        store = user_decrease_dm_stat_helper(u_id, curr_time, store)

    # Disable this dm by changing boolean to true and empty the members list 
    store['dms'][dm_id]['removed'] = True
    store['dms'][dm_id]['members'] = []

    # Updates user stats involvement_rates 
    for u_id in dm_members:
        store = user_involvement_calculator_updater(u_id, store)

    data_store.set(store)

    return {}

def dm_details_v1(auth_user_id, dm_id):
    '''
    dm_details_v1

    Given a DM with ID dm_id that the authorised user is a member of,
    provide basic details about the DM.

    Arguments:

        auth_user_id (integer) - creator of the dm
        dm_id (integer) - list of ids that are to be added to the dm

    Exceptions:

        InputError - Occurs when dm_id does not refer to a valid DM

        AccessError - Occurs when dm_id is valid and the authorised user is not a member of the DM

    Return Value:
        name (string)
        members (list of dictionaries)

    '''

    # Fetch stored data
    store = data_store.get()
    
    # Raise InputError if the dm id is invalid
    if dm_id < 0 or dm_id >= len(store['dms']) or store['dms'][dm_id]['removed']:
        raise InputError("Invalid dm ID")
    
    # Raise AccessError if user is not a member
    if auth_user_id not in store['dms'][dm_id]['members']:
        raise AccessError("User is not a member of dm")

    dm_details = {
        'name': "handle",
        'members': [],
    }
    
    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            dm_details['name'] = dm['name']
            for member in store['dms'][dm_id]['members']:
                # Create a new dictionary for a member
                user = store['users'][member]
                dm_details_member = {
                    'u_id': user['u_id'],
                    'name_first': user['name_first'],
                    'name_last': user['name_last'],
                    'email': user['email'],
                    'handle_str': user['handle_str'],
                    'profile_img_url': user['profile_img_url']
                }
                # Append member details to dm_details
                dm_details['members'].append(dm_details_member)

    return dm_details

def dm_list_v1(u_id):
    '''
    Returns the list of DMs that the user is a member of.
    Arguments:
        auth_id (integer)   - ID of the user requesting the dm list
    
    Exceptions:
        NONE

    Returns:
        dms      List of dictionaries, where each dictionary contains types { dm_id, name }
    
    '''
    # List for storing the dms that the member is a part of 
    dm_list = []
    # Fetch some data 
    store = data_store.get()

    # Gets the dms that the user is a part of 
    for dm in store['dms']:
        if u_id in dm['members']:
            dm_list.append({
                'dm_id' : dm['dm_id'],
                'name' : dm['name']
            })

    return {
        'dms' : dm_list
    }

def dm_leave_v1(auth_user_id, dm_id):
    '''
    Given a dm_id, the auth_user_id is removed from the dm
    Arguments:
        auth_id (integer)   - ID of the user
        dm_id (integer)     - ID of the dm to leave 

    Exceptions:
        InputError          - Occurs when dm_id passed is invalid 
        AccessError         - Occurs when user is not a member of the DM 

    Returns:
        None
    '''
    # Fetch some data 
    store = data_store.get()

    # Checks to ensure that dm_id is valid
    if dm_id < 0 or dm_id >= len(store['dms']) or store['dms'][dm_id]['removed']:
        raise InputError("Invalid dm_id")

    # Checks to ensure that auth_user_id is a member of the dm 
    if auth_user_id not in store['dms'][dm_id]['members']:
        raise AccessError("Not a member of DM.")

    # Get time
    curr_time = int( time.time() )

    # Updates user stats to decrease by 1
    store = user_decrease_dm_stat_helper(auth_user_id, curr_time, store)

    # Remove the user from being a member in the dm field
    store['dms'][dm_id]['members'].remove(auth_user_id)

    # Update user involvement_rate
    store = user_involvement_calculator_updater(auth_user_id, store)

    data_store.set(store)

    return {}
