import sys
import os
import signal
import threading
from json import dumps, load, dump
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from flask_mail import Mail
from src import config, auth, channels, channel, other, user, users, admin, dm, message, standup
from src.data_store import data_store
from src.tokens import encode_session_token, decode_session_token, remove_session_token
import atexit

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response


APP = Flask(__name__, static_url_path='/static/')
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# Below is configuration for sending emails to users
APP.config['MAIL_SERVER']='smtp.gmail.com'
APP.config['MAIL_PORT'] = 465
APP.config['MAIL_USERNAME'] = 'seamsbotbeepboop@gmail.com'
APP.config['MAIL_PASSWORD'] = 'GuacLuac12$?'
APP.config['MAIL_USE_TLS'] = False
APP.config['MAIL_USE_SSL'] = True
# Mail object used to send mail
mail = Mail(APP)

# NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

# INITIALISE THE SERVER DATA
# Function to load data from data_store.json
def peristence_load_v1():
    try:
        # Get the server data on server init
        with open('datastore.json', 'r') as f:
            data_store.set(load(f))
    except Exception:
        pass

# Function to store data in data_store.json
def persistence_store_v1():
    store = data_store.get()
    th = threading.Timer(1.0, persistence_store_v1)
    th.daemon =  True
    th.start()
    with open('datastore.json', 'w') as fp:
        dump(store, fp, indent=4, separators=(", ", ": "), sort_keys=True)
        # print("Data has been stored...")

peristence_load_v1()                    # Load the data from data_store.json
persistence_store_v1()                  # Initialise infinite data_store threads
atexit.register(persistence_store_v1)   # Server will be stored on exit


# clear_v2 function wrapper
@APP.route("/clear/v1", methods=['DELETE'])
def clear_v1_http():
    other.clear_v1()
    return dumps({})

# auth_login_v2 function wrapper
@APP.route("/auth/login/v2", methods=['POST'])
def auth_login_v2():
    # fetch the data from the request
    data = request.get_json()
    # login using v1 function
    user_id = auth.auth_login_v1(
        data['email'], 
        data['password'])['auth_user_id']
    # return a new session token and user id
    return dumps({
        'token': encode_session_token(user_id)['token'],
        'auth_user_id': user_id
        })

# auth_register_v2 function wrapper
@APP.route("/auth/register/v2", methods=['POST'])
def auth_register_v2():
    # fetch the data from the request
    data = request.get_json()
    # register using the v1 function
    new_user_id = auth.auth_register_v1(
        data['email'], 
        data['password'], 
        data['name_first'], 
        data['name_last'])['auth_user_id']
    # return a new session token (user automatically logged in) and user id
    return dumps({
        'token': encode_session_token(new_user_id)['token'],
        'auth_user_id': new_user_id
    })

# channels_creates_v2 function wrapper
@APP.route("/channels/create/v2", methods=['POST'])
def channels_create_v2():
    # Retrieve input
    data = request.get_json()
    u_id = decode_session_token(data['token'])['auth_user_id']
    # Call channels_create_v1 with given input
    ret = channels.channels_create_v1(u_id, data['name'], data['is_public'])
    # Return channel id
    return dumps(ret)

# channels_list_v2 function wrapper
@APP.route("/channels/list/v2", methods=['GET'])
def channels_list_v2():
    # Retrieve input
    u_id = decode_session_token(request.args.get('token', type = str))['auth_user_id']
    # Call channels_list_v1 with given input
    ret = channels.channels_list_v1(u_id)
    # Return list of channels that the authorised user is a part of
    return dumps(ret)

# channels_listall_v2 function wrapper
@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall_v2():
    # Retrive input
    u_id = decode_session_token(request.args.get('token', type = str))['auth_user_id']
    # Call channels_listall_v1 with given input
    ret = channels.channels_listall_v1(u_id)
    # Return list of all channels
    return dumps(ret)

# channel_details_v2 function wrapper
@APP.route("/channel/details/v2", methods=['GET'])
def channel_details_v2():
    # Retrieve input
    u_id = decode_session_token(request.args.get('token', type = str))['auth_user_id']
    channel_id = request.args.get('channel_id')
    # Call channel_details_v1 with given input
    ret = channel.channel_details_v1(u_id, int(channel_id))
    # Return channel details of given channnel id
    return dumps(ret)

