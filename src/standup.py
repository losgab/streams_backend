
from src.data_store import data_store
from src.other import get_message_id
from src.error import InputError, AccessError
import time
import threading

def standup_dump_messages_helper(u_id, channel_id, length):
    '''
    Helper function that runs on seperate thread to dump standup messages into the channel when the 
    standup period is finished.

    Arguments
        u_id        (int)   - the auth user id starting the standup
        channel_id  (int)   - the channel where the standup period is started
        length      (int)   - the length in seconds of the standup period
    Exceptions
        [NONE]
    Returns
        [NONE]

    '''

    # Pause thread for standup lenth
    time.sleep(length)
    store = data_store.get()
    # Set standup back to default values
    store['channels'][channel_id]['standup']['is_active'] = False
    store['channels'][channel_id]['standup']['time_finish'] = 0
    messages = store['channels'][channel_id]['standup']['messages']
    store['channels'][channel_id]['standup']['messages'] = []

    # Generate a message string to send to the server
    message_string = ""
    for message in messages:
        message_string += f"{store['users'][message['u_id']]['handle_str']}: " + message['message'] + f"\n"
    
    # Add message to server
    store['channels'][channel_id]['messages'].append({
        'message_id' : get_message_id(),
        'u_id' : u_id,
        'message' : message_string,
        'time_sent' : int( time.time()),
        'reacts': [],
        'is_pinned': False
    })
    data_store.set(store)

    

def standup_start_v1(u_id, channel_id, length):
    '''
    For a given channel, start the standup period.
    Arguments
        u_id        (int)   - the auth user id starting the standup
        channel_id  (int)   - the channel where the standup period is started
        length      (int)   - the length in seconds of the standup period
    Exceptions:
        InputError      - channel_id does not refer to a valid channel
                        - length is a negative number
                        - an active standup is currently running
        AccessError     - channel_id is valid but the u_id is not a member
    Returns:
        {time_finish (int): unix timestamp of when standup period finishes} 

    '''
    store = data_store.get()
    # Checks if channel_id is valid
    if channel_id < 0 or channel_id >= len(store['channels']):
        raise InputError(description="Invalid channel id for standup start")
    if length < 0:
        raise InputError(description="Length of the standup is negative")
    if store['channels'][channel_id]['standup']['is_active'] == True:
        raise InputError(description="A standup is already active")
    if u_id not in store['channels'][channel_id]['members']:
        raise AccessError(description="User is not a member of standup channel")

    # Set the standup data to active
    store['channels'][channel_id]['standup']['is_active'] = True
    store['channels'][channel_id]['standup']['time_finish'] = int( time.time()) + length
    store['channels'][channel_id]['standup']['messages'] =  []

    # TOODDODODO: Create a thread on a timer to send standup messages on time finish and send a message
    t = threading.Thread(target = standup_dump_messages_helper, args =(u_id, channel_id, length ))
    t.daemon = True
    t.start()

    data_store.set(store)
    
    return {
        'time_finish' : store['channels'][channel_id]['standup']['time_finish']
    }

def standup_active_v1(u_id, channel_id):
    '''
    For a given channel, return whether a standup is active in it, and what time the standup finishes. 
    If no standup is active, then time_finish returns None.

    Arguments
        u_id        (int)   - the auth user id requesting the standup status
        channel_id  (int)   - the channel where the standup period was started
    Exceptions:
        InputError      - channel_id does not refer to a valid channel
        AccessError     - channel_id is valid but the u_id is not a member
    Returns:
        {is_active  (bool)  : the active status of the standup
        time_finish (int)   : unix timestamp of when standup period finishes} 
    '''
    store = data_store.get()

    if channel_id < 0 or channel_id >= len(store['channels']):
        raise InputError(description="Invalid channel id for standup active")
    if u_id not in store['channels'][channel_id]['members']:
        raise AccessError(description="User is not a member of standup channel")


    is_active = store['channels'][channel_id]['standup']['is_active']
    time_finish = store['channels'][channel_id]['standup']['time_finish']
    
    return {
        'is_active' : is_active,
        'time_finish' : time_finish if is_active else None
    }


def standup_send_v1(u_id, channel_id, message_str):
        
    store = data_store.get()

    # Channel id is valid
    if channel_id < 0 or channel_id >= len(store['channels']):
        raise InputError(description="Invalid channel id for standup active")

    # Length of message is too long
    if len(message_str) > 1000:
        raise InputError(description="Length of message is over 1000 characters")

    # An active standup is not curently running
    if not store['channels'][channel_id]['standup']['is_active']:
        raise InputError(description="An active standup is not currently running in the channel")

    # Channel id valid but user is not a member of the channel
    if u_id not in store['channels'][channel_id]['members']:
        raise AccessError(description="User is not a member of standup channel")

    store['channels'][channel_id]['standup']['messages'].append(
        {
            'u_id' : u_id,
            'message' : message_str
        }
    )
    return