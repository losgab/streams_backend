import jwt
from src.error import AccessError

SECRET = "Attack on titan is bad"
sessions = []

def encode_session_token(user_id):
    '''
    Creates a new token for the user unique to their login session

    Arguments:
        user_id (int)   - The user id of the person trying to create a new session/JWT
    Exceptions:
        None
    Returns:
        ['token'] : (string) - Encoded JWT generated on each login event from a user
    '''
    # makes sure each jwt for a user is unique on each login/register
    session_count = 0 
    while jwt.encode({'session_id': session_count, 'u_id' : user_id}, SECRET, algorithm = 'HS256') in sessions:
        session_count += 1
    new_jwt = jwt.encode({'session_id': session_count, 'u_id' : user_id}, SECRET, algorithm = 'HS256')
    # add new jwt to list of sessions
    sessions.append(new_jwt)
    # return the new jwt
    return {
        'token' : str(new_jwt)
    }

def decode_session_token(token):
    '''
    Returns token package if it exists in the sessions list

    Arguments:
        token (string)  - The user id of the person trying to create a new session
    Exceptions:
        AccessError     - Occurs when When the token is not inside the list 
    Returns:
        ['auth_user_id'] : (int)  - The user id that was packaged into the token initially
    '''
    # if the token is in the sessions list decode it and return the user id
    if token in sessions:
        return {
            'auth_user_id' : jwt.decode(token, SECRET, algorithms=['HS256'])['u_id']
            # Add more fields below if necessary...
        }
    else:
        # Raise an access error if the token not in the sessions list
        raise AccessError(description="Token does not exist")
        

def remove_session_token(token):
    '''
    Removes token from sessions

    Arguments:
        token (string)  - Removes specific token
    Exceptions:
        N/a
    Returns:
        N/A
    '''

    if token not in sessions:
        raise AccessError(description="Invalid token")

    sessions.remove(token)

    return 

def remove_all_instances_of_id(u_id):
    '''
    Removes all instances of a users sessions when they are removed

    Arguments:
        u_id (integer)  - The user id of the person who's sessions are to be deleted
    Exceptions:
        N/a
    Returns:
        N/A
    '''
    for session in sessions:
        if decode_session_token(session)['auth_user_id'] == u_id:
            sessions.remove(session)

    return