# channel_messages_v2 function wrapper
@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages_v2():
    token = request.args.get('token', type = str)
    u_id = decode_session_token(token)['auth_user_id']
    channel_id = request.args.get('channel_id', type = int)
    start = request.args.get('start', type = int)
    ret = channel.channel_messages_v1(u_id, channel_id, start)
    return dumps(ret)

# channel_join_v2 function wrapper 
@APP.route("/channel/join/v2", methods=['POST'])
def channel_join_v2():
    data = request.get_json()
    u_id = decode_session_token(data['token'])['auth_user_id']
    channel_id = data['channel_id']
    ret = channel.channel_join_v1(u_id, channel_id)
    return dumps(ret)

# channel_leave_v1 function wrapper
@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave_v1():
    data = request.get_json()
    u_id = decode_session_token(data['token'])['auth_user_id']
    channel_id = data['channel_id']
    ret = channel.channel_leave_v1(u_id, channel_id)
    return dumps(ret)

# channel_invite_v2 function wrapper 
@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite_v2():
    data = request.get_json()
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    channel_id = data['channel_id']
    u_id = data['u_id']
    ret = channel.channel_invite_v1(auth_user_id, channel_id, u_id)
    return dumps(ret)

# channel_addowner_v1 function wrapper
@APP.route("/channel/addowner/v1", methods=["POST"])
def channel_addowner_v1():
    # Retrieve input
    data = request.get_json()
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    channel_id = data['channel_id']
    u_id = data['u_id']
    # Call channel_addowner with given input
    ret = channel.channel_addowner(auth_user_id, channel_id, u_id)
    # Return nothing (expected)
    return dumps(ret)

# users_all_v1 function wrapper
@APP.route("/users/all/v1", methods=["GET"])
def users_all_v1_http():
    # check if token is valid
    decode_session_token(request.args.get('token', type = str))
    ret = users.users_all_v1()
    return dumps(ret)

# user_profile_setemail_v1 function wrapper
@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def user_profile_setemail_v1():
    data = request.get_json()
    # Get the data from the request
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    email = data['email']
    # Call the function
    ret = user.user_profile_setemail(auth_user_id, email)
    return dumps(ret)

# channel_removeowner_v1 function wrapper 
@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner_v1():
    # Retrieve input
    data = request.get_json()
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    channel_id = data['channel_id']
    u_id = data['u_id']
    # Call channel_removeowner with given input
    ret = channel.channel_removeowner_v1(auth_user_id, channel_id, u_id)
    # Return nothing (expected)
    return dumps(ret)

# user_profile_v1 function wrapper 
@APP.route("/user/profile/v1", methods=["GET"])
def user_profile_v1_http():
    auth_user_id = decode_session_token(request.args.get('token', type = str))['auth_user_id']
    u_id = request.args.get('u_id', type = int)
    ret = user.user_profile_v1(auth_user_id, u_id)
    return dumps(ret)

# user_profile_sethandle_v1 function wrapper 
@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def set_handle_v2():
    # Get the data from the request
    data = request.get_json()
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    # Call the set handle function
    user.set_handle_v1(auth_user_id, data['handle_str'])
    return dumps({})

# auth_logout function wrapper 
@APP.route("/auth/logout/v1", methods=['POST'])
def auth_logout_v1():
    # Get the data from the request
    data = request.get_json()
    # Remove the token fd
    remove_session_token(data['token'])
    return dumps({})

# admin_user_remove function wrapper 
@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def admin_user_remove_v1():
    # Get the data from the request
    data = request.get_json()
    # Remove the token fd
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    admin.admin_user_remove_v1(auth_user_id, data['u_id'])
    return dumps({})

# profile_setname_v1 function wrapper 
@APP.route("/user/profile/setname/v1", methods=['PUT'])
def user_profile_setname_v1():
    # Get the data from the request
    data = request.get_json()
    # Remove the token 
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    name_first = data['name_first']
    name_last = data['name_last']
    # Call the function
    ret = user.profile_setname_v1(auth_user_id, name_first, name_last)
    return dumps(ret)

# message_send_v1 function wrapper 
@APP.route("/message/send/v1", methods=['POST'])
def message_send_v2():
    # Get the data from the request
    data = request.get_json()
    # Remove the token fd
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    message_id = message.message_send_v1(auth_user_id, data['channel_id'], data['message'])
    return dumps(message_id)

