from src.data_store import data_store
import src.tokens as token
from src import auth
import re
import os
from src.error import InputError

def clear_v1():
    '''
    clear_v1
    This function resets all data stored in data_store.py and clears sessions.

    Arguments: none
    Exceptions: none
    Return value: none
    '''
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    store['dms'] = []
    token.sessions = []
    auth.reset_keys = []
    
    cwd = os.getcwd()
    for f in os.listdir(f"{cwd}/src/static"):
        if f != "default_sushi.jpg":
            os.remove(f"{cwd}/src/static/{f}")

    data_store.set(store)

def search_v1(auth_user_id, query_str):
    '''
    Given a query string, returns messages containing this string in any of the channels/DMs that the user has joined

    Arguments:
        auth_user_id    (integer)   - The user id of the user
        query_str       (string)    - string to be searched for in all messages in channels and dms that user is a part of 
    
    Exceptions: 
        InputError - when length of query_str is less than 1 or over 1000 characters

    Return value: 
        Dictionary containing list of all messages that query string appears in 
        {
            messages 
        }
    '''
    # InputError checking for the query string 
    if query_str == '' or len(query_str) > 1000:
        raise InputError("Invalid query string to search")

    # Fetch data from the json
    store = data_store.get()

    user_permission = store['users'][auth_user_id]['permission_id']
    messages = []

    # Iterating through channel messages
    for channel in store['channels']:
        if auth_user_id in channel['members'] or user_permission == 1:
            for message in channel['messages']:
                if query_str.lower() in message['message'].lower():
                    messages.append(message)

    # Iterating through dm messages
    for dm in store['dms']:
        if auth_user_id in dm['members']:
            for message in dm['messages']:
                if query_str.lower() in message['message'].lower():
                    messages.append(message)

    return {
        'messages': messages
    }
    
def notifications_get_v1(auth_user_id):
    '''
    Given a query string, returns messages containing this string in any of the channels/DMs that the user has joined

    Arguments:
        auth_user_id    (integer)   - The user id of the user

    Return value: 
        Dictionary containing list of all related notifications
        {
            notifications
        }
    '''
    # Fetch data store 
    store = data_store.get()
    return {
        'notifications': store['users'][auth_user_id]['notifications'][:21]
    }

def react_notification(reactor_id, message_id, store):
    '''
    Helper function with adding a reacted notification to the concerned user.

    Arguments:
        reactor_id      (integer)   - The user id of the user
        message_id      (integer)   - message id of focus
        store           (dictionary)- the data

    Return value: 
        store
    '''
    reactor_handle = store['users'][reactor_id]['handle_str']
    
    # Iterate over all channels that the user is a member of
    for channel in store['channels']:
        if reactor_id in channel['members'] or reactor_id in channel['owners']:
            for message in channel['messages']:
                # Message id is valid
                if message['message'] != '' and message['message_id'] == message_id:
                    channel_name = channel['name']
                    message_author = message['u_id']
                    if message_author in channel['members'] and message_author != reactor_id:
                        # Access the user profile and notifications list
                        store['users'][message_author]['notifications'].insert(0, 
                            {
                                'channel_id': channel['channel_id'],
                                'dm_id': -1,
                                'notification_message': f'{reactor_handle} reacted to your message in {channel_name}'
                            }
                        )

    # Iterate over all dms that the user is a member of
    for dm in store['dms']:
        for message in dm['messages']:
            # Message id is valid
            if message['message'] != '' and message['message_id'] == message_id:
                dm_name = dm['name']
                message_author = message['u_id']
                if message_author in dm['members'] and message_author != reactor_id:
                    # Access the user profile and notifications list
                    store['users'][message_author]['notifications'].insert(0, 
                        {
                            'channel_id': -1,
                            'dm_id': dm['dm_id'],
                            'notification_message': f'{reactor_handle} reacted to your message in {dm_name}'
                        }
                    )

    return store
                        
