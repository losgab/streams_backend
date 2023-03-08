import re
import os
from PIL import Image
from urllib.request import urlopen, urlretrieve
from urllib.error import URLError

from src.data_store import data_store
from src.error import InputError
from src.other import get_message_id

def user_profile_setemail(auth_user_id, email):
    '''
    Update the authorised user's email address

    Arguments:
        auth_user_id (integer)  -  The user to be changed
        email (string)          -  The new email 

    Exceptions:
        InputError              - Occurs when the email is not valid
                                - Occurs when email is already used
                                
        AccessError             - Occurs when the auth_user_id does not exist      
                                
    Return Value:
        None
    '''

    # Fetch stored data
    store = data_store.get()
    
    # Checks if email is valid
    if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
        raise InputError("Invalid email")

    # Check if email is already in use
    for user in store['users']:
        if user['email'] == email:
            raise InputError("Email already in use")

    # Find given user and change to given email
    store['users'][auth_user_id]['email'] = email
    
    data_store.set(store)
    
    # Return nothing
    return {
    }

def set_handle_v1(u_id, handle_str):
    '''
    Change the handle of the give user 

    Arguments:
        auth_user_id (integer)  - User ID of person requesting set_handle_v1.
        handle_str (string)    - User ID of person requesting set_handle_v1.

    Exceptions:
        InputError              - The handle is already used
                                - The handle is not between 3 and 20 characters (inclusive)
                                - The handle contains characters that are not alphanumeric

    Return Value:
        N/A

    '''
    if len(handle_str) <= 3 or len(handle_str) >= 20:
        raise InputError(description="handle errror: handle string is invalid length")
    if not handle_str.isalnum():
        raise InputError(description="handle error: handle string is not all alphanumeric")
    
    store = data_store.get()

    for user in store['users']:
        if user['handle_str'] == handle_str:
            raise InputError(description="handle error: handle string is already taken")

    store['users'][u_id]['handle_str'] = handle_str

    data_store.set(store)
    
    return

def user_profile_v1(auth_user_id, u_id):
    '''
    For a valid user, returns information about their user_id, email, first name, last name, and handle

    Arguments:
        auth_user_id (int) - The user id of the person calling the function
        u_id (int)         - The user whose details are being viewed
    
    Exceptions:
        InputError         - Occurs when u_id does not refer to a valid user
    
    Returns:
        user (dictionary)  - dictionary containing u_id, email, name_first, name_last, handle_str
    '''
    
    store = data_store.get()
    users = store['users']

    # decode_session_token checks if the token is valid (this is in the http wrapper)
    
    # check if u_id is valid
    if u_id < 0 or u_id >= len(store['users']):
        raise InputError("Invalid u_id user")
    
    # get the u_id user dictionary
    user_dict = users[u_id]

    return { 
        'user': { 
            'u_id': u_id,
            'email': user_dict['email'],
            'name_first': user_dict['name_first'],
            'name_last': user_dict['name_last'],
            'handle_str': user_dict['handle_str'],
            'profile_img_url': user_dict['profile_img_url']
        }   
    }

def profile_setname_v1(auth_user_id, name_first, name_last):
    '''
    For a valid user, takes in a last and first name and updates the name currently stored on their profile

    Arguments:
        auth_user_id (int) - The user id of the person calling the function
        name_first (string)        - The name that the user wants to set their profile first name as 
        name_last (string)         - The name that the user wants to set their profile last name as 
    
    Exceptions:
        InputError         - Occurs when u_id does not refer to a valid user
    
    Returns:
        None
    '''
    
    # Fetch stored data
    store = data_store.get()
    
    # Raise InputError if name_first is too short
    if len(name_first) == 0:
        raise InputError("First name must have more than 0 characters!")
    
    # Raise InputError if name_first is too long
    if len(name_first) > 50:
        raise InputError("First name must not be more than 50 characters!")
    
    # Raise InputError if name_last is too short
    if len(name_last) == 0:
        raise InputError("Last name must have more than 0 characters!")
    
    # Raise InputError if name_last is too long
    if len(name_last) > 50:
        raise InputError("Last name must not be more than 50 characters!")
    
    # Update the details of the user as desired
    store['users'][auth_user_id]['name_first'] = name_first
    store['users'][auth_user_id]['name_last'] = name_last
    
    # Store da data
    data_store.set(store)
    
    # Returns nothing
    return {}

