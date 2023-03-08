import time
import threading
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import react_notification, tag_notification, is_valid_message_id, get_message_id
from src.user import user_increase_message_stat_helper, user_involvement_calculator_updater

def message_send_v1(u_id, channel_id, message):
    '''
    Sends a message to the specified channel
    
    Arguments:
        u_id        (integer)   - The user id of the user that is sending the message
        channel_id  (integer)   - The channel id that the message is being sent to
        message     (string)    - Message that is to be sent
    Exceptions:
        InputError      - Occurs when the channel id is not valid
                        - Occurs when the length of the message is greater than 1000 or less than 1 character
        AccessError     - Occurs when the channel exists but the user is not a member
    Returns:
        The id of the new message {message_id}
    
    '''
    # Fetch data from datastore
    store = data_store.get()

    # Channel id is not valid
    if channel_id > len(store['channels']) - 1 or channel_id < 0:
        raise InputError(description='Invalid channel ID')

    # Message is ont valid
    if len(message) > 1000 or len(message) < 1:
        raise InputError(description='Length of message is invalid')

    if u_id not in store['channels'][channel_id]['members']:
        raise AccessError(description='User is not a member of the channel')
    
    # Get unique message id
    message_id = get_message_id()

    # Get time
    curr_time = int( time.time() )

    # Add messages to channel
    store['channels'][channel_id]['messages'].append(
        {
            'message_id' : message_id,
            'u_id' : u_id,
            'message' : message, 
            'time_sent' : curr_time,
            'reacts': [],
            'is_pinned': False,
        }
    )
    
    # Record when this message was sent and update messages_sent for user
    store = user_increase_message_stat_helper(u_id, curr_time, store)

    # Update user involvement_rate
    store = user_involvement_calculator_updater(u_id, store)

    # Helper function for notifying if message tags an existing user 
    store = tag_notification(u_id, message_id, message, store)

    data_store.set(store)

    return {
        'message_id' : message_id
        }

def message_remove_v1(u_id, message_id):
    '''
    Removes a message from a channel or DM with the specified message_id

    Arguments:
        u_id (int)       - The id of the user calling the function
        message_id (int) - The id of the message which is to be removed

    Exceptions:
        InputError       - Occurs when the message_id does not refer to a valid message
                           within a channel/DM that the authorised user has joined
        AccessError      - Occurs when message_id refers to a valid message in a joined
                           channel/DM and none of the following are true:
                                - the message was sent by the authorised user making this request
                                - the authorised user has owner permissions in the channel/DM
    
    Returns:
        None
    '''
    # fetch data from datastore
    store = data_store.get()

    # Iterate over all channels that the user is a member of
    for channel in store['channels']:
        if u_id in channel['members'] or u_id in channel['owners']:
            for message in channel['messages']:
                # Message id is valid
                if message['message'] != '' and message['message_id'] == message_id:
                    # Check if it was sent by user or check for owner permissions (owner of channel or global owner in member list)
                    if u_id in channel['owners'] or message['u_id'] == u_id or store['users'][u_id]['permission_id'] == 1:
                        message['message'] = ''
                        data_store.set(store)
                        return {}
                    else:
                        # Message not sent by user and user does not have owner permissions 
                        raise AccessError(description="Message id exists but the user requesting is invalid")
                    # Make message and message invalid
                    

    # Iterate over all dms that the user is a member of 
    for dm in store['dms']:
        if u_id in dm['members']:
            for message in dm['messages']:
                # Message id is valid
                if message['message'] != '' and message['message_id'] == message_id:
                    # Check if message was sent by user or owner permisssion (original creator of dm) 
                    if u_id == dm['owner'] or message['u_id'] == u_id:
                        message['message'] = ''
                        data_store.set(store)
                        return {}
                    else:
                        # Message not sent by user and user does not have owner permissions 
                        raise AccessError(description="Message id exists but the user requesting is invalid")

    # Message id is invalid (does not exist in available dms/channels)
    raise InputError("Message id does not refer to a valid message within a channel/DM")



