import re
import hashlib
from src.data_store import data_store
from src.error import InputError
# Below are imports for sending emails
from src.tokens import remove_all_instances_of_id
from flask_mail import Message
from src.server import mail
import secrets
import string

# Dictionary to store reset keys
reset_keys = []

CHARACTERS = (
    string.ascii_letters
    + string.digits
    + '-._~'
)

def generate_unique_reset_code(size=15):
    '''
    Generates a unique 15 char length key for reseting password
    '''
    return secrets.token_urlsafe(size)[:size]


def auth_login_v1(email, password):
    '''
    If the email and password arguments are correct this function returns the respective user id.

    Arguments:
        email       (string) -  The users inputed email.
        password    (string) -  The users inputed password.

    Exceptions:
        InputError  -   Occurs when the email does not exist within the user database or
                        when the email does exist but the password is incorrect.
        
    Return Value:
        Returns the user id on the condition that the email and password match an existing user.
    '''

    # Fetch the stored data
    store = data_store.get()

    for user in store['users']:
        # find an account with a matching email that has not been removed
        if (user['email'] == email):
            if user['removed'] == True:
                print("User with same email has been removed")
                continue
            else:
                # If the password is correct return
                if user['password'] == hashlib.sha256(password.encode()).hexdigest():
                    return {
                    'auth_user_id' : user['u_id']
                    }
                else:
                    # If the password is not correct raise an error
                    raise InputError("Incorrect password")

    # If the email is not found raise an error
    raise InputError("Email not found")


def auth_register_v1(email, password, name_first, name_last):
    '''
    This function creates a new SEAMS user from the given input details.

    Arguments:
        email       (string) -  The users desired email.
        password    (string) -  The users desired password.
        name_first  (string) -  The users first name
        name_last   (string) -  The users last name

    Exceptions:
        InputError  -   Occurs when name_first or name_last are not within a valid length.
                        OR when the email is not in a valid format OR when the user already 
                        exits in the database

    Return Value:
        Returns the user's new id on the condition that all arguments are valid and the new user
        has been added to the database.
    '''
    # Fetch the stored data
    store = data_store.get()

    # Check if the email mathces
    if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
        raise InputError("Invalid email")

    ## if the name is too long or too short raise an error
    if len(name_first) == 0 or len(name_first) > 50:
        raise InputError("Invalid first name")
    if len(name_last) == 0 or len(name_last) > 50:
        raise InputError("Invalid last name")
    if len(password) < 6:
        raise InputError("Password is Invalid")
    
    # Check if the user already exists
    for user in store['users']:
        if user['email'] == email:
            if not user['removed']:
                raise InputError("Users email already in use")

    # Create a handle for the user and append a number to the handle if it already exists
    new_handle = "".join(re.findall("[a-z0-9]+", (name_first+name_last).lower()))[:20]
    handle_counter = -1
    for user in store['users']:
        if (user['handle_str'] == new_handle if handle_counter == -1 else new_handle + f'{handle_counter}') and not user['removed']:
            handle_counter += 1
    final_handle = new_handle + f'{handle_counter}' if handle_counter != -1 else new_handle         

    # Append the new user to the list of users
    new_id = len(store['users'])
    store['users'].append({
        'u_id' : new_id, 
        'email' : email, 
        'password' : hashlib.sha256(password.encode()).hexdigest(), 
        'name_first' : name_first, 
        'name_last' : name_last, 
        'handle_str' : final_handle,
        'permission_id': 1 if new_id == 0 else 2,
        'notifications': [],
        'tagged_messages_notified': [],
        'channels_joined': [
            {
                'num_channels_joined': 0,
                'time_stamp': 0
            }
        ],
        'dms_joined': [
            {
                'num_dms_joined': 0,
                'time_stamp': 0
            }
        ],
        'messages_sent': [
            {
                'num_messages_sent': 0,
                'time_stamp': 0
            }
        ],
        'involvement_rate': 0.0,
        'profile_img_url': 'http://127.0.0.1:8080/static/default_sushi.jpg',
        'removed': False})
    data_store.set(store)

    # print(store) # uncomment for debugging purposes

    return {
        'auth_user_id': new_id,
    }

def auth_passwordreset_request_v1(email):
    '''
    This function sends out an email containing a code to request for a password reset

    Arguments:
        email (string)  -  The users email.
    Exceptions:
        InputError      -  No error should be raised when passed an invalid email, as that would pose a security/privacy concern. 

    Return Value:
        None
    '''
    # Fetch global data
    global reset_keys
    store = data_store.get()
    # Check for user with same email
    for user in store['users']:
        if user['email'] == email:
            # Set the message heading, sender and recipients
            msg = Message('Reset Code', sender = 'seamsbotbeepboop@gmail.com', recipients = [email])
            # Generate a unique string
            reset_key = generate_unique_reset_code()
            msg.body = reset_key
            # Send the message
            mail.send(msg)
            # Log the user out
            remove_all_instances_of_id(user['u_id'])
            # Add the reset key to the dictionary of reset keys
            reset_keys.append({'u_id' : user['u_id'], 'key' : reset_key})
            print(reset_keys)   # Uncomment for debugging

    return

def auth_passwordreset_reset_v1(code, password):

    '''
    Given a reset code for a user, set that user's new password to the password provided. Once a reset code has been used, it is then invalidated.

    Arguments:
        code (string)       -  The reset code
        password (string)   -  The new password string
    Exceptions:
        InputError      -  reset_code is not a valid reset code
                        -  password entered is less than 6 characters long

    Return Value:
        None
    '''
    if len(password) < 6:
        raise InputError(description="New password is too short")

    global reset_keys
    keys_list = [keys for keys in reset_keys if keys['key'] == code]
    if len(keys_list) == 0:
        raise InputError(description="Code is incorrect")
    key_data = keys_list[0]
    # Invalidate reset code
    reset_keys.remove(keys_list[0])
    store = data_store.get()
    
    for user in store['users']:
        if user['u_id'] == key_data['u_id']:
            user['password'] = hashlib.sha256(password.encode()).hexdigest()
        
    data_store.set(store)
    return