def user_stats_v1(auth_user_id):
    '''
    user_stats_v1
    
    Fetches the required statistics about this user's use of UNSW Seams.
    
    Arguments:
        auth_user_id (integer) - the id of an existing (registered) user
    
    Exceptions:
        None

    Return Value:
        user_stats (dictionary)

    '''
    # Fetch stored data
    store = data_store.get()

    return {
        'user_stats': {
            'channels_joined': store['users'][auth_user_id]['channels_joined'],
            'dms_joined': store['users'][auth_user_id]['dms_joined'],
            'messages_sent': store['users'][auth_user_id]['messages_sent'],
            'involvement_rate': store['users'][auth_user_id]['involvement_rate']
        }
    }

def profile_uploadphoto_v1(auth_user_id, img_url, x_start, y_start, x_end, y_end):
    '''
    Given a URL of a n image on the internet, crops it with the given bounds.
    Stores the image with a user specific filename, and adds this save location to the user's profile. 

    Arguments:
        auth_user_id    (int)   - The user id of the person calling the function
        img_url         (string)- string of URL that the image is located at
        x_start         (int)
        y_start         (int)
        x_end           (int)
        y_end           (int)
    
    Exceptions:
        InputError      - when img_url returns a HTTP status other than 200 or any other error when attempting image retreival
                        - any of start or end boundaries are not within the dimensions of the image 
                        - x_end is less than or equal to x_start
                        - y_end is less than or equal to y_start
                        - Image uploaded is not a JPG

    Returns:
        None
    '''
    # Raises InputError if invalid URL causes a connection error
    # try:
    #     resp_data = urlopen(img_url)
    # except URLError:
    #     raise InputError("Invalid URL")
    
    try:
         with urlopen(img_url) as resp_data:
            # InputError if URL returns a non 200 status, or if the file is not a jpg
            if  not img_url.endswith('.jpg') or resp_data.getcode() != 200:
                raise InputError("Error retrieving image. Might need to check if jpg.")
    except URLError as err: 
        raise InputError("Invalid URL") from err    

    # Raise InputError if bounds are invalid
    if x_end <= x_start or y_end <= y_start:
        raise InputError("End values cannot be less than or equal to start values")

    # Downloads the image into server-side folder, loads into a python object
    urlretrieve(img_url, "src/static/img0.jpg")
    imageObject = Image.open("src/static/img0.jpg")

    # Getting dimensions of image for next set of error testing
    width, height = imageObject.size
    # Raise InputError if bounds are invalid
    for value in [x_start, x_end]:
        if value not in range(width):
            raise InputError("Crop values are not within dimension of image!")
    for value in [y_start, y_end]:
        if value not in range(height):
            raise InputError("Crop values are not within dimension of image!")

    # Crops the image within given bounds 
    imageObject = imageObject.crop((x_start, y_start, x_end, y_end))

    # Saves the image with unique filename for 
    save_location = f"/static/user{auth_user_id}_pfp.jpg"
    imageObject.save("src" + save_location)
    
    # Update profile_img_url for the user
    store = data_store.get()
    store['users'][auth_user_id]['profile_img_url'] = "http://127.0.0.1:8080" + save_location
    data_store.set(store)
    
    # Close the image object and remove the temporary file 
    imageObject.close()
    os.remove("src/static/img0.jpg")
    return {}

def user_increase_channel_stat_helper(u_id, time_stamp, store):
    '''
    Updates the num_channels_joined record to increase by 1

    Arguments:
        u_id            (int)   - The user id of the person calling the function
        time_stamp      (int)   - time of occurence
        store           (dict)  - data

    Returns:
        store           (dict)  - data
    '''
    # Get current number channels that user is in
    curr_channels_joined = store['users'][u_id]['channels_joined'][-1]['num_channels_joined']
    # Append a new record into channels_joined stat in the user data
    store['users'][u_id]['channels_joined'].append(
        {
            'num_channels_joined': curr_channels_joined + 1,
            'time_stamp': time_stamp
        }
    )
    return store 