# dm_create_v1 function wrapper
@APP.route("/dm/create/v1", methods=['POST'])
def dm_create_v2():
    # Get the data from the request
    data = request.get_json()
    # Remove the token fd
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    dm_id = dm.dm_create_v1(auth_user_id, data['u_ids'])
    return dumps(dm_id)

# dm_messages_v1 function wrapper
@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages_v2():
    # Decode the token
    auth_user_id = decode_session_token(request.args.get('token', type = str))['auth_user_id']
    dm_id = request.args.get('dm_id', type = int)
    start = request.args.get('start', type = int)
    ret = dm.dm_messages_v1(auth_user_id, dm_id, start)
    return dumps(ret)

# admin_user_permissions_change_v1 function wrapper
@APP.route("/admin/userpermission/change/v1", methods=["POST"])
def admin_userpermission_change_v1():
    # Get the data from the request
    data = request.get_json()
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    u_id = data['u_id']
    permission_id = data['permission_id']
    # Call function
    ret = admin.admin_userpermission_change(auth_user_id, u_id, permission_id)
    # Return expected output
    return dumps(ret)

# message/senddm/v1 function wrapper
@APP.route("/message/senddm/v1", methods=["POST"])
def message_senddm_v1():
    # Get the data from the request
    data = request.get_json()
    # Retrieve data
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    dm_id = data['dm_id']
    msg = data['message']
    # Call function 
    ret = message.message_senddm(auth_user_id, dm_id, msg)
    # Return expected output
    return dumps(ret)

# message/remove/v1 function wrapper 
@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove_v2():
    # Get the data from the request
    data = request.get_json()
    # Remove the token fd
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    message.message_remove_v1(auth_user_id, data['message_id'])
    return dumps({})

# message/edit/v1 function wrapper 
@APP.route("/message/edit/v1", methods=['PUT'])
def message_edit_v2():
    # Get the data from the request
    data = request.get_json()
    # Remove the token fd
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    message.message_edit_v1(auth_user_id, data['message_id'], data['message'])
    return dumps({})

# dm/remove/v1 function wrapper 
@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove_v2():
    # Get the data from the request
    data = request.get_json()
    # Remove the token fd
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    dm_id = data['dm_id']
    ret = dm.dm_remove_v1(auth_user_id, dm_id)
    return dumps(ret)

# dm/list/v1 function wrapper 
@APP.route("/dm/list/v1", methods=['GET'])
def dm_list_v2():
    # Get the data from the request
    auth_user_id = decode_session_token(request.args.get('token', type = str))['auth_user_id']    # Remove the token fd
    return dumps(dm.dm_list_v1(auth_user_id))

# dm/details/v1 function wrapper
@APP.route("/dm/details/v1", methods=['GET'])
def dm_details_v1():
    auth_user_id = decode_session_token(request.args.get('token', type = str))['auth_user_id']
    dm_id = request.args.get('dm_id', type = int)
    ret = dm.dm_details_v1(auth_user_id, dm_id)
    return dumps(ret)

# dm_leave_v1 function wrapper
@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave_v2():
    # Get the data from the request
    data = request.get_json()
    # Remove the token fd
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    dm_id = data['dm_id']
    ret = dm.dm_leave_v1(auth_user_id, dm_id)
    return dumps(ret)

# message react function wrapper
@APP.route("/message/react/v1", methods=['POST'])
def message_react_v1():
    # Get the data from the request
    data = request.get_json()
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    message_id = data['message_id']
    react_id = data['react_id']
    # Call function
    ret = message.message_react(auth_user_id, message_id, react_id)
    # Return result
    return dumps(ret)

# message unreact function wrapper
@APP.route("/message/unreact/v1", methods=['POST'])
def message_unreact_v1():
    # Get the data from the request
    data = request.get_json()
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    message_id = data['message_id']
    react_id = data['react_id']
    # Call function
    ret = message.message_unreact(auth_user_id, message_id, react_id)
    # Return result
    return dumps(ret)

# password reset request function wrapper
@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def passwordreset_request_v2():
    # Get the data from the request
    data = request.get_json()

    auth.auth_passwordreset_request_v1(data['email'])

    return dumps({})

# password reset function wrapper
@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def password_reset_v2():
    # Get the data from the request
    data = request.get_json()
    # Reset the password
    auth.auth_passwordreset_reset_v1(data['reset_code'], data['new_password'])
    return dumps({})

