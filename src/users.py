from src.data_store import data_store
from src.error import InputError, AccessError

def users_all_v1():
    '''
    Returns a list of all users and their associated details.
    
    Arguments:
        None
        Note that the http wrapper handles the token input
    
    Exceptions:
        None
        Note that invalid tokens are not handled by user/all/v1,
        but rather the decode_session_token function in src/tokens.py
    
    Returns:
        users (list of dictionaries) - users is a list of dictionaries, where each
                                       individual dictionary is the "user" dictionary
                                       which contains u_id, email, name_first, name_last, handle_str                         
    '''
    store = data_store.get()
    users = store['users']
    return_list = []

    # decode_session_token in src/tokens.py checks if the token is valid (this is used in the http wrapper)

    for user in range(len(store['users'])):
        user_dict = users[user]
        # ignore deleted users
        if user_dict['removed'] == False:
            return_list.append({
                'u_id': user_dict['u_id'],
                'email': user_dict['email'],
                'name_first': user_dict['name_first'],
                'name_last': user_dict['name_last'],
                'handle_str': user_dict['handle_str'],  
                'profile_img_url': user_dict['profile_img_url']
            })
    
    return {
        'users' : return_list
    }