def message_senddm(auth_user_id, dm_id, message):
    '''
    Send a message from authorised_user to the DM specified by dm_id
    
    Arguments:
        auth_user_id (integer)   - The user id of the user that is sending the message
        dm_id        (integer)   - The dm id that the message is being sent to
        message      (string)    - Message that is to be sent
    Exceptions:
        InputError      - Occurs when the channel id is not valid
                        - Occurs when the length of the message is greater than 1000 or less than 1 character
       
        AccessError     - Occurs when the channel exists but the user is not a member

    Returns:
        The id of the new message {message_id}
    
    '''

    # Fetch data from datastore
    store = data_store.get()

    # Check for valid dm id 
    if dm_id < 0 or dm_id >= len(store['dms']):
        raise InputError(description="Invalid dm")

    # Check for valid message
    if len(message) > 1000 or len(message) < 1:
        raise InputError(description='Length of message is invalid')

    # Check if user is in dm
    if auth_user_id not in store['dms'][dm_id]['members']:
        raise AccessError(description='User is not a member of given dm id')
    
    # Get unique message id
    message_id = get_message_id()
    
    # Get time
    curr_time = int( time.time() )

    # Add messages to dm
    store['dms'][dm_id]['messages'].append(
        {
            'message_id' : message_id,
            'u_id' : auth_user_id,
            'message' : message,
            'time_sent' : curr_time,
            'reacts': [],
            'is_pinned': False,
        }
    )

    # Record when this message was sent and update messages_sent for user
    store = user_increase_message_stat_helper(auth_user_id, curr_time, store)

    # Update user involvement_rate
    store = user_involvement_calculator_updater(auth_user_id, store)

    # Helper function to notify the dm members if they are tagged 
    store = tag_notification(auth_user_id, message_id, message, store)

    data_store.set(store)

    return {
        'message_id': message_id,
    }
    
def message_share_v1(auth_user_id, og_message_id, message, channel_id, dm_id):
    '''
    message_share_v1

    A new message should be sent to the channel/DM identified by the channel_id/dm_id that contains the contents of both the original message and the optional message.

    Arguments:

        auth_user_id (integer) - the id of an existing (registered) user
        og_message_id (integer) - the id of the original message
        message (string) - message that is to be sent
        channel_id (integer) - the id of an existing channel
        dm_id (integer) - the id of an existing dm

    Exceptions:

        InputError - Occurs when both channel_id and dm_id are invalid
                   - Occurs when neither channel_id nor dm_id are -1
                   - Occurs when og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined
                   - Occurs when length of message is more than 1000 characters

        AccessError - Occurs when the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) and the authorised user has not joined the channel or DM they are
        trying to share the message to

    Return Value:
        shared_message_id (integer)

    '''

    # Fetch stored data
    store = data_store.get()
    
    # Raise InputError if the channel_id and dm_id are invalid
    if (channel_id < -1 or channel_id >= len(store['channels'])) and (dm_id < -1 or dm_id >= len(store['dms'])):
        raise InputError("Invalid channel ID and dm ID")
    
    # Raise InputError if neither channel_id nor dm_id are -1
    if channel_id != -1 and dm_id != -1:
        raise InputError("message not shared")
 
    # Raise InputError if og_message_id is invalid
    if is_valid_message_id(og_message_id) == False:
        raise InputError(description="Invalid message ID")
    
    # Raise InputError if the length of message is more than 1000 characters
    if len(message) > 1000:
        raise InputError("message too long")
    
    # Get unique message id
    shared_message_id = get_message_id()
    
    # Get time
    curr_time = int(time.time())
    
    # share messages to dm
    if channel_id == -1:
        # Raise AccessError if user is not a member of dm
        if auth_user_id not in store['dms'][dm_id]['members']:
            raise AccessError("User is not a member of dm")
        
        store['dms'][dm_id]['messages'].append(
            {
                'message_id': shared_message_id,
                'u_id': auth_user_id,
                'message': message,
                'time_sent': curr_time,
                'reacts': [],
                'is_pinned': False,
            }
        )
    
    # share messages to channel
    else:
        # Raise AccessError if user is not a member of channel
        if auth_user_id not in store['channels'][channel_id]['members']:
            raise AccessError("User is not a member of channel")
        
        store['channels'][channel_id]['messages'].append(
            {
                'message_id': shared_message_id,
                'u_id': auth_user_id,
                'message': message,
                'time_sent': curr_time,
                'reacts': [],
                'is_pinned': False,
            }
        )
    
    # Record when this message was sent and update messages_sent for user
    store = user_increase_message_stat_helper(auth_user_id, curr_time, store)
    
    # Update user involvement_rate
    store = user_involvement_calculator_updater(auth_user_id, store)

    # notify if message tags a user
    store = tag_notification(auth_user_id, shared_message_id, message, store)
    
    data_store.set(store)
    
    return {
        'shared_message_id': shared_message_id
    }