def user_decrease_channel_stat_helper(u_id, time_stamp, store):
    '''
    Updates the num_channels_joined record to decrease by 1

    Arguments:
        u_id            (int)   - The user id of the person calling the function
        time_stamp      (int)   - time of occurence
        store           (dict)  - data

    Returns:
        store           (dict)  - data
    '''
    # Get current number channels that user is in
    curr_channels_joined = store['users'][u_id]['channels_joined'][-1]['num_channels_joined']
    # Append a new record into channels_joined stat in the user data
    store['users'][u_id]['channels_joined'].append(
        {
            'num_channels_joined': curr_channels_joined - 1,
            'time_stamp': time_stamp
        }
    )
    return store

def user_increase_dm_stat_helper(u_id, time_stamp, store):
    '''
    Updates the num_dms_joined record to increase by 1

    Arguments:
        u_id            (int)   - The user id of the person calling the function
        time_stamp      (int)   - time of occurence
        store           (dict)  - data

    Returns:
        store           (dict)  - data
    '''
    # Get current number channels that user is in
    curr_dms_joined = store['users'][u_id]['dms_joined'][-1]['num_dms_joined']
    # Append a new record into channels_joined stat in the user data
    store['users'][u_id]['dms_joined'].append(
        {
            'num_dms_joined': curr_dms_joined + 1,
            'time_stamp': time_stamp
        }
    )
    return store 

def user_decrease_dm_stat_helper(u_id, time_stamp, store):
    '''
    Updates the num_dms_joined record to decrease by 1

    Arguments:
        u_id            (int)   - The user id of the person calling the function
        time_stamp      (int)   - time of occurence
        store           (dict)  - data

    Returns:
        store           (dict)  - data
    '''
    # Get current number channels that user is in
    curr_dms_joined = store['users'][u_id]['dms_joined'][-1]['num_dms_joined']
    # Append a new record into channels_joined stat in the user data
    store['users'][u_id]['dms_joined'].append(
        {
            'num_dms_joined': curr_dms_joined - 1,
            'time_stamp': time_stamp
        }
    )
    return store

def user_increase_message_stat_helper(u_id, time_stamp, store):
    '''
    Updates the num_messages_sent record to increase by 1

    Arguments:
        u_id            (int)   - The user id of the person calling the function
        time_stamp      (int)   - time of occurence
        store           (dict)  - data

    Returns:
        store           (dict)  - data
    '''
    # Record when this message was sent and update messages_sent for user
    store['users'][u_id]['messages_sent'].append(
        {
            'num_messages_sent': len(store['users'][u_id]['messages_sent']),
            'time_stamp': time_stamp
        }
    )
    return store 

def user_involvement_calculator_updater(u_id, store):
    '''
    Calculates and Updates the user's involvement_rate

    Arguments:
        u_id            (int)   - The user id of the person calling the function
        store           (dict)  - data

    Returns:
        store           (dict)  - data
    '''
    # Getting involvement variables
    num_channels_joined = store['users'][u_id]['channels_joined'][-1]['num_channels_joined']
    num_dms_joined = store['users'][u_id]['dms_joined'][-1]['num_dms_joined']
    num_messages_sent = store['users'][u_id]['messages_sent'][-1]['num_messages_sent']
    involvement_rate_numerator = sum([num_channels_joined, num_dms_joined, num_messages_sent])
    # Getting current number of channels, dms and messages
    num_channels = len(store['channels'])
    num_dms = 0
    for dm in store['dms']:
        if not dm['removed']:
            num_dms += 1
    num_messages = 0
    for channel in store['channels']:
        num_messages += len(channel['messages'])
    for dm in store['dms']:
        num_messages += len(dm['messages'])
    involvement_rate_denominator = sum([num_channels, num_dms, num_messages])
    
    # Checks & Calculation
    if involvement_rate_denominator == 0:
        involvement_rate = 0
    else:
        involvement_rate = involvement_rate_numerator / involvement_rate_denominator
    
    # Further checks
    if involvement_rate > 1: involvement_rate = 1

    # Record involvement rate
    store['users'][u_id]['involvement_rate'] = float(num_messages)
    return store