from src.data_store import data_store
from src.error import InputError, AccessError
from src.tokens import remove_all_instances_of_id

def admin_user_remove_v1(auth_user_id, u_id):
    '''
    Arguments:
        auth_user_id (integer)  - Admin user id that is requesting for user to be removed
        u_id (integer)          - User id of the user that is to be removed

    Exceptions:
        InputError              - Occurs when u_id does not refer to a valid user
                                - Occurs when u_id refers to a user who is the only global owner
        AccessError             - Occursa when auth_user_id is not a global owner

    Returns:
        N/A
    '''
    # Fetch data from data store
    store = data_store.get()

    # Check if user id is valid
    if u_id >= len(store['users']) or u_id < 0:
        raise InputError(description="u_id does not refer to a valid user")

    # Check if the auth user is a global owner
    if store['users'][auth_user_id]['permission_id'] == 2:
        raise AccessError(description="authorised user is not a global owner")

    # count global owners
    global_owner_count = 0
    for user in store['users']:
        if user['permission_id'] == 1:
            global_owner_count += 1
    
    # If global owner count is 1 and the u_id is only global owner then raise error
    if global_owner_count == 1 and store['users'][u_id]['permission_id'] == 1:
        raise InputError(description="u_id refers to a user who is the only global owner")

    # Otherwise change the user details to removed
    store['users'][u_id]['removed'] = True
    store['users'][u_id]['permission_id'] = 2
    store['users'][u_id]['name_first'] = 'Removed'
    store['users'][u_id]['name_last'] = 'user'

    # Invalidate all the tokens of the user
    remove_all_instances_of_id(u_id)

    # Change all messages of removed user
    for channel in store['channels']:
        for message in channel['messages']:
            if message['u_id'] == u_id:
                message['message'] = 'Removed user'
        if u_id in channel['owners']:
            channel['owners'].remove(u_id)
        if u_id in channel['members']:
            channel['members'].remove(u_id)

    for dm in store['dms']:
        for message in dm['messages']:
            if message['u_id'] == u_id:
                message['message'] = 'Removed user'
        if u_id in dm['members']:
            dm['members'].remove(u_id)
            
    return

def admin_userpermission_change(auth_user_id, u_id, permission_id):
    '''
    Arguments:
        auth_user_id (integer)  - Admin user id that is requesting for user to be removed
        u_id (integer)          - User id of the user that is to be removed
        permission_id (integer) - Permission ID of seams (1 = global owner, 2 = member)

    Exceptions:
        InputError              - Occurs when u_id does not refer to a valid user
                                - Occurs when u_id refers to a user who is the only global owner
                                - Occurs when permission_id is ibvalid
                                - Occurs when the user already has permission 

        AccessError             - Occurs when auth_user_id is not a global owner
                                - Occurs when auth_user_id is invalid

    Returns:
        N/A
    '''

    # Fetch data from data store and set valid permissions
    store = data_store.get()
    permissions = [1,2]

    # Check if user id is valid
    if u_id >= len(store['users']) or u_id < 0:
        raise InputError(description="u_id does not refer to a valid user")

    # Check if the auth user is a global owner
    if store['users'][auth_user_id]['permission_id'] == 2:
        raise AccessError(description="authorised user is not a global owner")

    # count global owners
    global_owner_count = 0
    for user in store['users']:
        if user['permission_id'] == 1:
            global_owner_count += 1
    
    # If global owner count is 1 and the u_id is only global owner then raise error
    if global_owner_count == 1 and store['users'][u_id]['permission_id'] == 1:
        raise InputError(description="u_id refers to a user who is the only global owner")
    
    # Check if the permission id is valid
    if permission_id not in permissions:
        raise InputError(description="Invalid permission id")

    # Check if given permission_id is current permission id
    if store['users'][u_id]['permission_id'] == permission_id:
        raise InputError(description="Permission already set")

    # Find given user id and change their permission id
    store['users'][u_id]['permission_id'] = permission_id

    data_store.set(store)

    # Return nothing
    return {
    }
    