def message_edit_v1(u_id, message_id, message_str):  
    '''
    Given a message, update its text with new text. If the new message is an empty string, the message is deleted.

    Arguments:
        u_id (int)       - The id of the user calling the function
        message_id (int) - The id of the message which is to be removed
        message_str (string) - The new message string

    Exceptions:
        InputError       - Occurs when the message_id does not refer to a valid message
                           within a channel/DM that the authorised user has joined
                         - Length of the message is over 1000 chracters
        AccessError      - Occurs when message_id refers to a valid message in a joined
                           channel/DM and none of the following are true:
                                - the message was sent by the authorised user making this request
                                - the authorised user has owner permissions in the channel/DM
    
    Returns:
        None
    '''
    # fetch data from datastore
    store = data_store.get()

    # InputError when the length of message is over 1000 characters
    if len(message_str) > 1000:
        raise InputError(description="The length of the message is over 1000 characters")

    # Iterate over all channels that the user is a member of
    for channel in store['channels']:
        if u_id in channel['members']:
            for message in channel['messages']:
                # Message id is valid
                if message['message'] != '' and message['message_id'] == message_id:
                    # Check if it was sent by user or check for owner permissions (owner of channel or global owner in member list)
                    if u_id in channel['owners'] or message['u_id'] == u_id or store['users'][u_id]['permission_id'] == 1:
                        message['message'] = message_str
                        # Helper function for notifying when message tags an existing user 
                        store = tag_notification(u_id, message_id, message_str, store)
                        data_store.set(store)
                        return {}
                    else:
                        # Message not sent by user and user does not have owner permissions 
                        raise AccessError(description="Message id exists but the user requesting is invalid")
                    # Make message and message invalid
                    

    # Iterate over all dms that the user is a member of 
    for dm in store['dms']:
        if u_id in dm['members']:
            for message in dm['messages']:
                # Message id is valid
                if message['message'] != '' and message['message_id'] == message_id:
                    # Check if message was sent by user or owner permisssion (original creator of dm) 
                    if u_id == dm['owner'] or message['u_id'] == u_id:
                        message['message'] = message_str
                        # Helper function for notifying when message tags an existing user 
                        store = tag_notification(u_id, message_id, message_str, store)
                        data_store.set(store)
                        return {}
                    else:
                        # Message not sent by user and user does not have owner permissions 
                        raise AccessError(description="Message id exists but the user requesting is invalid")

    # Message id is invalid (does not exist in available dms/channels)
    raise InputError("Message id does not refer to a valid message within a channel/DM")