@APP.route("/standup/start/v1", methods = ['POST'])
def standup_start_v2():
    # Get the data from the request
    data = request.get_json()
    # Reset the password
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    time_fin = standup.standup_start_v1(auth_user_id, data['channel_id'], data['length'])
    return dumps(time_fin)

@APP.route("/standup/active/v1", methods = ['GET'])
def standup_active_v2():
    # Reset the password
    auth_id = decode_session_token(request.args.get('token', type = str))['auth_user_id']
    channel_id = request.args.get('channel_id', type = int)
    return dumps(standup.standup_active_v1(auth_id, channel_id))

@APP.route("/standup/send/v1", methods = ['POST'])
def standup_send_v2():
    # Get the data from the request
    data = request.get_json()
    # Reset the password
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    standup.standup_send_v1(auth_user_id, data['channel_id'], data['message'])
    return dumps({})


# message pin function wrapper
@APP.route("/message/pin/v1", methods=['POST'])
def message_pin_v1():
    # Fetch the data from the request
    data = request.get_json()
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    message_id = data['message_id']
    # Call function
    ret = message.message_pin(auth_user_id, message_id)
    # Return 
    return dumps(ret)

# message unpin function wrapper
@APP.route("/message/unpin/v1", methods=['POST'])
def message_unpin_v1():
    # Fetch the data from the request
    data = request.get_json()
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    message_id = data['message_id']
    # Call function
    ret = message.message_unpin(auth_user_id, message_id)
    # Return 
    return dumps(ret)

# Search function wrapper 
@APP.route("/search/v1", methods=['GET'])
def search_v1():
    auth_user_id = decode_session_token(request.args.get('token', type = str))['auth_user_id']
    query_str = request.args.get('query_str', type = str)
    ret = other.search_v1(auth_user_id, query_str)
    return dumps(ret)

# message_share_v1 function wrapper
@APP.route("/message/share/v1", methods=['POST'])
def message_share_v1():
    # fetch data
    data = request.get_json()
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    og_message_id = data['og_message_id']
    message_data = data['message']
    channel_id = data['channel_id']
    dm_id = data['dm_id']
    # call function
    ret = message.message_share_v1(auth_user_id, og_message_id, message_data, channel_id, dm_id)
    return dumps(ret)

# message_sendlater_v1 function wrapper
@APP.route("/message/sendlater/v1", methods=['POST'])
def message_sendlater_v1_http():
    # get the data from the request
    data = request.get_json()
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    ret = message.message_sendlater_v1(auth_user_id, data['channel_id'], data['message'], data['time_sent'])
    return dumps(ret)

# message_sendlaterdm_v1 function wrapper
@APP.route("/message/sendlaterdm/v1", methods=['POST'])
def message_sendlaterdm_v1_http():
    # get the data from the request
    data = request.get_json()
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    ret = message.message_sendlaterdm_v1(auth_user_id, data['dm_id'], data['message'], data['time_sent'])
    return dumps(ret)

# get notifications function wrapper 
@APP.route("/notifications/get/v1", methods=['GET'])
def notifications_get_v1():
    auth_user_id = decode_session_token(request.args.get('token', type = str))['auth_user_id']
    ret = other.notifications_get_v1(auth_user_id)
    return dumps(ret)

# user_stats_v1 function wrapper
@APP.route("/user/stats/v1", methods=['GET'])
def user_stats_v1():
    auth_user_id = decode_session_token(request.args.get('token', type = str))['auth_user_id']
    ret = user.user_stats_v1(auth_user_id)
    return dumps(ret)

# Upload photo function wrapper
@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def profile_uploadphoto_v1():
    data = request.get_json()
    auth_user_id = decode_session_token(data['token'])['auth_user_id']
    img_url = data['img_url']
    x_start = data['x_start']
    y_start = data['y_start']
    x_end = data['x_end']
    y_end = data['y_end']
    ret = user.profile_uploadphoto_v1(auth_user_id, img_url, x_start, y_start, x_end, y_end)
    return dumps(ret)

# Returns user profile photos
@APP.route("/static/<path:filename>")
def pfp_return(filename):
    return send_from_directory('', "filename")

# NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully)  # For coverage
    APP.run(port=config.port)  # Do not edit this port