def tag_notification(author_id, message_id, message_str, store):
    '''
    Helper function with deciding whether message tags any user, and adding a tagged notification to the concerned user. 

    Arguments:
        author_id    (integer)   - The user id of the user
        message_id      (integer)   - message id
        message_str     (string)    - the message contents/body
        store           (dictionary)- the data

    Return value: 
        store
    '''
    # Get some details 
    tagger = store['users'][author_id]['handle_str']

    # Finding the channel that the message was added to
    for channel in store['channels']:
        channel_name = channel['name']
        # Going through messages in each channel
        for message in channel['messages']:
            if message['message'] != '' and message['message_id'] == message_id:
                for member_id in channel['members']:
                    # For each user in this channel, add a notification if they were tagged 
                    handle = store['users'][member_id]['handle_str']
                    processed_message = message_str.replace('@', ' ')
                    # Exact word search with word boundaries to find valid tags 
                    if re.search(r'\b' + handle + r'\b', processed_message) and message_id not in store['users'][member_id]['tagged_messages_notified']:
                        # User has been tagged
                        tag_string = message_str[:20]
                        store['users'][member_id]['notifications'].insert(0,
                            {
                                'channel_id': channel['channel_id'],
                                'dm_id': -1,
                                'notification_message': f'{tagger} tagged you in {channel_name}: {tag_string}'
                            }
                        )
                        # Update what the user has already been notified of
                        store['users'][member_id]['tagged_messages_notified'].append(message_id)
                        continue

    # Finding the dm that the message was added to
    for dm in store['dms']:
        dm_name = dm['name']
        # Going through messages in each channel
        for message in dm['messages']:
            if message['message'] != '' and message['message_id'] == message_id:
                for member_id in dm['members']:
                    # For each user in this channel, add a notification if they were tagged 
                    handle = store['users'][member_id]['handle_str']
                    processed_message = message_str.replace('@', ' ')
                    # Exact word search with word boundaries to find valid tags 
                    if re.search(r'\b' + handle + r'\b', processed_message) and message_id not in store['users'][member_id]['tagged_messages_notified']:
                        # User has been tagged
                        tag_string = message_str[:20]
                        store['users'][member_id]['notifications'].insert(0,
                            {
                                'channel_id': -1,
                                'dm_id': dm['dm_id'],
                                'notification_message': f'{tagger} tagged you in {dm_name}: {tag_string}'
                            }
                        )
                        # Update what the user has already been notified of
                        store['users'][member_id]['tagged_messages_notified'].append(message_id)
                        continue
    return store

def channel_member_added_notification(auth_user_id, channel_id, u_id, store):
    '''
    Helper function with adding a member added notification to the concerned user. 

    Arguments:
        auth_user_id    (integer)   - adder
        channel_id      (integer)   - id of the channel user just added to
        u_id            (integer)   - addee
        store           (dictionary)- the data

    Return value: 
        store
    '''
    # Get some details of the person who did the adding 
    adder = store['users'][auth_user_id]['handle_str']
    channel_name = store['channels'][channel_id]['name']

    # Add notification
    store['users'][u_id]['notifications'].insert(0, 
        {
            'channel_id': channel_id,
            'dm_id': -1,
            'notification_message': f'{adder} added you to {channel_name}'
        }
    )
    return store

def dm_member_added_notification(auth_id, u_ids, dm_id, store):
    '''
    Helper function with adding a member added notification to the concerned user. 

    Arguments:
        auth_id         (integer)   - adder
        u_ids           (list)      - addees
        dm_id           (interger)  - message id 
        store           (dictionary)- the data

    Return value: 
        store
    '''
    # Get some details of the person who did the adding 
    adder = store['users'][auth_id]['handle_str']
    dm_name = store['dms'][dm_id]['name']

    # Add notification of being added to the DM
    for u_id in u_ids:
        # Add notification
        store['users'][u_id]['notifications'].insert(0, 
            {
                'channel_id': -1,
                'dm_id': dm_id,
                'notification_message': f'{adder} added you to {dm_name}'
            }
        )

    return store

def is_valid_message_id(message_id):
    '''
    Helper function that checks if a message id is valid

    Arguments:
        message_id      (integer) - the message_id to be checked
    
    Return value:
        True or False
    '''
    # Fetch data
    store = data_store.get()

    # Check channels
    for channel in store['channels']:
        for message in channel['messages']:
            if message['message'] != '' and message['message_id'] == message_id:
                return True

    # Check dms
    for dm in store['dms']:
        for message in dm['messages']:
            if message['message'] != '' and message['message_id'] == message_id:
                return True
    
    return False
    
def get_message_id():
    '''
    Helper function which gets the message id of the message which is to be sent

    Arguments:
        None
    Exceptions:
        None
    Returns:
        The id of the message
    '''
    store = data_store.get()

    message_id = 0
    for channel in store['channels']:
        message_id += len(channel['messages'])
    for dm in store['dms']:
        message_id += len(dm['messages'])

    return message_id