def message_react(auth_user_id, message_id, react_id):
    '''
    Given a message within a channel or DM the authorised user is part of, add a "react" 
    to that particular message.

    Arguments:
        auth_user_id (integer)  - the id of the authorised user
        message_id (integer)    - the id of the message that wants to be reacted
        react_id (integer)      - the id of a react, only 1 is available

    Exceptions:
        InputError              - Occurs when message_id is valid but the auth user 
                                  is not part of the channel / dm
                                - Occurs when react_id is invalid
                                - Occurs when the message is already reacted by auth user

        AccessError             - Occurs when the auth_user_id is invalid

    Return Value:
        None

    '''

    # fetch data from datastore
    store = data_store.get()

    # Check for valid react_id (Only 1 is valid)
    if react_id != 1:
        raise InputError(description='Invalid react ID')

    # Iterate over all channels that the user is a member of
    for channel in store['channels']:
        if auth_user_id in channel['members'] or auth_user_id in channel['owners']:
            for message in channel['messages']:
                # Message id is valid
                if message['message'] != '' and message['message_id'] == message_id:
                    # Check if message is already reacted; if not react
                    if auth_user_id not in message['reacts']:
                        message['reacts'].append(auth_user_id)
                        # Helper function for notifying when message tags an existing user 
                        store = react_notification(auth_user_id, message_id, store)
                        data_store.set(store)
                        return {}

    # Iterate over all dms that the user is a member of 
    for dm in store['dms']:
        if auth_user_id in dm['members']:
            for message in dm['messages']:
                # Message id is valid
                if message['message'] != '' and message['message_id'] == message_id:
                    # Check if message is already reacted; if not react
                    if auth_user_id not in message['reacts']:
                        message['reacts'].append(auth_user_id)
                        # Helper function for notifying when message tags an existing user 
                        store = react_notification(auth_user_id, message_id, store)
                        data_store.set(store)
                        return {}

    # Message id is invalid (does not exist in available dms/channels)
    raise InputError("Message id does not refer to a valid message within a channel/DM")

def message_unreact(auth_user_id, message_id, react_id):
    '''
    Given a message within a channel or DM the authorised user is part of, remove a "react" 
    to that particular message.

    Arguments:
        auth_user_id (integer)  - the id of the authorised user
        message_id (integer)    - the id of the message that wants to be reacted
        react_id (integer)      - the id of a react, only 1 is available

    Exceptions:
        InputError              - Occurs when message_id is valid but the auth user 
                                  is not part of the channel / dm
                                - Occurs when react_id is invalid
                                - Occurs when the message hasn't been reacted by the
                                  auth user

        AccessError             - Occurs when the auth_user_id is invalid

    Return Value:
        None

    '''

    # fetch data from datastore
    store = data_store.get()

    # Check for valid react_id (Only 1 is valid)
    if react_id != 1:
        raise InputError(description='Invalid react ID')

    # Iterate over all channels that the user is a member of
    for channel in store['channels']:
        if auth_user_id in channel['members'] or auth_user_id in channel['owners']:
            for message in channel['messages']:
                # Message id is valid
                if message['message'] != '' and message['message_id'] == message_id:
                    # Check if message is already reacted; if not react
                    if auth_user_id in message['reacts']:
                        message['reacts'].remove(auth_user_id)
                        data_store.set(store)
                        return {}

    # Iterate over all dms that the user is a member of 
    for dm in store['dms']:
        if auth_user_id in dm['members']:
            for message in dm['messages']:
                # Message id is valid
                if message['message'] != '' and message['message_id'] == message_id:
                    # Check if message is already reacted; if not react
                    if auth_user_id in message['reacts']:
                        message['reacts'].remove(auth_user_id)
                        data_store.set(store)
                        return {}

    # Message id is invalid (does not exist in available dms/channels)
    raise InputError("Message id does not refer to a valid message within a channel/DM")

def message_pin(auth_user_id, message_id):
    '''
    Given a message within a channel or DM, mark it as "pinned".

    Arguments:
        auth_user_id (integer)  - the id of the authorised user
        message_id (integer)    - the id of the message that is to be pinned

    Exceptions:
        InputError              - Occurs when message_id is valid but the auth user 
                                  is not part of the channel / dm
                                - Occurs when the message is already pinned

        AccessError             - Occurs when the auth_user_id is invalid
                                - Occurs when the auth_user has no permission in the channel/dm

    Return Value:
        None

    '''

    # Fetch data from datastore
    store = data_store.get()

    # Iterate over all channels that the user is a member of
    for channel in store['channels']:
        if auth_user_id in channel['members'] or auth_user_id in channel['owners']:
            for message in channel['messages']:
                # Check if message id is valid
                if message['message'] != '' and message['message_id'] == message_id:
                    # Check if message is already pinned
                    if message['is_pinned'] == True:
                        raise InputError(description='Message is already pinned')
                    # Check if auth user has permissions, if so pin message
                    if auth_user_id in channel['owners'] or store['users'][auth_user_id]['permission_id'] == 1:
                        message['is_pinned'] = True
                        data_store.set(store)
                        return {}
                    else:
                        raise AccessError(description='No permissions')
    
    # Iterate over all dms that the user is part of
    for dm in store['dms']:
        if auth_user_id in dm['members']:
            for message in dm['messages']:
                # Check if message id is valid
                if message['message'] != '' and message['message_id'] == message_id:
                    # Check if message is already pinned
                    if message['is_pinned'] == True:
                        raise InputError(description='Message is already pinned')
                    # Check if auth user has permissions, if so pin message
                    if auth_user_id == dm['owner']:
                        message['is_pinned'] = True
                        data_store.set(store)
                        return {}
                    else:
                        raise AccessError(description='No permissions')
    
    raise InputError(description='Message ID does not refer to a valid message in a channel/DM')

def message_unpin(auth_user_id, message_id):
    '''
    Given a message within a channel or DM, remove its mark as pinned.

    Arguments:
        auth_user_id (integer)  - the id of the authorised user
        message_id (integer)    - the id of the message that is to be pinned

    Exceptions:
        InputError              - Occurs when message_id is valid but the auth user 
                                  is not part of the channel / dm
                                - Occurs when the message is not already pinned

        AccessError             - Occurs when the auth_user_id is invalid
                                - Occurs when the auth_user has no permission in the channel/dm

    Return Value:
        None

    '''

    # Fetch data from datastore
    store = data_store.get()

    # Iterate over all channels that the user is a member of
    for channel in store['channels']:
        if auth_user_id in channel['members'] or auth_user_id in channel['owners']:
            for message in channel['messages']:
                # Check if message id is valid
                if message['message'] != '' and message['message_id'] == message_id:
                    # Check if message is already pinned
                    if message['is_pinned'] == False:
                        raise InputError(description='Message is already pinned')
                    # Check if auth user has permissions, if so pin message
                    if auth_user_id in channel['owners'] or store['users'][auth_user_id]['permission_id'] == 1:
                        message['is_pinned'] = False
                        data_store.set(store)
                        return {}
                    else:
                        raise AccessError(description='No permissions')
    
    # Iterate over all dms that the user is part of
    for dm in store['dms']:
        if auth_user_id in dm['members']:
            for message in dm['messages']:
                # Check if message id is valid
                if message['message'] != '' and message['message_id'] == message_id:
                    # Check if message is already pinned
                    if message['is_pinned'] == False:
                        raise InputError(description='Message is already pinned')
                    # Check if auth user has permissions, if so pin message
                    if auth_user_id == dm['owner']:
                        message['is_pinned'] = False
                        data_store.set(store)
                        return {}
                    else:
                        raise AccessError(description='No permissions')
    
    raise InputError(description='Message ID does not refer to a valid message in a channel/DM')

def message_sendlater_helper(message_id, message_str):
    '''
    Helper function for message/sendlater that runs at time_sent. Updates the message field from ''
    to the desired message.

    Arguments:
        message_id (int) - The id of the message which is to be updated
        message_str (string) - The message string
    
    Exceptions:
        None

    Returns:
        None
    '''
    store = data_store.get()

    # update the message field to the desired message
    for channel in store['channels']:
        for message in channel['messages']:
            if message['message_id'] == message_id and message['message'] == '':
                message['message'] = message_str
                data_store.set(store)
                return

    for dm in store['dms']:
        for message in dm['messages']:
            if message['message_id'] == message_id and message['message'] == '':
                message['message'] = message_str
                data_store.set(store)
                return

def message_sendlater_v1(u_id, channel_id, message, time_sent):
    '''
    Send a message by the authorised user to the channel specified by channel_id at a time in the future, specified by time_sent
    
    Arguments:
        u_id (integer)       - The user id of the user that is sending the message
        channel_id (integer) - The channel id that the message is being sent to
        message (string)     - The message that is to be sent

    Exceptions:
        InputError  - Occurs when channel_id is not valid
                    - Occurs when the length of the message is less than 1 or over 1000 characters
                    - Occurs if time_sent is a time in the past
        AccessError - Occurs when the channel exists but the user is not a member

    Returns:
        The id of the new message {message_id}
    '''

    # Fetch data from datastore
    store = data_store.get()

    # time_sent is in the past
    delta_t = time_sent - int(time.time())
    if delta_t < 0:
        raise InputError('time_sent cannot be in the past')

    # Channel id is not valid
    if channel_id > len(store['channels']) - 1 or channel_id < 0:
        raise InputError(description='Invalid channel ID')

    # Message is not valid
    if len(message) > 1000 or len(message) < 1:
        raise InputError(description='Length of message is invalid')

    if u_id not in store['channels'][channel_id]['members']:
        raise AccessError(description='User is not a member of the channel')
    
    # Get unique message id
    message_id = get_message_id()

    # preallocate an empty message
    store['channels'][channel_id]['messages'].append(
        {
            'message_id' : message_id,
            'u_id' : u_id,
            'message' : '',
            'time_sent' : time_sent,
            'reacts' : [],
            'is_pinned' : False
        }
    )

    t = threading.Timer(delta_t, message_sendlater_helper, [message_id, message])
    t.start()

    # Record when this message was sent and update messages_sent for user
    store = user_increase_message_stat_helper(u_id, time_sent, store)

    # Update user involvement_rate
    store = user_involvement_calculator_updater(u_id, store)

    # notify if message tags a user
    store = tag_notification(u_id, message_id, message, store)

    data_store.set(store)

    return {
        'message_id': message_id
    }
def message_sendlaterdm_v1(u_id, dm_id, message, time_sent):
    '''
    Send a message by the authorised user to the dm specified by dm_id at a time in the future, specified by time_sent
    
    Arguments:
        u_id (integer)       - The user id of the user that is sending the message
        dm_id (integer)      - The dm id that the message is being sent to
        message (string)     - The message that is to be sent

    Exceptions:
        InputError  - Occurs when channel_id is not valid
                    - Occurs when the length of the message is less than 1 or over 1000 characters
                    - Occurs if time_sent is a time in the past
        AccessError - Occurs when the channel exists but the user is not a member

    Returns:
        The id of the new message {message_id}
    '''

    # Fetch data from datastore
    store = data_store.get()

    # time_sent is in the past
    delta_t = time_sent - int(time.time())
    if delta_t < 0:
        raise InputError('time_sent cannot be in the past')

    # dm id is not valid
    if dm_id >= len(store['dms']) or dm_id < 0:
        raise InputError(description='Invalid DM ID')

    # Message is not valid
    if len(message) > 1000 or len(message) < 1:
        raise InputError(description='Length of message is invalid')

    if u_id not in store['dms'][dm_id]['members']:
        raise AccessError(description='User is not a member of the channel')
    
    # Get unique message id
    message_id = get_message_id()

    # preallocate an empty message
    store['dms'][dm_id]['messages'].append(
        {
            'message_id' : message_id,
            'u_id' : u_id,
            'message' : '',
            'time_sent' : time_sent,
            'reacts' : [],
            'is_pinned' : False
        }
    )

    t = threading.Timer(delta_t, message_sendlater_helper, [message_id, message])
    t.start()

    # Record when this message was sent and update messages_sent for user
    store = user_increase_message_stat_helper(u_id, time_sent, store)

    # Update user involvement_rate
    store = user_involvement_calculator_updater(u_id, store)

    # notify if message tags a user
    store = tag_notification(u_id, message_id, message, store)

    data_store.set(store)

    return {
        'message_id': message_id
    }
    